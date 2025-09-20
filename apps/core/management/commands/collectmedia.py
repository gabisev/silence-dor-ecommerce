import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Collect media files to staticfiles directory for production'

    def handle(self, *args, **options):
        self.stdout.write('Collecting media files...')
        
        # Source and destination directories
        media_root = settings.MEDIA_ROOT
        static_root = settings.STATIC_ROOT
        static_dirs = getattr(settings, 'STATICFILES_DIRS', [])
        
        if not os.path.exists(static_root):
            os.makedirs(static_root)
            
        # Create media directory in staticfiles
        media_dest = os.path.join(static_root, 'media')
        if not os.path.exists(media_dest):
            os.makedirs(media_dest)
            
        # Copy media files if media root exists
        if os.path.exists(media_root):
            try:
                for root, dirs, files in os.walk(media_root):
                    for file in files:
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, media_root)
                        dest_path = os.path.join(media_dest, rel_path)
                        
                        # Create destination directory if it doesn't exist
                        dest_dir = os.path.dirname(dest_path)
                        if not os.path.exists(dest_dir):
                            os.makedirs(dest_dir)
                            
                        # Copy file
                        shutil.copy2(src_path, dest_path)
                        self.stdout.write(f'Copied media: {rel_path}')
                        
                self.stdout.write(
                    self.style.SUCCESS('Successfully collected media files')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error collecting media files: {e}')
                )
        else:
            self.stdout.write(
                self.style.WARNING(f'Media root {media_root} does not exist')
            )
            
        # Copy static files to ensure they're available
        for static_dir in static_dirs:
            if os.path.exists(static_dir):
                try:
                    for root, dirs, files in os.walk(static_dir):
                        for file in files:
                            src_path = os.path.join(root, file)
                            rel_path = os.path.relpath(src_path, static_dir)
                            dest_path = os.path.join(static_root, rel_path)
                            
                            # Create destination directory if it doesn't exist
                            dest_dir = os.path.dirname(dest_path)
                            if not os.path.exists(dest_dir):
                                os.makedirs(dest_dir)
                                
                            # Copy file
                            shutil.copy2(src_path, dest_path)
                            self.stdout.write(f'Copied static: {rel_path}')
                            
                    self.stdout.write(
                        self.style.SUCCESS('Successfully collected static files')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error collecting static files: {e}')
                    )
