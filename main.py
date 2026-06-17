"""
🔮 FalımaBak - Premium Fal Uygulaması v1.3.0
Mystic Dark Dashboard — mobil odaklı
"""

import os
import shutil
import traceback

os.environ['KIVY_ORIENTATION'] = 'portrait'

from kivy.config import Config

_ANDROID = (
    'ANDROID_ARGUMENT' in os.environ
    or 'ANDROID_ROOT' in os.environ
    or 'ANDROID_BOOTLOGO' in os.environ
)

if _ANDROID:
    try:
        from ai_yorum import ssl_hazirla
        ssl_hazirla()
    except Exception:
        pass

if not _ANDROID:
    Config.set('graphics', 'width', '400')
    Config.set('graphics', 'height', '780')
Config.set('kivy', 'window_icon', '')
if not _ANDROID:
    Config.set('input', 'mouse', 'mouse,disable_multitouch')

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp

from theme import (
    RENKLER, KART_MENU_AR,
    SAFE_UST, SAFE_ALT,
    fontlari_yukle, emoji_font_yukle, emoji_label,
    fal_ikon_widget, guvenli_textinput, klavye_kapat,
    metin_label, gradient_arka_plan_ekle, asset_yolu,
    alt_nav_bar, ekran_icerik_sar, kart_zemin_bagla, baslik_satir,
    yorum_baslik_metin, gorsel_arkaplan_ekle, siyah_buton, kart_ikon_widget,
)
from gecmis import (
    onboarding_gerekli, onboarding_tamamla, kullanici_ismi,
    gunluk_fal, gecmis_listesi, kurabiye_ac, kurabiye_bugun_acildi_mi,
)

_ikon = asset_yolu('app_icon.png')
if os.path.isfile(_ikon):
    try:
        Window.set_icon(_ikon)
    except Exception:
        pass


class DashboardKart(ButtonBehavior, BoxLayout):
    """Menü kartı — ikon ortalı, koyu zemin, altın başlık."""

    def __init__(self, baslik='', aciklama='', ikon_anahtar='tarot', renk='#7c4dff', hedef='', **kwargs):
        from kivy.uix.anchorlayout import AnchorLayout

        super().__init__(orientation='horizontal', **kwargs)
        self.hedef = hedef
        kart_bg = KART_MENU_AR.get(ikon_anahtar, RENKLER['kart_arka'])
        self.size_hint_y = None
        self.height = dp(84)
        self.padding = [dp(12), dp(10), dp(12), dp(10)]
        self.spacing = dp(10)

        bg = get_color_from_hex(kart_bg)
        stripe = get_color_from_hex(renk)
        gold = get_color_from_hex(RENKLER['altin'])

        with self.canvas.before:
            Color(0, 0, 0, 0.32)
            self._golge = RoundedRectangle(radius=[dp(12)])
            Color(bg[0], bg[1], bg[2], 1)
            self._bg = RoundedRectangle(radius=[dp(12)])
            Color(stripe[0], stripe[1], stripe[2], 1)
            self._serit = RoundedRectangle(radius=[dp(2)])

        with self.canvas.after:
            Color(gold[0], gold[1], gold[2], 0.28)
            self._kenar = Line(width=dp(1))

        self.bind(pos=self._kart_ciz, size=self._kart_ciz)
        Clock.schedule_once(lambda *_: self._kart_ciz(), 0)

        ikon_kutu = AnchorLayout(
            size_hint=(None, 1),
            width=dp(50),
            anchor_x='center',
            anchor_y='center',
        )
        ikon_kutu.add_widget(fal_ikon_widget(
            ikon_anahtar, renk,
            size_hint=(None, None),
            size=(dp(44), dp(44)),
        ))
        self.add_widget(ikon_kutu)

        metin_kutu = BoxLayout(
            orientation='vertical',
            size_hint_x=1,
            size_hint_y=1,
            spacing=dp(3),
            padding=[dp(2), dp(4), 0, dp(4)],
        )
        metin_kutu.add_widget(metin_label(
            baslik, font_size='16sp', bold=True, color=RENKLER['altin_parlak'],
            halign='left', valign='middle',
            size_hint_x=1, size_hint_y=None, height=dp(24),
        ))
        metin_kutu.add_widget(metin_label(
            aciklama, font_size='11sp', color=RENKLER['gri_acik'],
            halign='left', valign='top',
            size_hint_x=1, size_hint_y=None, height=dp(36),
        ))
        self.add_widget(metin_kutu)

        ok_kutu = AnchorLayout(
            size_hint=(None, 1),
            width=dp(26),
            anchor_x='center',
            anchor_y='center',
        )
        ok_kutu.add_widget(metin_label(
            '>', font_size='20sp', bold=True, color=RENKLER['altin'],
            halign='center', valign='middle',
            size_hint=(None, None),
            size=(dp(22), dp(28)),
        ))
        self.add_widget(ok_kutu)

    def _kart_ciz(self, *_):
        x, y = self.pos
        w, h = self.size
        if w < 1 or h < 1:
            return
        r = dp(12)
        self._golge.pos = (x + dp(2), y - dp(2))
        self._golge.size = (w - dp(4), h)
        self._bg.pos = (x, y)
        self._bg.size = (w, h)
        self._serit.pos = (x + dp(4), y + dp(8))
        self._serit.size = (dp(4), max(h - dp(16), dp(12)))
        self._kenar.rounded_rectangle = (x, y, w, h, r)

    def on_press(self):
        Animation(opacity=0.85, duration=0.06).start(self)

    def on_release(self):
        Animation(opacity=1, duration=0.1).start(self)
        app = App.get_running_app()
        sm = getattr(app, '_sm', None) if app else None
        if sm and self.hedef:
            sm.current = self.hedef


class GunlukFalKarti(ButtonBehavior, BoxLayout):
    """Günlük fal önerisi kartı."""

    def __init__(self, **kwargs):
        from dil import t
        super().__init__(orientation='horizontal', **kwargs)
        self.size_hint_y = None
        self.height = dp(72)
        self.padding = [dp(14), dp(10), dp(14), dp(10)]
        self.spacing = dp(10)
        self._gunluk = gunluk_fal()

        with self.canvas.before:
            Color(*get_color_from_hex('#1A1238'))
            self._bg = RoundedRectangle(radius=[dp(14)])
            Color(*get_color_from_hex(RENKLER['altin']))
            self._serit = RoundedRectangle(radius=[dp(2)])

        self.bind(pos=self._cizim, size=self._cizim)
        Clock.schedule_once(lambda *_: self._cizim(), 0)

        from kivy.uix.anchorlayout import AnchorLayout
        ikon_kutu = AnchorLayout(
            size_hint=(None, 1), width=dp(48),
            anchor_x='center', anchor_y='center',
        )
        hedef = self._gunluk['hedef']
        ikon_anahtar = 'diger' if hedef == 'diger_fallar' else hedef
        ikon_kutu.add_widget(kart_ikon_widget(
            anahtar=ikon_anahtar, boyut=dp(44),
            renk_hex=RENKLER['altin'],
        ))
        self.add_widget(ikon_kutu)
        kutu = BoxLayout(orientation='vertical', size_hint=(1, 1), spacing=dp(2))
        kutu.add_widget(metin_label(
            f"{t('daily_fal')} — {self._gunluk['tarih']}",
            font_size='12sp', bold=True, color=RENKLER['altin'],
            halign='left', size_hint_y=None, height=dp(18),
        ))
        kutu.add_widget(metin_label(
            self._gunluk['mesaj'][:55] + ('…' if len(self._gunluk['mesaj']) > 55 else ''),
            font_size='11sp', color=RENKLER['gri_acik'],
            halign='left', size_hint_y=None, height=dp(32),
        ))
        self.add_widget(kutu)
        self.add_widget(metin_label(
            f"{t('luck')}: {self._gunluk['sansli_sayi']}",
            font_size='11sp', bold=True, color=RENKLER['yesil_parlak'],
            halign='right', size_hint=(None, 1), width=dp(58),
        ))

    def _cizim(self, *_):
        x, y = self.pos
        w, h = self.size
        self._bg.pos = (x, y)
        self._bg.size = (w, h)
        self._serit.pos = (x + dp(4), y + dp(8))
        self._serit.size = (dp(4), max(h - dp(16), dp(8)))

    def on_release(self):
        app = App.get_running_app()
        sm = getattr(app, '_sm', None) if app else None
        if sm:
            sm.current = self._gunluk['hedef']


class SansKurabiyesiKarti(ButtonBehavior, BoxLayout):
    """Günlük şans kurabiyesi — günde bir kez açılır."""

    def __init__(self, **kwargs):
        from dil import t
        super().__init__(orientation='horizontal', **kwargs)
        self.size_hint_y = None
        self.height = dp(92)
        self.padding = [dp(14), dp(10), dp(14), dp(10)]
        self.spacing = dp(12)

        with self.canvas.before:
            Color(*get_color_from_hex('#1A1238'))
            self._bg = RoundedRectangle(radius=[dp(16)])
            Color(*get_color_from_hex(RENKLER['altin']))
            self._serit = RoundedRectangle(radius=[dp(2)])

        self.bind(pos=self._cizim, size=self._cizim)
        Clock.schedule_once(lambda *_: self._cizim(), 0)

        from kivy.uix.anchorlayout import AnchorLayout
        ikon_kutu = AnchorLayout(
            size_hint=(None, 1), width=dp(64),
            anchor_x='center', anchor_y='center',
        )
        ikon_kutu.add_widget(kart_ikon_widget(
            dosya='icon_kurabiye.png', boyut=dp(52),
        ))
        self.add_widget(ikon_kutu)

        metin = BoxLayout(orientation='vertical', size_hint=(1, 1), spacing=dp(3))
        isim = kullanici_ismi()
        if isim:
            metin.add_widget(metin_label(
                t('hello', name=isim),
                font_size='11sp', bold=True, color=RENKLER['altin_parlak'],
                halign='left', size_hint_y=None, height=dp(16),
            ))
        metin.add_widget(metin_label(
            t('cookie_title'), font_size='15sp', bold=True, color=RENKLER['altin'],
            halign='left', size_hint_y=None, height=dp(22),
        ))
        self._ipucu = metin_label(
            '', font_size='11sp', color=RENKLER['gri_acik'],
            halign='left', size_hint_y=None, height=dp(32),
        )
        metin.add_widget(self._ipucu)
        self.add_widget(metin)
        self.add_widget(metin_label(
            '›', font_size='24sp', bold=True, color=RENKLER['altin'],
            halign='center', size_hint=(None, 1), width=dp(20),
        ))
        self.yenile()

    def _cizim(self, *_):
        x, y = self.pos
        w, h = self.size
        if w < 1 or h < 1:
            return
        self._bg.pos = (x, y)
        self._bg.size = (w, h)
        self._serit.pos = (x + dp(4), y + dp(10))
        self._serit.size = (dp(4), max(h - dp(20), dp(12)))

    def yenile(self):
        from dil import t
        if kurabiye_bugun_acildi_mi():
            self._ipucu.text = t('cookie_hint_opened')
            self._ipucu.color = get_color_from_hex(RENKLER['yesil_parlak'])
        else:
            self._ipucu.text = t('cookie_hint')
            self._ipucu.color = get_color_from_hex(RENKLER['gri_acik'])

    def on_press(self):
        Animation(opacity=0.88, duration=0.06).start(self)

    def on_release(self):
        from dil import t
        from kivy.uix.anchorlayout import AnchorLayout
        from kivy.uix.popup import Popup
        Animation(opacity=1, duration=0.1).start(self)
        sonuc = kurabiye_ac()
        self.yenile()

        icerik = BoxLayout(orientation='vertical', padding=[dp(16), dp(12), dp(16), dp(14)], spacing=dp(8))

        baslik_kutu = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(6))
        ikon_satir = AnchorLayout(size_hint_y=None, height=dp(56), anchor_x='center', anchor_y='center')
        ikon_satir.add_widget(kart_ikon_widget(dosya='icon_kurabiye.png', boyut=dp(52)))
        baslik_kutu.add_widget(ikon_satir)
        baslik_kutu.add_widget(metin_label(
            t('cookie_title'),
            font_size='17sp', bold=True, color=RENKLER['altin_parlak'],
            halign='center', valign='middle',
            size_hint_y=None, height=dp(26),
        ))
        baslik_kutu.bind(minimum_height=baslik_kutu.setter('height'))
        icerik.add_widget(baslik_kutu)

        icerik.add_widget(metin_label(
            sonuc['mesaj'], font_size='14sp', color=RENKLER['beyaz'],
            halign='center', valign='middle',
            size_hint_y=None, height=dp(88),
        ))
        if not sonuc['yeni']:
            icerik.add_widget(metin_label(
                t('cookie_already'), font_size='11sp', color=RENKLER['gri_acik'],
                halign='center', size_hint_y=None, height=dp(40),
            ))
        kapat = siyah_buton(t('cookie_close'), vurgu=True, font_size='14sp')
        icerik.add_widget(kapat)

        popup = Popup(
            title='',
            content=icerik,
            size_hint=(0.88, None),
            height=dp(320),
            separator_color=get_color_from_hex(RENKLER['altin']),
            title_color=get_color_from_hex(RENKLER['altin']),
            title_size=0,
        )
        kapat.bind(on_press=lambda *_: popup.dismiss())
        popup.open()


class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._kur()

    def _kur(self):
        from dil import t
        gradient_arka_plan_ekle(self)
        root = FloatLayout()
        banner_yol = asset_yolu('splash_banner.png')
        self._banner_var = os.path.isfile(banner_yol)
        self._root = root

        if self._banner_var:
            self._splash_img = Image(
                source=banner_yol, allow_stretch=True, keep_ratio=True, size_hint=(None, None),
            )
            root.add_widget(self._splash_img)
            root.bind(size=self._splash_kapak, pos=self._splash_kapak)
            self._splash_img.bind(texture=self._splash_kapak)
            self.logo = BoxLayout(size_hint=(0, 0))
        else:
            ikon_yol = asset_yolu('app_icon.png')
            logo_boyut = dp(96)
            if os.path.isfile(ikon_yol):
                self.logo = Image(
                    source=ikon_yol,
                    pos_hint={'center_x': 0.5, 'center_y': 0.58},
                    size_hint=(None, None),
                    size=(logo_boyut, logo_boyut),
                    allow_stretch=True,
                    keep_ratio=True,
                )
            else:
                self.logo = emoji_label('🔮', font_size='72sp',
                    pos_hint={'center_x': 0.5, 'center_y': 0.58}, size_hint=(None, None),
                    size=(logo_boyut, logo_boyut))
            root.add_widget(self.logo)
            root.add_widget(metin_label(
                'FalımaBak', font_size='36sp', bold=True, color=RENKLER['altin'],
                halign='center', pos_hint={'center_x': 0.5, 'center_y': 0.46},
                size_hint=(0.9, None), height=dp(44),
            ))
            root.add_widget(metin_label(
                yorum_baslik_metin(), font_size='13sp', color=RENKLER['gri_acik'],
                halign='center', pos_hint={'center_x': 0.5, 'center_y': 0.40},
                size_hint=(0.9, None), height=dp(24),
            ))

        self._yukleme_kutu = FloatLayout(
            size_hint=(1, None),
            height=dp(64) + SAFE_ALT,
            pos_hint={'x': 0, 'y': 0},
        )
        with self._yukleme_kutu.canvas.before:
            Color(0.06, 0.04, 0.14, 0.82)
            self._yukleme_bg = Rectangle()
        self._yukleme_kutu.bind(pos=self._yukleme_ciz, size=self._yukleme_ciz)

        self.yukleniyor = metin_label(
            t('loading'), font_size='16sp', bold=True, color=RENKLER['altin'],
            halign='center', valign='middle',
            pos_hint={'center_x': 0.5, 'center_y': 0.55},
            size_hint=(1, None), height=dp(32),
        )
        self._yukleme_kutu.add_widget(self.yukleniyor)
        self._yukleme_kutu.add_widget(metin_label(
            t('loading_hint'), font_size='11sp', color=RENKLER['gri_acik'],
            halign='center', pos_hint={'center_x': 0.5, 'y': 0.12},
            size_hint=(1, None), height=dp(20),
        ))
        root.add_widget(self._yukleme_kutu)
        self.add_widget(root)
        Clock.schedule_once(lambda *_: self._splash_kapak(), 0)
        Clock.schedule_once(lambda *_: self._yukleme_ciz(), 0)

        if not _ANDROID and not self._banner_var:
            boyut = dp(96)
            anim_logo = (
                Animation(size=(boyut * 1.08, boyut * 1.08), opacity=0.88, duration=1.0, t='in_out_sine')
                + Animation(size=(boyut, boyut), opacity=1.0, duration=1.0, t='in_out_sine')
            )
            anim_logo.repeat = True
            self._anim_logo = anim_logo
            anim_logo.start(self.logo)
        else:
            self._anim_logo = None

        anim_txt = Animation(opacity=0.35, duration=0.6) + Animation(opacity=1, duration=0.6)
        anim_txt.repeat = True
        self._anim_txt = anim_txt
        anim_txt.start(self.yukleniyor)

        self._nokta = 0
        self._nokta_ev = Clock.schedule_interval(self._yukleme_nokta, 0.4)

        Clock.schedule_once(self._gec, 2.2)

    def _yukleme_ciz(self, *_):
        if not getattr(self, '_yukleme_kutu', None):
            return
        x, y = self._yukleme_kutu.pos
        w, h = self._yukleme_kutu.size
        self._yukleme_bg.pos = (x, y)
        self._yukleme_bg.size = (w, h)

    def _yukleme_nokta(self, _dt):
        from dil import t
        if not getattr(self, 'yukleniyor', None):
            return
        self._nokta = (self._nokta + 1) % 4
        taban = t('loading').rstrip('.')
        self.yukleniyor.text = taban + ('.' * self._nokta if self._nokta else '...')

    def _splash_kapak(self, *_):
        if not getattr(self, '_banner_var', False):
            return
        img = getattr(self, '_splash_img', None)
        root = getattr(self, '_root', None)
        if not img or not root or root.width < 1 or root.height < 1:
            return
        tex = img.texture
        if not tex:
            return
        pw, ph = root.width, root.height
        tw, th = tex.size
        olcek = max(pw / tw, ph / th)
        iw, ih = tw * olcek, th * olcek
        img.size = (iw, ih)
        img.pos = (root.x + (pw - iw) * 0.5, root.y + (ph - ih) * 0.5)

    def _gec(self, *_):
        if getattr(self, '_nokta_ev', None):
            self._nokta_ev.cancel()
            self._nokta_ev = None
        if getattr(self, '_anim_logo', None):
            self._anim_logo.cancel(self.logo)
        if getattr(self, '_anim_txt', None):
            self._anim_txt.cancel(self.yukleniyor)
        if not self.manager:
            return
        if 'hata' in self.manager.screen_names:
            self.manager.current = 'hata'
            return
        hedef = 'onboarding' if onboarding_gerekli() else 'anasayfa'
        if hedef not in self.manager.screen_names:
            Clock.schedule_once(self._gec, 0.25)
            return
        self.manager.current = hedef


class OnboardingScreen(Screen):
    SLAYTLAR = [
        ('🔮', 'FalımaBak\'a Hoş Geldin', 'Tarot, kahve, astroloji ve daha fazlası tek uygulamada.'),
        ('📸', 'Fotoğraf Çek, Yorum Al', 'Kahve ve el falında kendi fotoğrafını kullan.'),
        ('✦', 'FalımaBak Yorumluyor', 'Her fal sana özel, mistik ve anlamlı yorumlar sunar.'),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._adim = 0
        self._kur()

    def _kur(self):
        self._ana = BoxLayout(orientation='vertical', padding=[dp(20), SAFE_UST + dp(20), dp(20), SAFE_ALT])
        ekran_icerik_sar(self, self._ana)
        self._goster()

    def _goster(self):
        self._ana.clear_widgets()
        ikon, baslik, aciklama = self.SLAYTLAR[self._adim]

        self._ana.add_widget(emoji_label(ikon, font_size='64sp', halign='center',
            size_hint_y=None, height=dp(90)))
        self._ana.add_widget(metin_label(baslik, font_size='24sp', bold=True, color=RENKLER['altin'],
            halign='center', size_hint_y=None, height=dp(36)))
        self._ana.add_widget(metin_label(aciklama, font_size='14sp', color=RENKLER['gri_acik'],
            halign='center', size_hint_y=None, height=dp(60)))

        if self._adim == len(self.SLAYTLAR) - 1:
            isim_kutu = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(52),
                padding=[0, dp(4), 0, 0],
            )
            self._isim = guvenli_textinput(
                hint_text='Adınız (isteğe bağlı)',
                size_hint_y=None,
                height=dp(44),
            )
            isim_kutu.add_widget(self._isim)
            self._ana.add_widget(isim_kutu)

        self._ana.add_widget(BoxLayout(size_hint_y=1))

        noktalar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(20), spacing=dp(8))
        for i in range(len(self.SLAYTLAR)):
            renk = RENKLER['altin'] if i == self._adim else RENKLER['gri_koyu']
            noktalar.add_widget(metin_label('●', font_size='12sp', color=renk, halign='center'))
        self._ana.add_widget(noktalar)

        from theme import siyah_buton, TUS
        son = self._adim == len(self.SLAYTLAR) - 1
        from theme import tus_buton
        btn = tus_buton('tamam', vurgu=True, font_size='15sp') if son else siyah_buton('İleri →', vurgu=True, font_size='15sp')
        btn.bind(on_press=self._ileri)
        self._ana.add_widget(btn)

    def _ileri(self, *_):
        if self._adim < len(self.SLAYTLAR) - 1:
            klavye_kapat()
            self._adim += 1
            self._goster()
            return
        isim_metni = ''
        isim_w = getattr(self, '_isim', None)
        if isim_w:
            try:
                isim_metni = (isim_w.text or '').strip()
                isim_w.focus = False
            except Exception:
                pass
        klavye_kapat()
        try:
            onboarding_tamamla(isim_metni)
        except Exception as e:
            print(f'Onboarding kayit: {e}', flush=True)
        sm = self.manager
        if sm and 'anasayfa' in sm.screen_names:
            Clock.schedule_once(lambda *_: setattr(sm, 'current', 'anasayfa'), 0.2)


class GecmisScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._kur()

    def _kur(self):
        from dil import t
        ana = BoxLayout(orientation='vertical', padding=[dp(12), SAFE_UST, dp(12), 0], spacing=dp(8))

        ana.add_widget(baslik_satir('📜', t('history_title'), font_size='22sp', height=dp(36)))

        kaydir = ScrollView(size_hint_y=1, do_scroll_x=False, bar_width=dp(3),
            bar_color=get_color_from_hex(RENKLER['mor_parlak']),
            bar_inactive_color=get_color_from_hex(RENKLER['kart_kenar']))
        self._liste = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None, padding=[0, dp(4)])
        self._liste.bind(minimum_height=self._liste.setter('height'))
        kaydir.add_widget(self._liste)
        ana.add_widget(kaydir)

        try:
            from reklam import reklam_alani_bosluk
            ana.add_widget(reklam_alani_bosluk())
        except Exception:
            pass
        ana.add_widget(alt_nav_bar('gecmis', on_sec=self._nav))
        ekran_icerik_sar(self, ana)
        self._yenile()

    def on_enter(self, *_):
        self._yenile()

    def _yenile(self):
        from dil import t
        if not hasattr(self, '_liste'):
            return
        self._liste.clear_widgets()
        try:
            kayitlar = gecmis_listesi()
        except Exception:
            kayitlar = []
        if not kayitlar:
            self._liste.add_widget(metin_label(
                t('history_empty'),
                font_size='13sp', color=RENKLER['gri'], halign='center',
                size_hint_y=None, height=dp(80),
            ))
            return
        for kayit in kayitlar:
            kart = BoxLayout(
                orientation='vertical', size_hint_y=None, height=dp(100),
                padding=[dp(12), dp(8), dp(12), dp(8)], spacing=dp(4),
            )
            kart_zemin_bagla(kart)

            baslik = kayit.get('baslik', 'Fal')
            tarih = kayit.get('tarih', '')
            yorum = kayit.get('yorum', '')
            kart.add_widget(metin_label(
                f'{baslik}  ·  {tarih}',
                font_size='12sp', bold=True, color=RENKLER['altin'],
                halign='left', size_hint_y=None, height=dp(20),
            ))
            ozet = yorum[:120] + ('…' if len(yorum) > 120 else '')
            kart.add_widget(metin_label(
                ozet,
                font_size='11sp', color=RENKLER['gri_acik'],
                halign='left', size_hint_y=None, height=dp(60),
            ))
            self._liste.add_widget(kart)

    def _nav(self, hedef):
        if not self.manager:
            return
        if hedef == 'anasayfa':
            self.manager.current = 'anasayfa'
        elif hedef == 'ayarlar':
            self.manager.current = 'ayarlar'


class Anasayfa(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._kur()

    def _kur(self):
        from dil import t
        ana = BoxLayout(orientation='vertical', padding=[dp(12), SAFE_UST, dp(12), 0], spacing=dp(8))
        self._kurabiye = SansKurabiyesiKarti()
        ana.add_widget(self._kurabiye)
        ana.add_widget(GunlukFalKarti())
        ana.add_widget(metin_label(
            t('menu_fortunes'),
            font_size='13sp', bold=True, color=RENKLER['altin_parlak'],
            halign='center', size_hint_y=None, height=dp(22),
        ))

        menu_wrap = BoxLayout(orientation='vertical', size_hint_y=1)
        gorsel_arkaplan_ekle(menu_wrap, 'menu_bg.png', opak=0.88)
        menu_kaydir = ScrollView(size_hint_y=1, do_scroll_x=False, bar_width=dp(3))
        menu = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, padding=[dp(6), dp(8), dp(6), dp(8)])
        menu.bind(minimum_height=menu.setter('height'))
        for baslik, aciklama, ikon, renk, hedef in [
            (t('menu_tarot'), t('menu_tarot_desc'), 'tarot', RENKLER['mor'], 'tarot'),
            (t('menu_kahve'), t('menu_kahve_desc'), 'kahve', RENKLER['turuncu'], 'kahve'),
            (t('menu_astro'), t('menu_astro_desc'), 'astroloji', RENKLER['mavi_acik'], 'astroloji'),
            (t('menu_el'), t('menu_el_desc'), 'elfali', RENKLER['pembe'], 'elfali'),
            (t('menu_burc_esles'), t('menu_burc_esles_desc'), 'burc_eslesme', RENKLER['pembe_acik'], 'burc_eslesme'),
            (t('menu_ruya'), t('menu_ruya_desc'), 'ruya', RENKLER['mor'], 'ruya'),
            (t('menu_diger'), t('menu_diger_desc'), 'diger', RENKLER['yesil'], 'diger_fallar'),
        ]:
            menu.add_widget(DashboardKart(baslik=baslik, aciklama=aciklama,
                ikon_anahtar=ikon, renk=renk, hedef=hedef))
        menu_kaydir.add_widget(menu)
        menu_wrap.add_widget(menu_kaydir)
        ana.add_widget(menu_wrap)

        try:
            from reklam import reklam_alani_bosluk
            ana.add_widget(reklam_alani_bosluk())
        except Exception:
            pass
        ana.add_widget(alt_nav_bar('anasayfa', on_sec=self._nav))
        ekran_icerik_sar(self, ana)

    def on_enter(self, *_):
        if hasattr(self, '_kurabiye'):
            self._kurabiye.yenile()
        try:
            from coin_ui import coin_baslangic_kontrol, coin_ui_yenile
            coin_baslangic_kontrol()
            coin_ui_yenile()
        except Exception:
            pass
        try:
            from reklam import reklam_hazirla, ekran_reklam_guncelle
            reklam_hazirla()
            ekran_reklam_guncelle('anasayfa')
        except Exception:
            pass
        try:
            from muzik import muzik_uygula
            muzik_uygula()
        except Exception:
            pass

    def _nav(self, hedef):
        if not self.manager:
            return
        if hedef == 'gecmis':
            self.manager.current = 'gecmis'
        elif hedef == 'ayarlar':
            self.manager.current = 'ayarlar'


class HataScreen(Screen):
    """Başlangıç hatasını ekranda göster (logcat olmadan teşhis)."""

    def __init__(self, mesaj='', **kwargs):
        super().__init__(**kwargs)
        gradient_arka_plan_ekle(self)
        kutu = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        kutu.add_widget(metin_label(
            'Başlangıç hatası', font_size='20sp', bold=True, color=RENKLER['altin'],
            halign='center', size_hint_y=None, height=dp(36),
        ))
        kutu.add_widget(metin_label(
            mesaj[:1200],
            font_size='11sp', color=RENKLER['gri_acik'],
            halign='left', size_hint_y=1,
        ))
        self.add_widget(kutu)


class FalimaBakApp(App):
    _GERI_ALT = frozenset({
        'tarot', 'kahve', 'astroloji', 'elfali', 'diger_fallar',
        'burc_eslesme', 'ruya', 'gizlilik',
    })
    _GERI_SEKME = frozenset({'gecmis', 'ayarlar'})

    @staticmethod
    def _acik_modal_kapat():
        """Kivy 2.3+ Popup._popups yok — açık ModalView/Popup kapat."""
        from kivy.uix.modalview import ModalView
        for child in list(Window.children):
            if isinstance(child, ModalView) and getattr(child, '_is_open', False):
                child.dismiss()
                return True
        return False

    def on_start(self):
        Window.bind(on_keyboard=self._geri_tusu)
        if _ANDROID:
            try:
                from android_geri import geri_tusu_kur
                geri_tusu_kur(self)
                Clock.schedule_once(lambda *_: geri_tusu_kur(self), 1.0)
                Clock.schedule_once(lambda *_: geri_tusu_kur(self), 3.0)
            except Exception as e:
                print(f'Geri kurulum: {e}', flush=True)
        if not _ANDROID:
            return
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            hedef = os.path.join(self.user_data_dir, 'config.json')
            ornek = os.path.join(os.path.dirname(__file__), 'config.ornek.json')
            if not os.path.isfile(hedef) and os.path.isfile(ornek):
                shutil.copy2(ornek, hedef)
        except Exception as e:
            print(f'Config kopyalama: {e}', flush=True)
        try:
            from ai_yorum import mobil_ai_hazirla
            Clock.schedule_once(lambda *_: mobil_ai_hazirla(), 0.5)
        except Exception as e:
            print(f'AI mobil hazırlık: {e}', flush=True)
        try:
            from kamera import kamera_hazirla
            Clock.schedule_once(lambda *_: kamera_hazirla(), 0.8)
        except Exception:
            pass
        try:
            from reklam import reklam_hazirla
            Clock.schedule_once(lambda *_: reklam_hazirla(), 1.2)
        except Exception:
            pass
        try:
            from muzik import muzik_hazirla, muzik_uygula
            muzik_hazirla()
            Clock.schedule_once(lambda *_: muzik_uygula(), 1.5)
        except Exception:
            pass
        try:
            from bildirim import bildirim_baslat
            Clock.schedule_once(lambda *_: bildirim_baslat(), 2.0)
        except Exception as e:
            print(f'Bildirim baslat: {e}', flush=True)

    def on_pause(self):
        try:
            from bildirim import bildirim_baslat
            bildirim_baslat()
        except Exception:
            pass
        return False

    def on_resume(self):
        if _ANDROID:
            try:
                from android_geri import geri_tusu_kur
                geri_tusu_kur(self)
            except Exception:
                pass

    def _geri_tusu(self, _window, key, *args):
        # Android: key 4 = BACK. Masaüstü SDL: scancode 4 = A tuşu — karışmasın!
        if _ANDROID:
            if key not in (4, 27):
                return False
        elif key != 27:
            return False
        return self._geri_isle()

    def _geri_isle(self):
        """Geri navigasyon veya çıkış onayı."""
        if self._acik_modal_kapat():
            return True
        sm = self._sm
        if not sm:
            return False
        cur = sm.current
        if cur in self._GERI_ALT:
            sm.current = 'anasayfa'
            return True
        if cur == 'onboarding':
            ob = sm.get_screen('onboarding')
            if getattr(ob, '_adim', 0) > 0:
                ob._adim -= 1
                ob._goster()
            else:
                self._cikis_onay()
            return True
        if cur in self._GERI_SEKME:
            sm.current = 'anasayfa'
            return True
        if cur == 'anasayfa':
            self._cikis_onay()
            return True
        if cur in ('splash', 'hata'):
            return False
        return False

    def _cikis_onay(self):
        from dil import t
        from kivy.uix.popup import Popup

        if getattr(self, '_cikis_popup', None):
            return
        icerik = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        icerik.add_widget(metin_label(
            t('exit_msg'), font_size='14sp', color=RENKLER['beyaz'],
            halign='center', size_hint_y=None, height=dp(48),
        ))
        btn_satir = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        iptal = siyah_buton(t('exit_no'), font_size='14sp')
        cik = siyah_buton(t('exit_yes'), vurgu=True, font_size='14sp')
        btn_satir.add_widget(iptal)
        btn_satir.add_widget(cik)
        icerik.add_widget(btn_satir)

        popup = Popup(
            title=t('exit_title'),
            content=icerik,
            size_hint=(0.85, None),
            height=dp(180),
            separator_color=get_color_from_hex(RENKLER['altin']),
            title_color=get_color_from_hex(RENKLER['altin']),
            auto_dismiss=False,
        )
        self._cikis_popup = popup

        def _kapat(*_):
            self._cikis_popup = None
            popup.dismiss()

        iptal.bind(on_press=_kapat)
        cik.bind(on_press=lambda *_: ( _kapat(), self.stop()))
        popup.bind(on_dismiss=lambda *_: setattr(self, '_cikis_popup', None))
        popup.open()

    def ekranlari_yenile_dil(self):
        from ayarlar import AyarlarScreen
        from gizlilik import GizlilikScreen
        sm = self._sm
        if not sm:
            return
        cur = sm.current
        for name, fab in [
            ('anasayfa', lambda: Anasayfa(name='anasayfa')),
            ('gecmis', lambda: GecmisScreen(name='gecmis')),
            ('ayarlar', lambda: AyarlarScreen(name='ayarlar')),
            ('gizlilik', lambda: GizlilikScreen(name='gizlilik')),
        ]:
            if name in sm.screen_names:
                sm.remove_widget(sm.get_screen(name))
            sm.add_widget(fab())
        if cur in sm.screen_names:
            sm.current = cur

    def build(self):
        try:
            from koruma import koruma_baslat
            koruma_baslat()
        except Exception:
            pass
        fontlari_yukle()
        emoji_font_yukle()
        if _ANDROID:
            try:
                from kamera import kamera_hazirla
                kamera_hazirla()
            except Exception:
                pass
        self.title = 'FalımaBak'
        Window.clearcolor = get_color_from_hex(RENKLER['arka_plan'])
        if _ANDROID:
            try:
                Window.softinput_mode = 'resize'
            except Exception:
                pass
        sm = ScreenManager(transition=FadeTransition(duration=0.25))
        with sm.canvas.before:
            Color(*get_color_from_hex(RENKLER['arka_plan']))
            sm._tam_zemin = RoundedRectangle(radius=[0])

        def _sm_zemin(*_):
            sm._tam_zemin.pos = sm.pos
            sm._tam_zemin.size = sm.size

        sm.bind(pos=_sm_zemin, size=_sm_zemin)
        Clock.schedule_once(lambda *_: _sm_zemin(), 0)
        sm.add_widget(SplashScreen(name='splash'))
        self._sm = sm
        Clock.schedule_once(lambda *_: self._ekranlari_yukle(), 0.05)

        from coin_ui import CoinChip
        from theme import COIN_SAG_KENAR, COIN_UST_KENAR

        kok = FloatLayout()
        kok.add_widget(sm)
        self._coin_chip = CoinChip()
        self._coin_chip.size_hint = (None, None)
        kok.add_widget(self._coin_chip)

        def _coin_konum(*_):
            ch = self._coin_chip
            # Tam sağ üst köşe — SAFE_UST kullanma (buton satırına kayıyordu)
            ch.pos = (
                max(0, kok.width - ch.width - COIN_SAG_KENAR),
                max(0, kok.height - ch.height - COIN_UST_KENAR),
            )

        kok.bind(size=_coin_konum, pos=_coin_konum)

        def _coin_gorunurluk(*_):
            gizle = sm.current in ('splash', 'onboarding', 'hata')
            self._coin_chip.opacity = 0 if gizle else 1
            self._coin_chip.disabled = gizle

        sm.bind(current=_coin_gorunurluk)
        Clock.schedule_once(lambda *_: (_coin_konum(), _coin_gorunurluk()), 0)
        return kok

    def _ekranlari_yukle(self):
        sm = self._sm
        try:
            from tarot import TarotScreen
            from kahve import KahveScreen
            from astroloji import AstrolojiScreen
            from diger_fallar import DigerFallarScreen
            from elfali import ElFaliScreen
            from burc_eslesme import BurcEslesmeScreen
            from ruya import RuyaScreen
            from ayarlar import AyarlarScreen
            from gizlilik import GizlilikScreen

            ekranlar = [
                ('onboarding', lambda: OnboardingScreen(name='onboarding')),
                ('anasayfa', lambda: Anasayfa(name='anasayfa')),
                ('gecmis', lambda: GecmisScreen(name='gecmis')),
                ('ayarlar', lambda: AyarlarScreen(name='ayarlar')),
                ('gizlilik', lambda: GizlilikScreen(name='gizlilik')),
                ('tarot', lambda: TarotScreen(name='tarot')),
                ('kahve', lambda: KahveScreen(name='kahve')),
                ('astroloji', lambda: AstrolojiScreen(name='astroloji')),
                ('diger_fallar', lambda: DigerFallarScreen(name='diger_fallar')),
                ('elfali', lambda: ElFaliScreen(name='elfali')),
                ('burc_eslesme', lambda: BurcEslesmeScreen(name='burc_eslesme')),
                ('ruya', lambda: RuyaScreen(name='ruya')),
            ]
            for _, fab in ekranlar:
                sm.add_widget(fab())
            try:
                from reklam import ekran_reklam_guncelle
                sm.bind(current=lambda _, ekran: ekran_reklam_guncelle(ekran))
            except Exception:
                pass
        except Exception:
            err = traceback.format_exc()
            print(err, flush=True)
            if 'hata' not in sm.screen_names:
                sm.add_widget(HataScreen(mesaj=err, name='hata'))
            sm.current = 'hata'


if __name__ == '__main__':
    FalimaBakApp().run()
