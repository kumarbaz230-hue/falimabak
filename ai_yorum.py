"""
FalımaBak - Fal yorumu motoru.
Öncelik: Gemini (mobil/bulut) → Ollama (masaüstü) → offline yedek.
"""

import base64
import json
import os
import platform
import random
import threading
import time
import urllib.error
import urllib.request
from io import BytesIO

from kivy.clock import Clock

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_ORNEK_YOLU = os.path.join(BASE_DIR, 'config.ornek.json')
SECRETS_YOLU = os.path.join(BASE_DIR, 'secrets.json')
SECRETS_ORNEK_YOLU = os.path.join(BASE_DIR, 'secrets.ornek.json')
_gomulu_anahtar = None


def _config_yolu():
    """Android'de yazılabilir uygulama klasörü."""
    if _android_mi():
        try:
            from kivy.app import App
            app = App.get_running_app()
            if app and app.user_data_dir:
                os.makedirs(app.user_data_dir, exist_ok=True)
                return os.path.join(app.user_data_dir, 'config.json')
        except Exception:
            pass
    return os.path.join(BASE_DIR, 'config.json')

_varsayilan = {
    # otomatik | gemini | ollama | offline
    'ai_mod': 'otomatik',
    'ai_aktif': True,
    'ai_timeout': 45,
    # Google Gemini — mobil + Play Store için (ücretsiz API key)
    # https://aistudio.google.com/apikey
    'gemini_api_key': '',
    'gemini_model': 'gemini-2.5-flash-lite',
    'gemini_yedek_modeller': [
        'gemini-2.5-flash',
        'gemini-2.0-flash',
        'gemini-1.5-flash',
    ],
    # Masaüstü Ollama (mobilde atlanır)
    'ollama_url': 'http://127.0.0.1:11434/api/generate',
    'ollama_model': 'llama3.1:8b',
    'ollama_masaustu': True,
}


def _ayar_yukle():
    config_yolu = _config_yolu()
    if os.path.isfile(config_yolu):
        try:
            with open(config_yolu, encoding='utf-8') as f:
                data = json.load(f)
                return {**_varsayilan, **data}
        except Exception:
            pass
    if os.path.isfile(CONFIG_ORNEK_YOLU):
        try:
            with open(CONFIG_ORNEK_YOLU, encoding='utf-8') as f:
                data = json.load(f)
                return {**_varsayilan, **data}
        except Exception:
            pass
    return dict(_varsayilan)


def config_kaydet(guncelle=None):
    """Ayarları config.json dosyasına yazar (mobil + masaüstü)."""
    data = _ayar_yukle()
    if guncelle:
        data.update(guncelle)
    kayit = {k: data.get(k, _varsayilan[k]) for k in _varsayilan}
    try:
        yol = _config_yolu()
        with open(yol, 'w', encoding='utf-8') as f:
            json.dump(kayit, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f'Config kayıt hatası: {e}', flush=True)
        return False


def gemini_key_kisa(ayar=None):
    """Arayüzde göstermek için maskelenmiş key."""
    key = _gemini_anahtar(ayar or _ayar_yukle())
    if not key:
        return ''
    if len(key) <= 8:
        return '••••••••'
    return f'{key[:4]}…{key[-4:]}'


def _gomulu_anahtar_yukle():
    """Şifreli koruma modülü → secrets.json yedeği."""
    global _gomulu_anahtar
    if _gomulu_anahtar is not None:
        return _gomulu_anahtar
    try:
        from koruma import gomulu_api_anahtar
        ham = (gomulu_api_anahtar() or '').strip()
        if ham:
            _gomulu_anahtar = ham
            return ham
    except Exception:
        pass
    for yol in (SECRETS_YOLU,):
        if not os.path.isfile(yol):
            continue
        try:
            with open(yol, encoding='utf-8') as f:
                ham = (json.load(f).get('gemini_api_key') or '').strip()
            if ham and ham != 'BURAYA_GOOGLE_AI_STUDIO_KEY':
                _gomulu_anahtar = ham
                return ham
        except Exception:
            pass
    _gomulu_anahtar = ''
    return ''


def _gemini_anahtar(ayar=None):
    ayar = ayar or _ayar_yukle()
    anahtar = (
        _gomulu_anahtar_yukle()
        or (ayar.get('gemini_api_key') or '').strip()
        or os.environ.get('GEMINI_API_KEY', '').strip()
    )
    if not anahtar:
        return ''
    # Yanlışlıkla AIzaSy + AQ. birleştirilmişse düzelt
    if anahtar.startswith('AIzaSyAQ.'):
        anahtar = anahtar[6:]  # "AIzaSy" kaldır → AQ....
    # Google'ın yeni formatı (AQ.) veya klasik (AIza) — olduğu gibi
    if anahtar.startswith('AQ.') or anahtar.startswith('AIza'):
        return anahtar
    # Sadece gövde yapıştırıldıysa eski AIzaSy öneki ekle
    return f'AIzaSy{anahtar}'


def _android_mi():
    return (
        'ANDROID_ARGUMENT' in os.environ
        or 'ANDROID_ROOT' in os.environ
        or 'ANDROID_BOOTLOGO' in os.environ
    )


def bulut_ai_hazir_mi():
    """Gemini API anahtarı tanımlı mı?"""
    ayar = _ayar_yukle()
    return bool(_gemini_anahtar(ayar)) and ayar.get('ai_aktif', True)


def ollama_aktif_mi():
    """Yerel Ollama çalışıyor mu? (masaüstü)"""
    ayar = _ayar_yukle()
    if not ayar.get('ai_aktif', True):
        return False
    if _android_mi():
        return False
    if platform.system() != 'Windows' and not ayar.get('ollama_masaustu', True):
        return False
    try:
        url = ayar['ollama_url'].replace('/api/generate', '/api/tags')
        with urllib.request.urlopen(url, timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def ai_kaynak():
    """Aktif AI kaynağının kısa adı."""
    ayar = _ayar_yukle()
    for kaynak in _kaynak_sirasi(ayar):
        if kaynak == 'gemini' and _gemini_anahtar(ayar):
            return 'bulut'
        if kaynak == 'ollama' and ollama_aktif_mi():
            return 'ollama'
    return 'offline'


def ai_durum_metni():
    """Kullanıcıya gösterilebilir durum metni."""
    k = ai_kaynak()
    if k == 'bulut':
        return 'FalımaBak Yorumluyor (Bulut)'
    if k == 'ollama':
        return 'FalımaBak Yorumluyor (Yerel)'
    return 'FalımaBak Yorumluyor'


def _kaynak_sirasi(ayar):
    mod = (ayar.get('ai_mod') or 'otomatik').lower()
    if mod == 'offline':
        return []
    if mod == 'gemini':
        return ['gemini']
    if mod == 'ollama':
        return ['ollama']
    # otomatik — mobilde önce bulut, PC'de bulut + ollama
    sira = []
    if _gemini_anahtar(ayar):
        sira.append('gemini')
    if not _android_mi() and ayar.get('ollama_masaustu', True):
        sira.append('ollama')
    return sira


def _ana_thread(fn):
    Clock.schedule_once(lambda *_: fn(), 0)


def _http_post(url, body_dict, headers=None, timeout=45):
    body = json.dumps(body_dict).encode('utf-8')
    hdrs = {'Content-Type': 'application/json'}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, data=body, headers=hdrs, method='POST')
    with urllib.request.urlopen(req, timeout=timeout) as yanit:
        return json.loads(yanit.read().decode('utf-8'))


def _foto_hazirla(yol, max_kenar=1024):
    """Fotoğrafı Gemini Vision için JPEG base64'e çevirir."""
    if not yol or not os.path.isfile(yol):
        return None
    try:
        from PIL import Image

        with Image.open(yol) as img:
            img = img.convert('RGB')
            if max(img.size) > max_kenar:
                img.thumbnail((max_kenar, max_kenar), Image.Resampling.LANCZOS)
            buf = BytesIO()
            img.save(buf, format='JPEG', quality=85)
            return {
                'mime_type': 'image/jpeg',
                'data': base64.b64encode(buf.getvalue()).decode('ascii'),
            }
    except Exception as e:
        print(f'AI: fotoğraf hazırlanamadı: {e}', flush=True)
        return None


def _gorseller_listesi(gorsel):
    if not gorsel:
        return []
    if isinstance(gorsel, list):
        return [g for g in gorsel if g]
    return [gorsel]


def _fotolar_hazirla(yollar):
    gorseller = []
    for yol in yollar or []:
        g = _foto_hazirla(yol)
        if g:
            gorseller.append(g)
    return gorseller


def _gemini_istek(prompt, ayar, model=None, gorsel=None):
    anahtar = _gemini_anahtar(ayar)
    if not anahtar:
        return None
    model = model or ayar.get('gemini_model', 'gemini-2.5-flash-lite')
    url = (
        f'https://generativelanguage.googleapis.com/v1beta/models/'
        f'{model}:generateContent'
    )
    headers = {}
    if anahtar.startswith('AQ.'):
        headers['x-goog-api-key'] = anahtar
    else:
        url = f'{url}?key={anahtar}'

    parcalar = []
    for g in _gorseller_listesi(gorsel):
        parcalar.append({
            'inline_data': {
                'mime_type': g['mime_type'],
                'data': g['data'],
            },
        })
    parcalar.append({'text': prompt})

    gorsel_sayisi = len(_gorseller_listesi(gorsel))
    zaman_asimi = int(ayar.get('ai_timeout', 45))
    if gorsel_sayisi:
        zaman_asimi = max(zaman_asimi, 60 + gorsel_sayisi * 15)

    veri = _http_post(
        url,
        {
            'contents': [{'parts': parcalar}],
            'generationConfig': {
                'temperature': 0.88,
                'maxOutputTokens': 1100 if gorsel_sayisi > 1 else 900,
            },
        },
        headers=headers or None,
        timeout=zaman_asimi,
    )
    adaylar = veri.get('candidates') or []
    if not adaylar:
        return None
    parcalar = adaylar[0].get('content', {}).get('parts') or []
    metinler = [p.get('text', '') for p in parcalar if p.get('text')]
    return '\n'.join(metinler).strip() or None


def _gemini_modeller(ayar):
    primary = ayar.get('gemini_model', 'gemini-2.5-flash-lite')
    modeller = [primary]
    for yedek in ayar.get('gemini_yedek_modeller') or (
        'gemini-2.5-flash',
        'gemini-3.5-flash',
    ):
        if yedek and yedek not in modeller:
            modeller.append(yedek)
    return modeller


def _gemini_dene(prompt, ayar, gorsel=None):
    """Gemini'yi ana + yedek modelle dener. (metin, son_http_kodu)"""
    anahtar = _gemini_anahtar(ayar)
    if not anahtar:
        return None, None

    primary = ayar.get('gemini_model', 'gemini-2.5-flash-lite')
    modeller = _gemini_modeller(ayar)

    son_kod = None
    kota_doldu = False
    for model in modeller:
        for deneme in range(2):
            try:
                metin = _gemini_istek(prompt, ayar, model=model, gorsel=gorsel)
                if metin:
                    if model != primary:
                        print(f'AI: Gemini yedek model ({model})', flush=True)
                    return metin, None
            except urllib.error.HTTPError as e:
                son_kod = e.code
                if e.code == 429:
                    kota_doldu = True
                detay = ''
                try:
                    detay = e.read().decode('utf-8', errors='replace')[:280]
                except Exception:
                    pass
                print(
                    f'AI HTTP hatası (gemini/{model}): {e.code} {e.reason}'
                    + (f' — {detay}' if detay else ''),
                    flush=True,
                )
                if e.code == 429 and deneme == 0:
                    time.sleep(5)
                    continue
                if e.code == 404:
                    break
                break
            except (urllib.error.URLError, TimeoutError, Exception) as e:
                print(f'AI yorum hatası (gemini/{model}): {e}', flush=True)
                break
    if kota_doldu:
        print('AI: Gemini kotası doldu — Ollama veya hazır yorum devreye girer', flush=True)
    return None, 429 if kota_doldu else son_kod


def _kullanici_hata_mesaji(hatalar):
    if not hatalar:
        return 'Gerçek AI yorumu alınamadı; hazır yorum gösteriliyor.'
    kodlar = []
    for h in hatalar:
        if ':' in h:
            kodlar.append(h.split(':', 1)[1])
    if '429' in kodlar:
        return 'Bulut kotası dolu; biraz bekleyip tekrar deneyin. Şimdilik hazır yorum.'
    if any(k in ('401', '403', '400') for k in kodlar):
        return 'Yapay zeka servisi yanıt vermedi; hazır yorum gösteriliyor.'
    return 'AI bağlantısı kurulamadı; hazır yorum gösteriliyor.'


def _ollama_istek(prompt, ayar):
    veri = _http_post(
        ayar['ollama_url'],
        {
            'model': ayar['ollama_model'],
            'prompt': prompt,
            'stream': False,
            'options': {'temperature': 0.85, 'num_predict': 600},
        },
        timeout=int(ayar.get('ai_timeout', 90)),
    )
    return (veri.get('response') or '').strip() or None


def _prompt_olustur(tip, veri, gorsel_var=False):
    kullanici = ''
    try:
        from gecmis import kullanici_ismi
        isim = kullanici_ismi()
        if isim:
            kullanici = f'Kullanıcının adı: {isim}. Samimi hitap edebilirsin.\n'
    except Exception:
        pass

    if tip == 'tarot':
        kartlar = veri.get('kartlar', [])
        satirlar = []
        for k in kartlar:
            satirlar.append(
                f"- {k.get('pozisyon', '')}: {k.get('isim', '')} "
                f"({k.get('durum', '')}) — {k.get('anlam', '')}"
            )
        liste = '\n'.join(satirlar)
        return (
            'Sen deneyimli bir Türk tarot yorumcususun. Eğlence amaçlı, mistik ama sıcak bir dille yaz.\n'
            f'{kullanici}'
            f'Çekilen kartlar:\n{liste}\n\n'
            '3-5 paragraf Türkçe yorum yaz. Aşk, kariyer ve genel enerji hakkında ipuçları ver. '
            'Korkutucu veya kesin gelecek iddiası kullanma.'
        )

    if tip == 'kahve':
        if gorsel_var:
            aciklamalar = veri.get('foto_aciklamalari') or []
            if aciklamalar:
                foto_metin = '\n'.join(
                    f'- Fotoğraf {i + 1}: {a}' for i, a in enumerate(aciklamalar)
                )
            else:
                foto_metin = '- Kahve fincanı ve tabak fotoğrafları ektedir.'
            return (
                'Sen deneyimli bir Türk kahve falı yorumcususun. Eğlence amaçlı, samimi Türkçe yaz.\n'
                f'{kullanici}'
                f'Ekte {len(aciklamalar) or "birkaç"} fotoğraf var:\n{foto_metin}\n'
                'Tüm fotoğrafları birlikte incele. Fincan içi telveleri ve tabaktaki izleri değerlendir.\n'
                'Önce gördüğün 3-6 sembolü madde madde listele, sonra 3-5 paragraf yorum yaz: '
                'aşk, para, sağlık ve genel mesaj. Olumlu ama gerçekçi ol. '
                'Korkutucu veya kesin gelecek iddiası kullanma.'
            )
        sekiller = veri.get('sekiller', [])
        return (
            'Sen Türk kahve falı yorumcususun. Eğlence amaçlı, samimi Türkçe yaz.\n'
            f'{kullanici}'
            f'Fincanda görülen semboller: {", ".join(sekiller)}\n'
            '3-4 paragraf yorum: aşk, para, sağlık ve genel mesaj. Olumlu ama gerçekçi ol.'
        )

    if tip == 'elfali':
        if gorsel_var:
            aciklamalar = veri.get('foto_aciklamalari') or []
            if aciklamalar:
                foto_metin = '\n'.join(
                    f'- Fotoğraf {i + 1}: {a}' for i, a in enumerate(aciklamalar)
                )
            else:
                foto_metin = '- Avuç içi ve el dışı fotoğrafları ektedir.'
            return (
                'Sen deneyimli bir el falı yorumcususun. Eğlence amaçlı, samimi Türkçe yaz.\n'
                f'{kullanici}'
                f'Ekte {len(aciklamalar) or 2} fotoğraf var:\n{foto_metin}\n'
                'Avuç içi çizgileri ile elin dış/üst görünümünü birlikte değerlendir.\n'
                'Önce gözlemlerini kısaca özetle, sonra 3-5 paragraf yaz: karakter, aşk, kariyer, şans.\n'
                'Olumlu ama gerçekçi ol. Kesin gelecek iddiası kullanma.'
            )
        cizgiler = veri.get('cizgiler', [])
        el_tipi = veri.get('el_tipi', '')
        return (
            'Sen el falı yorumcususun. Eğlence amaçlı Türkçe yaz.\n'
            f'{kullanici}'
            f'El tipi: {el_tipi}\n'
            f'Çizgiler: {", ".join(cizgiler)}\n'
            '3-4 paragraf: karakter, aşk, kariyer ve şans.'
        )

    if tip == 'astroloji':
        return (
            'Sen astroloji yorumcususun. Eğlence amaçlı Türkçe yaz.\n'
            f'{kullanici}'
            f"Burç: {veri.get('burc', '')}\n"
            f"Doğum: {veri.get('dogum', '')}\n"
            'Haftalık yorum: aşk, iş, sağlık ve şans. 3-4 paragraf.'
        )

    if tip == 'diger':
        return (
            'Sen mistik fal yorumcususun. Eğlence amaçlı Türkçe yaz.\n'
            f'{kullanici}'
            f"Fal türü: {veri.get('tur', '')}\n"
            f"Sonuç: {veri.get('sonuc', '')}\n"
            '2-3 paragraf yorum.'
        )

    return f'Eğlence amaçlı kısa Türkçe fal yorumu yaz.\n{kullanici}{veri}'


def _yedek_yorum(tip, veri):
    isim = ''
    try:
        from gecmis import kullanici_ismi
        isim = kullanici_ismi()
    except Exception:
        pass
    hitap = f'{isim}, ' if isim else ''

    if tip == 'tarot':
        return random.choice([
            f'{hitap}kartlarınız güçlü bir dönüşüm döngüsünü işaret ediyor. Geçmişte yaşadıklarınız sizi bugünkü kararlarınıza hazırlamış; şimdi sezgilerinize güvenme zamanı.',
            f'{hitap}seçilen kartlar umut, denge ve içsel güç temalarını taşıyor. Yakın zamanda beklenmedik bir haber moralinizi yükseltebilir.',
            f'{hitap}kartlar cesaret ve sabır istiyor. Acele etmeden attığınız adımlar sizi doğru yola taşıyacak.',
        ])
    if tip == 'kahve':
        return random.choice([
            f'{hitap}fincanınızda hareket ve yenilenme sembolleri baskın. Aşk hayatında tatlı sürprizler kapıda olabilir.',
            f'{hitap}kahve telveleri yeni bir başlangıcı müjdeler. Eski defterleri kapatıp önünüze bakmanız için güçlü bir enerji var.',
        ])
    if tip == 'elfali':
        return (
            f'{hitap}avuç çizgileriniz güçlü bir yaşam enerjisi taşıyor. '
            'Hayat çizginiz dayanıklılığı, kalp çizginiz duygusal derinliği vurguluyor.'
        )
    if tip == 'astroloji':
        burc = veri.get('burc', 'yıldızlar')
        return f'{hitap}{burc} burcu için enerji yükseliyor. İş ve ilişkilerde denge kurduğunuzda şans sizinle olacak.'
    if tip == 'diger':
        return f'{hitap}yıldızlar size güzel günler müjdeliyor. Pozitif kalın ve sezgilerinize güvenin.'
    return f'{hitap}evren size güzel haberler hazırlıyor. Pozitif kalın ve fırsatları değerlendirin.'


def _yorum_uret(text_prompt, ayar, gorsel=None, vision_prompt=None):
    """Sırayla kaynakları dener; (metin, kaynak, hatalar)."""
    hatalar = []
    gemini_prompt = vision_prompt if gorsel and vision_prompt else text_prompt
    for kaynak in _kaynak_sirasi(ayar):
        if kaynak == 'gemini':
            metin, kod = _gemini_dene(gemini_prompt, ayar, gorsel=gorsel)
            if metin:
                if gorsel:
                    print('AI kaynak: Gemini Vision (bulut)', flush=True)
                else:
                    print('AI kaynak: Gemini (bulut)', flush=True)
                return metin, 'gemini', None
            if kod:
                hatalar.append(f'gemini:{kod}')
        elif kaynak == 'ollama' and ollama_aktif_mi():
            try:
                metin = _ollama_istek(text_prompt, ayar)
                if metin:
                    if hatalar:
                        print(
                            f'AI kaynak: Ollama (Gemini başarısız: {", ".join(hatalar)})',
                            flush=True,
                        )
                    else:
                        print('AI kaynak: Ollama (yerel)', flush=True)
                    return metin, 'ollama', None
            except urllib.error.HTTPError as e:
                hatalar.append(f'ollama:{e.code}')
                print(f'AI HTTP hatası (ollama): {e.code} {e.reason}', flush=True)
            except (urllib.error.URLError, TimeoutError, Exception) as e:
                hatalar.append('ollama:hata')
                print(f'AI yorum hatası (ollama): {e}', flush=True)
    return None, None, hatalar


def yorum_al(tip, veri, callback):
    """
    callback(metin, ai_kullanildi, hata, kaynak)
    ai_kullanildi=True → Gemini veya Ollama kullanıldı.
    kaynak: 'gemini' | 'ollama' | None
    """

    def _sonuc(metin, ai_kullanildi, hata, kaynak=None, fotograf=False):
        if metin:
            try:
                from gecmis import baslik_olustur, fal_kaydet
                fal_kaydet(tip, baslik_olustur(tip, veri), metin)
            except Exception:
                pass
        callback(metin, ai_kullanildi, hata, kaynak, fotograf)

    def _calistir():
        ayar = _ayar_yukle()
        if not ayar.get('ai_aktif', True):
            yedek = _yedek_yorum(tip, veri)
            _ana_thread(lambda y=yedek: _sonuc(y, False, None, None))
            return

        foto_yollari = list(veri.get('foto_yollari') or [])
        if not foto_yollari:
            tek = veri.get('foto_yolu') or veri.get('foto')
            if tek:
                foto_yollari = [tek]
        gorsel = None
        if foto_yollari and tip in ('kahve', 'elfali') and _gemini_anahtar(ayar):
            gorseller = _fotolar_hazirla(foto_yollari)
            if gorseller:
                gorsel = gorseller if len(gorseller) > 1 else gorseller[0]
                print(
                    f'AI: {len(gorseller)} fotoğraf Gemini Vision ile gönderiliyor',
                    flush=True,
                )

        text_prompt = _prompt_olustur(tip, veri, gorsel_var=False)
        vision_prompt = (
            _prompt_olustur(tip, veri, gorsel_var=True) if gorsel else text_prompt
        )
        fotograf_ai = bool(gorsel)
        metin, kaynak, hatalar = _yorum_uret(
            text_prompt, ayar, gorsel=gorsel, vision_prompt=vision_prompt,
        )
        if metin:
            _ana_thread(
                lambda m=metin, k=kaynak, f=fotograf_ai and k == 'gemini':
                _sonuc(m, True, None, k, f),
            )
            return

        yedek = _yedek_yorum(tip, veri)
        kullanici_hata = _kullanici_hata_mesaji(hatalar or [])
        print(f'AI: hazır yorum kullanıldı ({kullanici_hata})', flush=True)
        _ana_thread(lambda y=yedek, h=kullanici_hata: _sonuc(y, False, h, None))

    threading.Thread(target=_calistir, daemon=True).start()
