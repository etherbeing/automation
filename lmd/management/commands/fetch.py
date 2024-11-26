import logging
import sys
from django.core.management.base import BaseCommand
from lmd.scrappers.main import generate_all_diocesis, generate_rcs
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class Command(BaseCommand):
    help = "Obtiene los datos necesarios para operar el sistema de las discimiles fuentes programadas."
    requires_migrations_checks = True
    stealth_options = ("stdin",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self, *args, **options):
        self.stdin = options.get("stdin", sys.stdin)  # Used for testing
        return super().execute(*args, **options)

    def handle(self, *args, **options):
        # logging.basicConfig(level=logging.DEBUG) # To watch the requests made
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("{task.description}"),
                transient=False,
                expand=True,
            ) as progress:
                total = int("z".encode()[0]) - int("a".encode()[0])
                task_id = progress.add_task(
                    f"Fetching remote resources from official sites...", 
                    total=total,
                    completed=0,
                )
                pr = 0
                for rc in generate_rcs(progress):
                    if rc and rc.municipality:
                        initial = rc.municipality.province.name[0].lower()
                        if initial.isascii():
                            pr = total - (int("z".encode()[0]) - int(initial.encode()[0]))
                    progress.update(task_id, description=f"[progress.percentage]{pr*100/total}%[/progress.percentage] [success]Loaded civil registry: {rc}[/success]", completed=pr)
                
                for dc in generate_all_diocesis():
                    if dc and dc.municipality:
                        initial = dc.municipality.province.name[0].lower()
                    if initial.isascii():
                        pr = total - (int("z".encode()[0]) - int(initial.encode()[0]))
                    progress.update(task_id, description=f"[progress.percentage]{pr*100/total}%[/progress.percentage] [success]Loaded diocesis: {rc}[/success]", completed=pr)
                    
                progress.update(task_id, description="All resources loaded successfully.")
                
        except KeyboardInterrupt:
            logging.warning("Quitting without ending")
            exit(1)
