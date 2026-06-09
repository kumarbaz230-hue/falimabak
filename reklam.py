"""
FalımaBak — AdMob reklam yönetimi (banner + interstitial).
Test modu varsayılan; gerçek ID'ler secrets.json içinde.
"""

import json
import os
import time

from kivy.clock import Clock
from kivy.metrics import dp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRETS_YOLU = os.path.join(BASE_DIR, 'secrets.json')
SECRETS_ORNEK = os.path.join(BASE_DIR, 'secrets.ornek.json')

_BANNER_EKRANLAR = frozenset({'anasayfa', 'gecmis', 'ayarlar'})
_INTERSTITIAL_ARALIK = 90

_ads = None
_baslati = False
_banner_gorunur = False
_son_interstitial = 0.0


def _android_mi():
    return (
        'ANDROID_ARGUMENT' in os.environ
        or 'ANDROID_ROOT' in os.environ
        or 'ANDROID_BOOTLOGO' in os.environ
    )


def _reklam_ayar():
    """AdMob birimleri — config.ornek.json APK içinde; secrets.json masaüstü geliştirme."""
    veri = {}
    yollar = [SECRETS_YOLU, os.path.join(BASE_DIR, 'config.ornek.json')]
    if _android_mi():
        try:
            from kivy.app import App
            app = App.get_running_app()
            if app and app.user_data_dir:
                yollar.insert(0, os.path.join(app.user_data_dir, 'config.json'))
        except Exception:
            pass
    for yol in yollar:
        if yol and os.path.isfile(yol):
            try:
                with open(yol, encoding='utf-8') as f:
                    veri.update(json.load(f))
            except Exception:
                pass
    test_mod = bool(veri.get('admob_test_mod', True))
    app_id = veri.get('admob_app_id', '').strip()
    banner_id = veri.get('admob_banner_id', '').strip()
    inter_id = veri.get('admob_interstitial_id', '').strip()

    from kivmob import TestIds

    def _gecerli(unit_id):
        return unit_id and 'XXXX' not in unit_id and unit_id.startswith('ca-app-pub-')

    if not _gecerli(app_id):
        app_id = TestIds.APP
    if not _gecerli(banner_id):
        banner_id = TestIds.BANNER
    if not _gecerli(inter_id):
        inter_id = TestIds.INTERSTITIAL

    return {
        'test_mod': banner_id == TestIds.BANNER or inter_id == TestIds.INTERSTITIAL,
        'app_id': app_id,
        'banner_id': banner_id,
        'interstitial_id': inter_id,
    }


def reklam_aktif():
    return _android_mi() and _baslati


def banner_yukseklik():
    """Kivy layout altında banner için boşluk."""
    return dp(52) if (_android_mi() and _banner_gorunur) else 0


def reklam_alani_bosluk():
    """Banner alt boşluğu — native reklamın üstüne binmemesi için."""
    from kivy.uix.widget import Widget
    return Widget(size_hint_y=None, height=banner_yukseklik())


def reklam_hazirla():
    """Uygulama açılışında bir kez çağır."""
    global _ads, _baslati
    if not _android_mi() or _baslati:
        return
    try:
        from kivmob import KivMob
        ayar = _reklam_ayar()
        _ads = KivMob(ayar['app_id'])
        _ads.new_banner(ayar['banner_id'], top_pos=False)
        _ads.request_banner()
        _ads.new_interstitial(ayar['interstitial_id'])
        _ads.request_interstitial()
        _baslati = True
        print(f"Reklam hazır (test={ayar['test_mod']})", flush=True)
    except Exception as e:
        print(f'Reklam başlatılamadı: {e}', flush=True)


def _banner_goster():
    global _banner_gorunur
    if not _ads:
        return
    try:
        _ads.show_banner()
        _banner_gorunur = True
    except Exception as e:
        print(f'Banner göster: {e}', flush=True)


def _banner_gizle():
    global _banner_gorunur
    if not _ads:
        return
    try:
        _ads.hide_banner()
        _banner_gorunur = False
    except Exception as e:
        print(f'Banner gizle: {e}', flush=True)


def ekran_reklam_guncelle(ekran_adi):
    """ScreenManager.current değişince çağır."""
    if not _baslati:
        return
    if ekran_adi in _BANNER_EKRANLAR:
        Clock.schedule_once(lambda *_: _banner_goster(), 0.15)
    else:
        _banner_gizle()


def _interstitial_yenile():
    if _ads:
        try:
            _ads.request_interstitial()
        except Exception:
            pass


def fal_sonrasi_reklam():
    """Başarılı fal yorumundan sonra tam ekran reklam (cooldown ile)."""
    global _son_interstitial
    if not _ads or not _android_mi():
        return
    simdi = time.time()
    if simdi - _son_interstitial < _INTERSTITIAL_ARALIK:
        return

    def _goster(*_):
        global _son_interstitial
        try:
            if _ads.is_interstitial_loaded():
                _banner_gizle()
                _ads.show_interstitial()
                _son_interstitial = time.time()
                Clock.schedule_once(lambda *__: _interstitial_yenile(), 3)
                try:
                    from kivy.app import App
                    app = App.get_running_app()
                    if app and app.root:
                        Clock.schedule_once(
                            lambda *__, e=app.root.current: ekran_reklam_guncelle(e), 4,
                        )
                except Exception:
                    pass
        except Exception as e:
            print(f'Interstitial: {e}', flush=True)

    Clock.schedule_once(_goster, 0.4)


def gizlilik_url():
    return 'https://kumarbaz230-hue.github.io/falimabak/gizlilik.html'


def url_ac(url):
    if not url:
        return
    if _android_mi():
        try:
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            activity.startActivity(intent)
            return
        except Exception as e:
            print(f'URL aç: {e}', flush=True)
    try:
        import webbrowser
        webbrowser.open(url)
    except Exception:
        pass
