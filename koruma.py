"""
FalımaBak — gömülü Gemini anahtarı (base64). Uygulamayı kapatmaz.
"""

import base64

# API anahtarı — APK içinde; dağıtımda rotate edin
_B64 = (
    'QVEuQWliOFJONkEzWk1YUTFBekJPS2JFOE5GSURGQjZVd2RIcWJE'
    'Zl92dk1JYldVX3VJYkJhZw=='
)

_anahtar_cache = None


def _coz_ham():
    try:
        metin = base64.b64decode(_B64).decode('utf-8').strip()
        if (metin.startswith('AQ.') or metin.startswith('AIza')) and len(metin) >= 20:
            return metin
    except Exception:
        pass
    return ''


def gomulu_api_anahtar():
    global _anahtar_cache
    if _anahtar_cache is not None:
        return _anahtar_cache
    _anahtar_cache = _coz_ham()
    return _anahtar_cache


_DS_B64 = 'c2stMDQ0YjNjZTRiNzQyNDE5MmJkZjcyYzI2ZDRkYTIzM2M='
_ds_cache = None


def gomulu_deepseek_anahtar():
    """APK içi DeepSeek anahtarı."""
    global _ds_cache
    if _ds_cache is not None:
        return _ds_cache
    try:
        metin = base64.b64decode(_DS_B64).decode('utf-8').strip()
        if metin.startswith('sk-') and len(metin) >= 20:
            _ds_cache = metin
            return metin
    except Exception:
        pass
    _ds_cache = ''
    return ''


def koruma_baslat():
    """Açılışta çağrılır — uygulamayı asla kapatmaz."""
    anahtar = gomulu_api_anahtar()
    print(f'Koruma: API anahtarı {"hazır" if anahtar else "YOK"}', flush=True)
