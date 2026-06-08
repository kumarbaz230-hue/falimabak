"""Kart arkası görseli oluştur."""
from PIL import Image, ImageDraw, ImageFont
import os

assets = os.path.join(os.path.dirname(__file__), 'assets')

img = Image.new('RGBA', (220, 340), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Mor gradient arka plan
r, g, b = 124, 77, 255
for y in range(340):
    t = y / 340
    r2 = min(255, int(r + 80 * t))
    g2 = min(255, int(g + 40 * t))
    b2 = min(255, int(b + 80 * t))
    draw.line([(0, y), (220, y)], fill=(r2, g2, b2, 230))

# Altın çerçeve
draw.rounded_rectangle([(5, 5), (215, 335)], radius=12, outline=(255, 215, 0, 180), width=3)

# Desen - büyük soru işareti
try:
    f = ImageFont.truetype("segoeuiemj.ttf", 80)
except:
    f = ImageFont.load_default()

draw.text((70, 100), "🔮", font=f, fill=(255, 215, 0, 200))
draw.text((55, 200), "FAL", font=f, fill=(255, 215, 0, 150))

img.save(os.path.join(assets, 'card_back.png'))
print("✅ card_back.png oluşturuldu")