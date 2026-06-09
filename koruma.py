"""
FalımaBak — API anahtarı koruma ve temel anti-tamper.
İstemci APK'sında anahtar %100 gizlenemez; bu katman zorlaştırır ve debugger'da kapanır.
"""

import os
import sys

# XOR 0x5C ile şifrelenmiş parça (düz metin yok)
_ENC = (
    25, 9, 114, 25, 90, 84, 14, 118, 14, 48, 79, 6, 33, 52, 9, 93,
    25, 38, 14, 47, 23, 90, 57, 84, 118, 30, 37, 40, 30, 14, 14, 25,
    51, 40, 118, 61, 90, 40, 113, 50, 50, 33, 37, 90, 31, 25, 113, 49,
    37, 90, 14, 61, 59,
)
_MASK = 0x5C

_anahtar_cache = None
_ihlal = False
_erisim_sayaci = 0


def _android_mi():
    return (
        'ANDROID_ARGUMENT' in os.environ
        or 'ANDROID_ROOT' in os.environ
        or 'ANDROID_BOOTLOGO' in os.environ
    )


def _coz_ham():
    try:
        metin = ''.join(chr(b ^ _MASK) for b in _ENC)
        if not metin.startswith('AQ.') or len(metin) < 20:
            return ''
        return metin
    except Exception:
        return ''


def _debugger_bagli_mi():
    if not _android_mi():
        return False
    try:
        from jnius import autoclass
        Debug = autoclass('android.os.Debug')
        return bool(Debug.isDebuggerConnected())
    except Exception:
        return False


def _hook_tespit_mi():
    """Yaygın hook / reverse ortam ipuçları."""
    ipuclari = (
        'FRIDA', 'XPOSED', 'SUBSTRATE', 'MAGISK',
        'LD_PRELOAD', 'RIOT', 'GDB',
    )
    for anahtar, deger in os.environ.items():
        ust = f'{anahtar}={deger}'.upper()
        if any(ip in ust for ip in ipuclari):
            return True
    return False


def _guvenlik_ihlali(neden=''):
    global _ihlal, _anahtar_cache
    _ihlal = True
    _anahtar_cache = ''
    print(f'Koruma: ihlal ({neden})', flush=True)
    try:
        from kivy.app import App
        app = App.get_running_app()
        if app:
            app.stop()
    except Exception:
        pass
    os._exit(1)


def butunluk_kontrol():
    if _ihlal:
        return False
    if _debugger_bagli_mi():
        _guvenlik_ihlali('debugger')
        return False
    if _hook_tespit_mi():
        _guvenlik_ihlali('hook')
        return False
    if not _coz_ham():
        _guvenlik_ihlali('format')
        return False
    return True


def gomulu_api_anahtar():
    """Çözülmüş Gemini anahtarı."""
    global _anahtar_cache, _erisim_sayaci
    if _ihlal:
        return ''
    _erisim_sayaci += 1
    if _erisim_sayaci > 48:
        _guvenlik_ihlali('fazla_erisim')
        return ''
    if _anahtar_cache is not None:
        return _anahtar_cache
    if not butunluk_kontrol():
        return ''
    _anahtar_cache = _coz_ham()
    return _anahtar_cache


def koruma_baslat():
    """Uygulama açılışında çağrılır."""
    butunluk_kontrol()
