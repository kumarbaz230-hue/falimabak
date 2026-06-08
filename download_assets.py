"""
🌐 FalımaBak - Gerçek Asset İndirici
Ücretsiz API'lerden profesyonel görseller indirir.
"""

import os, requests, random, io
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
os.makedirs(ASSETS, exist_ok=True)

def download_image(url, filename, size=None):
    """URL'den resim indir ve kaydet"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            img = Image.open(io.BytesIO(r.content))
            if size:
                img = img.resize(size, Image.LANCZOS)
            # RGBA'ya çevir
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            img.save(os.path.join(ASSETS, filename), 'PNG')
            return True
    except Exception as e:
        print(f"  ⚠ İndirme hatası ({filename}): {e}")
    return False

def fix_text_visibility_on_images():
    """Tüm kart görsellerindeki yazıları daha belirgin yap"""
    assets_dir = ASSETS
    for f in os.listdir(assets_dir):
        if not f.endswith('.png') or f.startswith('icon_') or f in ['splash.png', 'kahve_fincani.png', 'el_ornek.png', 'yildiz_deseni.png']:
            continue
        if f == 'icon_astroloji.png' or f == 'icon_diger.png' or f == 'icon_elfali.png' or f == 'icon_kahve.png' or f == 'icon_tarot.png':
            continue
        
        path = os.path.join(assets_dir, f)
        try:
            img = Image.open(path).convert('RGBA')
            draw = ImageDraw.Draw(img)
            
            # Görsel boyutlarını al
            w, h = img.size
            
            try:
                fnt = ImageFont.truetype("arial.ttf", 20)
                fnt_small = ImageFont.truetype("arial.ttf", 14)
            except:
                fnt = ImageFont.load_default()
                fnt_small = fnt
            
            # Her görsele kart ismini belirgin şekilde yaz
            kart_adi = os.path.splitext(f)[0].replace('_', ' ').upper()
            
            # Beyaz arka plan üzerine siyah yazı veya siyah arka plan üzerine beyaz yazı
            # Önce yazıyı ölç
            bbox = draw.textbbox((0, 0), kart_adi, font=fnt)
            tw = bbox[2] - bbox[0] + 20
            th = bbox[3] - bbox[1] + 10
            
            # Alt kısma yarı saydam siyah bant ekle
            y_pos = h - 50
            draw.rectangle([(10, y_pos-5), (w-10, y_pos+th)], fill=(0, 0, 0, 180))
            
            # Altın renkli, belirgin yazı
            x_pos = (w - tw) // 2
            draw.text((x_pos, y_pos), kart_adi, font=fnt, fill=(255, 215, 0, 255))
            
            img.save(path, 'PNG')
            print(f"  ✓ {f} - yazı eklendi")
        except Exception as e:
            print(f"  ⚠ {f}: {e}")

def create_professional_assets():
    """Profesyonel kalitede assetler oluştur"""
    print("""
╔══════════════════════════════════════╗
║  🌐 FALIMABAK PROFESYONEL ASSETLER  ║
╚══════════════════════════════════════╝
    """)
    
    # 1. KART GÖRSELLERİNİ DÜZELT
    print("📝 Kart yazıları düzeltiliyor...")
    fix_text_visibility_on_images()
    
    # 2. SPLASH EKRANINI YENİLE
    print("\n🖼 Splash ekranı yenileniyor...")
    # Unsplash'ten rastgele mistik görsel
    splash_urls = [
        "https://images.unsplash.com/photo-1507146426996-ef05306b995a?w=400",  # Kristal küre
        "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=400",  # Yıldızlar
        "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=400",  # Astroloji
    ]
    
    try:
        # splash.png üzerine logo ekle (indirme çalışmazsa)
        splash = Image.open(os.path.join(ASSETS, 'splash.png')).convert('RGBA')
        draw = ImageDraw.Draw(splash)
        
        # Daha belirgin logo
        try:
            f1 = ImageFont.truetype("arial.ttf", 58)
            f2 = ImageFont.truetype("arial.ttf", 20)
        except:
            f1 = f2 = ImageFont.load_default()
        
        # Gölgeli yazı
        draw.text((73, 313), "🔮", font=f1, fill=(0, 0, 0, 100))
        draw.text((138, 328), "FalımaBak", font=f1, fill=(0, 0, 0, 100))
        draw.text((72, 312), "🔮", font=f1, fill=(255, 215, 0, 255))
        draw.text((137, 327), "FalımaBak", font=f1, fill=(255, 215, 0, 255))
        
        splash.save(os.path.join(ASSETS, 'splash.png'))
        print("  ✓ Splash güncellendi")
    except Exception as e:
        print(f"  ⚠ Splash hatası: {e}")
    
    # 3. MENÜ İKONLARINI YENİLE
    print("\n🔘 Menü ikonları yenileniyor...")
    ikon_renk = {
        'tarot': ('🃏', '#7c4dff'),
        'kahve': ('☕', '#ff9100'),
        'astroloji': ('⭐', '#40c4ff'),
        'elfali': ('👐', '#e040fb'),
        'diger': ('✨', '#00e676'),
    }
    
    for isim, (sembol, renk) in ikon_renk.items():
        img = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        r, g, b = int(renk[1:3], 16), int(renk[3:5], 16), int(renk[5:7], 16)
        
        # Gradient daire
        for y in range(100):
            t = y / 100
            r2 = min(255, int(r + 60 * t))
            g2 = min(255, int(g + 30 * t))
            b2 = min(255, int(b + 60 * t))
            draw.line([(5, y), (95, y)], fill=(r2, g2, b2, 200))
        
        # Çerçeve
        draw.ellipse([(3, 3), (97, 97)], outline=(255, 255, 255, 100), width=2)
        
        try:
            f = ImageFont.truetype("segoeuiemj.ttf", 42)
        except:
            f = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), sembol, font=f)
        sw = bbox[2] - bbox[0]
        sh = bbox[3] - bbox[1]
        draw.text(((100-sw)//2, (100-sh)//2), sembol, font=f, fill=(255, 255, 255, 255))
        
        # Gölge
        shadow = img.filter(ImageFilter.GaussianBlur(4))
        result = Image.new('RGBA', (110, 110), (0, 0, 0, 0))
        result.paste(shadow, (5, 5), shadow)
        result.paste(img, (5, 5), img)
        result.save(os.path.join(ASSETS, f'icon_{isim}.png'))
        
        print(f"  ✓ icon_{isim}.png")
    
    # 4. ÖZET
    print(f"""
╔══════════════════════════════════════╗
║  ✅ TÜM ASSETLER HAZIR!             ║
║  📂 {ASSETS}  ║
║  📦 Toplam: {len([f for f in os.listdir(ASSETS) if f.endswith('.png')])} asset  ║
╚══════════════════════════════════════╝
    """)

if __name__ == "__main__":
    create_professional_assets()