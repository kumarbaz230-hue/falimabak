"""Play Store — uygulama sayfası ve değerlendirme."""

import os

PAKET = 'org.kumar.falimabak.falimabak'
WEB_URL = f'https://play.google.com/store/apps/details?id={PAKET}'


def _android_mi():
    return (
        'ANDROID_ARGUMENT' in os.environ
        or 'ANDROID_ROOT' in os.environ
        or 'ANDROID_BOOTLOGO' in os.environ
    )


def magaza_degerlendir():
    """Play Store uygulama sayfasını aç (değerlendirme için)."""
    if _android_mi():
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            activity = PythonActivity.mActivity
            uri = Uri.parse(f'market://details?id={PAKET}')
            intent = Intent(Intent.ACTION_VIEW, uri)
            intent.setPackage('com.android.vending')
            activity.startActivity(intent)
            return True
        except Exception as e:
            print(f'Play Store market: {e}', flush=True)
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            activity = PythonActivity.mActivity
            intent = Intent(Intent.ACTION_VIEW, Uri.parse(WEB_URL))
            activity.startActivity(intent)
            return True
        except Exception as e:
            print(f'Play Store web: {e}', flush=True)
    try:
        import webbrowser
        webbrowser.open(WEB_URL)
        return True
    except Exception:
        return False


def magaza_degerlendir_odullu():
    """Play Store aç; ilk kez değerlendiren kullanıcıya coin ver."""
    acildi = magaza_degerlendir()
    if not acildi:
        return False, False, 0
    from coin import degerlendirme_odulu_ver
    verildi, miktar = degerlendirme_odulu_ver()
    return acildi, verildi, miktar
