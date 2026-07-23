"""Coin göstergesi (sağ üst) ve reklam popup."""

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex

from coin import (
    FAL_MALIYET, GUNLUK_GIRIS_BONUS, HOSGELDIN_BONUS, REKLAM_COIN_ODUL, REKLAM_GUNLUK_MAX,
    coin_miktar, gunluk_giris_kontrol, hosgeldin_kontrol, reklam_hakki_var, reklam_kalan,
    reklam_coin_kazan,
)
from theme import (
    RENKLER, kart_ikon_widget, metin_label, siyah_buton,
    COIN_CHIP_EN, COIN_CHIP_YUK, COIN_HIT_EN, COIN_HIT_YUK,
)

_CHIPLER = []


def coin_ui_yenile():
    for chip in list(_CHIPLER):
        try:
            chip.guncelle()
        except Exception:
            pass


def _coin_ikon_widget(boyut=None, **kwargs):
    w = kart_ikon_widget(dosya='icon_coin.png', boyut=boyut or dp(28), **kwargs)
    if w:
        return w
    return metin_label('★', font_size='18sp', bold=True, color=RENKLER['altin'], **kwargs)


class CoinChip(ButtonBehavior, BoxLayout):
    """Sağ üst altın coin rozeti — geniş dokunma alanı, şık altın pill rozet."""

    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)
        self.size_hint = (None, None)
        self.size = (dp(92), dp(36))
        self.padding = [dp(6), dp(4), dp(10), dp(4)]
        self.spacing = dp(4)

        altin = get_color_from_hex(RENKLER['altin'])
        altin2 = get_color_from_hex(RENKLER['buton_altin'])
        with self.canvas.before:
            Color(0, 0, 0, 0.40)
            self._golge = RoundedRectangle(radius=[dp(18)])
            Color(0.12, 0.08, 0.24, 0.96)
            self._bg = RoundedRectangle(radius=[dp(18)])
            Color(altin2[0], altin2[1], altin2[2], 0.20)
            self._parilti = RoundedRectangle(radius=[dp(18)])
            Color(altin[0], altin[1], altin[2], 0.80)
            self._kenar = Line(width=dp(1.2), rounded_rectangle=(0, 0, 0, 0, dp(18)))
        with self.canvas.after:
            Color(altin[0], altin[1], altin[2], 0.20)
            self._isik = Line(width=dp(0.8), rounded_rectangle=(0, 0, 0, 0, dp(18)))

        ikon_kutu = AnchorLayout(
            size_hint_x=None, width=dp(26),
            anchor_x='center', anchor_y='center',
        )
        ikon_kutu.add_widget(_coin_ikon_widget(boyut=dp(22)))
        self.add_widget(ikon_kutu)

        self._sayi = metin_label(
            '0', font_size='15sp', bold=True, color=RENKLER['altin_parlak'],
            halign='left', valign='middle',
            size_hint_x=None, width=dp(48),
            shorten=True,
        )
        self.add_widget(self._sayi)

        self.bind(pos=self._ciz, size=self._ciz)
        Clock.schedule_once(lambda *_: self._ciz(), 0)

        _CHIPLER.append(self)
        Clock.schedule_once(lambda *_: self.guncelle(), 0)

    def _ciz(self, *_):
        vx, vy = self.pos
        vw, vh = self.size
        if vw < 1 or vh < 1:
            return
        r = dp(18)
        self._golge.pos = (vx + dp(1), vy - dp(2))
        self._golge.size = (vw - dp(2), vh)
        self._bg.pos = (vx, vy)
        self._bg.size = (vw, vh)
        self._parilti.pos = (vx + dp(2), vy + vh * 0.45)
        self._parilti.size = (vw - dp(4), vh * 0.5)
        self._kenar.rounded_rectangle = (vx, vy, vw, vh, r)
        self._isik.rounded_rectangle = (vx + dp(2), vy + dp(2), vw - dp(4), vh - dp(4), r - dp(2))

    def guncelle(self):
        self._sayi.text = str(coin_miktar())

    def on_press(self):
        Animation(opacity=0.82, duration=0.06).start(self)

    def on_release(self):
        Animation(opacity=1, duration=0.12).start(self)
        coin_popup_goster()

    def __del__(self):
        try:
            _CHIPLER.remove(self)
        except ValueError:
            pass


# Geriye uyumluluk — main.py CoinHitArea import edebilir
CoinHitArea = CoinChip


def coin_satir_ekle(ust_layout):
    """Sağ üste hizalı coin satırı (BoxLayout/vertical içine)."""
    satir = BoxLayout(size_hint_y=None, height=COIN_HIT_YUK)
    satir.add_widget(BoxLayout(size_hint_x=1))
    anchor = AnchorLayout(size_hint_x=None, width=COIN_HIT_EN, anchor_x='right', anchor_y='center')
    chip = CoinChip()
    anchor.add_widget(chip)
    satir.add_widget(anchor)
    ust_layout.add_widget(satir)
    return chip


def _popup_baslik_coin():
    """Popup üstünde büyük coin ikonu."""
    satir = BoxLayout(
        orientation='horizontal', size_hint_y=None, height=dp(52),
        padding=[0, 0, 0, dp(4)],
    )
    satir.add_widget(BoxLayout(size_hint_x=1))
    ikon = AnchorLayout(size_hint_x=None, width=dp(52), anchor_x='center', anchor_y='center')
    ikon.add_widget(_coin_ikon_widget(boyut=dp(44)))
    satir.add_widget(ikon)
    satir.add_widget(BoxLayout(size_hint_x=1))
    return satir


def coin_popup_goster():
    from dil import t
    from reklam import reklam_onyukle, reklam_izle

    reklam_onyukle()
    kalan = reklam_kalan()
    bakiye = coin_miktar()

    icerik = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(8))
    icerik.add_widget(_popup_baslik_coin())
    icerik.add_widget(metin_label(
        t('coin_balance', coin=bakiye),
        font_size='17sp', bold=True, color=RENKLER['altin_parlak'],
        halign='center', size_hint_y=None, height=dp(30),
    ))
    icerik.add_widget(metin_label(
        t('coin_fal_cost', cost=FAL_MALIYET),
        font_size='12sp', color=RENKLER['gri_acik'],
        halign='center', size_hint_y=None, height=dp(36),
    ))
    icerik.add_widget(metin_label(
        t('coin_ad_info', odul=REKLAM_COIN_ODUL, kalan=kalan, max=REKLAM_GUNLUK_MAX),
        font_size='12sp', color=RENKLER['beyaz'],
        halign='center', size_hint_y=None, height=dp(48),
    ))
    btn_satir = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
    kapat = siyah_buton(t('coin_close'), font_size='14sp')
    btn_satir.add_widget(kapat)
    izle = siyah_buton(t('coin_watch_ad', odul=REKLAM_COIN_ODUL), vurgu=True, font_size='14sp')
    if not reklam_hakki_var():
        izle.disabled = True
        izle.opacity = 0.45
    btn_satir.add_widget(izle)
    icerik.add_widget(btn_satir)

    popup = Popup(
        title=t('coin_title'),
        content=icerik,
        size_hint=(0.88, None),
        height=dp(280),
        separator_color=get_color_from_hex(RENKLER['altin']),
        title_color=get_color_from_hex(RENKLER['altin']),
        auto_dismiss=False,
    )

    def _kapat(*_):
        popup.dismiss()

    def _reklam(*_):
        def _sonuc(ok):
            if ok and reklam_coin_kazan():
                coin_ui_yenile()
                _kapat()
                Clock.schedule_once(lambda *_: coin_popup_goster(), 0.15)
            elif not ok:
                _reklam_hata_popup()

        reklam_izle(_sonuc)

    kapat.bind(on_press=_kapat)
    izle.bind(on_press=_reklam)
    popup.open()


def _reklam_hata_popup():
    from dil import t

    icerik = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
    icerik.add_widget(metin_label(
        t('limit_ad_fail'),
        font_size='12sp', color=RENKLER['beyaz'],
        halign='center', size_hint_y=None, height=dp(56),
    ))
    tamam = siyah_buton(t('coin_close'), vurgu=True, font_size='14sp')
    icerik.add_widget(tamam)
    popup = Popup(
        title=t('coin_title'),
        content=icerik,
        size_hint=(0.85, None),
        height=dp(160),
        separator_color=get_color_from_hex(RENKLER['altin']),
        title_color=get_color_from_hex(RENKLER['altin']),
    )
    tamam.bind(on_press=lambda *_: popup.dismiss())
    popup.open()


def hosgeldin_popup_goster(gunluk_de=False):
    from dil import t

    icerik = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
    icerik.add_widget(_popup_baslik_coin())
    if gunluk_de:
        metin = t(
            'coin_welcome_first',
            bonus=HOSGELDIN_BONUS,
            gunluk=GUNLUK_GIRIS_BONUS,
            toplam=coin_miktar(),
        )
    else:
        metin = t('coin_welcome', bonus=HOSGELDIN_BONUS)
    icerik.add_widget(metin_label(
        metin,
        font_size='14sp', color=RENKLER['beyaz'],
        halign='center', size_hint_y=None, height=dp(88),
    ))
    tamam = siyah_buton(t('coin_welcome_ok'), vurgu=True, font_size='14sp')
    icerik.add_widget(tamam)
    popup = Popup(
        title=t('coin_welcome_title'),
        content=icerik,
        size_hint=(0.88, None),
        height=dp(260),
        separator_color=get_color_from_hex(RENKLER['altin']),
        title_color=get_color_from_hex(RENKLER['altin']),
    )
    tamam.bind(on_press=lambda *_: popup.dismiss())
    popup.open()
    coin_ui_yenile()


def gunluk_giris_popup_goster():
    from dil import t

    icerik = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
    icerik.add_widget(_popup_baslik_coin())
    icerik.add_widget(metin_label(
        t('coin_daily', bonus=GUNLUK_GIRIS_BONUS, toplam=coin_miktar()),
        font_size='14sp', color=RENKLER['beyaz'],
        halign='center', size_hint_y=None, height=dp(72),
    ))
    tamam = siyah_buton(t('coin_welcome_ok'), vurgu=True, font_size='14sp')
    icerik.add_widget(tamam)
    popup = Popup(
        title=t('coin_daily_title'),
        content=icerik,
        size_hint=(0.88, None),
        height=dp(230),
        separator_color=get_color_from_hex(RENKLER['altin']),
        title_color=get_color_from_hex(RENKLER['altin']),
    )
    tamam.bind(on_press=lambda *_: popup.dismiss())
    popup.open()
    coin_ui_yenile()


def coin_baslangic_kontrol():
    """Uygulama açılışında hoşgeldin + günlük giriş bonusu."""
    yeni_hosgeldin, _ = hosgeldin_kontrol()
    yeni_gunluk, _ = gunluk_giris_kontrol()
    if yeni_hosgeldin:
        Clock.schedule_once(lambda *_: hosgeldin_popup_goster(gunluk_de=yeni_gunluk), 0.6)
    elif yeni_gunluk:
        Clock.schedule_once(lambda *_: gunluk_giris_popup_goster(), 0.6)
    else:
        coin_ui_yenile()
