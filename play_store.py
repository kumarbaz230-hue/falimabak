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


def _in_app_review_dene():
    """Google In-App Review — uygulamadan çıkmadan yıldız penceresi."""
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Helper = autoclass('org.kumar.falimabak.falimabak.PlayReviewHelper')
        activity = PythonActivity.mActivity
        return bool(Helper.tryInAppReview(activity))
    except Exception as e:
        print(f'In-App Review: {e}', flush=True)
        return False


def _magaza_sayfasi_ac():
    """Play Store uygulama sayfasını harici olarak aç."""
    if _android_mi():
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Helper = autoclass('org.kumar.falimabak.falimabak.PlayReviewHelper')
            activity = PythonActivity.mActivity
            if Helper.openStoreListing(activity):
                return True
        except Exception as e:
            print(f'Play Store helper: {e}', flush=True)
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            activity = PythonActivity.mActivity
            intent = Intent(Intent.ACTION_VIEW, Uri.parse(WEB_URL))
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
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


def magaza_degerlendir():
    """Önce uygulama içi değerlendirme; olmazsa Play Store sayfası."""
    if _android_mi():
        if _in_app_review_dene():
            return True
    return _magaza_sayfasi_ac()


def magaza_degerlendir_odullu():
    """Değerlendirme penceresini aç; ilk kez coin ver."""
    acildi = magaza_degerlendir()
    if not acildi:
        return False, False, 0
    from coin import degerlendirme_odulu_ver
    verildi, miktar = degerlendirme_odulu_ver()
    return acildi, verildi, miktar
