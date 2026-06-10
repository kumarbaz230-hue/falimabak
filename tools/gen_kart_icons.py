"""Ana sayfa kart ikonları — Android emoji yedeği."""
import os
from PIL import Image, ImageDraw

BASE = os.path.join(os.path.dirname(__file__), '..', 'assets')
os.makedirs(BASE, exist_ok=True)

size = 128
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
# Kurabiye gövdesi
draw.ellipse([18, 38, 110, 112], fill=(196, 142, 58, 255), outline=(255, 215, 0, 255), width=4)
# Kırık çizgi
draw.arc([32, 48, 96, 102], start=210, end=340, fill=(120, 75, 30, 220), width=3)
# Noktalar
for cx, cy in ((45, 72), (70, 85), (88, 68)):
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(90, 55, 20, 200))

out = os.path.join(BASE, 'icon_kurabiye.png')
img.save(out, 'PNG')
print('OK', out)
