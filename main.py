"""
🔮 FalımaBak - Premium Fal Uygulaması v1.0.15
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
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse, Rectangle
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp

from theme import (
    RENKLER, KART_MENU_AR, YORUM_BASLIK,
    SAFE_UST, SAFE_ALT,
    fontlari_yukle, emoji_font_yukle, emoji_label,
    fal_ikon_widget, guvenli_textinput,
    metin_label, gradient_arka_plan_ekle, asset_yolu,
    alt_nav_bar, ekran_icerik_sar, kart_zemin_bagla, baslik_satir,
)
from gecmis import (
    onboarding_gerekli, onboarding_tamamla, kullanici_ismi,
    gunluk_fal, gecmis_listesi,
)

_ikon = asset_yolu('app_icon.png')
if os.path.isfile(_ikon):
    try:
        Window.set_icon(_ikon)
    except Exception:
        pass


class DashboardKart(ButtonBehavior, BoxLayout):
    """Tıklanabilir premium fal kartı."""

    def __init__(self, baslik='', aciklama='', ikon_anahtar='tarot', renk='#7c4dff', hedef='', **kwargs):
        super().__init__(orientation='horizontal', **kwargs)
        self.hedef = hedef
        self.renk = renk
        self.kart_bg = KART_MENU_AR.get(ikon_anahtar, RENKLER['kart_arka'])
        self.size_hint_y = None
        self.height = dp(86)
        self.padding = [dp(14), dp(10), dp(14), dp(10)]
        self.spacing = dp(12)

        with self.canvas.before:
            Color(0, 0, 0, 0.45)
            self._golge = RoundedRectangle(radius=[dp(16)])
            Color(*get_color_from_hex('#06040E'))
            self._golge2 = RoundedRectangle(radius=[dp(16)])
            Color(*get_color_from_hex(self.kart_bg))
            self._bg = RoundedRectangle(radius=[dp(16)])
            Color(*get_color_from_hex(renk), 0.18)
            self._parilti = RoundedRectangle(radius=[dp(16)])
            Color(*get_color_from_hex(renk))
            self._serit = RoundedRectangle(radius=[dp(2)])

        with self.canvas.after:
            Color(*get_color_from_hex(RENKLER['altin']), 0.22)
            self._kenar = Line(width=dp(1.2))

        self.bind(pos=self._kart_ciz, size=self._kart_ciz)
        Clock.schedule_once(lambda *_: self._kart_ciz(), 0)

        ikon_sarmal = BoxLayout(size_hint=(None, 1), width=dp(46))
        with ikon_sarmal.canvas.before:
            ikon_sarmal._daire_koyu = Color(*get_color_from_hex(RENKLER['kart_arka_cam']))
            ikon_sarmal._daire_ic = Ellipse()
            ikon_sarmal._daire_renk = Color(*get_color_from_hex(renk))
            ikon_sarmal._daire_dis = Ellipse()
        ikon_sarmal.bind(
            pos=lambda *a, k=ikon_sarmal: self._ikon_daire_guncelle(k),
            size=lambda *a, k=ikon_sarmal: self._ikon_daire_guncelle(k),
        )
        Clock.schedule_once(lambda *_: self._ikon_daire_guncelle(ikon_sarmal), 0)
        ikon_sarmal.add_widget(fal_ikon_widget(ikon_anahtar, renk, font_size='26sp', size_hint=(1, 1)))
        self.add_widget(ikon_sarmal)

        metin_kutu = BoxLayout(orientation='vertical', size_hint=(1, 1), spacing=dp(2))
        metin_kutu.add_widget(metin_label(
            baslik, font_size='18sp', bold=True, color=RENKLER['beyaz'],
            halign='left', valign='middle', size_hint=(1, 0.55),
        ))
        metin_kutu.add_widget(metin_label(
            aciklama, font_size='11sp', color=RENKLER['altin_yumusak'],
            halign='left', valign='top', size_hint=(1, 0.45),
        ))
        self.add_widget(metin_kutu)
        ok = BoxLayout(size_hint=(None, 1), width=dp(28))
        with ok.canvas.before:
            Color(*get_color_from_hex(RENKLER['altin']), 0.12)
            ok._halka = Ellipse()
        ok.bind(pos=lambda *a, k=ok: self._ok_guncelle(k), size=lambda *a, k=ok: self._ok_guncelle(k))
        Clock.schedule_once(lambda *_: self._ok_guncelle(ok), 0)
        ok.add_widget(metin_label(
            '›', font_size='26sp', bold=True, color=RENKLER['altin'],
            halign='center', valign='middle',
        ))
        self.add_widget(ok)

    def _kart_ciz(self, *_):
        x, y = self.pos
        w, h = self.size
        r = dp(16)
        self._golge.pos = (x + dp(3), y - dp(4))
        self._golge.size = (w - dp(6), h)
        self._golge2.pos = (x + dp(1), y - dp(2))
        self._golge2.size = (w - dp(2), h)
        self._bg.pos = (x, y)
        self._bg.size = (w, h)
        self._parilti.pos = (x, y + h * 0.55)
        self._parilti.size = (w, h * 0.45)
        self._serit.pos = (x + dp(5), y + dp(10))
        self._serit.size = (dp(5), max(h - dp(20), dp(10)))
        self._kenar.rounded_rectangle = (x, y, w, h, r)

    def _ok_guncelle(self, kutu, *_):
        cx, cy = kutu.center_x, kutu.center_y
        r = min(kutu.width, kutu.height) * 0.42
        kutu._halka.pos = (cx - r, cy - r)
        kutu._halka.size = (r * 2, r * 2)

    def _ikon_daire_guncelle(self, kutu, *_):
        cx, cy = kutu.center_x, kutu.center_y
        r = min(kutu.width, kutu.height) * 0.44
        kutu._daire_ic.pos = (cx - r + dp(2), cy - r + dp(2))
        kutu._daire_ic.size = ((r - dp(2)) * 2, (r - dp(2)) * 2)
        kutu._daire_dis.pos = (cx - r, cy - r)
        kutu._daire_dis.size = (r * 2, r * 2)

    def on_press(self):
        Animation(opacity=0.82, duration=0.06).start(self)

    def on_release(self):
        Animation(opacity=1, duration=0.1).start(self)
        app = App.get_running_app()
        if app and app.root and self.hedef:
            app.root.current = self.hedef


class GunlukFalKarti(ButtonBehavior, BoxLayout):
    """Günlük fal önerisi kartı."""

    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)
        self.size_hint_y = None
        self.height = dp(72)
        self.padding = [dp(14), dp(10), dp(14), dp(10)]
        self.spacing = dp(10)
        self._gunluk = gunluk_fal()

        with self.canvas.before:
            Color(0, 0, 0, 0.4)
            self._golge = RoundedRectangle(radius=[dp(16)])
            Color(*get_color_from_hex('#1A1238'))
            self._bg = RoundedRectangle(radius=[dp(16)])
            Color(*get_color_from_hex('#2A1F52'))
            self._cizgi_sol = RoundedRectangle(radius=[dp(2)])
            Color(*get_color_from_hex(RENKLER['altin']), 0.15)
            self._parilti = RoundedRectangle(radius=[dp(16)])
            Color(*get_color_from_hex(RENKLER['altin']))
            self._ciz = RoundedRectangle(radius=[dp(1)])

        with self.canvas.after:
            Color(*get_color_from_hex(RENKLER['altin']), 0.28)
            self._kenar = Line(width=dp(1))

        self.bind(pos=self._cizim, size=self._cizim)
        Clock.schedule_once(lambda *_: self._cizim(), 0)

        self.add_widget(emoji_label(self._gunluk['ikon'], font_size='28sp', size_hint=(None, 1), width=dp(40)))
        kutu = BoxLayout(orientation='vertical', size_hint=(1, 1), spacing=dp(2))
        kutu.add_widget(metin_label(
            f"Günlük Fal — {self._gunluk['tarih']}",
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
            f"Şans: {self._gunluk['sansli_sayi']}",
            font_size='11sp', bold=True, color=RENKLER['yesil_parlak'],
            halign='right', size_hint=(None, 1), width=dp(58),
        ))

    def _cizim(self, *_):
        x, y = self.pos
        w, h = self.size
        r = dp(16)
        self._golge.pos = (x + dp(2), y - dp(3))
        self._golge.size = (w - dp(4), h)
        self._bg.pos = (x, y)
        self._bg.size = (w, h)
        self._parilti.pos = (x, y + h * 0.5)
        self._parilti.size = (w, h * 0.5)
        self._cizgi_sol.pos = (x + dp(5), y + dp(10))
        self._cizgi_sol.size = (dp(5), max(h - dp(20), dp(10)))
        self._ciz.pos = (x + dp(12), y + h - dp(3))
        self._ciz.size = (w - dp(24), dp(2))
        self._kenar.rounded_rectangle = (x, y, w, h, r)

    def on_release(self):
        app = App.get_running_app()
        if app and app.root:
            app.root.current = self._gunluk['hedef']


class BaslikKarti(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, spacing=dp(6), **kwargs)
        banner_yol = asset_yolu('menu_banner.png')
        isim = kullanici_ismi()

        if os.path.isfile(banner_yol):
            self.height = dp(118)
            sarmal = BoxLayout(size_hint_y=None, height=dp(110))
            with sarmal.canvas.before:
                Color(0, 0, 0, 0.35)
                sarmal._g = RoundedRectangle(radius=[dp(18)])
            sarmal.bind(
                pos=lambda *a, s=sarmal: self._banner_golge(s),
                size=lambda *a, s=sarmal: self._banner_golge(s),
            )
            Clock.schedule_once(lambda *_: self._banner_golge(sarmal), 0)
            sarmal.add_widget(Image(
                source=banner_yol,
                size_hint=(1, 1),
                allow_stretch=True,
                keep_ratio=False,
            ))
            self.add_widget(sarmal)
            if isim:
                self.height = dp(138)
                self.add_widget(metin_label(
                    f'✦ Merhaba, {isim}!',
                    font_size='12sp', bold=True, color=RENKLER['altin_parlak'],
                    halign='left', size_hint_y=None, height=dp(18),
                ))
            return

    def _banner_golge(self, w, *_):
        w._g.pos = (w.x + dp(2), w.y - dp(2))
        w._g.size = w.size

        self.height = dp(140)
        self.padding = [dp(14), dp(12), dp(14), dp(10)]
        self.spacing = dp(4)
        with self.canvas.before:
            Color(*get_color_from_hex(RENKLER['kart_arka']))
            self._panel = RoundedRectangle(radius=[dp(16)])
            Color(*get_color_from_hex(RENKLER['altin']))
            self._cizgi = RoundedRectangle(radius=[dp(2)])
        self.bind(pos=self._baslik_ciz, size=self._baslik_ciz)
        Clock.schedule_once(lambda *_: self._baslik_ciz(), 0)

        selam = f'Merhaba, {isim}!' if isim else 'Geleceğinizi Keşfedin'
        ust = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(44), spacing=dp(8))
        ust.add_widget(emoji_label('🔮', font_size='34sp', size_hint=(None, 1), width=dp(40)))
        ust.add_widget(metin_label(
            'FalımaBak', font_size='30sp', bold=True, color=RENKLER['altin'],
            halign='left', valign='middle',
        ))
        self.add_widget(ust)
        self.add_widget(metin_label(selam, font_size='13sp', color=RENKLER['beyaz'],
            halign='left', size_hint_y=None, height=dp(22)))
        self.add_widget(metin_label(YORUM_BASLIK, font_size='11sp', color=RENKLER['gri_acik'],
            halign='left', size_hint_y=None, height=dp(18)))

    def _baslik_ciz(self, *_):
        if not hasattr(self, '_panel'):
            return
        self._panel.pos = self.pos
        self._panel.size = self.size
        self._cizgi.pos = (self.x, self.y)
        self._cizgi.size = (dp(4), self.height)


class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._kur()

    def _kur(self):
        gradient_arka_plan_ekle(self)
        root = FloatLayout()
        banner_yol = asset_yolu('splash_banner.png')
        self._banner_var = os.path.isfile(banner_yol)

        if self._banner_var:
            root.add_widget(Image(
                source=banner_yol,
                allow_stretch=True,
                keep_ratio=False,
                size_hint=(1, 1),
            ))
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

        if not self._banner_var:
            root.add_widget(metin_label(
                'FalımaBak', font_size='36sp', bold=True, color=RENKLER['altin'],
                halign='center', pos_hint={'center_x': 0.5, 'center_y': 0.46},
                size_hint=(0.9, None), height=dp(44),
            ))
            root.add_widget(metin_label(
                YORUM_BASLIK, font_size='13sp', color=RENKLER['gri_acik'],
                halign='center', pos_hint={'center_x': 0.5, 'center_y': 0.40},
                size_hint=(0.9, None), height=dp(24),
            ))

        self.yukleniyor = metin_label(
            'Yükleniyor...', font_size='13sp', color=RENKLER['altin_yumusak'],
            halign='center', pos_hint={'center_x': 0.5, 'y': 0.08},
            size_hint=(0.8, None), height=dp(28),
        )
        root.add_widget(self.yukleniyor)
        self.add_widget(root)

        if not _ANDROID and not self._banner_var:
            boyut = dp(96)
            anim_logo = (
                Animation(size=(boyut * 1.08, boyut * 1.08), opacity=0.88, duration=1.0, t='in_out_sine')
                + Animation(size=(boyut, boyut), opacity=1.0, duration=1.0, t='in_out_sine')
            )
            anim_logo.repeat = True
            self._anim_logo = anim_logo
            anim_logo.start(self.logo)
            anim_txt = Animation(opacity=0.35, duration=0.6) + Animation(opacity=1, duration=0.6)
            anim_txt.repeat = True
            self._anim_txt = anim_txt
            anim_txt.start(self.yukleniyor)
        else:
            self._anim_logo = None
            self._anim_txt = None
            if not self._banner_var:
                anim_txt = Animation(opacity=0.35, duration=0.6) + Animation(opacity=1, duration=0.6)
                anim_txt.repeat = True
                self._anim_txt = anim_txt
                anim_txt.start(self.yukleniyor)

        Clock.schedule_once(self._gec, 2.2)

    def _gec(self, *_):
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
            self._isim = guvenli_textinput(hint_text='Adınız (isteğe bağlı)')
            self._ana.add_widget(self._isim)

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
            self._adim += 1
            self._goster()
            return
        isim = getattr(self, '_isim', None)
        onboarding_tamamla(isim.text if isim else '')
        if self.manager and 'anasayfa' in self.manager.screen_names:
            self.manager.current = 'anasayfa'


class GecmisScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._kur()

    def _kur(self):
        ana = BoxLayout(orientation='vertical', padding=[dp(12), SAFE_UST, dp(12), 0], spacing=dp(8))

        ana.add_widget(baslik_satir('📜', 'Fal Geçmişi', font_size='22sp', height=dp(36)))

        kaydir = ScrollView(size_hint_y=1, do_scroll_x=False, bar_width=dp(3),
            bar_color=get_color_from_hex(RENKLER['mor_parlak']),
            bar_inactive_color=get_color_from_hex(RENKLER['kart_kenar']))
        self._liste = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None, padding=[0, dp(4)])
        self._liste.bind(minimum_height=self._liste.setter('height'))
        kaydir.add_widget(self._liste)
        ana.add_widget(kaydir)

        ana.add_widget(alt_nav_bar('gecmis', on_sec=self._nav))
        ekran_icerik_sar(self, ana)
        self._yenile()

    def on_enter(self, *_):
        self._yenile()

    def _yenile(self):
        if not hasattr(self, '_liste'):
            return
        self._liste.clear_widgets()
        try:
            kayitlar = gecmis_listesi()
        except Exception:
            kayitlar = []
        if not kayitlar:
            self._liste.add_widget(metin_label(
                'Henüz kayıtlı fal yok.\nBir fal baktır, burada görünsün.',
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
        ana = BoxLayout(orientation='vertical', padding=[dp(12), SAFE_UST, dp(12), 0], spacing=dp(8))
        ana.add_widget(BaslikKarti())
        ana.add_widget(GunlukFalKarti())
        ana.add_widget(metin_label(
            '✦  Fallarınız  ✦',
            font_size='13sp', bold=True, color=RENKLER['altin_parlak'],
            halign='center', size_hint_y=None, height=dp(22),
        ))

        menu = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=1)
        for baslik, aciklama, ikon, renk, hedef in [
            ('Tarot Falı', '78 kartlık deste ile geleceğinizi görün', 'tarot', RENKLER['mor'], 'tarot'),
            ('Kahve Falı', 'Fincanınızı fotoğraflayın, yorumlayalım', 'kahve', RENKLER['turuncu'], 'kahve'),
            ('Yıldız Falı', 'Burcunuza özel astroloji yorumları', 'astroloji', RENKLER['mavi_acik'], 'astroloji'),
            ('El Falı', 'Avuç içi çizgilerinizi okuyun', 'elfali', RENKLER['pembe'], 'elfali'),
            ('Diğer Fallar', 'İskambil, çiçek, nazar ve daha fazlası', 'diger', RENKLER['yesil'], 'diger_fallar'),
        ]:
            menu.add_widget(DashboardKart(baslik=baslik, aciklama=aciklama,
                ikon_anahtar=ikon, renk=renk, hedef=hedef))
        ana.add_widget(menu)

        ana.add_widget(metin_label('FalımaBak v1.0.15', font_size='10sp', bold=True,
            color=RENKLER['altin_yumusak'], halign='center', size_hint_y=None, height=dp(18)))
        ana.add_widget(alt_nav_bar('anasayfa', on_sec=self._nav))
        ekran_icerik_sar(self, ana)

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
    def on_start(self):
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
            from kamera import uygulama_izinlerini_iste
            Clock.schedule_once(lambda *_: uygulama_izinlerini_iste(), 1.5)
        except Exception:
            pass

    def build(self):
        try:
            from koruma import koruma_baslat
            koruma_baslat()
        except Exception:
            pass
        fontlari_yukle()
        emoji_font_yukle()
        self.title = 'FalımaBak'
        Window.clearcolor = get_color_from_hex(RENKLER['arka_plan'])
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
        return sm

    def _ekranlari_yukle(self):
        sm = self._sm
        try:
            from tarot import TarotScreen
            from kahve import KahveScreen
            from astroloji import AstrolojiScreen
            from diger_fallar import DigerFallarScreen
            from elfali import ElFaliScreen
            from ayarlar import AyarlarScreen

            ekranlar = [
                ('onboarding', lambda: OnboardingScreen(name='onboarding')),
                ('anasayfa', lambda: Anasayfa(name='anasayfa')),
                ('gecmis', lambda: GecmisScreen(name='gecmis')),
                ('ayarlar', lambda: AyarlarScreen(name='ayarlar')),
                ('tarot', lambda: TarotScreen(name='tarot')),
                ('kahve', lambda: KahveScreen(name='kahve')),
                ('astroloji', lambda: AstrolojiScreen(name='astroloji')),
                ('diger_fallar', lambda: DigerFallarScreen(name='diger_fallar')),
                ('elfali', lambda: ElFaliScreen(name='elfali')),
            ]
            for _, fab in ekranlar:
                sm.add_widget(fab())
        except Exception:
            err = traceback.format_exc()
            print(err, flush=True)
            if 'hata' not in sm.screen_names:
                sm.add_widget(HataScreen(mesaj=err, name='hata'))
            sm.current = 'hata'


if __name__ == '__main__':
    FalimaBakApp().run()
