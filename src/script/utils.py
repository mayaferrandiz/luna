import logging
import os
import re
import subprocess
from pathlib import Path

import yaml
from PIL import Image

from src.script.constants import Files


def setup_logging(name: str):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    return logging.getLogger(name)

def strip_emoji(text: str) -> str:
    """Remove emoji characters from text"""
    emoji_pattern = re.compile("[\U0001F000-\U0001F6FF]|[\U0001F900-\U0001F9FF]|[\u2600-\u26FF]|[\u2700-\u27BF]|[\uFE00-\uFE0F]")
    return emoji_pattern.sub('', text).strip()

def load_template(self, template_name: str) -> str:
    """Load a template file and return its contents"""
    script_dir = Path(__file__).resolve().parent
    templates_dir = script_dir.parent / 'templates'
    template_path = templates_dir / template_name
    try:
        with open(template_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        self.logger.error(f"Template file not found: {template_path}")
        raise

def is_public_github_repo(self, name) -> str:
    project_dir = get_project_path(self, name)
    os.chdir(project_dir)
    visibility = subprocess.run(['gh', 'repo', 'view', '--json', 'visibility', '-q', '.visibility'], capture_output=True, text=True)
    visibility = visibility.stdout.strip().upper()
    if visibility == 'PUBLIC':
        return True
    else:
        return False

def is_project(self, item) -> bool:
    return item.is_dir() and (item / 'content' / Files.METADATA).exists()

def get_media_files(self, name, type):
    project_dir = get_project_path(self, name)
    media_path = project_dir / 'media' / type
    files = []
    if media_path.exists():
        for ext in self.media[type]:
            files.extend(list(media_path.glob(ext)))
    return files

def get_project_metadata(self, name: str) -> yaml:
    project_dir = get_project_path(self, name)
    with open(project_dir / 'content' / Files.METADATA, 'r') as f:
        return yaml.safe_load(f)

def get_project_content(self, name: str) -> str:
    project_dir = get_project_path(self, name)
    with open(project_dir / 'content' / Files.CONTENT, 'r') as f:
        return f.read()

def get_project_readme(self, name: str) -> str:
    project_dir = get_project_path(self, name)
    with open(project_dir / 'content' / Files.README, 'r') as f:
        return f.read()

def get_project_path(self, name: str) -> Path:
    return self.config.base_dir / name

def resize_image_file(image_path, max_width: int=-1, max_height: int=-1):
    with Image.open(image_path) as img:
        # Get original dimensions
        width, height = img.size

        width_ratio = 1 if max_width == -1 else max_width / width
        height_ratio = 1 if max_height == -1 else max_height / height
        
        # Use the smaller ratio to ensure both dimensions fit within maximums
        scale_ratio = min(width_ratio, height_ratio)
        
        # Calculate new dimensions
        new_width = int(width * scale_ratio)
        new_height = int(height * scale_ratio)
                    
        # Resize the image
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return resized_img