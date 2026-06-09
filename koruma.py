"""
FalımaBak — API anahtarı (XOR). Uygulamayı kapatmaz; sadece anahtarı gizler.
"""

import os

_ENC = (
    25, 9, 114, 25, 90, 84, 14, 118, 14, 48, 79, 6, 33, 52, 9, 93,
    25, 38, 14, 47, 23, 90, 57, 84, 118, 30, 37, 40, 30, 14, 14, 25,
    51, 40, 118, 61, 90, 40, 113, 50, 50, 33, 37, 90, 31, 25, 113, 49,
    37, 90, 14, 61, 59,
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
    gomulu_api_anahtar()
