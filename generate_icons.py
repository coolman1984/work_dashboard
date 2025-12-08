import os
from PIL import Image, ImageDraw

ICONS_DIR = "icons"
if not os.path.exists(ICONS_DIR):
    os.makedirs(ICONS_DIR)

icon_specs = {
    'folder.png': '#F8D775',
    'document.png': '#A0C5E8',
    'spreadsheet.png': '#107C10',
    'image.png': '#B146C2',
    'code.png': '#ECE05D',
    'archive.png': '#E0E0E0',
    'executable.png': '#888888',
    'audio.png': '#0078D4',
    'video.png': '#E34F26',
    'file.png': '#CCCCCC'
}

size = (16, 16)

for filename, color in icon_specs.items():
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Draw a simple rounded rectangle or just a rectangle
    draw.rectangle([2, 2, 14, 14], fill=color, outline=None)
    
    path = os.path.join(ICONS_DIR, filename)
    img.save(path)
    print(f"Generated {path}")
