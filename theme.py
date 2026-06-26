"""FalımaBak - Ortak tema, renkler ve font yönetimi."""

import os
import platform
import re

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex
from kivy.metrics import dp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
APP_SURUM = '1.7.4'

# ============================================================
#  PROFESYONEL RENK PALETİ
# ============================================================
RENKLER = {
    # Mystic Dark Theme — gece mavisi / antrasit
    'arka_plan':       '#0F0C20',
    'arka_plan2':      '#120E2E',
    'kart_arka':       '#1A1435',
    'kart_arka_cam':   '#221A42',
    'kart_kenar':      '#2D2460',
    
    # Ana vurgu renkleri (kart ikonları için)
    'mor':             '#7c4dff',
    'mor_koyu':        '#4a148c',
    'mor_parlak':      '#b388ff',
    'turuncu':         '#ff9100',
    'mavi_acik':       '#40c4ff',
    'mavi_parlak':     '#00e5ff',
    'pembe':           '#e040fb',
    'pembe_acik':      '#ff80ab',
    'yesil':           '#00e676',
    
    # Metin — koyu kart üzerinde yüksek kontrast
    'beyaz':           '#FFFFFF',
    'gri_acik':        '#D6D0E8',
    'gri':             '#9B93B8',
    'gri_koyu':        '#6E668A',

    # Vurgu metinleri
    'altin':           '#FFD700',
    'altin_parlak':    '#FFEC6E',
    'altin_yumusak':   '#E8D5A3',
    
    # Durum renkleri
    'yesil_parlak':    '#69f0ae',
    'kirmizi':         '#ff1744',
    'kirmizi_acik':    '#ff5252',
    
    # Fallara özel renkler
    'lacivert':        '#0d47a1',
    'kahve':           '#6d4c41',
    'kahve_acik':      '#a1887f',
    'ten':             '#ffccbc',
    
    # Gölge
    'golge':           '#000000',

    # Siyah buton teması
    'buton_arka':      '#0A0A0A',
    'buton_arka2':     '#141414',
    'buton_kenar':     '#2B2B2B',
    'buton_vurgu':     '#1F1F1F',
    'buton_altin':     '#C9A84C',
}

# ============================================================
#  İKON SETİ - Material Design benzeri Unicode ikonlar
# ============================================================
# Ana menü kart arka planları — koyu, opak (beyaz kart görünümünü önler)
KART_MENU_AR = {
    'tarot':     '#1A1435',
    'kahve':     '#2A1810',
    'astroloji': '#101E35',
    'elfali':    '#221535',
    'diger':     '#122820',
    'burc_eslesme': '#281428',
    'ruya':      '#181828',
}

# Tuş metinleri (Segoe UI) + ayrı emoji ikonları
TUS = {
    'geri':      'Geri',
    'fal_ac':    'Fal Aç',
    'tekrar':    'Tekrar',
    'galeri':    'Galeri',
    'kamera':    'Kamera',
    'yorumla':   'Yorumla',
    'fal_bak':   'Fala Bak',
    'bekle':     'Bekleyin',
    'kart_adet': 'Kart',
    'tamam':     'Tamam',
}

TUS_IKON = {
    'fal_ac':    '🃏',
    'tekrar':    '🔁',
    'galeri':    '🖼',
    'kamera':    '📷',
    'yorumla':   '☕',
    'fal_bak':   '🔮',
    'bekle':     '⏳',
    'kart_adet': '🃏',
    'tamam':     '✅',
}

# Yorum markası — dil destekli
YORUM_BEKLE = 'FalımaBak yorumluyor...'
YORUM_BASLIK = 'FalımaBak Yorumluyor'
YORUM_EK = 'FalımaBak Önerisi'


def tus_metin(k):
    from dil import t
    return t(f'tus_{k}')


def yorum_bekle_metin():
    from dil import t
    return t('yorum_bekle')


def yorum_baslik_metin():
    from dil import t
    return t('yorum_baslik')

FAL_IKONLARI = {
    'tarot':     '🔮',
    'kahve':     '☕',
    'astroloji': '🌟',
    'elfali':    '✋',
    'diger':     '✨',
    'burc_eslesme': '💞',
    'ruya':      '🌙',
    'ok':        '›',
}

# Menü PNG ikonları (assets/ klasörü)
MENU_IKON_DOSYALARI = {
    'tarot':     'menu_tarot.png',
    'kahve':     'menu_kahve.png',
    'astroloji': 'menu_astroloji.png',
    'elfali':    'menu_elfali.png',
    'diger':     'menu_diger.png',
    'burc_eslesme': 'menu_burc_eslesme.png',
    'ruya':      'menu_ruya.png',
}

NAV_IKON_DOSYALARI = {
    'anasayfa': 'nav_anasayfa.png',
    'gecmis':   'nav_gecmis.png',
    'ayarlar':  'nav_ayarlar.png',
}

# Diğer Fallar ekranı — iskambil, çiçek, el, nazar
DIGER_FAL_IKONLARI = {
    'iskambil': 'diger_iskambil.png',
    'cicek':    'diger_cicek.png',
    'el':       'diger_el.png',
    'nazar':    'diger_nazar.png',
}

# Mobil safe area (çentik / gesture bar) — Android'de aşağıda genişletilir
SAFE_UST = dp(8)
COIN_SAG_BOSLUK = dp(96)
COIN_UST_KENAR = dp(4)
COIN_SAG_KENAR = dp(6)
SAFE_ALT = dp(10)
BUTON_MIN_YUKSEK = dp(48)

# Emoji yoksa Android'de gösterilecek yedek karakterler (Roboto uyumlu)
EMOJI_YEDEK = {
    '🔮': '◆', '📸': '◎', '✦': '✦', '🃏': '♠', '🔁': '↻', '🖼': '▣',
    '📷': '◎', '☕': '♨', '⏳': '…', '✅': '✓', '🌟': '★', '✋': '✋',
    '✨': '✦', '🏠': '⌂', '📜': '≡', '⚙️': '⚙', '⚙': '⚙',
    '✦': '*',
}

FON_ADI = 'AppFont'
_font_yuklendi = False
_emoji_font_yolu = None
_emoji_font_denendi = False

# Windows emoji font adayları (sırayla dene)
_EMOJI_FONT_ADLARI = (
    'seguiemj.ttf',
    'segoeuiemj.ttf',
    'SegoeUIEmoji.ttf',
)


def _windows_font_yolu(dosya):
    return os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts', dosya)


def _android_mi():
    return (
        'ANDROID_ARGUMENT' in os.environ
        or 'ANDROID_ROOT' in os.environ
        or 'ANDROID_BOOTLOGO' in os.environ
    )


def _mobil_safe_alan_ayarla():
    """Çentik ve gesture bar için Android safe area."""
    global SAFE_UST, SAFE_ALT
    if _android_mi():
        SAFE_UST = dp(32)
        SAFE_ALT = dp(24)


_mobil_safe_alan_ayarla()


def fontlari_yukle():
    """Windows: Segoe. Android: gömülü Roboto (dosya yolu ile register etme — presplash'te takılır)."""
    global _font_yuklendi, FON_ADI
    if _font_yuklendi:
        return

    if platform.system() == 'Windows':
        regular = _windows_font_yolu('segoeui.ttf')
        bold = _windows_font_yolu('segoeuib.ttf')
        if os.path.isfile(regular):
            LabelBase.register(
                name=FON_ADI,
                fn_regular=regular,
                fn_bold=bold if os.path.isfile(bold) else regular,
            )
            _font_yuklendi = True
            return

    if _android_mi():
        # Kivy Android APK içindeki Roboto — AppFont olarak yanlış path register ETME
        FON_ADI = 'Roboto'
        _font_yuklendi = True
        return

    bundled = os.path.join(ASSETS_DIR, 'Roboto-Regular.ttf')
    if os.path.isfile(bundled):
        bold_path = os.path.join(ASSETS_DIR, 'Roboto-Bold.ttf')
        LabelBase.register(
            name=FON_ADI,
            fn_regular=bundled,
            fn_bold=bold_path if os.path.isfile(bold_path) else bundled,
        )
    else:
        FON_ADI = 'Roboto'
    _font_yuklendi = True


def emoji_font_yolu():
    """Emoji fontunun tam dosya yolunu döndürür (Kivy'ye doğrudan verilir)."""
    global _emoji_font_yolu, _emoji_font_denendi
    if _emoji_font_denendi:
        return _emoji_font_yolu or ''

    _emoji_font_denendi = True
    if platform.system() == 'Windows':
        for dosya in _EMOJI_FONT_ADLARI:
            yol = os.path.normpath(_windows_font_yolu(dosya))
            if os.path.isfile(yol):
                _emoji_font_yolu = yol
                return yol

    if _android_mi():
        for yol in (
            '/system/fonts/NotoColorEmoji.ttf',
            '/system/fonts/NotoColorEmojiLegacy.ttf',
            '/system/fonts/AndroidEmoji.ttf',
            '/system/fonts/NotoEmoji-Regular.ttf',
        ):
            if os.path.isfile(yol):
                _emoji_font_yolu = yol
                return yol
        bundled = os.path.join(ASSETS_DIR, 'NotoColorEmoji.ttf')
        if os.path.isfile(bundled):
            _emoji_font_yolu = bundled
            return bundled

    _emoji_font_yolu = ''
    return ''


def emoji_font_yukle():
    """Geriye dönük uyumluluk."""
    return emoji_font_yolu() or FON_ADI


def emoji_label(text, font_size='28sp', **kwargs):
    """Kırık kutu (X) olmadan emoji gösteren Label."""
    fontlari_yukle()
    yol = emoji_font_yolu()
    metin = text
    if not yol:
        metin = EMOJI_YEDEK.get(text, text)
    fon = yol if yol else FON_ADI
    kwargs.setdefault('halign', 'center')
    kwargs.setdefault('valign', 'middle')
    kwargs.setdefault('color', get_color_from_hex(RENKLER['beyaz']))
    return Label(text=metin, font_name=fon, font_size=font_size, **kwargs)


def menu_ikon_resmi(anahtar, renk_hex=None, font_size='26sp', **kwargs):
    """Menü kartı için PNG ikon (yoksa emoji/harf yedeği)."""
    from kivy.uix.image import Image

    dosya = MENU_IKON_DOSYALARI.get(anahtar, '')
    yol = asset_yolu(dosya) if dosya else ''
    if yol and os.path.isfile(yol):
        defaults = {
            'allow_stretch': False,
            'keep_ratio': True,
            'size_hint': (None, None),
            'size': (dp(44), dp(44)),
        }
        defaults.update(kwargs)
        return Image(source=yol, **defaults)
    return fal_ikon_widget_yedek(
        anahtar, renk_hex or RENKLER['altin'], font_size=font_size, **kwargs,
    )


def fal_ikon_widget_yedek(anahtar, renk_hex, font_size='26sp', **kwargs):
    """PNG yoksa emoji veya harf."""
    fontlari_yukle()
    metin = FAL_IKONLARI.get(anahtar, '🔮')
    yol = emoji_font_yolu()
    if yol:
        return emoji_label(metin, font_size=font_size, color=renk_hex, **kwargs)
    harf = {
        'tarot': 'T', 'kahve': 'K', 'astroloji': 'Y',
        'elfali': 'E', 'diger': 'D', 'burc_eslesme': 'B', 'ruya': 'R',
    }.get(anahtar, 'F')
    return metin_label(
        harf, font_size=font_size, bold=True, color=renk_hex,
        halign='center', valign='middle', **kwargs,
    )


def fal_ikon_widget(anahtar, renk_hex, font_size='26sp', **kwargs):
    """Menü kartı ikonu — önce PNG."""
    return menu_ikon_resmi(anahtar, renk_hex=renk_hex, font_size=font_size, **kwargs)


def png_ikon_widget(dosya, boyut=None, **kwargs):
    """Sabit PNG ikon (Android'de emoji yerine)."""
    from kivy.uix.image import Image

    yol = asset_yolu(dosya) if not os.path.isabs(dosya) else dosya
    if not yol or not os.path.isfile(yol):
        return None
    b = boyut or dp(44)
    if isinstance(b, (int, float)):
        b = (b, b)
    defaults = {
        'source': yol,
        'allow_stretch': False,
        'keep_ratio': True,
        'size_hint': (None, None),
        'size': b,
    }
    defaults.update(kwargs)
    return Image(**defaults)


def kart_ikon_widget(anahtar=None, dosya=None, boyut=None, renk_hex=None, **kwargs):
    """Ana sayfa kart ikonu — PNG öncelikli."""
    if dosya:
        w = png_ikon_widget(dosya, boyut=boyut, **kwargs)
        if w:
            return w
    if anahtar:
        w = menu_ikon_resmi(anahtar, renk_hex=renk_hex or RENKLER['altin'], **kwargs)
        if boyut:
            b = boyut if isinstance(boyut, tuple) else (boyut, boyut)
            w.size = b
        return w
    return metin_label('?', font_size='22sp', bold=True, color=renk_hex or RENKLER['altin'], **kwargs)


def _textinput_topla(root):
    from kivy.uix.textinput import TextInput

    bulunan = []

    def _gez(w):
        if isinstance(w, TextInput):
            bulunan.append(w)
        for ch in w.children:
            _gez(ch)

    _gez(root)
    return bulunan


def klavye_kaydir_bagla(scroll=None, root=None, *widgets):
    """TextInput odaklanınca klavye altında kalmaması için ScrollView kaydır."""
    from kivy.clock import Clock
    from kivy.uix.textinput import TextInput
    from kivy.uix.scrollview import ScrollView

    alanlar = list(widgets)
    if root is not None:
        alanlar.extend(_textinput_topla(root))

    def _scrollview_bul(w):
        if scroll is not None:
            return scroll
        p = w.parent
        while p is not None:
            if isinstance(p, ScrollView):
                return p
            p = p.parent
        return None

    def _scroll_iceriginde(sv, w):
        p = w
        while p is not None:
            if p is sv:
                return True
            p = p.parent
        return False

    def _focus_cb(instance, focused):
        if not focused:
            return

        def _kaydir(*_):
            try:
                sv = _scrollview_bul(instance)
                if sv and _scroll_iceriginde(sv, instance):
                    sv.scroll_to(instance, padding=dp(56), animate=True)
            except Exception:
                pass

        Clock.schedule_once(_kaydir, 0.08)
        Clock.schedule_once(_kaydir, 0.28)

    goruldu = set()
    for w in alanlar:
        if isinstance(w, TextInput) and id(w) not in goruldu:
            goruldu.add(id(w))
            w.bind(focus=_focus_cb)


def klavye_kapat():
    """Açık klavyeyi kapat (TextInput odak çökmesi önleme)."""
    try:
        from kivy.core.window import Window
        Window.release_all_keyboards()
    except Exception:
        pass
    try:
        from kivy.uix.textinput import TextInput
        from kivy.app import App

        app = App.get_running_app()
        if not app or not app.root:
            return

        def _gez(w):
            if isinstance(w, TextInput) and w.focus:
                w.focus = False
            for ch in w.children:
                _gez(ch)

        _gez(app.root)
    except Exception:
        pass


def guvenli_textinput(hint_text='', **kwargs):
    """Android/desktop güvenli TextInput — mobilde font_name yok, IME uyumlu zemin."""
    from kivy.uix.textinput import TextInput

    fontlari_yukle()
    android = _android_mi()
    cok_satir = bool(kwargs.get('multiline', False))
    guvenli_mod = android or cok_satir
    if android:
        kwargs.pop('font_name', None)

    temel = {
        'hint_text': hint_text,
        'multiline': False,
        'size_hint_y': None,
        'height': dp(44),
        'font_size': '15sp',
        'write_tab': False,
        'input_type': 'text',
        'use_bubble': False,
        'use_handles': False,
    }
    if guvenli_mod:
        # background_normal='' bazı Android cihazlarda IME açılınca native crash yapar
        temel.update({
            'padding': [12, 10, 12, 10],
            'background_color': get_color_from_hex(RENKLER['kart_arka']),
            'foreground_color': (1, 1, 1, 1),
            'hint_text_color': (0.65, 0.65, 0.72, 1),
            'cursor_color': (1, 1, 1, 1),
        })
    else:
        temel.update({
            'font_name': FON_ADI,
            'padding': [dp(12), dp(10)],
            'background_color': get_color_from_hex(RENKLER['kart_arka']),
            'foreground_color': get_color_from_hex(RENKLER['beyaz']),
            'hint_text_color': get_color_from_hex(RENKLER['gri']),
        })
    temel.update(kwargs)
    if android:
        temel.pop('font_name', None)
        temel.pop('background_normal', None)
        temel.pop('background_active', None)
    return TextInput(**temel)


def siyah_buton(text='', ikon=None, vurgu=False, altin_yazi=False, **kwargs):
    """Siyah temalı buton — ikon varsa emoji + metin yan yana."""
    if ikon:
        return ikonlu_siyah_buton(ikon, text, vurgu=vurgu, altin_yazi=altin_yazi, **kwargs)

    from kivy.uix.button import Button

    fontlari_yukle()
    arka = RENKLER['buton_vurgu'] if vurgu else RENKLER['buton_arka']
    yazi = RENKLER['buton_altin'] if altin_yazi else RENKLER['beyaz']
    defaults = {
        'text': text,
        'font_name': FON_ADI,
        'font_size': '14sp',
        'bold': True,
        'background_normal': '',
        'background_color': get_color_from_hex(arka),
        'color': get_color_from_hex(yazi),
        'size_hint_y': None,
        'height': BUTON_MIN_YUKSEK,
    }
    defaults.update(kwargs)
    return Button(**defaults)


def ikonlu_siyah_buton(ikon, metin, vurgu=False, altin_yazi=False, **kwargs):
    """Emoji ikon + metin içeren tıklanabilir buton."""
    from kivy.graphics import Color, RoundedRectangle
    from kivy.uix.behaviors import ButtonBehavior
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label

    fontlari_yukle()
    arka = RENKLER['buton_vurgu'] if vurgu else RENKLER['buton_arka']
    yazi = RENKLER['buton_altin'] if altin_yazi else RENKLER['beyaz']
    font_size = kwargs.pop('font_size', '14sp')
    ikon_size = kwargs.pop('ikon_size', '15sp')
    height = kwargs.pop('height', BUTON_MIN_YUKSEK)

    class _IkonluButon(ButtonBehavior, BoxLayout):
        pass

    btn = _IkonluButon(
        orientation='horizontal',
        spacing=dp(4),
        padding=[dp(8), dp(6)],
        size_hint_y=None,
        height=height,
        **kwargs,
    )
    with btn.canvas.before:
        Color(*get_color_from_hex(arka))
        btn._bg = RoundedRectangle(radius=[dp(8)])

    def _ciz(inst, *_):
        btn._bg.pos = inst.pos
        btn._bg.size = inst.size

    btn.bind(pos=_ciz, size=_ciz)
    Clock.schedule_once(lambda dt: _ciz(btn), 0)

    btn.add_widget(emoji_label(
        ikon, font_size=ikon_size,
        size_hint_x=None, width=dp(28),
    ))
    btn._metin_lbl = Label(
        text=metin,
        font_name=FON_ADI,
        font_size=font_size,
        bold=True,
        color=get_color_from_hex(yazi),
        halign='left',
        valign='middle',
        size_hint_x=1,
    )
    btn.add_widget(btn._metin_lbl)
    return btn


def png_ikonlu_siyah_buton(png_dosya, metin, vurgu=False, altin_yazi=False, **kwargs):
    """PNG ikon + metin — Diğer Fallar butonları için."""
    from kivy.graphics import Color, RoundedRectangle
    from kivy.uix.behaviors import ButtonBehavior
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.image import Image
    from kivy.uix.label import Label

    fontlari_yukle()
    arka = RENKLER['buton_vurgu'] if vurgu else RENKLER['buton_arka']
    yazi = RENKLER['buton_altin'] if altin_yazi else RENKLER['beyaz']
    font_size = kwargs.pop('font_size', '14sp')
    height = kwargs.pop('height', BUTON_MIN_YUKSEK)

    class _PngButon(ButtonBehavior, BoxLayout):
        pass

    btn = _PngButon(
        orientation='horizontal',
        spacing=dp(6),
        padding=[dp(8), dp(6)],
        size_hint_y=None,
        height=height,
        **kwargs,
    )
    with btn.canvas.before:
        Color(*get_color_from_hex(arka))
        btn._bg = RoundedRectangle(radius=[dp(8)])

    def _ciz(inst, *_):
        btn._bg.pos = inst.pos
        btn._bg.size = inst.size

    btn.bind(pos=_ciz, size=_ciz)
    Clock.schedule_once(lambda dt: _ciz(btn), 0)

    yol = asset_yolu(png_dosya) if png_dosya else ''
    if yol and os.path.isfile(yol):
        btn.add_widget(Image(
            source=yol,
            size_hint=(None, 1),
            width=dp(32),
            allow_stretch=True,
            keep_ratio=True,
        ))
    btn._metin_lbl = Label(
        text=metin,
        font_name=FON_ADI,
        font_size=font_size,
        bold=True,
        color=get_color_from_hex(yazi),
        halign='left',
        valign='middle',
        size_hint_x=1,
    )
    btn.add_widget(btn._metin_lbl)
    return btn


def diger_fal_buton(metin, fal_anahtar, vurgu=True, **kwargs):
    """Diğer Fallar grid butonu."""
    png = DIGER_FAL_IKONLARI.get(fal_anahtar, '')
    return png_ikonlu_siyah_buton(png, metin, vurgu=vurgu, **kwargs)


def buton_metin_guncelle(btn, metin):
    """İkonlu veya normal buton metnini günceller."""
    if hasattr(btn, '_metin_lbl'):
        btn._metin_lbl.text = metin
    elif hasattr(btn, 'text'):
        btn.text = metin


def tus_buton(anahtar, vurgu=False, altin_yazi=False, **kwargs):
    """Dil destekli standart buton."""
    try:
        from dil import t
        metin = t(f'tus_{anahtar}')
    except Exception:
        metin = TUS.get(anahtar, anahtar)
    ikon = TUS_IKON.get(anahtar, '')
    if _android_mi():
        ikon = ''
    return siyah_buton(metin, ikon=ikon, vurgu=vurgu, altin_yazi=altin_yazi, **kwargs)


def baslik_satir(ikon, metin, font_size='22sp', renk=None, height=None, **kwargs):
    """Ekran başlığı: emoji + metin (kırık kutu yok)."""
    from kivy.uix.boxlayout import BoxLayout

    satir = BoxLayout(
        orientation='horizontal',
        size_hint_y=None,
        height=height or dp(40),
        spacing=dp(8),
        padding=[0, dp(2), 0, dp(2)],
        **kwargs,
    )
    if ikon:
        satir.add_widget(emoji_label(
            ikon, font_size=font_size,
            size_hint_x=None, width=dp(36),
        ))
    satir.add_widget(metin_label(
        metin,
        font_size=font_size,
        bold=True,
        color=renk or RENKLER['altin'],
        halign='left',
        valign='middle',
        size_hint_x=1,
    ))
    from kivy.uix.widget import Widget
    satir.add_widget(Widget(size_hint_x=None, width=COIN_SAG_BOSLUK))
    return satir


def talimat_kutusu(ikon, satirlar, font_size='16sp', renk=None):
    """Kamera/talimat alanı — büyük emoji + Türkçe metin."""
    from kivy.uix.boxlayout import BoxLayout

    kutu = BoxLayout(orientation='vertical', spacing=dp(6), padding=dp(8))
    kutu.add_widget(emoji_label(ikon, font_size='42sp', size_hint_y=None, height=dp(52)))
    for satir in satirlar:
        kutu.add_widget(metin_label(
            satir,
            font_size=font_size,
            color=renk or RENKLER['gri_acik'],
            halign='center',
            size_hint_y=None,
            height=dp(22),
        ))
    return kutu


def emoji_temizle(metin):
    """Android'de görünmeyen emoji/kutu karakterlerini temizler."""
    if not metin:
        return metin
    for em, yedek in EMOJI_YEDEK.items():
        metin = metin.replace(em, yedek)
    metin = re.sub(
        r'[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0000FE00-\U0000FEFF'
        r'\U0001F000-\U0001F02F\U0001F0A0-\U0001F0FF]+',
        '',
        metin,
    )
    return re.sub(r'  +', ' ', metin).strip()


def yorum_baslik(ai_kullanildi=True, kaynak=None, fotograf=False):
    """Kullanıcıya her zaman aynı marka — AI/bulut/hazır ayrımı yok."""
    return yorum_baslik_metin()


def yorum_bekle_markup():
    return f"[color={RENKLER['altin_yumusak']}]{yorum_bekle_metin()}[/color]"


def yorum_durum_notu(hata=None, ai_kullanildi=True):
    """Kullanıcıya hata/AI bilgisi gösterme."""
    return ''


def yorum_sonuc_metni(temel, metin, ai_kullanildi=True, hata=None, kaynak=None, fotograf=False):
    """Fal ekranları için birleşik yorum metni."""
    baslik = yorum_baslik(ai_kullanildi, kaynak, fotograf)
    govde = emoji_temizle(metin or '')
    return (
        emoji_temizle(temel or '')
        + f"\n\n[b][color={RENKLER['altin']}]» {baslik}[/color][/b]\n"
        + f"[color={RENKLER['pembe_acik']}]{govde}[/color]"
    )


def foto_fal_sonuc(metin, hata=None, kaynak=None):
    """Fotoğraflı fal ekranları."""
    if hata and not metin:
        return f"[color={RENKLER['kirmizi']}]{emoji_temizle(hata)}[/color]"
    govde = emoji_temizle(metin or '')
    baslik = yorum_baslik_metin()
    return (
        f"[b][color={RENKLER['altin']}]» {baslik}[/color][/b]\n\n"
        f"[color={RENKLER['pembe_acik']}]{govde}[/color]"
    )


def kaydirici_metin(yukseklik_hint=0.2, zemin_renk=None):
    """Koyu zeminli kaydırılabilir metin alanı — yuvarlatılmış modern panel."""
    from kivy.graphics import Color, RoundedRectangle, Line
    from kivy.uix.scrollview import ScrollView

    scroll = ScrollView(
        size_hint=(1, yukseklik_hint),
        do_scroll_x=False,
        bar_width=0,
        scroll_type=['bars', 'content'],
    )
    renk = zemin_renk or RENKLER['kart_arka_cam']
    radius = dp(14)
    with scroll.canvas.before:
        Color(*get_color_from_hex(renk))
        scroll._kaydir_bg = RoundedRectangle(radius=[radius])

    with scroll.canvas.after:
        Color(*get_color_from_hex(RENKLER['kart_kenar']))
        scroll._kaydir_cerceve = Line(rounded_rectangle=(0, 0, 0, 0, radius), width=dp(1.2))

    def _kaydir_bg_guncelle(*_):
        scroll._kaydir_bg.pos = scroll.pos
        scroll._kaydir_bg.size = scroll.size
        x, y = scroll.pos
        w, h = scroll.size
        scroll._kaydir_cerceve.rounded_rectangle = (x, y, w, h, radius)

    scroll.bind(pos=_kaydir_bg_guncelle, size=_kaydir_bg_guncelle)
    Clock.schedule_once(lambda *_: _kaydir_bg_guncelle(), 0)

    fontlari_yukle()
    label = Label(
        text='',
        font_name=FON_ADI,
        font_size='13sp',
        color=get_color_from_hex(RENKLER['gri_acik']),
        size_hint_y=None,
        halign='left',
        valign='top',
        markup=True,
        padding=(dp(10), dp(10)),
    )

    def _metin_genisligi(*_):
        label.text_size = (max(scroll.width - dp(20), dp(100)), None)

    def _metin_yuksekligi(inst, texture_size):
        inst.height = max(texture_size[1] + dp(12), dp(40))

    label.bind(texture_size=_metin_yuksekligi)
    scroll.bind(width=_metin_genisligi)
    Clock.schedule_once(lambda *_: _metin_genisligi(), 0)

    scroll.add_widget(label)
    return scroll, label


def fal_form_duz():
    """Düz, kaydırmasız form paneli — zemin canvas'ta, içerik ezilmez."""
    from kivy.graphics import Color, RoundedRectangle, Rectangle
    from kivy.uix.boxlayout import BoxLayout

    panel = BoxLayout(
        orientation='vertical',
        size_hint_y=None,
        padding=dp(12),
        spacing=dp(6),
    )
    radius = dp(14)
    with panel.canvas.before:
        Color(*get_color_from_hex(RENKLER['kart_arka_cam']))
        panel._form_bg = RoundedRectangle(radius=[radius])
        Color(*get_color_from_hex(RENKLER['mor']))
        panel._form_serit = Rectangle()

    def _form_zemin(*_):
        x, y = panel.pos
        w, h = panel.size
        panel._form_bg.pos = (x, y)
        panel._form_bg.size = (w, h)
        panel._form_serit.pos = (x + dp(8), y + dp(10))
        panel._form_serit.size = (dp(3), max(h - dp(20), dp(8)))

    panel.bind(pos=_form_zemin, size=_form_zemin)

    form = BoxLayout(
        orientation='vertical',
        size_hint_y=None,
        spacing=dp(8),
    )
    form.bind(minimum_height=form.setter('height'))

    def _panel_h(*_):
        panel.height = form.height + dp(24)
        _form_zemin()

    form.bind(height=_panel_h)
    panel.add_widget(form)
    Clock.schedule_once(lambda *_: _panel_h(), 0)
    return panel, form


def fal_form_panel(yukseklik=None, esnek=False):
    """Geriye dönük — artık kaydırmasız düz panel."""
    panel, form = fal_form_duz()
    if yukseklik and not esnek:
        panel.height = max(yukseklik, panel.height)
    return panel, form, None


def yorum_panel_baslik(metin='Yorum'):
    """Yorum alanı üst etiketi."""
    return metin_label(
        metin,
        font_size='11sp',
        bold=True,
        color=RENKLER['altin_parlak'],
        halign='left',
        size_hint_y=None,
        height=dp(18),
    )


class FotoKutucukPanel(BoxLayout):
    """Çoklu fotoğraf yükleme kutucukları — galeri/kamera ile doldurulur."""

    def __init__(self, slotlar, yukseklik=None, **kwargs):
        from kivy.uix.behaviors import ButtonBehavior
        from kivy.uix.image import Image
        from kivy.uix.relativelayout import RelativeLayout
        from kivy.graphics import Color, Line

        super().__init__(
            orientation='horizontal',
            spacing=dp(8),
            padding=(dp(4), dp(6)),
            size_hint_y=None,
            height=yukseklik or dp(132),
            **kwargs,
        )
        self._slotlar = list(slotlar)
        self._yollar = {s['anahtar']: None for s in slotlar}
        self._kutular = {}
        self._secili = slotlar[0]['anahtar'] if slotlar else None

        class _FotoSlot(ButtonBehavior, RelativeLayout):
            pass

        fontlari_yukle()
        for slot in slotlar:
            anahtar = slot['anahtar']
            kutu = _FotoSlot(size_hint=(1, 1))
            kutu.anahtar = anahtar
            kutu.panel = self
            kutu.bind(on_press=lambda inst, a=anahtar: self.kutu_sec(a))

            koyu_zemin_ekle(kutu, RENKLER['kart_arka_cam'], radius=12)

            oniz = Image(
                allow_stretch=True,
                keep_ratio=True,
                size_hint=(0.92, 0.72),
                pos_hint={'center_x': 0.5, 'center_y': 0.58},
                opacity=0,
            )
            ikon_metin = slot.get('ikon_metin') or EMOJI_YEDEK.get(slot.get('ikon', ''), '+')
            ikon = metin_label(
                ikon_metin,
                font_size='22sp',
                bold=True,
                color=RENKLER['altin'],
                halign='center',
                size_hint=(1, None),
                height=dp(32),
                pos_hint={'center_x': 0.5, 'center_y': 0.55},
            )
            baslik = metin_label(
                slot['baslik'],
                font_size='10sp',
                color=RENKLER['gri_acik'],
                halign='center',
                size_hint=(1, None),
                height=dp(28),
                pos_hint={'center_x': 0.5, 'y': dp(4)},
            )

            with kutu.canvas.after:
                kutu._cerceve_renk = Color(*get_color_from_hex(RENKLER['kart_kenar']))
                kutu._cerceve = Line(rounded_rectangle=(0, 0, 0, 0, dp(12)), width=dp(1.2))

            kutu.onizleme = oniz
            kutu.ikon = ikon
            kutu.baslik = baslik
            kutu.add_widget(oniz)
            kutu.add_widget(ikon)
            kutu.add_widget(baslik)

            def _cerceve_guncelle(inst, *_):
                w, h = inst.size
                inst._cerceve.rounded_rectangle = (0, 0, w, h, dp(12))

            kutu.bind(size=_cerceve_guncelle)
            Clock.schedule_once(lambda *_: _cerceve_guncelle(kutu), 0)

            self._kutular[anahtar] = kutu
            self.add_widget(kutu)

        self.kutu_sec(self._secili)

    def kutu_sec(self, anahtar):
        if anahtar not in self._kutular:
            return
        self._secili = anahtar
        for key, kutu in self._kutular.items():
            secili = key == anahtar
            kutu.baslik.color = get_color_from_hex(
                RENKLER['altin'] if secili else RENKLER['gri_acik'],
            )
            kutu.baslik.bold = secili
            kutu._cerceve_renk.rgba = get_color_from_hex(
                RENKLER['altin'] if secili else RENKLER['kart_kenar'],
            )
            kutu._cerceve.width = dp(2.2) if secili else dp(1.2)

    def fotograf_ekle(self, yol):
        """Seçili kutuya fotoğraf ata; doluysa sonraki boş kutuya geç."""
        if not yol:
            return
        hedef = self._secili
        if self._yollar.get(hedef):
            for slot in self._slotlar:
                if not self._yollar.get(slot['anahtar']):
                    hedef = slot['anahtar']
                    break
        self._yollar[hedef] = yol
        self._onizleme_guncelle(hedef)
        self.kutu_sec(hedef)
        for slot in self._slotlar:
            if not self._yollar.get(slot['anahtar']):
                self.kutu_sec(slot['anahtar'])
                break

    def _onizleme_guncelle(self, anahtar):
        kutu = self._kutular.get(anahtar)
        yol = self._yollar.get(anahtar)
        if not kutu:
            return
        if yol:
            kutu.onizleme.source = yol
            kutu.onizleme.reload()
            kutu.onizleme.opacity = 1
            kutu.ikon.opacity = 0.15
        else:
            kutu.onizleme.opacity = 0
            kutu.ikon.opacity = 1

    def tamam_mi(self):
        return all(self._yollar.get(s['anahtar']) for s in self._slotlar)

    def eksik_basliklar(self):
        return [s['baslik'] for s in self._slotlar if not self._yollar.get(s['anahtar'])]

    def tum_veri(self):
        yollar = []
        aciklamalar = []
        for slot in self._slotlar:
            yol = self._yollar.get(slot['anahtar'])
            if yol:
                yollar.append(yol)
                aciklamalar.append(slot['baslik'])
        return {
            'foto_yollari': yollar,
            'foto_aciklamalari': aciklamalar,
        }


def metin_label(text, font_size='16sp', bold=False, color=None, halign='left', valign='middle', **kwargs):
    """Türkçe karakter destekli, düzgün hizalanmış Label."""
    fontlari_yukle()
    renk = get_color_from_hex(color or RENKLER['beyaz'])
    lbl = Label(
        text=text,
        font_name=FON_ADI,
        font_size=font_size,
        bold=bold,
        color=renk,
        halign=halign,
        valign=valign,
        **kwargs,
    )

    def _text_size_guncelle(inst, *_):
        genislik = max(inst.width, dp(1))
        if genislik < dp(8):
            return
        sabit_y = inst.size_hint_y is None and inst.height > dp(10)
        if sabit_y:
            inst.text_size = (genislik, inst.height)
        elif halign in ('left', 'right', 'center'):
            inst.text_size = (genislik, None)
        else:
            inst.text_size = (genislik, max(inst.height, dp(16)))

    lbl.bind(size=_text_size_guncelle, pos=_text_size_guncelle)
    Clock.schedule_once(lambda *_: _text_size_guncelle(lbl), 0)
    Clock.schedule_once(lambda *_: _text_size_guncelle(lbl), 0.05)
    return lbl


def koyu_zemin_ekle(parent, renk_hex, radius=18, vurgu_renk=None):
    """Kart içine tam kaplama koyu zemin (canvas.before yerine — beyaz flash önlenir)."""
    from kivy.graphics import Color, RoundedRectangle, Rectangle
    from kivy.uix.widget import Widget

    r = dp(radius)
    zemin = Widget(size_hint=(1, 1))
    with zemin.canvas:
        Color(*get_color_from_hex(renk_hex))
        govde = RoundedRectangle(radius=[r])
        if vurgu_renk:
            Color(*get_color_from_hex(vurgu_renk))
            serit = Rectangle()

    def _guncelle(*_):
        w, h = zemin.size
        govde.pos = (0, 0)
        govde.size = (w, h)
        if vurgu_renk:
            serit.pos = (dp(6), dp(12))
            serit.size = (dp(4), max(h - dp(24), dp(8)))

    zemin.bind(size=_guncelle)
    parent.add_widget(zemin, index=0)
    Clock.schedule_once(lambda *_: _guncelle(), 0)
    return zemin


def arka_plan_ekle(widget, renk=None):
    """Mystic dark arka plan — tek katman, clear() yok (render çökmesini önler)."""
    from kivy.graphics import Color, Rectangle

    renk_hex = renk or RENKLER['arka_plan']
    with widget.canvas.before:
        Color(*get_color_from_hex(renk_hex))
        rect = Rectangle(size=widget.size, pos=widget.pos)

    def _guncelle_rect(*_):
        rect.pos = widget.pos
        rect.size = widget.size

    widget.bind(pos=_guncelle_rect, size=_guncelle_rect)
    return rect


def gradient_arka_plan_ekle(widget):
    """Opak mistik gradient — yarı saydam katman yok (beyaz sızıntı önlenir)."""
    from kivy.core.window import Window
    from kivy.graphics import Color, Rectangle

    with widget.canvas.before:
        Color(*get_color_from_hex(RENKLER['arka_plan']))
        kat1 = Rectangle()
        Color(*get_color_from_hex(RENKLER['arka_plan2']))
        kat2 = Rectangle()
        Color(*get_color_from_hex('#18122E'))
        kat3 = Rectangle()

    def _guncelle(*_):
        x, y = widget.pos
        w = widget.width if widget.width > 1 else Window.width
        h = widget.height if widget.height > 1 else Window.height
        kat1.pos = (x, y)
        kat1.size = (w, h)
        kat2.pos = (x, y + h * 0.35)
        kat2.size = (w, h * 0.65)
        kat3.pos = (x, y + h * 0.68)
        kat3.size = (w, h * 0.32)

    widget.bind(pos=_guncelle, size=_guncelle)
    Window.bind(size=lambda *_: _guncelle())
    Clock.schedule_once(lambda *_: _guncelle(), 0)
    return kat1, kat2, kat3


def gorsel_arkaplan_ekle(widget, dosya, opak=0.92):
    """PNG arka plan (menü alanı vb.)."""
    from kivy.graphics import Color, Rectangle

    yol = asset_yolu(dosya) if not os.path.isabs(dosya) else dosya
    if not yol or not os.path.isfile(yol):
        return None
    with widget.canvas.before:
        Color(1, 1, 1, opak)
        rect = Rectangle(source=yol)

    def _guncelle(*_):
        rect.pos = widget.pos
        rect.size = widget.size

    widget.bind(pos=_guncelle, size=_guncelle)
    Clock.schedule_once(lambda *_: _guncelle(), 0)
    return rect


def ekran_icerik_sar(screen, icerik):
    """Tam ekran opak zemin + içerik (beyaz boşlukları kapatır)."""
    from kivy.core.window import Window
    from kivy.graphics import Color, Rectangle
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.widget import Widget

    gradient_arka_plan_ekle(screen)

    kok = FloatLayout(size_hint=(1, 1))
    zemin = Widget(size_hint=(1, 1))
    with zemin.canvas:
        Color(*get_color_from_hex(RENKLER['arka_plan']))
        z_rect = Rectangle()

    def _zemin_guncelle(*_):
        z_rect.pos = (0, 0)
        z_rect.size = zemin.size

    zemin.bind(size=_zemin_guncelle, pos=_zemin_guncelle)
    Window.bind(size=lambda *_: Clock.schedule_once(lambda __: _zemin_guncelle(), 0))
    Clock.schedule_once(lambda *_: _zemin_guncelle(), 0)

    kok.add_widget(zemin)
    icerik.size_hint = (1, 1)
    kok.add_widget(icerik)
    screen.add_widget(kok)
    return kok


def mobil_ekran_sarmal(icerik_widget):
    """Safe area padding ile ekran sarmalayıcı."""
    from kivy.uix.boxlayout import BoxLayout

    sarmal = BoxLayout(
        orientation='vertical',
        padding=[dp(12), SAFE_UST, dp(12), SAFE_ALT],
    )
    sarmal.add_widget(icerik_widget)
    return sarmal


def ust_baslik_bar(baslik, geri_callback=None):
    """Tüm fal ekranları için ortak üst bar."""
    from kivy.uix.boxlayout import BoxLayout

    bar = BoxLayout(
        orientation='horizontal',
        size_hint_y=None,
        height=dp(52),
        spacing=dp(8),
        padding=[0, dp(4), 0, dp(4)],
    )
    if geri_callback:
        btn = tus_buton('geri', font_size='13sp', size_hint_x=0.3)
        btn.bind(on_press=lambda *_: geri_callback())
        bar.add_widget(btn)
    else:
        bar.add_widget(BoxLayout(size_hint_x=0.3))

    bar.add_widget(metin_label(
        baslik,
        font_size='17sp',
        bold=True,
        color=RENKLER['altin'],
        halign='center',
        size_hint_x=0.4,
    ))
    bar.add_widget(BoxLayout(size_hint_x=None, width=COIN_SAG_BOSLUK))
    return bar


class YukleniyorAnimasyon(Label):
    """FalımaBak yorumluyor — nabız animasyonlu gösterge."""

    def __init__(self, **kwargs):
        fontlari_yukle()
        super().__init__(
            text=yorum_bekle_metin(),
            font_name=FON_ADI,
            font_size='14sp',
            bold=True,
            color=get_color_from_hex(RENKLER['altin_yumusak']),
            halign='center',
            size_hint_y=None,
            height=dp(36),
            **kwargs,
        )
        self._anim = None
        Clock.schedule_once(lambda *_: self._baslat(), 0)

    def _baslat(self):
        self._anim = (
            Animation(opacity=0.4, duration=0.7)
            + Animation(opacity=1.0, duration=0.7)
        )
        self._anim.repeat = True
        self._anim.start(self)

    def durdur(self):
        if self._anim:
            self._anim.cancel(self)
            self.opacity = 1


def alt_nav_bar(aktif='anasayfa', on_sec=None):
    """Alt navigasyon: Ana Sayfa | Geçmiş | Ayarlar."""
    from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.behaviors import ButtonBehavior

    class NavBtn(ButtonBehavior, BoxLayout):
        def __init__(self, etiket, anahtar, secili=False, ikon='', **kw):
            super().__init__(orientation='vertical', **kw)
            self.anahtar = anahtar
            self.size_hint_x = 1 / 3
            self.size_hint_y = None
            self.height = dp(54)
            self.padding = [0, dp(4), 0, dp(2)]
            self.spacing = dp(2)
            renk = RENKLER['altin'] if secili else RENKLER['gri']
            nav_png = NAV_IKON_DOSYALARI.get(anahtar, '')
            nav_yol = asset_yolu(nav_png) if nav_png else ''
            if nav_yol and os.path.isfile(nav_yol):
                from kivy.uix.image import Image
                from kivy.uix.anchorlayout import AnchorLayout
                ikon_k = AnchorLayout(size_hint_y=None, height=dp(26))
                ikon_k.add_widget(Image(
                    source=nav_yol,
                    size_hint=(None, None),
                    size=(dp(24), dp(24)),
                    allow_stretch=False,
                    keep_ratio=True,
                ))
                self.add_widget(ikon_k)
            elif ikon:
                from kivy.uix.anchorlayout import AnchorLayout
                ikon_k = AnchorLayout(size_hint_y=None, height=dp(26))
                ikon_k.add_widget(metin_label(
                    EMOJI_YEDEK.get(ikon, ikon) if _android_mi() else ikon,
                    font_size='16sp', color=renk, halign='center',
                    size_hint=(None, None), size=(dp(24), dp(24)),
                ))
                self.add_widget(ikon_k)
            self.add_widget(metin_label(
                etiket,
                font_size='12sp',
                bold=secili,
                color=renk,
                halign='center',
                size_hint_y=None,
                height=dp(18),
            ))
            if secili:
                gold = get_color_from_hex(RENKLER['altin'])
                with self.canvas.after:
                    Color(gold[0], gold[1], gold[2], 0.8)
                    self._cizgi = RoundedRectangle(radius=[dp(1)])
                self.bind(pos=self._ciz, size=self._ciz)
                Clock.schedule_once(lambda *_: self._ciz(), 0)

        def _ciz(self, *_):
            if hasattr(self, '_cizgi'):
                self._cizgi.pos = (self.center_x - dp(16), self.y + dp(2))
                self._cizgi.size = (dp(32), dp(3))

        def on_release(self):
            if on_sec:
                on_sec(self.anahtar)

    nav = BoxLayout(
        orientation='horizontal',
        size_hint_y=None,
        height=dp(62),
        padding=[dp(10), dp(4), dp(10), SAFE_ALT],
        spacing=dp(6),
    )
    gold = get_color_from_hex(RENKLER['altin'])
    mor = get_color_from_hex(RENKLER['mor_parlak'])
    nav_bg = get_color_from_hex('#120E28')
    nav_bg2 = get_color_from_hex(RENKLER['kart_arka_cam'])
    with nav.canvas.before:
        Color(0, 0, 0, 0.55)
        nav._golge = Rectangle()
        Color(nav_bg[0], nav_bg[1], nav_bg[2], 1)
        nav._bg = Rectangle()
        Color(nav_bg2[0], nav_bg2[1], nav_bg2[2], 1)
        nav._bg2 = Rectangle()
        Color(gold[0], gold[1], gold[2], 0.55)
        nav._ust = Line(width=dp(1.5))
        Color(mor[0], mor[1], mor[2], 0.15)
        nav._alt = Line(width=dp(1))

    def _nav_ciz(*_):
        nav._golge.pos = (nav.x, nav.y - dp(2))
        nav._golge.size = (nav.width, nav.height + dp(2))
        nav._bg.pos = nav.pos
        nav._bg.size = nav.size
        nav._bg2.pos = nav.pos
        nav._bg2.size = nav.size
        nav._ust.points = [nav.x, nav.top, nav.right, nav.top]
        nav._alt.points = [nav.x, nav.y + dp(1), nav.right, nav.y + dp(1)]

    nav.bind(pos=_nav_ciz, size=_nav_ciz)
    Clock.schedule_once(lambda *_: _nav_ciz(), 0)

    from dil import t
    nav.add_widget(NavBtn(t('nav_home'), 'anasayfa', secili=aktif == 'anasayfa', ikon='🏠'))
    nav.add_widget(NavBtn(t('nav_history'), 'gecmis', secili=aktif == 'gecmis', ikon='📜'))
    nav.add_widget(NavBtn(t('nav_settings'), 'ayarlar', secili=aktif == 'ayarlar', ikon='⚙️'))
    return nav


def kart_zemin_bagla(widget, renk_hex=None, radius=12):
    """Kart canvas arka planını güvenli şekilde widget'a bağlar."""
    from kivy.graphics import Color, RoundedRectangle

    renk = renk_hex or RENKLER['kart_arka']
    r = dp(radius)
    with widget.canvas.before:
        Color(*get_color_from_hex(renk))
        rect = RoundedRectangle(radius=[r])

    def _ciz(inst=None, *_):
        hedef = inst if inst is not None else widget
        if not hasattr(hedef, 'pos'):
            return
        rect.pos = hedef.pos
        rect.size = hedef.size

    widget.bind(pos=lambda inst, *a: _ciz(inst), size=lambda inst, *a: _ciz(inst))
    Clock.schedule_once(lambda dt: _ciz(), 0)
    return rect


def asset_yolu(dosya):
    return os.path.join(ASSETS_DIR, dosya)