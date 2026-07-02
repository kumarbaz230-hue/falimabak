"""Play Store güncelleme kontrolü — yeni sürüm varsa tek seferlik bildirim."""

import os
import time

_KONTROL_ARALIK = 6 * 3600  # 6 saatte bir kontrol (Play API spam olmasın)


def _android_mi():
    return (
        'ANDROID_ARGUMENT' in os.environ
        or 'ANDROID_ROOT' in os.environ
        or 'ANDROID_BOOTLOGO' in os.environ
    )


def guncelleme_bildirimi_kontrol():
    """Play'de yeni sürüm varsa bildirim göster (her sürüm için yalnızca bir kez)."""
    if not _android_mi():
        return
    from gecmis import _yukle, _kaydet

    veri = _yukle()
    simdi = time.time()
    son = float(veri.get('guncelleme_kontrol_ts') or 0)
    if simdi - son < _KONTROL_ARALIK:
        return
    veri['guncelleme_kontrol_ts'] = simdi
    _kaydet(veri)

    try:
        from bildirim import bildirim_izni_var_mi
        if not bildirim_izni_var_mi():
            return
    except Exception:
        pass

    try:
        from jnius import autoclass
        from dil import t
        from bildirim import _context

        Helper = autoclass('org.kumar.falimabak.falimabak.PlayUpdateHelper')
        Helper.checkAndNotify(
            _context(),
            t('update_notify_title'),
            t('update_notify_msg'),
        )
        print('Guncelleme kontrolu baslatildi', flush=True)
    except Exception as e:
        print(f'Guncelleme kontrol: {e}', flush=True)
