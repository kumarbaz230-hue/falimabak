"""
🎨 FalımaBak - 1080p Profesyonel Görsel Oluşturucu
Tüm kart görselleri 1080p kalitede, belirgin texture ve yazılarla
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os, random, math

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
os.makedirs(ASSETS, exist_ok=True)
WIN_FONTS = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts')


def font_yukle(adi, boyut):
    for yol in (
        os.path.join(WIN_FONTS, adi),
        adi,
    ):
        if os.path.isfile(yol):
            return ImageFont.truetype(yol, boyut)
    return ImageFont.load_default()

def yazi_olc(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def golge_ekle(im, offset=(6,6), blur=12):
    """Gerçekçi gölge efekti"""
    shadow = Image.new('RGBA', im.size, (0,0,0,0))
    shadow.paste(im, (-offset[0], -offset[1]))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    result = Image.new('RGBA', im.size, (0,0,0,0))
    result.paste(shadow, (0,0), shadow)
    result.paste(im, (0,0), im)
    return result

def texture_ekle(draw, w, h, renk_hex, yogunluk=40):
    """Kartın üzerine desen/doku efekti ekle"""
    r, g, b = int(renk_hex[1:3],16), int(renk_hex[3:5],16), int(renk_hex[5:7],16)
    for _ in range(yogunluk):
        x = random.randint(20, w-20)
        y = random.randint(20, h-20)
        opacity = random.randint(5, 15)
        size = random.randint(1, 3)
        draw.ellipse([(x,y),(x+size,y+size)], fill=(min(255,r+50), min(255,g+50), min(255,b+50), opacity))
    
    # Çizgi desenleri
    for i in range(8):
        y = random.randint(50, h-50)
        draw.line([(10, y), (w-10, y)], fill=(min(255,r+30), min(255,g+30), min(255,b+30), 8), width=1)

def profesyonel_tarot_karti(isim, sembol, aciklama, renk_hex="#7c4dff"):
    """1080p profesyonel tarot kartı"""
    # 1080p çözünürlük (3x büyütülmüş)
    scale = 3
    w, h = 240 * scale, 380 * scale  # 720 x 1140
    
    img = Image.new('RGBA', (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    r = int(renk_hex[1:3], 16)
    g = int(renk_hex[3:5], 16)
    b = int(renk_hex[5:7], 16)
    
    # Gölge
    draw.rounded_rectangle([(18,18),(w-18,h-18)], radius=54, fill=(0,0,0,120))
    
    # Gradient arkaplan
    for y in range(h):
        t = y / h
        r2 = min(255, int(r + 180*t))
        g2 = min(255, int(g + 90*t))
        b2 = min(255, int(b + 180*t))
        draw.line([(12,y),(w-12,y)], fill=(r2,g2,b2,240))
    
    # Kart texture deseni
    texture_ekle(draw, w, h, renk_hex, 60)
    
    # Altın çerçeve (dış - kalın)
    draw.rounded_rectangle([(12,12),(w-12,h-12)], radius=54, outline=(255,215,0,220), width=9)
    # İç çerçeve (ince)
    draw.rounded_rectangle([(36,36),(w-36,h-36)], radius=36, outline=(255,215,0,60), width=3)
    
    # Köşe süslemeleri (büyük)
    for (cx, cy) in [(45,45),(w-45,45),(45,h-45),(w-45,h-45)]:
        draw.ellipse([(cx-15,cy-15),(cx+15,cy+15)], fill=(255,215,0,140))
        draw.ellipse([(cx-8,cy-8),(cx+8,cy+8)], fill=(255,215,0,200))
    
    # Kenar çizgileri
    draw.line([(60,54),(w-60,54)], fill=(255,215,0,100), width=2)
    draw.line([(60,h-54),(w-60,h-54)], fill=(255,215,0,100), width=2)
    
    f_big = font_yukle('segoeuiemj.ttf', 200)
    f_title = font_yukle('segoeuib.ttf', 52)
    f_desc = font_yukle('segoeui.ttf', 28)
    f_star = font_yukle('segoeuiemj.ttf', 40)
    
    # Büyük sembol (ortada)
    bw, bh = yazi_olc(draw, sembol, f_big)
    draw.text(((w-bw)//2, h//2 - 150), sembol, font=f_big, fill=(255,215,0,255))
    
    # Sembol gölgesi
    draw.text(((w-bw)//2 + 4, h//2 - 146), sembol, font=f_big, fill=(0,0,0,80))
    draw.text(((w-bw)//2, h//2 - 150), sembol, font=f_big, fill=(255,215,0,255))
    
    # Kart ismi (büyük harf, altın renkli)
    isim_up = isim.upper()
    
    # İsim için yarı saydam arka plan
    iw, ih = yazi_olc(draw, isim_up, f_title)
    # Arka plan dikdörtgeni
    arka_x = (w - iw - 60) // 2
    arka_y = h - 180
    draw.rectangle([(arka_x-10, arka_y-5), (arka_x+iw+70, arka_y+ih+15)], fill=(0,0,0,180), outline=(255,215,0,100), width=2)
    
    # İsim yazısı - PARLAK ALTIN
    draw.text((arka_x, arka_y), isim_up, font=f_title, fill=(255,215,0,255))
    # İkinci kat (daha parlak)
    draw.text((arka_x+2, arka_y+1), isim_up, font=f_title, fill=(255,236,110,255))
    
    # Altın ayraç
    draw.line([(w//2-100, h-130), (w//2+100, h-130)], fill=(255,215,0,120), width=2)
    
    # Açıklama - belirgin
    aw, ah = yazi_olc(draw, aciklama, f_desc)
    desc_x = (w - aw) // 2
    draw.text((desc_x, h-110), aciklama, font=f_desc, fill=(200,200,200,220))
    
    # ★ süslemeleri
    draw.text((40, 40), "⭐", font=f_star, fill=(255,215,0,90))
    draw.text((w-70, 40), "⭐", font=f_star, fill=(255,215,0,90))
    draw.text((40, h-70), "⭐", font=f_star, fill=(255,215,0,90))
    draw.text((w-70, h-70), "⭐", font=f_star, fill=(255,215,0,90))
    
    # Gölge ekle
    img = golge_ekle(img)
    
    # Kaydet (1080p PNG)
    dosya = isim.lower().replace(' ','_').replace('ç','c').replace('ı','i').replace('ğ','g').replace('ü','u').replace('ş','s').replace('ö','o') + '.png'
    img.save(os.path.join(ASSETS, dosya), 'PNG')
    print(f"  ✓ {isim} (720x1140)")

def menü_ikonlari():
    """1080p menü ikonları"""
    ikonlar = {
        'tarot': ('🃏', '#7c4dff'),
        'kahve': ('☕', '#ff9100'),
        'astroloji': ('⭐', '#40c4ff'),
        'elfali': ('👐', '#e040fb'),
        'diger': ('✨', '#00e676'),
    }
    
    for isim, (sembol, renk) in ikonlar.items():
        size = 200
        img = Image.new('RGBA', (size, size), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        
        r, g, b = int(renk[1:3],16), int(renk[3:5],16), int(renk[5:7],16)
        
        # Gradient daire
        for y in range(size):
            t = y / size
            r2 = min(255, int(r + 80 * t))
            g2 = min(255, int(g + 40 * t))
            b2 = min(255, int(b + 80 * t))
            draw.line([(8, y), (size-8, y)], fill=(r2, g2, b2, 220))
        
        # Çerçeve
        draw.ellipse([(5, 5), (size-5, size-5)], outline=(255,255,255,120), width=4)
        draw.ellipse([(10, 10), (size-10, size-10)], outline=(255,215,0,60), width=2)
        
        f = font_yukle('segoeuiemj.ttf', 90)
        
        sw, sh = yazi_olc(draw, sembol, f)
        draw.text(((size-sw)//2, (size-sh)//2 - 5), sembol, font=f, fill=(255,255,255,255))
        
        # Gölge
        shadow = img.filter(ImageFilter.GaussianBlur(6))
        result = Image.new('RGBA', (size+20, size+20), (0,0,0,0))
        result.paste(shadow, (10, 10), shadow)
        result.paste(img, (10, 10), img)
        result.save(os.path.join(ASSETS, f'icon_{isim}.png'))
        
        print(f"  ✓ icon_{isim}.png (200x200)")

def splash_1080p():
    """1080p splash ekranı"""
    w, h = 1200, 2340  # 3x scale
    img = Image.new('RGBA', (w, h), (13,2,33,255))
    draw = ImageDraw.Draw(img)
    
    # Gradient
    for y in range(h):
        t = y/h
        r = int(13*(1-t) + 36*t)
        g = int(2*(1-t) + 15*t)
        b = int(33*(1-t) + 90*t)
        draw.line([(0,y),(w,y)], fill=(r,g,b))
    
    # Dekoratif daireler
    draw.ellipse([(180,1050),(1020,1950)], fill=(124,77,255,18))
    draw.ellipse([(390,1290),(810,1710)], fill=(255,215,0,12))
    draw.ellipse([(-240,60),(540,840)], fill=(224,64,251,12))
    
    # Küçük yıldızlar
    for i in range(60):
        x = random.randint(20, w-20)
        y = random.randint(20, h-20)
        s = random.randint(2, 6)
        draw.ellipse([(x,y),(x+s,y+s)], fill=(255,255,255,random.randint(20,80)))
    
    f_emoji = font_yukle('segoeuiemj.ttf', 140)
    f_title = font_yukle('segoeuib.ttf', 96)
    f_slogan = font_yukle('segoeui.ttf', 42)
    f_ver = font_yukle('segoeui.ttf', 30)

    baslik = 'FalımaBak'
    slogan = 'Geleceğinizi Keşfedin'

    tw, th = yazi_olc(draw, baslik, f_title)
    sw, sh = yazi_olc(draw, slogan, f_slogan)
    cx = w // 2

    emoji_y = h // 2 - 120
    draw.text((cx - 70, emoji_y + 3), '🔮', font=f_emoji, fill=(0, 0, 0, 90))
    draw.text((cx - 73, emoji_y), '🔮', font=f_emoji, fill=(255, 215, 0, 255))

    title_x = cx - tw // 2
    title_y = emoji_y + 150
    draw.text((title_x + 3, title_y + 3), baslik, font=f_title, fill=(0, 0, 0, 100))
    draw.text((title_x, title_y), baslik, font=f_title, fill=(255, 215, 0, 255))

    slogan_x = cx - sw // 2
    slogan_y = title_y + th + 40
    draw.text((slogan_x, slogan_y), slogan, font=f_slogan, fill=(255, 128, 171, 255))

    draw.line([(cx - 220, slogan_y + sh + 30), (cx + 220, slogan_y + sh + 30)], fill=(255, 215, 0, 90), width=3)

    ver = 'v2.0'
    vw, vh = yazi_olc(draw, ver, f_ver)
    draw.text((cx - vw // 2, h - 120), ver, font=f_ver, fill=(150, 150, 150, 180))
    
    img = img.resize((400, 780), Image.LANCZOS)
    img.save(os.path.join(ASSETS, 'splash.png'))
    print("  ✓ Splash (400x780)")

def main():
    print("""
╔══════════════════════════════════════════╗
║  🎨 FALIMABAK 1080p ASSET ÜRETİCİ      ║
╚══════════════════════════════════════════╝
    """)
    
    print("📱 Splash Ekranı:", end=" ")
    splash_1080p()
    
    print("\n🔘 Menü İkonları:")
    menü_ikonlari()
    
    print("\n🃏 Tarot Kartları (1080p - 720x1140):")
    tarot_list = [
        ("Aşıklar","💑","Aşk, uyum, doğru seçim"),
        ("Ölüm","💀","Dönüşüm, yeniden doğuş"),
        ("Şans Çarkı","🎡","Kader, şans, değişim"),
        ("Güç","🦁","Cesaret, irade, güç"),
        ("Yıldız","⭐","Umut, ilham, huzur"),
        ("Kule","🗼","Yıkım, uyanış, değişim"),
        ("Ay","🌙","Sezgi, gizem, bilinçaltı"),
        ("Güneş","☀️","Mutluluk, başarı, zafer"),
        ("Büyücü","🧙","Yaratıcılık, beceri"),
        ("İmparatoriçe","👸","Bereket, annelik, bolluk"),
        ("İmparator","🤴","Otorite, disiplin, liderlik"),
        ("Dünya","🌍","Başarı, bütünlük"),
        ("Soytarı","🎭","Macera, özgürlük"),
        ("Yüksek Rahibe","🔮","Sezgi, bilgelik, gizem"),
        ("Denge","⚖️","Adalet, denge"),
        ("Adalet","⚖️","Hakikat, sorumluluk"),
    ]
    
    renkler = ["#7c4dff","#e74c3c","#f39c12","#2ecc71","#3498db","#e040fb","#00e5ff","#ff9100"]
    for i, (isim, sembol, aciklama) in enumerate(tarot_list):
        renk = renkler[i % len(renkler)]
        profesyonel_tarot_karti(isim, sembol, aciklama, renk)
    
    print(f"""
╔══════════════════════════════════════════╗
║  ✅ TÜM 1080p ASSETLER HAZIR!          ║
║  📁 {ASSETS}  ║
║  📦 {len([f for f in os.listdir(ASSETS) if f.endswith('.png')])} yüksek kalite asset  ║
╚══════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    main()