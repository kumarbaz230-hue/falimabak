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


_GR_ENC = (
    110, 60, 106, 24, 64, 84, 79, 83, 75, 66, 126, 114, 122, 62, 106, 114,
    87, 42, 99, 120, 46, 104, 113, 119, 87, 78, 98, 103, 79, 57, 68, 74,
    79, 108, 51, 75, 105, 11, 72, 35, 105, 54, 116, 51, 76, 65, 71, 96,
    92, 110, 101, 68, 53, 71, 107, 106,
)
_GR_SEED_A = 'falimabak_koruma_v1'
_GR_SEED_B = 'org.kumar.falimabak'
_gr_cache = None


def gomulu_groq_anahtar():
    """APK içi Groq anahtarı — mobil yedek AI."""
    global _gr_cache
    if _gr_cache is not None:
        return _gr_cache
    try:
        parca = []
        for i, c in enumerate(_GR_ENC):
            parca.append(chr(
                c ^ ord(_GR_SEED_A[i % len(_GR_SEED_A)])
                ^ ord(_GR_SEED_B[(i * 3) % len(_GR_SEED_B)])
            ))
        metin = ''.join(parca).strip()
        if metin.startswith('gsk_') and len(metin) >= 20:
            _gr_cache = metin
            return metin
    except Exception:
        pass
    _gr_cache = ''
    return ''


def koruma_baslat():
    """Açılışta çağrılır — uygulamayı asla kapatmaz."""
    anahtar = gomulu_api_anahtar()
    print(f'Koruma: API anahtarı {"hazır" if anahtar else "YOK"}', flush=True)
