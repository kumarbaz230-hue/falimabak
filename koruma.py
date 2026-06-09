"""
FalımaBak — API anahtarı (XOR). Uygulamayı kapatmaz; sadece anahtarı gizler.
"""

import os

_ENC = (
    29, 57, 118, 29, 62, 116, 14, 38, 110, 24, 111, 6, 33, 52, 57, 93,
    29, 66, 14, 35, 23, 62, 116, 38, 30, 37, 40, 30, 14, 110, 9, 67,
    88, 38, 57, 62, 40, 59, 78, 78, 33, 37, 62, 11, 9, 59, 73, 37,
    62, 14, 61, 79,
)
_MASK = 0x5C

_anahtar_cache = None


def _coz_ham():
    try:
        metin = ''.join(chr(b ^ _MASK) for b in _ENC)
        if metin.startswith('AQ.') and len(metin) >= 20:
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


def koruma_baslat():
    """Açılışta çağrılır — uygulamayı asla kapatmaz."""
    anahtar = gomulu_api_anahtar()
    print(f'Koruma: API anahtarı {"hazır" if anahtar else "YOK"}', flush=True)
