from django.core.management.base import BaseCommand
import subprocess
from pathlib import Path
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Automatically track static and media files changes in Git'

    def handle(self, *args, **options):
        # Пути к статическим файлам и медиа
        tracked_dirs = [
            str(settings.STATIC_ROOT),
            str(settings.MEDIA_ROOT),
        ]

        changed = False

        for dir_path in tracked_dirs:
            if Path(dir_path).exists():
                result = subprocess.run(['git', 'add', dir_path])
                if result.returncode == 0:
                    changed = True
                    self.stdout.write(f"Added {dir_path} to Git")

        if changed:
            subprocess.run(['git', 'commit', '-m', 'Auto-update static and media files'])
            self.stdout.write(self.style.SUCCESS('Static and media files updated in Git'))
        else:
            self.stdout.write('No static/media files changes detected')