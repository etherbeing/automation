from http import HTTPStatus
import json
import logging
import re
import time
import requests
from urllib.parse import urljoin, parse_qs

from rich.progress import Progress
from lmd.consts.base import BASE_URL, CACHE_TIME, DIOCESIS_BASE_URL, I18N_STANDARD, MAX_RETRIES, TIMEWAIT, USER_AGENT
from lmd.models import DiocesisModel, MunicipalityModel, ProvinceModel, RegistroCivilModel
from lmd.data.provinces import PROVINCES
from base.redis import redis_instance
from bs4 import BeautifulSoup, ResultSet
from typing import Any, Optional


# Regex to capture most RFC-compliant emails
email_regex = r"""
[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+       # Local part: letters, digits, and special characters
@
(?:[a-zA-Z0-9-]+\.)+                   # Domain part: subdomains separated by dots
[a-z]{2,}                          # Top-level domain (e.g., .com, .org)
"""
# Multiline and verbose mode for better readability
compiled_email_regex = re.compile(email_regex, re.VERBOSE)
# Regex for Spanish phone numbers
phone_regex = r"""
(?:\+34|0034)?                     # Optional country code (+34 or 0034)
[ -.]?                             # Optional separator after country code
(?:\d{9}                           # 9-digit numbers without separators
|(?:\d{3}[ -.]?\d{3}[ -.]?\d{3}))  # 9-digit numbers with separators
"""
# Multiline and verbose mode for better readability
compiled_phone_regex = re.compile(phone_regex, re.VERBOSE)
class InconsistentLayout(Exception):
    pass

def get_rc_details(
        municipality: MunicipalityModel, 
        progress: Optional[Progress] = None,
    ) -> dict|None:
    task = None
    if progress:
        task = progress.add_task("Obtaining registry details")
    redis_key = f"details-{municipality}"
    details = redis_instance.get(redis_key)
    if details:
        if progress and task:
            progress.update(task, description="Loaded registry from redis cache")
        details = json.loads(details) # type: ignore
    elif municipality.official_link:
        details = {}
        res = None
        model = RegistroCivilModel.objects.filter(municipality=municipality)
        if model and model.exists():
            details = model.values("address", "fax", "phone", "email", "postal_code", "locality")[0]
        else:
            for _ in range(MAX_RETRIES):
                time.sleep(TIMEWAIT) # To avoid loading the servers with too much requests
                if progress and task:
                    progress.update(task, description="Fetching resources remotely")
                res = requests.get(url=municipality.official_link, headers={
                    "User-Agent": USER_AGENT
                })
                if res.ok:
                    break
                if res.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                    res.raise_for_status()
                time.sleep(0.75)
            else:
                if progress and task:
                    progress.update(task, description=f"Registry {municipality} cannot be fetched successfuly")
                    progress.remove_task(task)
                logging.error(f"Error while fetching the data for municipality {municipality}")
                return None
            html = BeautifulSoup(res.text, "html.parser")
            ul = html.find(attrs={"class": "listado_05"}, recursive=True)
            if not ul:
                if progress and task:
                    progress.update(task, description=f"Registry {municipality} cannot be fetched successfuly")
                    progress.remove_task(task)
                try:
                    link = html.find(text="Registro Civil: ", recursive=True)
                    if not link:
                        link = html.find(text="REGISTRO CIVIL", recursive=True)
                    link = link.parent.find("a").attrs.get("href") # type: ignore
                    
                    time.sleep(TIMEWAIT) # To avoid loading the servers with too much requests
                    res = requests.get(
                        link,  # type: ignore
                        headers={
                        "User-Agent": USER_AGENT
                    })
                    html = BeautifulSoup(res.text, "html.parser")
                    ul = html.find(attrs={"class": "listado_05"}, recursive=True)
                except Exception:
                    return None

            additional_content = ul.find("ul", recursive=False) # type: ignore
            children = (
                (ul.find_all('li', recursive=False) or []) + # type: ignore
                (additional_content and additional_content.find_all("li") or []) # type: ignore
            )
            for child in children: 
                multiple = child.find("ul")
                value = None # type: ignore
                
                name = child.find("strong")
                if not name:
                    name = child.get_text()
                else:
                    name = name.get_text().strip().strip("\"").strip(':') # type: ignore
                name: str = re.sub(r"[\ \n\t]", "", name)
                
                if multiple:
                    value: list = [] # type: ignore
                    for li in multiple.find_all("li"):
                        v: str = li.get_text()
                        v = re.sub(r"[\ ]+", " ", v)
                        v = re.sub(r"[\n]+", "\n", v)
                        v = re.sub(r"([\t]+)|([\"\'])|([\"\']$)", "", v)
                        v = v.strip()
                        value.append(v) # type: ignore
                else:
                    value: str = child.get_text().split(":", 1)[-1].strip()
                    value = re.sub(r"[\ ]+", " ", value)
                    value = re.sub(r"[\n]+", "\n", value)
                    value = re.sub(r"([\t]+)|([\"\'])|([\"\']$)", "", value)
                    value = value.strip()

                details[I18N_STANDARD[name.lower()]] = value
            
            if progress and task:
                progress.update(task, description="Storing registry in cache")
        redis_instance.set(redis_key, json.dumps(details), ex=CACHE_TIME)
    else:
        details = None
    if progress and task:
        progress.update(task, description=f"Registry {municipality} fetched successfuly")
        progress.remove_task(task)
    return details

def get_provinces():
    return PROVINCES

def get_province(province_id: str):
    return ProvinceModel.objects.filter(id=province_id).first()

def generate_provinces():
    for province in get_provinces():
        yield ProvinceModel.objects.get_or_create(
            id=province.get('value'),
            name=province.get('label'),
        )[0]

def get_municipalities(province_id: str, progress: Optional[Progress] = None):
    task = None
    if progress:
        task = progress.add_task(f"Fetching municipalities for province {province_id}")
    redis_key = f"province-{province_id}"
    municipalities = redis_instance.get(redis_key)
    if not municipalities:
        # First try to look for it in the DB
        municipalities = []
        province = ProvinceModel.objects.filter(id=province_id)
        if province.exists():
            municipalities = list(province.first().municipalities.values("official_link", "name", "id")) # type: ignore
            if progress and task:
                progress.update(task, description="Storing municipalities in cache")
            redis_instance.set(redis_key, json.dumps(municipalities), ex=CACHE_TIME)
        else:
            url = "https://www.mjusticia.gob.es/BUSCADIR/ServletControlador"
            params = {
                "apartado":"buscadorMunicipios",
                "tipo":"RC",
                "lang":"es_es",
                "URL_ORIGEN": "",
                "origen":"G",
                "provincia": province_id 
            }
            
            time.sleep(TIMEWAIT) # To avoid loading the servers with too much requests
            if progress and task:
                progress.update(task, description="Fetching municipalities from network")
            res = requests.get(url=url, params=params, headers={
                "User-Agent": USER_AGENT
            })
            res.raise_for_status()
            html = BeautifulSoup(res.text, "html5lib")
            el = html.find(attrs={
                "class": "listado_02"
            }, recursive=True)
            if el:
                elements: ResultSet[Any] = el.find_all("a") # type: ignore
                for a in elements:
                    link = urljoin(BASE_URL, a.attrs.get("href"))
                    id = parse_qs(link).get("municipio")
                    if type(id) == list:
                        id = id[0]
                    municipalities.append(
                        {
                            "official_link": link,
                            "name": a.get_text(),
                            "id": id,
                        }
                    )
                if progress and task:
                    progress.update(task, description="Storing municipalities in cache")
                redis_instance.set(redis_key, json.dumps(municipalities), ex=CACHE_TIME)
            else:
                # Alternative Operation
                if progress and task:
                    progress.update(task, description="Using alternative branch due to non standard data layout")
                name = html.find("h3")
                municipalities.append(
                    {
                        "official_link": res.request.url,
                        "name": name and name.text,
                        "id": province_id,
                    }
                )
    else:
        if progress and task:
            progress.update(task, description="Municipalities retrieved from cache")
        municipalities = json.loads(municipalities) # type: ignore
    if progress and task:
        progress.remove_task(task)
    return municipalities    

def generate_municipalities():
    for province in generate_provinces():
        for municipality in get_municipalities(province_id=province.id):
            yield MunicipalityModel.objects.update_or_create(
                id=municipality.get('id', province.id),
                province=province,
                defaults=dict(
                    official_link=municipality.get("official_link"),
                    name=municipality.get('name'),
                )
            )[0]

def generate_rcs(progress: Optional[Progress]=None):
    task = None
    if progress:
        task = progress.add_task("Generating Civil Registries",)
    for municipality in generate_municipalities():
        if progress and task:
            progress.update(task, description=f"[info]Loading civil registries for {municipality}[/info]")
        rc = get_rc_details(municipality=municipality, progress=progress)
        if rc:
            yield RegistroCivilModel.objects.get_or_create(
                municipality=municipality,
                email=rc.get('email'),
                phone=rc.get('phone', [None])[0] if type(rc.get('phone')) == list else rc.get('phone'),
                locality=rc.get('locality'),
                address=rc.get('address'),
                postal_code=rc.get('postal_code'),
                fax=rc.get('fax', [None])[0] if type(rc.get('phone')) == list else rc.get('fax'),
            )[0]
        else:
            logging.warning(f"{municipality.official_link} : Not operable")
            yield None

    if task and progress:
        progress.remove_task(task)

def get_all_rc_details():
    for province in get_provinces():
        p = province.get("value", None)
        if not p:
            continue
        for municipality in get_municipalities(province_id=p):
            municipality = MunicipalityModel.objects.filter(id=municipality.get("id")).first()
            if municipality:
                yield get_rc_details(municipality=municipality)
            else:
                yield None
    yield None

def get_rc_by_province(province: str):
    for municipality in get_municipalities(province_id=province):
        municipality = MunicipalityModel.objects.filter(id=municipality.get("id")).first()
        if municipality:
            yield get_rc_details(municipality=municipality)
        else:
            yield None

def get_all_diocesis():
    redis_key = "diocesis"
    diocesis = redis_instance.get(redis_key)
    if diocesis:
        diocesis = json.loads(diocesis) # type: ignore
    else:
        logging.info("In network block, a network operation will be made for getting all diocesis")
        diocesis = []
        time.sleep(TIMEWAIT) # To avoid loading the servers with too much requests
        res = requests.get(urljoin(DIOCESIS_BASE_URL, "/diocesis/"), headers={
                "User-Agent": USER_AGENT
            })
        bs = BeautifulSoup(res.text, "html5lib")
        table = bs.find(attrs={
            'class': "wp-block-table"
        })
        if table:
            data = table.find_all("a") # type: ignore
            for diocesis_element in data:
                diocesis.append({
                    "name": diocesis_element.get_text(),
                    "link": diocesis_element.attrs.get("href")
                })
            redis_instance.set(redis_key, json.dumps(diocesis), ex=CACHE_TIME)
    return diocesis

def get_diocesis_details(diocesis: dict):
    redis_key = f"diocesis-{diocesis.get("name")}"
    details = redis_instance.get(redis_key)
    if details:
        return json.loads(details) # type: ignore
    model = DiocesisModel.objects.filter(name=diocesis.get("name"))
    if model.exists():
        return model.values("name", "phone", "email", "address")[0]
    time.sleep(TIMEWAIT)
    link = diocesis.get("link")
    if not link:
        return None
    res = requests.get(link, headers={
        "User-Agent": USER_AGENT
    })
    res.raise_for_status()
    b4 = BeautifulSoup(res.text, "html5lib")
    content = b4.find(attrs={"class": "entry-content"})
    if content:
        ct = content.get_text()
        st = "Contacto: "
        if st in ct:
            ct = ct[ct.index(st)+len(st): -1].strip()
        else:
            st = "Calle "
            ct = ct[ct.index(st): -1].strip()
        emails = compiled_email_regex.findall(ct)
        phones = compiled_phone_regex.findall(ct)
        address = None
        if phones: # for the case of /ordinariato-para-los-catolicos-orientales-en-espana/ as there is neither a phone nor any address
            address = ct[:ct.index(phones[0])]
        details = dict(
            name=diocesis.get('name'),
            phone=[phone.strip() for phone in phones],
            email=emails[0],
            address=address,
        )
        redis_instance.set(redis_key, json.dumps(details), ex=CACHE_TIME)
        return details
    else:
        return None

def generate_all_diocesis():
    for diocesis in get_all_diocesis():
        details = get_diocesis_details(diocesis=diocesis)
        if not details:
            logging.warning(f"Skipped diocesis with name {diocesis}")
            continue
        else:
            municiaplity = MunicipalityModel.objects.filter(name__in=details.get("address") or []).first()
            phone = details.get("phone")
            extra_phone = None
            if phone:
                if len(phone) > 1:
                    extra_phone = phone[1]
                phone = phone[0]
            diocesis_model = DiocesisModel.objects.get_or_create(
                name=diocesis.get('name'),
                defaults=dict(
                    phone=phone,
                    extra_phone=extra_phone,
                    email=details.get("email",),
                    municipality=municiaplity
                )
            )
            yield diocesis_model[0]