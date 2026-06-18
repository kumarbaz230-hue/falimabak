"""
FalımaBak - Fal yorumu motoru.
Öncelik (metin): Gemini → OpenRouter → Groq → Ollama (PC) → offline.
Görsel (kahve/el): yalnızca Gemini Vision → offline.
"""

import base64
import json
import os
import platform
import random
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from io import BytesIO

from kivy.clock import Clock

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_ORNEK_YOLU = os.path.join(BASE_DIR, 'config.ornek.json')
SECRETS_YOLU = os.path.join(BASE_DIR, 'secrets.json')
SECRETS_ORNEK_YOLU = os.path.join(BASE_DIR, 'secrets.ornek.json')
_gomulu_anahtar = None
_son_gemini_istek = 0.0
_model_kota = {}  # model -> kota bitiş zamanı (429 sonrası)

GEMINI_MIN_ARALIK = 1.5
GEMINI_KOTA_BEKLE = 90


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
    'gemini_model': 'gemini-2.5-flash',
    'gemini_yedek_modeller': [
        'gemini-2.0-flash',
        'gemini-1.5-flash',
    ],
    # Masaüstü Ollama (mobilde atlanır)
    'ollama_url': 'http://127.0.0.1:11434/api/generate',
    'ollama_model': 'llama3.1:8b',
    'ollama_masaustu': True,
    # OpenRouter — Gemini düşünce (DeepSeek / Qwen)
    # https://openrouter.ai/keys
    'openrouter_api_key': '',
    'openrouter_model': 'deepseek/deepseek-chat',
    'openrouter_yedek_modeller': [
        'qwen/qwen-2.5-72b-instruct',
    ],
    # Groq — son bulut yedek (gsk_ ile başlar)
    # https://console.groq.com/keys
    'groq_api_key': '',
    'groq_model': 'llama-3.3-70b-versatile',
    'groq_yedek_modeller': [
        'llama-3.1-8b-instant',
    ],
    # xAI Grok — xai- ile başlar (Groq değil)
    # https://console.x.ai/
    'xai_api_key': '',
    'xai_model': 'grok-2-1212',
    'xai_yedek_modeller': [
        'grok-beta',
    ],
}


def _ayar_yukle():
    config_yolu = _config_yolu()
    if os.path.isfile(config_yolu):
        try:
            with open(config_yolu, encoding='utf-8') as f:
                data = json.load(f)
                ayar = {**_varsayilan, **data}
                return _mobil_ayar_duzelt(ayar)
        except Exception:
            pass
    if os.path.isfile(CONFIG_ORNEK_YOLU):
        try:
            with open(CONFIG_ORNEK_YOLU, encoding='utf-8') as f:
                data = json.load(f)
                ayar = {**_varsayilan, **data}
                return _mobil_ayar_duzelt(ayar)
        except Exception:
            pass
    return _mobil_ayar_duzelt(dict(_varsayilan))


def _mobil_ayar_duzelt(ayar):
    """Android: AI her zaman Gemini; offline mod devre dışı."""
    if not _android_mi():
        return _gemini_ayar_duzelt(ayar)
    ayar = _gemini_ayar_duzelt(dict(ayar))
    ayar['ai_aktif'] = True
    ayar['ai_mod'] = 'otomatik'
    ayar['ai_timeout'] = max(int(ayar.get('ai_timeout') or 45), 90)
    return ayar


_GECERLI_GEMINI = frozenset({
    'gemini-2.5-flash',
    'gemini-2.5-pro',
    'gemini-2.0-flash',
    'gemini-2.0-flash-lite',
    'gemini-1.5-flash',
    'gemini-1.5-pro',
})


def _gemini_model_normalize(model):
    """Geçersiz/lite/8b modelleri güvenilir flash modeline çevir."""
    model = (model or 'gemini-2.5-flash').strip()
    ml = model.lower()
    if 'lite' in ml or '8b' in ml:
        return 'gemini-2.5-flash', 'kota/limit'
    if '3.5' in ml or not ml.startswith('gemini-') or model not in _GECERLI_GEMINI:
        return 'gemini-2.5-flash', 'tanımsız model'
    return model, None


def _gemini_ayar_duzelt(ayar):
    """Lite/8b modeller kotada hızlı tükenir — flash ailesine yönlendir."""
    ayar = dict(ayar)
    ham = (ayar.get('gemini_model') or 'gemini-2.5-flash').strip()
    model, neden = _gemini_model_normalize(ham)
    if neden:
        print(f'AI: {ham} yerine {model} kullanılıyor ({neden})', flush=True)
    ayar['gemini_model'] = model
    yedek = []
    for m in ayar.get('gemini_yedek_modeller') or []:
        m = (m or '').strip()
        if not m or m == model:
            continue
        m_norm, neden = _gemini_model_normalize(m)
        if neden == 'kota/limit':
            continue
        if m_norm not in yedek and m_norm != model:
            yedek.append(m_norm)
    if not yedek:
        yedek = ['gemini-2.0-flash', 'gemini-1.5-flash']
    ayar['gemini_yedek_modeller'] = yedek
    return ayar


def mobil_ai_hazirla():
    """Uygulama açılışında mobil AI yapılandırması."""
    if not _android_mi():
        return
    ssl_hazirla()
    _gomulu_anahtar_yukle()
    anahtar_var = bool(_gemini_anahtar(_ayar_yukle()))
    or_var = bool(_openrouter_anahtar(_ayar_yukle()))
    xai_var = bool(_xai_anahtar(_ayar_yukle()))
    groq_var = bool(_groq_anahtar(_ayar_yukle()))
    print(
        f'AI mobil: gemini={"hazır" if anahtar_var else "YOK"} '
        f'openrouter={"hazır" if or_var else "YOK"} '
        f'grok={"hazır" if xai_var else "YOK"} '
        f'groq={"hazır" if groq_var else "YOK"}',
        flush=True,
    )
    config_kaydet({
        'ai_aktif': True,
        'ai_mod': 'otomatik',
        'ai_timeout': 90,
    })
    if anahtar_var:
        threading.Thread(target=_mobil_ai_ping, daemon=True).start()


def _ai_log(mesaj):
    if not _android_mi():
        return
    try:
        from kivy.app import App
        app = App.get_running_app()
        if not app or not app.user_data_dir:
            return
        yol = os.path.join(app.user_data_dir, 'ai_log.txt')
        with open(yol, 'a', encoding='utf-8') as f:
            f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} {mesaj}\n')
    except Exception:
        pass


def _mobil_ai_ping():
    try:
        ayar = _ayar_yukle()
        metin, kod = _gemini_dene('Tek kelimeyle yanıt ver: tamam', ayar)
        if metin:
            print('AI mobil: bağlantı OK', flush=True)
            _ai_log('ping OK')
        else:
            print(f'AI mobil: ping başarısız kod={kod}', flush=True)
            _ai_log(f'ping fail kod={kod}')
    except Exception as e:
        _ai_log(f'ping error {e}')


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
    # Ayarlara kullanıcı key girdiyse öncelik (AIza formatı için)
    cfg_key = (ayar.get('gemini_api_key') or '').strip()
    anahtar = (
        cfg_key
        or _gomulu_anahtar_yukle()
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
        if kaynak == 'openrouter' and _openrouter_anahtar(ayar):
            return 'openrouter'
        if kaynak == 'xai' and _xai_anahtar(ayar):
            return 'grok'
        if kaynak == 'groq' and _groq_anahtar(ayar):
            return 'groq'
        if kaynak == 'ollama' and ollama_aktif_mi():
            return 'ollama'
    return 'cihaz'


def ai_durum_metni():
    """Kullanıcıya her zaman aynı marka metni."""
    try:
        from dil import t
        return t('yorum_baslik')
    except Exception:
        return 'FalımaBak Yorumluyor'


def _secrets_yukle():
    if not hasattr(_secrets_yukle, '_cache'):
        _secrets_yukle._cache = {}
        for yol in (SECRETS_YOLU,):
            if not os.path.isfile(yol):
                continue
            try:
                with open(yol, encoding='utf-8') as f:
                    _secrets_yukle._cache = json.load(f) or {}
            except Exception:
                pass
            break
    return _secrets_yukle._cache


def _api_anahtar_al(ayar, config_key, secret_key, env_key):
    ayar = ayar or {}
    v = (ayar.get(config_key) or '').strip()
    if v and not v.upper().startswith('BURAYA'):
        return v
    s = (_secrets_yukle().get(secret_key) or '').strip()
    if s and not s.upper().startswith('BURAYA'):
        return s
    return (os.environ.get(env_key) or '').strip()


def _openrouter_anahtar(ayar=None):
    return _api_anahtar_al(
        ayar or _ayar_yukle(), 'openrouter_api_key', 'openrouter_api_key', 'OPENROUTER_API_KEY',
    )


def _groq_anahtar(ayar=None):
    key = _api_anahtar_al(
        ayar or _ayar_yukle(), 'groq_api_key', 'groq_api_key', 'GROQ_API_KEY',
    )
    if key.startswith('xai-'):
        return ''
    return key


def _xai_anahtar(ayar=None):
    ayar = ayar or _ayar_yukle()
    key = _api_anahtar_al(ayar, 'xai_api_key', 'xai_api_key', 'XAI_API_KEY')
    if key:
        return key
    groq_slot = (_api_anahtar_al(ayar, 'groq_api_key', 'groq_api_key', 'GROQ_API_KEY') or '').strip()
    if groq_slot.startswith('xai-'):
        return groq_slot
    return ''


def _kaynak_sirasi(ayar, gorsel_var=False):
    """Görsel fallarda yalnızca Gemini; metin fallarda çoklu bulut zinciri."""
    if gorsel_var:
        if _gemini_anahtar(ayar):
            return ['gemini']
        return []

    mod = (ayar.get('ai_mod') or 'otomatik').lower()
    if mod == 'offline':
        return []
    if mod == 'gemini':
        return ['gemini'] if _gemini_anahtar(ayar) else []
    if mod == 'ollama':
        return ['ollama'] if ollama_aktif_mi() else []

    sira = []
    if _gemini_anahtar(ayar):
        sira.append('gemini')
    if _openrouter_anahtar(ayar):
        sira.append('openrouter')
    if _xai_anahtar(ayar):
        sira.append('xai')
    if _groq_anahtar(ayar):
        sira.append('groq')
    if not _android_mi() and ayar.get('ollama_masaustu', True):
        sira.append('ollama')
    return sira


def _veri_nonce(veri):
    """Her fal bakışında benzersiz rastgelelik."""
    v = dict(veri or {})
    v['_nonce'] = (time.time_ns() % 2_000_000_000) + random.randint(0, 999_999)
    return v


def _ana_thread(fn):
    Clock.schedule_once(lambda *_: fn(), 0)


def ssl_hazirla():
    """Android/Python SSL — certifi CA paketi (mobilde kritik)."""
    try:
        import certifi
        yol = certifi.where()
        os.environ['SSL_CERT_FILE'] = yol
        os.environ['REQUESTS_CA_BUNDLE'] = yol
        return yol
    except ImportError:
        return None


def _ssl_context():
    import ssl
    ca = ssl_hazirla()
    if ca and os.path.isfile(ca):
        return ssl.create_default_context(cafile=ca)
    return ssl.create_default_context()


def _http_post(url, body_dict, headers=None, timeout=45):
    body = json.dumps(body_dict).encode('utf-8')
    hdrs = {'Content-Type': 'application/json', 'User-Agent': 'Falimabak/1.0'}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, data=body, headers=hdrs, method='POST')
    ctx = _ssl_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as yanit:
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


_FOTO_DOGRULAMA = {
    'elfali': {
        'Avuç İçi': (
            'Bu fotoğrafta insan avuç içi (palm) net görünüyor mu? '
            'Manzara, hayvan, yüz, yemek veya başka nesne varsa HAYIR de.'
        ),
        'El Dışı': (
            'Bu fotoğrafta insan elinin dış/üst görünümü net mi? '
            'El değilse veya belirsizse HAYIR de.'
        ),
        '_default': (
            'Bu fotoğraf el falı için uygun bir el fotoğrafı mı? '
            'El/avuç yoksa HAYIR de.'
        ),
    },
    'kahve': {
        'Fincan İçi 1': (
            'Bu fotoğraf kahve fincanının içindeki telve/telvenin göründüğü bir fincan mı? '
            'Fincan değilse HAYIR de.'
        ),
        'Fincan İçi 2': (
            'Bu fotoğraf kahve fincanı içi telve fotoğrafı mı? Değilse HAYIR de.'
        ),
        'Tabak': (
            'Bu fotoğraf kahve falı tabağı veya fincan tabağı mı? Değilse HAYIR de.'
        ),
        '_default': (
            'Bu fotoğraf kahve falı için uygun bir fincan/tabağı fotoğrafı mı? '
            'Değilse HAYIR de.'
        ),
    },
}


def _cevap_evet_mi(metin):
    if not metin:
        return None
    c = metin.strip().upper()
    if c.startswith('HAYIR') or c.startswith('NO') or ' HAYIR' in c:
        return False
    if c.startswith('EVET') or c.startswith('YES') or ' EVET' in c:
        return True
    return None


def _foto_dogrula(tip, yollar, aciklamalar, ayar):
    """Her fotoğrafı Gemini Vision ile doğrular. (ok, hata_mesaji)"""
    if tip not in ('kahve', 'elfali'):
        return True, None
    if not _gemini_anahtar(ayar):
        return True, None

    sablonlar = _FOTO_DOGRULAMA.get(tip, {})
    for i, yol in enumerate(yollar or []):
        g = _foto_hazirla(yol)
        if not g:
            return False, f'Fotoğraf {i + 1} okunamadı. Lütfen tekrar yükleyin.'
        baslik = (aciklamalar[i] if aciklamalar and i < len(aciklamalar) else '')
        soru = sablonlar.get(baslik) or sablonlar.get('_default', '')
        prompt = (
            f'{soru}\n'
            'Sadece tek kelime yaz: EVET veya HAYIR. Başka hiçbir şey yazma.'
        )
        metin, kod = _gemini_dene(prompt, ayar, gorsel=g)
        sonuc = _cevap_evet_mi(metin)
        if sonuc is False:
            if tip == 'elfali':
                return False, (
                    f'"{baslik or "Fotoğraf"}" el fotoğrafı gibi görünmüyor. '
                    'Lütfen gerçek avuç içi ve el dışı fotoğrafı yükleyin.'
                )
            return False, (
                f'"{baslik or "Fotoğraf"}" kahve falı için uygun değil. '
                'Fincan içi ve tabak fotoğrafı yükleyin.'
            )
        if sonuc is None and not metin:
            _ai_log(f'dogrulama bos tip={tip} slot={baslik} kod={kod}')
    return True, None


def _gemini_istek_araligi():
    global _son_gemini_istek
    simdi = time.time()
    fark = simdi - _son_gemini_istek
    if fark < GEMINI_MIN_ARALIK:
        time.sleep(GEMINI_MIN_ARALIK - fark)
    _son_gemini_istek = time.time()


def _model_kota_aktif(model):
    return time.time() < _model_kota.get(model, 0)


def _model_kota_isaretle(model, saniye=GEMINI_KOTA_BEKLE):
    _model_kota[model] = time.time() + saniye


def _metin_eksik_mi(metin, finish_reason=''):
    """Kesik veya çok kısa AI yanıtını kullanıcıya gösterme."""
    if not metin:
        return True
    t = metin.strip()
    if len(t) < 140 or len(t.split()) < 25:
        return True
    fr = (finish_reason or '').upper()
    if fr and fr not in ('STOP', 'END_TURN', ''):
        return True
    if len(t) > 280 and t[-1] not in '.!?…"\')»':
        son = t[-100:]
        if son.count('.') + son.count('!') + son.count('?') == 0:
            return True
    return False


def _gecici_http_kodu(kod):
    return kod in (429, 503)


def _gemini_istek(prompt, ayar, model=None, gorsel=None, max_tokens=None):
    anahtar = _gemini_anahtar(ayar)
    if not anahtar:
        return None
    model = model or ayar.get('gemini_model', 'gemini-2.5-flash')
    base_url = (
        f'https://generativelanguage.googleapis.com/v1beta/models/'
        f'{model}:generateContent'
    )

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
        zaman_asimi = max(zaman_asimi, 75 + gorsel_sayisi * 12)

    if max_tokens is None:
        max_tokens = 1800 if gorsel_sayisi else 2048

    govde = {
        'contents': [{'parts': parcalar}],
        'generationConfig': {
            'temperature': 0.88,
            'maxOutputTokens': int(max_tokens),
        },
    }

    _gemini_istek_araligi()

    denemeler = [
        (base_url, {'Content-Type': 'application/json', 'x-goog-api-key': anahtar}),
        (
            f'{base_url}?key={urllib.parse.quote(anahtar, safe="")}',
            {'Content-Type': 'application/json'},
        ),
    ]

    son_hata = None
    for url, hdrs in denemeler:
        try:
            veri = _http_post(url, govde, headers=hdrs, timeout=zaman_asimi)
            adaylar = veri.get('candidates') or []
            if not adaylar:
                blok = veri.get('promptFeedback') or veri.get('error')
                if blok:
                    print(f'AI: Gemini boş yanıt ({model}): {str(blok)[:200]}', flush=True)
                continue
            yanit_parcalar = adaylar[0].get('content', {}).get('parts') or []
            metinler = [p.get('text', '') for p in yanit_parcalar if p.get('text')]
            metin = '\n'.join(metinler).strip()
            finish = adaylar[0].get('finishReason', 'STOP') or 'STOP'
            if metin:
                return metin, finish
        except urllib.error.HTTPError as e:
            son_hata = e
            detay = ''
            try:
                detay = e.read().decode('utf-8', errors='replace')[:280]
            except Exception:
                pass
            print(
                f'AI HTTP (gemini/{model}): {e.code} {e.reason}'
                + (f' — {detay}' if detay else ''),
                flush=True,
            )
            _ai_log(f'http {model} {e.code} {detay[:120]}')
            if e.code not in (400, 401, 403):
                raise
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            son_hata = e
            print(f'AI ağ hatası (gemini/{model}): {e}', flush=True)
            _ai_log(f'net {model} {e}')
            raise

    if son_hata and isinstance(son_hata, urllib.error.HTTPError):
        raise son_hata
    return None, None


def _gemini_modeller(ayar):
    primary = ayar.get('gemini_model', 'gemini-2.5-flash')
    modeller = [primary]
    for yedek in ayar.get('gemini_yedek_modeller') or (
        'gemini-2.0-flash',
        'gemini-1.5-flash',
    ):
        if yedek and yedek not in modeller:
            modeller.append(yedek)
    return modeller


def _gemini_dene(prompt, ayar, gorsel=None):
    """Gemini'yi ana + yedek modelle dener. (metin, son_http_kodu)"""
    ayar = _gemini_ayar_duzelt(ayar)
    anahtar = _gemini_anahtar(ayar)
    if not anahtar:
        return None, None

    primary = ayar.get('gemini_model', 'gemini-2.5-flash')
    modeller = _gemini_modeller(ayar)

    son_kod = None
    kota_doldu = False
    for model in modeller:
        if _model_kota_aktif(model):
            print(f'AI: {model} kotada — atlanıyor', flush=True)
            continue
        for deneme in range(3):
            try:
                for token_limit in (None, 3072):
                    metin, finish = _gemini_istek(
                        prompt, ayar, model=model, gorsel=gorsel, max_tokens=token_limit,
                    )
                    if not metin:
                        break
                    if _metin_eksik_mi(metin, finish):
                        if finish == 'MAX_TOKENS' and token_limit is None:
                            print(
                                f'AI: Yanıt kesildi ({model}) — uzun token ile tekrar',
                                flush=True,
                            )
                            continue
                        print(
                            f'AI: Eksik yanıt ({model}, {finish}) — sonraki deneme/model',
                            flush=True,
                        )
                        break
                    if model != primary:
                        print(f'AI: Gemini yedek model ({model})', flush=True)
                    return metin, None
            except urllib.error.HTTPError as e:
                son_kod = e.code
                if e.code == 429:
                    kota_doldu = True
                    _model_kota_isaretle(model)
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
                if _gecici_http_kodu(e.code) and deneme < 2:
                    time.sleep(2 ** deneme + (1 if e.code == 503 else 0))
                    continue
                if e.code == 404:
                    break
                break
            except (urllib.error.URLError, TimeoutError, Exception) as e:
                print(f'AI yorum hatası (gemini/{model}): {e}', flush=True)
                break
    if kota_doldu:
        print('AI: Gemini kotası doldu — hazır yorum devreye girer', flush=True)
    return None, 429 if kota_doldu else son_kod


def _kullanici_hata_mesaji(hatalar):
    if not hatalar:
        return None
    kodlar = []
    for h in hatalar:
        if ':' in h:
            kodlar.append(h.split(':', 1)[1])
    if '429' in kodlar or '503' in kodlar:
        return 'Servis yoğun; FalımaBak yorumu gösteriliyor. Biraz sonra tekrar deneyin.'
    if any(k in ('401', '403', '400') for k in kodlar):
        return 'Bağlantı kurulamadı; FalımaBak yorumu gösteriliyor.'
    return 'Bağlantı kurulamadı; FalımaBak yorumu gösteriliyor.'


def _gecersiz_foto_yaniti(metin, tip):
    if not metin:
        return None
    u = metin.upper().replace('İ', 'I').replace('Ş', 'S').replace('Ğ', 'G')
    if 'GECERSIZ FOTOGRAF' in u or 'GEÇERSİZ FOTOĞRAF' in metin.upper():
        if tip == 'elfali':
            return (
                'Bu fotoğraflar el falı için uygun değil. '
                'Gerçek avuç içi ve el dışı fotoğrafı yükleyin.'
            )
        return (
            'Bu fotoğraflar kahve falı için uygun değil. '
            'Fincan içi ve tabak fotoğrafı yükleyin.'
        )
    return None


def _ollama_istek(prompt, ayar):
    veri = _http_post(
        ayar['ollama_url'],
        {
            'model': ayar['ollama_model'],
            'prompt': prompt,
            'stream': False,
            'options': {'temperature': 0.85, 'num_predict': 1200},
        },
        timeout=int(ayar.get('ai_timeout', 90)),
    )
    return (veri.get('response') or '').strip() or None


def _chat_openai_istek(url, api_key, model, prompt, ayar, extra_headers=None):
    """OpenAI uyumlu chat/completions (OpenRouter, Groq)."""
    zaman_asimi = int(ayar.get('ai_timeout', 45))
    hdrs = {
        'Authorization': f'Bearer {api_key}',
    }
    if extra_headers:
        hdrs.update(extra_headers)
    veri = _http_post(
        url,
        {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.88,
            'max_tokens': 2048,
        },
        headers=hdrs,
        timeout=zaman_asimi,
    )
    secimler = veri.get('choices') or []
    if not secimler:
        return None
    mesaj = secimler[0].get('message') or {}
    metin = (mesaj.get('content') or '').strip()
    return metin or None


def _modeller_listesi(ayar, primary_key, yedek_key, varsayilan, varsayilan_yedek):
    primary = (ayar.get(primary_key) or varsayilan).strip()
    modeller = [primary] if primary else []
    for m in ayar.get(yedek_key) or varsayilan_yedek:
        m = (m or '').strip()
        if m and m not in modeller:
            modeller.append(m)
    return modeller


def _bulut_metin_dene(saglayici, prompt, ayar):
    """OpenRouter veya Groq — yalnızca metin fal."""
    if saglayici == 'openrouter':
        anahtar = _openrouter_anahtar(ayar)
        if not anahtar:
            return None, None
        url = 'https://openrouter.ai/api/v1/chat/completions'
        modeller = _modeller_listesi(
            ayar, 'openrouter_model', 'openrouter_yedek_modeller',
            'deepseek/deepseek-chat', ['qwen/qwen-2.5-72b-instruct'],
        )
        ek_hdr = {
            'HTTP-Referer': 'https://github.com/kumarbaz230-hue/falimabak',
            'X-Title': 'Falimabak',
        }
    elif saglayici == 'groq':
        anahtar = _groq_anahtar(ayar)
        if not anahtar:
            return None, None
        url = 'https://api.groq.com/openai/v1/chat/completions'
        modeller = _modeller_listesi(
            ayar, 'groq_model', 'groq_yedek_modeller',
            'llama-3.3-70b-versatile', ['llama-3.1-8b-instant'],
        )
        ek_hdr = {}
    elif saglayici == 'xai':
        anahtar = _xai_anahtar(ayar)
        if not anahtar:
            return None, None
        url = 'https://api.x.ai/v1/chat/completions'
        modeller = _modeller_listesi(
            ayar, 'xai_model', 'xai_yedek_modeller',
            'grok-2-1212', ['grok-beta'],
        )
        ek_hdr = {}
    else:
        return None, None

    son_kod = None
    for model in modeller:
        for deneme in range(2):
            try:
                _gemini_istek_araligi()
                metin = _chat_openai_istek(url, anahtar, model, prompt, ayar, ek_hdr)
                if metin and not _metin_eksik_mi(metin):
                    if model != modeller[0]:
                        print(f'AI: {saglayici} yedek model ({model})', flush=True)
                    return metin, None
                if metin:
                    print(f'AI: {saglayici} eksik yanıt ({model})', flush=True)
            except urllib.error.HTTPError as e:
                son_kod = e.code
                detay = ''
                try:
                    detay = e.read().decode('utf-8', errors='replace')[:200]
                except Exception:
                    pass
                print(f'AI HTTP ({saglayici}/{model}): {e.code} {e.reason} {detay}', flush=True)
                if _gecici_http_kodu(e.code) and deneme == 0:
                    time.sleep(2 + (1 if e.code == 503 else 0))
                    continue
                break
            except (urllib.error.URLError, TimeoutError, Exception) as e:
                print(f'AI hata ({saglayici}/{model}): {e}', flush=True)
                break
    return None, son_kod


def _veri_ozeti(tip, veri):
    """Kart/sembol veritabanı özeti — AI sadece hikâyeleştirir."""
    veri = veri or {}
    if tip == 'tarot':
        satirlar = []
        for k in veri.get('kartlar') or []:
            satirlar.append(
                f"• {k.get('pozisyon', '')}: {k.get('isim', '')} ({k.get('durum', '')}) "
                f"— anlam: {k.get('anlam', '')}"
            )
        return '\n'.join(satirlar) or 'Tarot kartları çekildi.'
    if tip == 'kahve':
        acik = veri.get('foto_aciklamalari') or []
        if acik:
            return 'Fotoğraflar: ' + '; '.join(acik)
        sek = veri.get('sekiller') or []
        return 'Semboller: ' + ', '.join(sek) if sek else 'Kahve falı sembolleri.'
    if tip == 'elfali':
        ciz = veri.get('cizgiler') or []
        el = veri.get('el_tipi') or ''
        parca = [f'El tipi: {el}'] if el else []
        if ciz:
            parca.append('Çizgiler: ' + ', '.join(ciz))
        return '\n'.join(parca) or 'El falı çizgileri.'
    if tip == 'astroloji':
        return f"Burç: {veri.get('burc', '')}\nDoğum: {veri.get('dogum', '')}"
    if tip == 'burc_eslesme':
        return (
            f"Kişi 1: {veri.get('isim1', '')} — {veri.get('burc1', '')} ({veri.get('dogum1', '')})\n"
            f"Kişi 2: {veri.get('isim2', '')} — {veri.get('burc2', '')} ({veri.get('dogum2', '')})\n"
            f"Uyum skoru: {veri.get('skor', '')}/100"
        )
    if tip == 'ruya':
        return (veri.get('ruya') or veri.get('ozet') or '').strip()
    if tip == 'diger':
        alt = veri.get('alt_tip') or veri.get('tur', '')
        ozet = veri.get('sonuc', '')
        if veri.get('kartlar'):
            ozet = '; '.join(
                f"{k.get('pozisyon')}: {k.get('isim')}" for k in veri['kartlar']
            )
        elif veri.get('cicekler'):
            ozet = ', '.join(c.get('isim', '') for c in veri['cicekler'])
        return f"Fal: {alt}\nSonuç/semboller: {ozet}"
    return str(veri)[:800]


def _prompt_hikayelestir(tip, veri, kullanici=''):
    """Kısa prompt — temel veri + hikâyeleştirme (düşük token)."""
    ozet = _veri_ozeti(tip, veri)
    tip_etiket = {
        'tarot': 'Tarot', 'kahve': 'Kahve', 'elfali': 'El Falı',
        'astroloji': 'Astroloji', 'burc_eslesme': 'Burç Eşleşmesi',
        'ruya': 'Rüya Tabiri', 'diger': 'Fal',
    }.get(tip, tip)
    return (
        f'Sen Türk {tip_etiket} yorumcususun. Eğlence amaçlı, sıcak Türkçe yaz.\n'
        f'{kullanici}'
        f'Temel fal verisi (doğru kabul et, kart/sembol uydurma):\n{ozet}\n\n'
        'Görev: Yukarıdaki veriyi en az 4 paragraf akıcı yoruma dönüştür. '
        'Sadece selamlama yazma; aşk, kariyer ve genel mesaj ekle. '
        'Kesin gelecek iddiası ve korku dili kullanma.\n'
        'Sadece yorum metnini yaz.'
    )


def _prompt_olustur(tip, veri, gorsel_var=False):
    kullanici = ''
    try:
        from gecmis import kullanici_ismi
        isim = kullanici_ismi()
        if isim:
            kullanici = f'Kullanıcının adı: {isim}. Samimi hitap edebilirsin.\n'
    except Exception:
        pass

    if not gorsel_var and tip in (
        'tarot', 'astroloji', 'burc_eslesme', 'ruya', 'diger', 'kahve', 'elfali',
    ):
        return _prompt_hikayelestir(tip, veri, kullanici)

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
                'ÖNEMLİ: Fotoğraflarda kahve fincanı/telve/tabağı yoksa (manzara, yüz, hayvan, '
                'rastgele nesne vb.) SADECE şunu yaz: '
                '"GEÇERSİZ FOTOĞRAF: Bu görüntüler kahve falı için uygun değil."\n'
                'Geçerli fincan fotoğraflarıysa tümünü birlikte incele. Fincan içi telveleri ve '
                'tabaktaki izleri değerlendir.\n'
                'Önce gördüğün 3-6 sembolü madde madde listele, sonra 3-5 paragraf yorum yaz: '
                'aşk, para, sağlık ve genel mesaj. Olumlu ama gerçekçi ol. '
                'Korkutucu veya kesin gelecek iddiası kullanma.'
            )

    if tip == 'elfali' and gorsel_var:
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
                'ÖNEMLİ: Fotoğraflarda gerçek el/avuç yoksa (manzara, yüz, hayvan, yemek, '
                'rastgele nesne vb.) SADECE şunu yaz: '
                '"GEÇERSİZ FOTOĞRAF: Bu görüntüler el falı için uygun değil."\n'
                'Geçerli el fotoğraflarıysa avuç içi çizgileri ile elin dış/üst görünümünü '
                'birlikte değerlendir.\n'
                'Önce gözlemlerini kısaca özetle, sonra 3-5 paragraf yaz: karakter, aşk, kariyer, şans.\n'
                'Olumlu ama gerçekçi ol. Kesin gelecek iddiası kullanma.'
            )

    return _prompt_hikayelestir(tip, veri, kullanici)


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
    if tip == 'burc_eslesme':
        b1 = veri.get('burc1', '')
        b2 = veri.get('burc2', '')
        skor = veri.get('skor', 70)
        return (
            f'{hitap}{b1} ve {b2} burçları %{skor} uyum gösteriyor. '
            'Farklılıklarınız sizi tamamlayabilir; iletişim ve sabırla güzel bir denge kurabilirsiniz.'
        )
    if tip == 'ruya':
        return random.choice([
            f'{hitap}rüyanız bilinçaltınızın size nazik bir mesaj taşıdığını gösteriyor. '
            'Semboller yakın zamanda için umut ve yenilenme enerjisi müjdeler.',
            f'{hitap}gördüğünüz imgeler duygusal bir dönüşümün habercisi olabilir. '
            'İç sesinize kulak verdiğinizde doğru yolu bulacaksınız.',
            f'{hitap}rüyanızdaki detaylar, bastırılmış bir arzunun veya çözülmeyi bekleyen '
            'bir konunun yansıması olabilir. Sabırlı ve meraklı kalın.',
        ])
    if tip == 'diger':
        return f'{hitap}yıldızlar size güzel günler müjdeliyor. Pozitif kalın ve sezgilerinize güvenin.'
    return f'{hitap}evren size güzel haberler hazırlıyor. Pozitif kalın ve fırsatları değerlendirin.'


def _yorum_uret(text_prompt, ayar, gorsel=None, vision_prompt=None):
    """Sırayla kaynakları dener; (metin, kaynak, hatalar)."""
    hatalar = []
    gemini_prompt = vision_prompt if gorsel and vision_prompt else text_prompt
    gorsel_var = bool(gorsel)
    for kaynak in _kaynak_sirasi(ayar, gorsel_var=gorsel_var):
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
        elif kaynak == 'openrouter':
            metin, kod = _bulut_metin_dene('openrouter', text_prompt, ayar)
            if metin:
                print('AI kaynak: OpenRouter (bulut yedek)', flush=True)
                return metin, 'openrouter', None
            if kod:
                hatalar.append(f'openrouter:{kod}')
        elif kaynak == 'xai':
            metin, kod = _bulut_metin_dene('xai', text_prompt, ayar)
            if metin:
                print('AI kaynak: Grok/xAI (bulut yedek)', flush=True)
                return metin, 'xai', None
            if kod:
                hatalar.append(f'xai:{kod}')
        elif kaynak == 'groq':
            metin, kod = _bulut_metin_dene('groq', text_prompt, ayar)
            if metin:
                print('AI kaynak: Groq (bulut yedek)', flush=True)
                return metin, 'groq', None
            if kod:
                hatalar.append(f'groq:{kod}')
        elif kaynak == 'ollama' and ollama_aktif_mi():
            try:
                metin = _ollama_istek(text_prompt, ayar)
                if metin and not _metin_eksik_mi(metin):
                    if hatalar:
                        print(
                            f'AI kaynak: Ollama (Gemini başarısız: {", ".join(hatalar)})',
                            flush=True,
                        )
                    else:
                        print('AI kaynak: Ollama (yerel)', flush=True)
                    return metin, 'ollama', None
                if metin:
                    print(
                        f'AI: Ollama yanıtı çok kısa ({len(metin.strip())} karakter) — atlanıyor',
                        flush=True,
                    )
                    hatalar.append('ollama:kisa')
            except urllib.error.HTTPError as e:
                hatalar.append(f'ollama:{e.code}')
                print(f'AI HTTP hatası (ollama): {e.code} {e.reason}', flush=True)
            except (urllib.error.URLError, TimeoutError, Exception) as e:
                hatalar.append('ollama:hata')
                print(f'AI yorum hatası (ollama): {e}', flush=True)
    return None, None, hatalar


def yorum_al(tip, veri, callback, coin_dahil=True):
    """
    callback(metin, ai_kullanildi, hata, kaynak)
    ai_kullanildi=True → Gemini veya Ollama kullanıldı.
    kaynak: 'gemini' | 'ollama' | None
    coin_dahil=False → coin zaten yorum_baslat ile düşüldü (tarot, kahve vb.)
    """
    if coin_dahil:
        from fal_limit import yorum_baslat
        yorum_baslat(tip, lambda: _yorum_al_calistir(tip, veri, callback))
    else:
        _yorum_al_calistir(tip, veri, callback)


def _yorum_al_calistir(tip, veri, callback):

    def _sonuc(metin, ai_kullanildi, hata, kaynak=None, fotograf=False):
        if hata and not metin:
            try:
                from fal_limit import fal_basarisiz_iade
                fal_basarisiz_iade(tip)
            except Exception:
                pass
        elif metin:
            try:
                from gecmis import baslik_olustur, fal_kaydet
                fal_kaydet(tip, baslik_olustur(tip, veri), metin)
            except Exception:
                pass
            try:
                from reklam import fal_sonrasi_reklam
                fal_sonrasi_reklam()
            except Exception:
                pass
        callback(metin, ai_kullanildi, hata, kaynak, fotograf)

    def _calistir():
        ayar = _ayar_yukle()
        foto_yollari = list(veri.get('foto_yollari') or [])
        if not foto_yollari:
            tek = veri.get('foto_yolu') or veri.get('foto')
            if tek:
                foto_yollari = [tek]
        aciklamalar = list(veri.get('foto_aciklamalari') or [])
        gorsel = None
        fotograf_fal = bool(foto_yollari and tip in ('kahve', 'elfali'))
        foto_ozellikleri = []

        if fotograf_fal:
            from foto_analiz import fotolar_dogrula
            ok, hata, foto_ozellikleri = fotolar_dogrula(tip, foto_yollari, aciklamalar)
            if not ok:
                _ana_thread(lambda h=hata: _sonuc(None, False, h, None))
                return

        if not ayar.get('ai_aktif', True):
            from offline_yorum import offline_yorum_uret
            metin = offline_yorum_uret(
                tip, _veri_nonce({**veri, 'foto_aciklamalari': aciklamalar}), foto_ozellikleri,
            )
            _ana_thread(lambda m=metin: _sonuc(m, True, None, 'cihaz', fotograf_fal))
            return

        if foto_yollari and tip in ('kahve', 'elfali') and _gemini_anahtar(ayar):
            gorseller = _fotolar_hazirla(foto_yollari)
            if gorseller:
                gorsel = gorseller if len(gorseller) > 1 else gorseller[0]
                print(
                    f'AI: {len(gorseller)} fotoğraf Gemini Vision ile deneniyor',
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
        if metin and _metin_eksik_mi(metin):
            print(
                f'AI: yanıt fal yorumu için yetersiz ({len(metin.strip())} karakter) — cihaz yorumu',
                flush=True,
            )
            hatalar = list(hatalar or [])
            hatalar.append('kisa_yanit')
            metin = None
        if metin:
            foto_hata = _gecersiz_foto_yaniti(metin, tip) if fotograf_fal else None
            if foto_hata:
                print('AI: geçersiz foto — kullanıcıya bildiriliyor', flush=True)
                _ana_thread(lambda h=foto_hata: _sonuc(None, False, h, kaynak, False))
                return
            _ana_thread(
                lambda m=metin, k=kaynak, f=fotograf_ai and k == 'gemini':
                _sonuc(m, True, None, k, f),
            )
            return

        from offline_yorum import offline_yorum_uret
        offline_metin = offline_yorum_uret(
            tip, _veri_nonce({**veri, 'foto_aciklamalari': aciklamalar}), foto_ozellikleri,
        )
        hata_mesaji = _kullanici_hata_mesaji(hatalar) if hatalar else None
        if hatalar:
            print(f'AI: bulut başarısız ({", ".join(hatalar)}), cihaz yorumu', flush=True)
        else:
            print('AI kaynak: Cihaz içi', flush=True)
        _ai_log(f'cihaz tip={tip} bulut_hata={hatalar}')
        _ana_thread(
            lambda m=offline_metin, h=hata_mesaji: _sonuc(m, True, h, 'cihaz', fotograf_fal),
        )

    threading.Thread(target=_calistir, daemon=True).start()
