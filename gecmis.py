"""FalımaBak — fal geçmişi, günlük fal ve kullanıcı ayarları."""

import json
import os
import random
from datetime import date, datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAX_GECMIS = 30


def _android_mi():
    return (
        'ANDROID_ARGUMENT' in os.environ
        or 'ANDROID_ROOT' in os.environ
        or 'ANDROID_BOOTLOGO' in os.environ
    )


def _veri_yolu():
    if _android_mi():
        try:
            from kivy.app import App
            app = App.get_running_app()
            if app and app.user_data_dir:
                os.makedirs(app.user_data_dir, exist_ok=True)
                return os.path.join(app.user_data_dir, 'kullanici_veri.json')
        except Exception:
            pass
    return os.path.join(BASE_DIR, 'kullanici_veri.json')

GUNLUK_MESAJLAR = [
    'Bugün sezgilerine güven; evren seninle konuşuyor.',
    'Küçük bir sürpriz kapını çalabilir — gözlerini açık tut.',
    'İç sesin bugün çok net; onu dinle.',
    'Yeni bir başlangıç için doğru gün olabilir.',
    'Sabır bugün en büyük şansın; acele etme.',
    'Kalbinden geçen bir dilek bu hafta yeşerebilir.',
    'Eski bir dosttan güzel bir haber gelebilir.',
    'Yaratıcılığın zirvede; hayal kurmaktan çekinme.',
    'Bugün verdiğin nazik bir söz sana geri dönecek.',
    'Maddi konularda şanslı bir döneme giriyorsun.',
]

GUNLUK_FALLAR = [
    ('Tarot', 'tarot', '🔮'),
    ('Kahve', 'kahve', '☕'),
    ('Yıldız', 'astroloji', '🌟'),
    ('El Falı', 'elfali', '✋'),
    ('Diğer', 'diger_fallar', '✨'),
]


def _yukle():
    yol = _veri_yolu()
    if os.path.isfile(yol):
        try:
            with open(yol, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _kaydet(veri):
    try:
        with open(_veri_yolu(), 'w', encoding='utf-8') as f:
            json.dump(veri, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def onboarding_gerekli():
    return not _yukle().get('onboarding_tamamlandi', False)


def onboarding_tamamla(isim=''):
    veri = _yukle()
    veri['onboarding_tamamlandi'] = True
    if isim.strip():
        veri['isim'] = isim.strip()
    _kaydet(veri)


def kullanici_ismi():
    return _yukle().get('isim', '')


def isim_guncelle(isim=''):
    veri = _yukle()
    isim = (isim or '').strip()
    if isim:
        veri['isim'] = isim
    elif 'isim' in veri:
        del veri['isim']
    _kaydet(veri)


def gecmis_temizle():
    veri = _yukle()
    veri['gecmis'] = []
    try:
        _kaydet(veri)
        return True
    except Exception:
        return False


def fal_kaydet(tip, baslik, yorum):
    if not yorum or not str(yorum).strip():
        return
    veri = _yukle()
    kayitlar = veri.get('gecmis', [])
    kayitlar.insert(0, {
        'tip': tip,
        'baslik': baslik,
        'yorum': str(yorum).strip()[:500],
        'tarih': datetime.now().strftime('%d.%m.%Y %H:%M'),
    })
    veri['gecmis'] = kayitlar[:MAX_GECMIS]
    _kaydet(veri)


def gecmis_listesi():
    ham = _yukle().get('gecmis', [])
    if not isinstance(ham, list):
        return []
    sonuc = []
    for kayit in ham:
        if not isinstance(kayit, dict):
            continue
        yorum = str(kayit.get('yorum', '')).strip()
        if not yorum:
            continue
        sonuc.append({
            'tip': str(kayit.get('tip', '')),
            'baslik': str(kayit.get('baslik', 'Fal')),
            'yorum': yorum,
            'tarih': str(kayit.get('tarih', '')),
        })
    return sonuc


def gunluk_fal():
    """Tarihe göre sabit günlük fal önerisi."""
    bugun = date.today().isoformat()
    rng = random.Random(bugun)
    fal = rng.choice(GUNLUK_FALLAR)
    mesaj = rng.choice(GUNLUK_MESAJLAR)
    sans = rng.randint(1, 99)
    return {
        'fal_adi': fal[0],
        'hedef': fal[1],
        'ikon': fal[2],
        'mesaj': mesaj,
        'sansli_sayi': sans,
        'tarih': date.today().strftime('%d.%m.%Y'),
    }


def baslik_olustur(tip, veri=None):
    veri = veri or {}
    if tip == 'tarot':
        adet = len(veri.get('kartlar', []))
        return f'Tarot Falı ({adet} kart)'
    if tip == 'kahve':
        return 'Kahve Falı'
    if tip == 'astroloji':
        return f"Astroloji — {veri.get('burc', 'Burç')}"
    if tip == 'elfali':
        return 'El Falı'
    if tip == 'diger':
        return f"Diğer — {veri.get('tur', 'Fal')}"
    return tip.capitalize()
