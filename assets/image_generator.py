"""
🎨 FalımaBak - Profesyonel Görsel Oluşturucu
Tüm kart görselleri, simgeler ve UI elemanlarını oluşturur
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))

def gradient_renk(draw, x1, y1, x2, y2, renk1, renk2):
    """İki renk arasında gradient oluştur"""
    for y in range(y1, y2):
        ratio = (y - y1) / max((y2 - y1 - 1), 1)
        r = int(renk1[0] * (1 - ratio) + renk2[0] * ratio)
        g = int(renk1[1] * (1 - ratio) + renk2[1] * ratio)
        b = int(renk1[2] * (1 - ratio) + renk2[2] * ratio)
        a = int(renk1[3] * (1 - ratio) + renk2[3] * ratio)
        draw.line([(x1, y), (x2, y)], fill=(r, g, b, a))

def tarot_karti_olustur(kart_adi, sembol, anlam_ozeti, renk="#7c4dff"):
    """Profesyonel tarot kartı görseli"""
    kart = Image.new('RGBA', (220, 340), (0, 0, 0, 0))
    draw = ImageDraw.Draw(kart)
    
    # Gölge
    draw.rounded_rectangle([(8, 8), (215, 335)], radius=15, fill=(0, 0, 0, 80))
    
    # Kart ana rengi
    r, g, b = int(renk[1:3], 16), int(renk[3:5], 16), int(renk[5:7], 16)
    
    # Gradient arka plan
    for y in range(10, 330):
        ratio = (y - 10) / 320
        r2 = min(255, int(r + 100 * ratio))
        g2 = min(255, int(g + 50 * ratio))
        b2 = min(255, int(b + 100 * ratio))
        draw.line([(10, y), (210, y)], fill=(r2, g2, b2, 230))
    
    # Çerçeve
    draw.rounded_rectangle([(10, 10), (210, 330)], radius=12, outline=(255, 215, 0, 200), width=3)
    draw.rounded_rectangle([(15, 15), (205, 325)], radius=10, outline=(255, 215, 0, 50), width=1)
    
    # Üst süsleme
    draw.line([(30, 22), (190, 22)], fill=(255, 215, 0, 150), width=1)
    draw.line([(30, 318), (190, 318)], fill=(255, 215, 0, 150), width=1)
    
    # Sembol
    try:
        font_big = ImageFont.truetype("segoeuiemj.ttf", 72)
        font_mid = ImageFont.truetype("arial.ttf", 18)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except:
        font_big = ImageFont.load_default()
        font_mid = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Büyük sembol
    bbox = draw.textbbox((0, 0), sembol, font=font_big)
    sw = bbox[2] - bbox[0]
    sh = bbox[3] - bbox[1]
    draw.text(((220-sw)//2, 100), sembol, font=font_big, fill=(255, 215, 0, 255))
    
    # Kart ismi
    bbox2 = draw.textbbox((0, 0), kart_adi.upper(), font=font_mid)
    iw = bbox2[2] - bbox2[0]
    draw.text(((220-iw)//2, 200), kart_adi.upper(), font=font_mid, fill=(255, 255, 255, 255))
    
    # Anlam özeti
    bbox3 = draw.textbbox((0, 0), anlam_ozeti, font=font_small)
    aw = bbox3[2] - bbox3[0]
    draw.text(((220-aw)//2, 235), anlam_ozeti, font=font_small, fill=(200, 200, 200, 200))
    
    # Dekoratif yıldızlar
    draw.text((30, 30), "⭐", font=font_small, fill=(255, 215, 0, 100))
    draw.text((170, 30), "⭐", font=font_small, fill=(255, 215, 0, 100))
    draw.text((30, 300), "⭐", font=font_small, fill=(255, 215, 0, 100))
    draw.text((170, 300), "⭐", font=font_small, fill=(255, 215, 0, 100))
    
    dosya_adi = kart_adi.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('ç', 'c').replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ö', 'o') + '.png'
    yol = os.path.join(ASSETS_DIR, dosya_adi)
    kart.save(yol)
    return yol

def splash_goruntusu():
    """Splash ekranı görseli"""
    img = Image.new('RGBA', (400, 780), (13, 2, 33, 255))
    draw = ImageDraw.Draw(img)
    
    # Gradient
    for y in range(780):
        ratio = y / 780
        r = int(13 * (1-ratio) + 26 * ratio)
        g = int(2 * (1-ratio) + 10 * ratio)
        b = int(33 * (1-ratio) + 62 * ratio)
        draw.line([(0, y), (400, y)], fill=(r, g, b))
    
    # Dekoratif daireler
    draw.ellipse([(80, 400), (320, 700)], fill=(124, 77, 255, 20))
    draw.ellipse([(150, 500), (250, 600)], fill=(255, 215, 0, 15))
    draw.ellipse([(-50, 50), (150, 250)], fill=(224, 64, 251, 15))
    
    # Büyük logo
    try:
        font_logo = ImageFont.truetype("arial.ttf", 56)
        font_slogan = ImageFont.truetype("arial.ttf", 18)
        font_version = ImageFont.truetype("arial.ttf", 12)
    except:
        font_logo = ImageFont.load_default()
        font_slogan = ImageFont.load_default()
        font_version = ImageFont.load_default()
    
    # FalımaBak yazısı
    draw.text((70, 320), "🔮", font=font_logo, fill=(255, 215, 0, 255))
    draw.text((140, 330), "FalımaBak", font=font_logo, fill=(255, 215, 0, 255))
    
    # Slogan
    draw.text((110, 400), "Geleceğinizi Keşfedin ✨", font=font_slogan, fill=(255, 128, 171, 255))
    
    # Süsleme
    draw.line([(100, 440), (300, 440)], fill=(255, 215, 0, 100), width=1)
    
    # Versiyon
    draw.text((155, 720), "v2.0", font=font_version, fill=(150, 150, 150, 200))
    
    yol = os.path.join(ASSETS_DIR, "splash.png")
    img.save(yol)
    return yol

def buton_ikonu(icon, renk="#7c4dff"):
    """Buton ikonu oluştur"""
    img = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    r, g, b = int(renk[1:3], 16), int(renk[3:5], 16), int(renk[5:7], 16)
    
    # Daire
    draw.ellipse([(2, 2), (48, 48)], fill=(r, g, b, 180))
    draw.ellipse([(5, 5), (45, 45)], fill=(r, g, b, 120))
    
    # İkon
    try:
        font = ImageFont.truetype("segoeuiemj.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), icon, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((50-w)//2, (50-h)//2), icon, font=font, fill=(255, 255, 255, 255))
    
    return img

def tumunu_olustur():
    """Tüm görselleri oluştur"""
    print("🎨 FalımaBak Görselleri Oluşturuluyor...")
    print("=" * 40)
    
    # Splash
    print("📱 Splash ekranı...", end=" ")
    splash_goruntusu()
    print("✓")
    
    # Tarot Kartları
    print("\n🃏 Tarot Kartları:")
    tarot_kartlari = [
        ("Aşıklar", "💑", "Aşk, uyum, doğru seçim"),
        ("Ölüm", "💀", "Dönüşüm, yeniden doğuş"),
        ("Şans Çarkı", "🎡", "Kader, şans, değişim"),
        ("Güç", "🦁", "Cesaret, irade, güç"),
        ("Yıldız", "⭐", "Umut, ilham, huzur"),
        ("Kule", "🗼", "Yıkım, uyanış, değişim"),
        ("Ay", "🌙", "Sezgi, gizem, bilinçaltı"),
        ("Güneş", "☀️", "Mutluluk, başarı, zafer"),
        ("Adalet", "⚖️", "Denge, hakikat, adalet"),
        ("Büyücü", "🧙", "Yaratıcılık, beceri, irade"),
        ("İmparatoriçe", "👸", "Bereket, annelik, bolluk"),
        ("İmparator", "🤴", "Otorite, disiplin, liderlik"),
        ("Dünya", "🌍", "Başarı, bütünlük, tamamlanma"),
        ("Soytarı", "🎭", "Macera, özgürlük, başlangıç"),
        ("Yüksek Rahibe", "🔮", "Sezgi, bilgelik, gizem"),
        ("Denge", "⚖️", "Adalet, denge, sorumluluk"),
    ]
    
    for isim, sembol, anlam in tarot_kartlari:
        tarot_karti_olustur(isim, sembol, anlam)
        print(f"  ✓ {isim}")
    
    print("\n✅ Tüm görseller başarıyla oluşturuldu!")
    print(f"📁 Dizin: {ASSETS_DIR}")

if __name__ == "__main__":
    tumunu_olustur()