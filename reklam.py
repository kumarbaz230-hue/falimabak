"""
FalımaBak — AdMob reklam yönetimi (banner + interstitial).
"""

import json
import os
import time
import traceback

from kivy.clock import Clock
from kivy.metrics import dp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRETS_YOLU = os.path.join(BASE_DIR, 'secrets.json')

_BANNER_EKRANLAR = frozenset({'anasayfa', 'gecmis', 'ayarlar'})
_INTERSTITIAL_ARALIK = 90

# APK içinde her zaman geçerli (config yedek)
_VARSAYILAN_ADMOB = {
    'admob_app_id': 'ca-app-pub-9430596197237392~1799758284',
    'admob_banner_id': 'ca-app-pub-9430596197237392/2682788969',
    'admob_interstitial_id': 'ca-app-pub-9430596197237392/7839128738',
}

_ads = None
_baslati = False
_banner_gorunur = False
_son_interstitial = 0.0
_deneme = 0


def _android_mi():
    return (
        'ANDROID_ARGUMENT' in os.environ
        or 'ANDROID_ROOT' in os.environ
        or 'ANDROID_BOOTLOGO' in os.environ
    )


def _reklam_ayar():
    veri = dict(_VARSAYILAN_ADMOB)
    yollar = [
        os.path.join(BASE_DIR, 'config.ornek.json'),
        SECRETS_YOLU,
    ]
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

    from kivmob import TestIds

    def _gecerli(unit_id):
        return unit_id and 'XXXX' not in unit_id and unit_id.startswith('ca-app-pub-')

    app_id = veri.get('admob_app_id', '').strip()
    banner_id = veri.get('admob_banner_id', '').strip()
    inter_id = veri.get('admob_interstitial_id', '').strip()

    if not _gecerli(app_id):
        app_id = TestIds.APP
    if not _gecerli(banner_id):
        banner_id = TestIds.BANNER
    if not _gecerli(inter_id):
        inter_id = TestIds.INTERSTITIAL

    return {
        'app_id': app_id,
        'banner_id': banner_id,
        'interstitial_id': inter_id,
        'test_banner': banner_id == TestIds.BANNER,
    }


def reklam_aktif():
    return _android_mi() and _baslati


def banner_yukseklik():
    return dp(52) if (_android_mi() and _banner_gorunur) else 0


def reklam_alani_bosluk():
    from kivy.uix.widget import Widget
    return Widget(size_hint_y=None, height=banner_yukseklik())


def _banner_yukle_goster():
    if not _ads:
        return
    try:
        _ads.show_banner()
        global _banner_gorunur
        _banner_gorunur = True
        print('Banner gösterildi', flush=True)
    except Exception as e:
        print(f'Banner göster: {e}', flush=True)


def reklam_hazirla():
    """Uygulama açılışında ve ana sayfada çağır."""
    global _ads, _baslati, _deneme
    if not _android_mi():
        return
    if _baslati:
        return
    if _deneme >= 3:
        return
    _deneme += 1

    try:
        from kivmob import KivMob
        ayar = _reklam_ayar()
        print(f"Reklam başlatılıyor: app={ayar['app_id'][:20]}...", flush=True)
        _ads = KivMob(ayar['app_id'])
        _ads.new_banner(ayar['banner_id'], top_pos=False)
        _ads.request_banner()
        try:
            _ads.new_interstitial(ayar['interstitial_id'])
            _ads.request_interstitial()
        except Exception as e:
            print(f'Interstitial atlandı: {e}', flush=True)
        _baslati = True
        Clock.schedule_once(lambda *_: _banner_yukle_goster(), 2.5)
        Clock.schedule_once(lambda *_: _banner_yukle_goster(), 5.0)
    except Exception:
        print(f'Reklam hatası: {traceback.format_exc()}', flush=True)
        _baslati = False


def _banner_goster():
    _banner_yukle_goster()


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
    if not _baslati:
        reklam_hazirla()
    if not _baslati:
        return
    if ekran_adi in _BANNER_EKRANLAR:
        Clock.schedule_once(lambda *_: _banner_goster(), 0.2)
        Clock.schedule_once(lambda *_: _banner_goster(), 2.0)
    else:
        _banner_gizle()


def _interstitial_yenile():
    if _ads:
        try:
            _ads.request_interstitial()
        except Exception:
            pass


def reklam_izle(callback):
    """Tam ekran reklam; kapanınca callback(basarili)."""
    if not _android_mi():
        Clock.schedule_once(lambda *_: callback(True), 0.2)
        return
    if not _baslati:
        reklam_hazirla()
    if not _ads:
        Clock.schedule_once(lambda *_: callback(False), 0)
        return

    def _goster(*_):
        if _ads.is_interstitial_loaded():
            _banner_gizle()

            def _bitti(ok):
                if ok:
                    Clock.schedule_once(lambda *__: _interstitial_yenile(), 0.5)
                callback(ok)

            _ads.show_interstitial_callback(_bitti)
            return
        try:
            _ads.request_interstitial()
        except Exception:
            pass
        Clock.schedule_once(lambda *_: callback(False), 0)

    Clock.schedule_once(_goster, 0.1)


def fal_sonrasi_reklam():
    global _son_interstitial
    if not _android_mi():
        return
    if not _baslati:
        reklam_hazirla()
    if not _ads:
        return
    if time.time() - _son_interstitial < _INTERSTITIAL_ARALIK:
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

    Clock.schedule_once(_goster, 0.5)


def gizlilik_ac(sm):
    """Uygulama içi gizlilik ekranı."""
    if sm and 'gizlilik' in sm.screen_names:
        sm.current = 'gizlilik'
