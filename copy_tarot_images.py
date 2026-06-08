"""
📦 tarotcardapi-main'deki 78 JPEG kart görselini
assets/ klasörüne kopyala ve uygun isimleri ata
"""

import os
import shutil

# Kaynak ve hedef yollar
KAYNAK_DIR = r"C:\Users\kumar\OneDrive\Desktop\tarotcardapi-main\images"
HEDEF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

os.makedirs(HEDEF_DIR, exist_ok=True)

# ============================================================
# İNGİLİZCE DOSYA ADI -> TÜRKÇE KART ADI EŞLEMESİ
# ============================================================
KART_ESLEME = {
    # MAJOR ARCANA (22)
    'thefool':            'soytari',
    'themagician':        'buyucu',
    'thehighpriestess':   'yuksek_rahibe',
    'theempress':         'imparatorice',
    'theemperor':         'imparator',
    'thehierophant':      'aziz',
    'thelovers':          'asiklar',
    'thechariot':         'savas_arabasi',
    'thestrength':        'guc',
    'thehermit':          'azize',
    'wheeloffortune':     'sans_carki',
    'justice':            'adalet',
    'thehangedman':      'asilmis_adam',
    'death':              'olum',
    'temperance':         'denge',
    'thedevil':           'seytan',
    'thetower':           'kule',
    'thestar':            'yildiz',
    'themoon':            'ay',
    'thesun':             'gunes',
    'judgement':          'yargi',
    'theworld':           'dunya',
    
    # DEĞNEK (Wands) - 14
    'aceofwands':        'degnek_asi',
    'twoofwands':        'degnek_ikili',
    'threeofwands':      'degnek_uclu',
    'fourofwands':       'degnek_dortlu',
    'fiveofwands':       'degnek_besli',
    'sixofwands':        'degnek_altili',
    'sevenofwands':      'degnek_yedili',
    'eightofwands':      'degnek_sekizli',
    'nineofwands':       'degnek_dokuzlu',
    'tenofwands':        'degnek_onlu',
    'pageofwands':       'degnek_vale',
    'knightofwands':     'degnek_sovalye',
    'queenofwands':      'degnek_kralice',
    'kingofwands':       'degnek_kral',
    
    # KUPALAR (Cups) - 14
    'aceofcups':         'kupa_asi',
    'twoofcups':         'kupa_ikili',
    'threeofcups':       'kupa_uclu',
    'fourofcups':        'kupa_dortlu',
    'fiveofcups':        'kupa_besli',
    'sixofcups':         'kupa_altili',
    'sevenofcups':       'kupa_yedili',
    'eightofcups':       'kupa_sekizli',
    'nineofcups':        'kupa_dokuzlu',
    'tenofcups':         'kupa_onlu',
    'pageofcups':        'kupa_vale',
    'knightofcups':      'kupa_sovalye',
    'queenofcups':       'kupa_kralice',
    'kingofcups':        'kupa_kral',
    
    # KILIÇLAR (Swords) - 14
    'aceofswords':       'kilic_asi',
    'twoofswords':       'kilic_ikili',
    'threeofswords':     'kilic_uclu',
    'fourofswords':      'kilic_dortlu',
    'fiveofswords':      'kilic_besli',
    'sixofswords':       'kilic_altili',
    'sevenofswords':     'kilic_yedili',
    'eightofswords':     'kilic_sekizli',
    'nineofswords':      'kilic_dokuzlu',
    'tenofswords':       'kilic_onlu',
    'pageofswords':      'kilic_vale',
    'knightofswords':    'kilic_sovalye',
    'queenofswords':     'kilic_kralice',
    'kingofswords':      'kilic_kral',
    
    # TILSIM (Pentacles) - 14
    'aceofpentacles':    'tilsim_asi',
    'twoofpentacles':    'tilsim_ikili',
    'threeofpentacles':  'tilsim_uclu',
    'fourofpentacles':   'tilsim_dortlu',
    'fiveofpentacles':   'tilsim_besli',
    'sixofpentacles':    'tilsim_altili',
    'sevenofpentacles':  'tilsim_yedili',
    'eightofpentacles':  'tilsim_sekizli',
    'nineofpentacles':   'tilsim_dokuzlu',
    'tenofpentacles':    'tilsim_onlu',
    'pageofpentacles':   'tilsim_vale',
    'knightofpentacles': 'tilsim_sovalye',
    'queenofpentacles':  'tilsim_kralice',
    'kingofpentacles':   'tilsim_kral',
}

# ============================================================
# KOPYALAMA İŞLEMİ
# ============================================================
print("=" * 55)
print("  📦 TAROT KART GÖRSELLERİ KOPYALANIYOR")
print("=" * 55)

basarili = 0
hata = 0

for ingilizce_ad, turkce_ad in KART_ESLEME.items():
    # Kaynak dosyayı bul (.jpeg veya .jpg)
    kaynak = None
    for ext in ['.jpeg', '.jpg', '.png', '.webp']:
        deneme = os.path.join(KAYNAK_DIR, ingilizce_ad + ext)
        if os.path.exists(deneme):
            kaynak = deneme
            break
        # Büyük harf kontrolü (TheLovers.jpg gibi)
        deneme2 = os.path.join(KAYNAK_DIR, ingilizce_ad[0].upper() + ingilizce_ad[1:] + ext)
        if os.path.exists(deneme2):
            kaynak = deneme2
            break
    
    if kaynak:
        # Hedef: PNG olarak kaydet
        hedef = os.path.join(HEDEF_DIR, turkce_ad + '.png')
        try:
            # PIL ile JPEG -> PNG dönüşümü
            from PIL import Image
            img = Image.open(kaynak)
            img = img.convert('RGBA')  # Şeffaflık için
            img.save(hedef, 'PNG')
            print(f"  ✅ {turkce_ad}.png <- {os.path.basename(kaynak)}")
            basarili += 1
        except Exception as e:
            # Basit kopyala dene
            try:
                shutil.copy2(kaynak, hedef)
                print(f"  ⚠ {turkce_ad}.png (kopyalandı, dönüşüm yok: {e})")
                basarili += 1
            except:
                print(f"  ❌ {turkce_ad}: {e}")
                hata += 1
    else:
        print(f"  ❌ {ingilizce_ad} KAYNAK DOSYA BULUNAMADI")
        hata += 1

print(f"\n{'=' * 55}")
print(f"  ✅ {basarili} görsel başarıyla kopyalandı!")
if hata:
    print(f"  ❌ {hata} hata oluştu")
print(f"  📁 Hedef: {HEDEF_DIR}")
print(f"{'=' * 55}")