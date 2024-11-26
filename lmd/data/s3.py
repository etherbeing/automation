def get_file(url: str):
    import requests
    response = requests.get(url)
    response.raise_for_status()
    return response.content
