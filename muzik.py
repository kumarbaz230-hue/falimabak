"""FalımaBak — arka plan müziği (ayarlardan aç/kapa + ses)."""

import os

from kivy.clock import Clock

from theme import asset_yolu

_sound = None
_hazir = False


def _yukle_ayar():
    try:
        from gecmis import muzik_acik_al, muzik_seviye_al
        return muzik_acik_al(), muzik_seviye_al()
    except Exception:
        return False, 0.35


def _kaydet_ayar(acik, seviye):
    try:
        from gecmis import muzik_acik_kaydet, muzik_seviye_kaydet
        muzik_acik_kaydet(acik)
        muzik_seviye_kaydet(seviye)
    except Exception:
        pass


def muzik_dosyasi():
    for ad in ('tarot_throat.mp3', 'ambiyans.ogg', 'ambiyans.mp3', 'ambiyans.wav'):
        yol = asset_yolu(os.path.join('muzik', ad))
        if yol and os.path.isfile(yol):
            return yol
    return ''


def muzik_hazirla():
    global _hazir
    if _hazir:
        return bool(muzik_dosyasi())
    _hazir = True
    return bool(muzik_dosyasi())


def _ses_uygula():
    """Yüklü ses nesnesine güncel ayarları uygula."""
    global _sound
    if not _sound:
        return
    acik, seviye = _yukle_ayar()
    seviye = max(0.0, min(1.0, seviye))
    _sound.volume = seviye if acik else 0.0
    if acik:
        if _sound.state == 'stop':
            try:
                _sound.play()
            except Exception:
                pass
    elif _sound.state == 'play':
        try:
            _sound.stop()
        except Exception:
            pass


def muzik_baslat():
    global _sound
    yol = muzik_dosyasi()
    if not yol:
        return False
    try:
        from kivy.core.audio import SoundLoader
        if _sound is None or getattr(_sound, '_source', None) != yol:
            if _sound and _sound.state == 'play':
                try:
                    _sound.stop()
                except Exception:
                    pass
            _sound = SoundLoader.load(yol)
            if _sound is None:
                return False
            _sound._source = yol
            _sound.loop = True
        _ses_uygula()
        return True
    except Exception as e:
        print(f'Müzik: {e}', flush=True)
        return False


def muzik_durdur():
    global _sound
    if _sound and _sound.state == 'play':
        try:
            _sound.stop()
        except Exception:
            pass


def muzik_acik_mi():
    acik, _ = _yukle_ayar()
    return acik


def muzik_seviye():
    _, sev = _yukle_ayar()
    return sev


def muzik_ac_kapat(acik):
    _kaydet_ayar(acik, muzik_seviye())
    muzik_baslat()
    _ses_uygula()


def muzik_seviye_ayarla(seviye):
    seviye = max(0.0, min(1.0, float(seviye)))
    _kaydet_ayar(muzik_acik_mi(), seviye)
    if muzik_acik_mi():
        muzik_baslat()
    _ses_uygula()


def muzik_uygula():
    """Ana sayfa / ayar sonrası çağır."""
    Clock.schedule_once(lambda *_: muzik_baslat(), 0.3)
