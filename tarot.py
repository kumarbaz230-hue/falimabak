"""
🎴 Tarot Falı — interaktif kart seçimi (grid + üst slot)
Kapalı kartlara dokun → çevir → yorum al
"""

import random
import os
import re
import traceback
import unicodedata

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.behaviors import ButtonBehavior
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp

from theme import (
    RENKLER, tus_metin, fontlari_yukle, metin_label, ASSETS_DIR,
    tus_buton, baslik_satir, buton_metin_guncelle, yorum_bekle_markup, yorum_sonuc_metni,
    kaydirici_metin, SAFE_UST, SAFE_ALT, ekran_icerik_sar, siyah_buton,
)
from ai_yorum import yorum_al

fontlari_yukle()

TR_MAP = str.maketrans({
    'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c',
    'İ': 'i', 'I': 'i', 'Ğ': 'g', 'Ü': 'u', 'Ş': 's', 'Ö': 'o', 'Ç': 'c',
})
_ALIASES = {
    'kilic_ikili': ('kilic_i_kili', 'kilic_2', 'swords_two'),
    'kilic_uclu': ('kilic_uclu', 'kilic_3', 'swords_three'),
}

GRID_COLS = 4
DESTE_GOSTER = 12
GRID_SATIR = (DESTE_GOSTER + GRID_COLS - 1) // GRID_COLS
MIN_DESTE_YUK = dp(108 * GRID_SATIR + 6 * (GRID_SATIR - 1) + 8)

POZ_MAP = {
    1: ['Kart'],
    3: ['Geçmiş', 'Şimdiki', 'Gelecek'],
    5: ['Geçmiş', 'Şimdiki', 'Gelecek', 'Etkiler', 'Umut'],
}

POZ_EMOJI = {
    1: ['✨'],
    3: ['🌅', '🌞', '🌠'],
    5: ['🌅', '🌞', '🌠', '💫', '🌟'],
}


def sanitize(adi):
    s = adi.strip().lower().replace('ı', 'i')
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.translate(TR_MAP)
    s = re.sub(r'[^a-z0-9]+', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return s


def _dosya_adaylari(kart_adi):
    base = sanitize(kart_adi)
    adaylar = [base]
    for ana, ekler in _ALIASES.items():
        if base == ana or base in ekler:
            adaylar = [ana, base, *ekler]
            break
    gordu = set()
    sonuc = []
    for ad in adaylar:
        if ad and ad not in gordu:
            gordu.add(ad)
            sonuc.append(ad)
    return sonuc


CARD_BACK = os.path.normpath(os.path.join(ASSETS_DIR, 'card_back.png'))


def kart_gorsel_yolu(kart_adi):
    for base in _dosya_adaylari(kart_adi):
        for ext in ('.png', '.jpg', '.jpeg', '.webp'):
            yol = os.path.normpath(os.path.join(ASSETS_DIR, base + ext))
            if os.path.isfile(yol):
                return yol
    return CARD_BACK if os.path.isfile(CARD_BACK) else ''


def krt(s, e, a, t):
    return {'isim': s, 'sembol': e, 'anlam': a, 'ters': t}


M = [
    ('Soytarı', '🎭', 'Macera, özgürlük', 'Saflık'), ('Büyücü', '🧙', 'Yaratıcılık', 'Manipülasyon'),
    ('Yüksek Rahibe', '🔮', 'Sezgi, gizem', 'Sır saklama'), ('İmparatoriçe', '👸', 'Bereket, annelik', 'Bağımlılık'),
    ('İmparator', '🤴', 'Otorite, disiplin', 'Zorbalık'), ('Aziz', '🙏', 'Bilgelik, gelenek', 'Dogmatizm'),
    ('Aşıklar', '💑', 'Aşk, uyum', 'Uyumsuzluk'), ('Savaş Arabası', '🏎️', 'Zafer, kontrol', 'Kontrol kaybı'),
    ('Güç', '🦁', 'Cesaret, içsel güç', 'Güçsüzlük'), ('Azize', '🧘', 'İç huzur, bilgelik', 'İzolasyon'),
    ('Şans Çarkı', '🎡', 'Kader, şans', 'Engeller'), ('Adalet', '⚖️', 'Adalet, denge', 'Adaletsizlik'),
    ('Asılmış Adam', '🙃', 'Fedakarlık, bekleyiş', 'Direnç'), ('Ölüm', '💀', 'Dönüşüm, yeniden doğuş', 'Değişime direnç'),
    ('Denge', '⚖️', 'Denge, uyum', 'Dengesizlik'), ('Şeytan', '😈', 'Bağımlılık, kısıtlama', 'Özgürleşme'),
    ('Kule', '🗼', 'Yıkım, ani değişim', 'Kaçış'), ('Yıldız', '⭐', 'Umut, ilham', 'Umutsuzluk'),
    ('Ay', '🌙', 'Sezgi, gizem, korkular', 'Aydınlanma'), ('Güneş', '☀️', 'Mutluluk, başarı', 'Geçici'),
    ('Yargı', '📯', 'Uyanış, yeniden doğuş', 'Şüphe'), ('Dünya', '🌍', 'Tamamlanma, başarı', 'Eksiklik'),
]
MAJOR = [krt(*x) for x in M]
WANDS = [krt(f'Değnek {s}', e, a, t) for s, e, a, t in [
    ('Ası', '🔥', 'Başlangıç', 'Ertelenme'), ('İkili', '2️⃣', 'Planlama', 'Kötü plan'), ('Üçlü', '3️⃣', 'İlerleme', 'Engel'),
    ('Dörtlü', '4️⃣', 'Kutlama', 'Geçici'), ('Beşli', '5️⃣', 'Mücadele', 'Kaçış'), ('Altılı', '6️⃣', 'Zafer', 'Kibir'),
    ('Yedili', '7️⃣', 'Cesaret', 'Bunaltı'), ('Sekizli', '8️⃣', 'Haber', 'Gecikme'), ('Dokuzlu', '9️⃣', 'Azim', 'Tükenmişlik'),
    ('Onlu', '🔟', 'Yük', 'Kurtulma'), ('Vale', '🤵', 'Keşif', 'Deneyimsiz'), ('Şövalye', '🏇', 'Tutku', 'Acele'),
    ('Kraliçe', '👑', 'Cesaret', 'Kıskançlık'), ('Kral', '👑', 'Liderlik', 'Zorbalık')]]
CUPS = [krt(f'Kupa {s}', e, a, t) for s, e, a, t in [
    ('Ası', '💧', 'Aşk başlangıç', 'Boşluk'), ('İkili', '2️⃣', 'İlişki', 'Ayrılık'), ('Üçlü', '3️⃣', 'Kutlama', 'Yalnızlık'),
    ('Dörtlü', '4️⃣', 'Düşünce', 'Uyanış'), ('Beşli', '5️⃣', 'Kayıp', 'Kabul'), ('Altılı', '6️⃣', 'Anılar', 'Takılma'),
    ('Yedili', '7️⃣', 'Hayaller', 'Odak'), ('Sekizli', '8️⃣', 'Kaçış', 'Korku'), ('Dokuzlu', '9️⃣', 'Bolluk', 'Tatminsizlik'),
    ('Onlu', '🔟', 'Mutluluk', 'Kavga'), ('Vale', '🤵', 'Haber', 'Olgunlaşmamış'), ('Şövalye', '🏇', 'Teklif', 'H kırıklığı'),
    ('Kraliçe', '👑', 'Şefkat', 'Kırılganlık'), ('Kral', '👑', 'Olgunluk', 'Baskı')]]
SWORDS = [krt(f'Kılıç {s}', e, a, t) for s, e, a, t in [
    ('Ası', '⚔️', 'Netlik', 'Karışıklık'), ('İkili', '2️⃣', 'İkilem', 'Kararsızlık'), ('Üçlü', '3️⃣', 'Acı', 'İyileşme'),
    ('Dörtlü', '4️⃣', 'Dinlenme', 'Tükenmişlik'), ('Beşli', '5️⃣', 'Çatışma', 'Uzlaşma'), ('Altılı', '6️⃣', 'Geçiş', 'Takılma'),
    ('Yedili', '7️⃣', 'Kurnazlık', 'Vicdan'), ('Sekizli', '8️⃣', 'Korku', 'Özgürleşme'), ('Dokuzlu', '9️⃣', 'Kaygı', 'Umut'),
    ('Onlu', '🔟', 'Çöküş', 'İyileşme'), ('Vale', '🤵', 'Fikir', 'Dedikodu'), ('Şövalye', '🏇', 'Hız', 'Acele'),
    ('Kraliçe', '👑', 'İletişim', 'Soğukluk'), ('Kral', '👑', 'Adalet', 'Zorbalık')]]
PENTS = [krt(f'Tılsım {s}', e, a, t) for s, e, a, t in [
    ('Ası', '💎', 'Fırsat', 'Kaçan'), ('İkili', '2️⃣', 'Denge', 'Dengesizlik'), ('Üçlü', '3️⃣', 'Beceri', 'Yetersizlik'),
    ('Dörtlü', '4️⃣', 'Birikim', 'Cimrilik'), ('Beşli', '5️⃣', 'Zorluk', 'Yardım'), ('Altılı', '6️⃣', 'Paylaşım', 'Borç'),
    ('Yedili', '7️⃣', 'Sabır', 'Sabırsızlık'), ('Sekizli', '8️⃣', 'Çalışma', 'Mükemmeliyetçi'), ('Dokuzlu', '9️⃣', 'Lüks', 'Harcama'),
    ('Onlu', '🔟', 'Miras', 'Kavga'), ('Vale', '🤵', 'Çalışkan', 'Tembellik'), ('Şövalye', '🏇', 'Azim', 'Durgunluk'),
    ('Kraliçe', '👑', 'Bereket', 'İhmal'), ('Kral', '👑', 'Başarı', 'Açgözlülük')]]
TUM_KARTLAR = MAJOR + WANDS + CUPS + SWORDS + PENTS


class SecilenSlot(BoxLayout):
    """Üstte seçilen kart slotu — Geçmiş / Şimdiki / Gelecek."""

    def __init__(self, pozisyon='', **kwargs):
        super().__init__(orientation='vertical', size_hint_x=1, spacing=dp(2), **kwargs)
        arka = CARD_BACK if os.path.isfile(CARD_BACK) else ''
        self._img = Image(
            source=arka,
            size_hint_y=None,
            height=dp(92),
            fit_mode='fill',
            opacity=0.35,
        )
        self._poz = metin_label(
            pozisyon, font_size='10sp', color=RENKLER['gri_acik'],
            halign='center', size_hint_y=None, height=dp(16),
        )
        self._isim = metin_label(
            '—', font_size='11sp', bold=True, color=RENKLER['altin'],
            halign='center', size_hint_y=None, height=dp(18),
        )
        self.add_widget(self._img)
        self.add_widget(self._poz)
        self.add_widget(self._isim)

    def bosalt(self):
        arka = CARD_BACK if os.path.isfile(CARD_BACK) else ''
        self._img.source = arka
        self._img.opacity = 0.35
        self._isim.text = '—'

    def doldur(self, kart, durum):
        yol = kart_gorsel_yolu(kart['isim'])
        if yol:
            self._img.source = yol
        self._img.opacity = 1.0
        ad = kart['isim']
        if durum == 'Ters':
            ad = f'{ad} (Ters)'
        self._isim.text = ad


class TiklanabilirKart(ButtonBehavior, RelativeLayout):
    """Griddeki kapalı kart — dokununca çevrilir (angle kullanılmaz, Android güvenli)."""

    def __init__(self, kart, durum, tikla_cb, **kwargs):
        super().__init__(
            size_hint_y=None,
            height=dp(108),
            **kwargs,
        )
        self.kart = kart
        self.durum = durum
        self.tikla_cb = tikla_cb
        self.acik = False
        self.secildi = False

        arka = CARD_BACK if os.path.isfile(CARD_BACK) else ''
        on_yol = kart_gorsel_yolu(kart['isim']) or arka

        self._arka = Image(source=arka or on_yol, size_hint=(1, 1), fit_mode='fill')
        self._on = Image(source=on_yol, size_hint=(1, 1), fit_mode='fill', opacity=0)

        self._band = metin_label(
            '', font_size='9sp', bold=True, color=RENKLER['beyaz'],
            halign='center', size_hint=(1, None), height=dp(22),
            pos_hint={'x': 0, 'y': 0},
        )
        self._band.opacity = 0

        self.add_widget(self._arka)
        self.add_widget(self._on)
        self.add_widget(self._band)

    def on_press(self):
        if self.secildi or self.acik or self.disabled:
            return
        try:
            self.tikla_cb(self)
        except Exception:
            print(traceback.format_exc(), flush=True)

    def cevir(self, bitti=None):
        if self.acik:
            return
        self.acik = True
        self.secildi = True

        etiket = self.kart['isim']
        if self.durum == 'Ters':
            etiket = f'{etiket} · Ters'
        self._band.text = etiket

        def _flip_done(*_):
            self._on.opacity = 1
            self._arka.opacity = 0
            self._band.opacity = 0.92
            if bitti:
                Clock.schedule_once(lambda *_: bitti(), 0.05)

        Animation(opacity=0, duration=0.18).start(self._arka)
        Clock.schedule_once(lambda *_: _flip_done(), 0.18)

    def pasif_yap(self):
        if self.secildi:
            return
        self.disabled = True
        self.opacity = 0.38


class TarotScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.secilen = []
        self.kart_adet = 3
        self._calisiyor = False
        self._mod = 'secim'
        self._deste_veri = []
        self._kart_widgetlari = []
        self._slotlar = []
        self._kuruldu = False
        self._deste_yukseklik_bagli = False
        self._secim_ekranda = False
        self._yorum_ekranda = False
        self._disardan_donulecek = False
        Clock.schedule_once(lambda *_: self.kur(), 0)

    def kur(self):
        self.ana = BoxLayout(
            orientation='vertical',
            spacing=dp(4),
            padding=[dp(10), SAFE_UST, dp(10), SAFE_ALT],
        )
        ana = self.ana

        ana.add_widget(baslik_satir('🃏', 'TAROT FALI', font_size='20sp', height=dp(32)))

        self._alt_baslik = metin_label(
            '', font_size='12sp', color=RENKLER['gri_acik'],
            halign='center', size_hint_y=None, height=dp(22),
        )
        ana.add_widget(self._alt_baslik)

        btsatir = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8),
        )
        gb = tus_buton('geri', font_size='13sp', size_hint_x=0.28, height=dp(48))
        self.geri_btn = gb
        gb.bind(on_press=self._geri_bas)
        btsatir.add_widget(gb)

        self.adet_btn = tus_buton(
            'kart_adet', font_size='13sp', altin_yazi=True,
            size_hint_x=0.34, height=dp(48),
        )
        buton_metin_guncelle(self.adet_btn, f'{self.kart_adet} Kart')
        self.adet_btn.bind(on_press=self.adet_degistir)
        btsatir.add_widget(self.adet_btn)

        self.fal_btn = tus_buton('tekrar', font_size='13sp', size_hint_x=0.38, height=dp(48))
        self.fal_btn.bind(on_press=self._yeni_desteye_basla)
        self.fal_btn.disabled = True
        btsatir.add_widget(self.fal_btn)
        ana.add_widget(btsatir)

        self._slot_satir = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(132),
            spacing=dp(8),
            padding=[dp(4), dp(4)],
        )
        ana.add_widget(self._slot_satir)

        self._secim_blok = BoxLayout(
            orientation='vertical',
            spacing=dp(4),
            size_hint_y=1,
        )
        self._durum = metin_label(
            '', font_size='12sp', color=RENKLER['altin_parlak'],
            halign='center', size_hint_y=None, height=dp(20),
            markup=True,
        )
        self._secim_blok.add_widget(self._durum)

        self.deste_grid = GridLayout(
            cols=GRID_COLS,
            spacing=dp(6),
            padding=[dp(2), dp(4)],
            size_hint_y=None,
        )
        self._deste_yukseklik_bagla()
        self._deste_scroll = ScrollView(
            size_hint_y=1,
            do_scroll_x=False,
            bar_width=0,
        )
        self._deste_scroll.add_widget(self.deste_grid)
        self._secim_blok.add_widget(self._deste_scroll)

        self._yorum_blok = BoxLayout(
            orientation='vertical',
            spacing=dp(4),
            size_hint_y=1,
        )
        yorum_ust = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8),
        )
        yorum_ust.add_widget(metin_label(
            'Tarot yorumunuz', font_size='11sp', bold=True,
            color=RENKLER['altin_parlak'], halign='left', size_hint_x=1,
        ))
        self._ana_sayfa_btn = siyah_buton(
            'Ana Sayfa', font_size='12sp', size_hint_x=0.34, height=dp(36),
        )
        self._ana_sayfa_btn.bind(on_press=self._ana_sayfaya_git)
        yorum_ust.add_widget(self._ana_sayfa_btn)
        self._yorum_blok.add_widget(yorum_ust)
        self.yorum_alani, self.yorum_label = kaydirici_metin(1)
        self.yorum_label.halign = 'left'
        self._yorum_blok.add_widget(self.yorum_alani)

        ana.add_widget(self._secim_blok)
        self._secim_ekranda = True

        ekran_icerik_sar(self, ana)
        self._kuruldu = True
        self._yeni_desteye_basla()

    def _deste_yukseklik_ayarla(self, grid, minimum_height, *_):
        grid.height = max(minimum_height, MIN_DESTE_YUK)

    def _deste_yukseklik_bagla(self):
        if not self._deste_yukseklik_bagli:
            self.deste_grid.bind(minimum_height=self._deste_yukseklik_ayarla)
            self._deste_yukseklik_bagli = True

    def _deste_yukseklik_coz(self):
        if self._deste_yukseklik_bagli:
            self.deste_grid.unbind(minimum_height=self._deste_yukseklik_ayarla)
            self._deste_yukseklik_bagli = False

    def _alt_baslik_guncelle(self):
        self._alt_baslik.text = (
            f'Yolunuzu aydınlatmak için {self.kart_adet} kart seçin'
        )

    def _slotlari_kur(self):
        self._slot_satir.clear_widgets()
        self._slotlar = []
        pozlar = POZ_MAP.get(self.kart_adet, [f'Kart {i + 1}' for i in range(self.kart_adet)])
        for i in range(self.kart_adet):
            poz = pozlar[i] if i < len(pozlar) else f'Kart {i + 1}'
            slot = SecilenSlot(pozisyon=poz)
            self._slotlar.append(slot)
            self._slot_satir.add_widget(slot)

    def _durum_guncelle(self):
        n = len(self.secilen)
        if self._mod == 'secim':
            self._durum.text = f'{n} / {self.kart_adet} kart seçildi'
        else:
            self._durum.text = 'Yorumunuz hazırlanıyor…'

    def _deste_grid_gizle(self):
        self._deste_yukseklik_coz()
        for w in self._kart_widgetlari:
            w.disabled = True
        self.deste_grid.clear_widgets()
        self._kart_widgetlari = []
        self.deste_grid.height = 0
        self.deste_grid.disabled = True

    def _deste_grid_goster(self):
        self.deste_grid.disabled = False
        self._deste_yukseklik_bagla()
        self._deste_yukseklik_ayarla(self.deste_grid, self.deste_grid.minimum_height)

    def _ana_sayfaya_git(self, *_):
        if self._calisiyor or not self.manager:
            return
        self.manager.current = 'anasayfa'

    def _arayuz_modu_guncelle(self):
        if self._mod == 'yorum':
            buton_metin_guncelle(self.geri_btn, '← Deste')
            self.adet_btn.disabled = True
            self.adet_btn.opacity = 0
            self.fal_btn.disabled = self._calisiyor
        else:
            buton_metin_guncelle(self.geri_btn, tus_metin('geri'))
            buton_metin_guncelle(self.adet_btn, f'{self.kart_adet} Kart')
            self.adet_btn.disabled = self._calisiyor
            self.adet_btn.opacity = 1
            self.fal_btn.disabled = True

    def _geri_bas(self, *_):
        if self._calisiyor:
            return
        if self._mod == 'yorum':
            self._yeni_desteye_basla()
            return
        self._ana_sayfaya_git()

    def on_enter(self, *_):
        if not self._kuruldu or self._calisiyor:
            return
        if self._disardan_donulecek or self._mod == 'yorum':
            self._disardan_donulecek = False
            Clock.schedule_once(lambda *_: self._ekrana_don(), 0)

    def on_leave(self, *_):
        self._calisiyor = False
        self._disardan_donulecek = True

    def _ekrana_don(self):
        if self._calisiyor:
            return
        self._yeni_desteye_basla()
        Clock.schedule_once(lambda *_: self._layout_yenile(), 0.05)

    def _layout_yenile(self):
        self._deste_yukseklik_ayarla(self.deste_grid, self.deste_grid.minimum_height)

    def _icerik_modu_degistir(self, mod):
        if mod == 'secim':
            if self._yorum_ekranda and self._yorum_blok.parent is self.ana:
                self.ana.remove_widget(self._yorum_blok)
                self._yorum_ekranda = False
            if not self._secim_ekranda:
                self.ana.add_widget(self._secim_blok)
                self._secim_ekranda = True
        else:
            if self._secim_ekranda and self._secim_blok.parent is self.ana:
                self.ana.remove_widget(self._secim_blok)
                self._secim_ekranda = False
            if not self._yorum_ekranda:
                self.ana.add_widget(self._yorum_blok)
                self._yorum_ekranda = True

    def _secim_modu_goster(self):
        self._mod = 'secim'
        self._icerik_modu_degistir('secim')
        self._secim_blok.size_hint_y = 1
        self._durum.opacity = 1
        self._durum.height = dp(20)
        self._deste_grid_goster()
        self._alt_baslik_guncelle()
        self._arayuz_modu_guncelle()

    def _yorum_modu_goster(self):
        self._mod = 'yorum'
        self._deste_grid_gizle()
        self._icerik_modu_degistir('yorum')
        self._yorum_blok.size_hint_y = 1
        self._alt_baslik.text = 'Tarot yorumunuz'
        self._arayuz_modu_guncelle()

    def _yeni_desteye_basla(self, *_):
        if self._calisiyor:
            return
        self.secilen = []
        self._calisiyor = False
        self.fal_btn.disabled = True
        buton_metin_guncelle(self.adet_btn, f'{self.kart_adet} Kart')
        buton_metin_guncelle(self.fal_btn, tus_metin('tekrar'))
        self.adet_btn.disabled = False

        self._secim_modu_goster()
        self._slotlari_kur()
        self.yorum_label.markup = True
        self.yorum_label.text = ''
        self._deste_hazirla()
        self._deste_goster()
        self._durum_guncelle()

    def _deste_hazirla(self):
        havuz = random.sample(TUM_KARTLAR, min(DESTE_GOSTER, len(TUM_KARTLAR)))
        self._deste_veri = [(k, random.choice(['Düz', 'Ters'])) for k in havuz]

    def _deste_goster(self):
        self.deste_grid.clear_widgets()
        self._kart_widgetlari = []
        for kart, durum in self._deste_veri:
            w = TiklanabilirKart(kart, durum, self._kart_tiklandi)
            self._kart_widgetlari.append(w)
            self.deste_grid.add_widget(w)
        self._deste_yukseklik_ayarla(self.deste_grid, self.deste_grid.minimum_height)

    def adet_degistir(self, instance):
        if self._mod != 'secim' or self._calisiyor:
            return
        if self.kart_adet == 3:
            self.kart_adet = 5
        elif self.kart_adet == 5:
            self.kart_adet = 1
        else:
            self.kart_adet = 3
        buton_metin_guncelle(self.adet_btn, f'{self.kart_adet} Kart')
        self._yeni_desteye_basla()

    def _kart_tiklandi(self, widget):
        if self._mod != 'secim' or self._calisiyor:
            return
        if len(self.secilen) >= self.kart_adet:
            return

        idx = len(self.secilen)
        self.secilen.append((widget.kart, widget.durum))

        def _devam():
            try:
                if idx < len(self._slotlar):
                    self._slotlar[idx].doldur(widget.kart, widget.durum)
                self._durum_guncelle()
                if len(self.secilen) >= self.kart_adet:
                    self._secim_tamam()
            except Exception:
                print(traceback.format_exc(), flush=True)
                self._secim_hata()

        widget.cevir(bitti=_devam)

    def _secim_hata(self):
        self._calisiyor = False
        self._arayuz_modu_guncelle()
        if self._mod == 'yorum':
            self.yorum_label.text = (
                f'[color={RENKLER["kirmizi"]}]Bir hata oluştu. Tekrar deneyin.[/color]'
            )
        else:
            self._durum.text = (
                f'[color={RENKLER["kirmizi"]}]Bir hata oluştu. Tekrar deneyin.[/color]'
            )

    def _secim_tamam(self):
        if self._calisiyor:
            return
        self._calisiyor = True
        self._arayuz_modu_guncelle()
        for w in self._kart_widgetlari:
            if not w.secildi:
                w.pasif_yap()
        Clock.schedule_once(lambda *_: self._yorum_baslat(), 0.4)

    def _yorum_baslat(self):
        try:
            from fal_limit import fal_izinli, yorum_baslat
            if not fal_izinli('tarot'):
                self._coin_yok()
                return
            yorum_baslat('tarot', self._fal_ac_devam)
        except Exception:
            print(traceback.format_exc(), flush=True)
            self._secim_hata()

    def _coin_yok(self):
        self._calisiyor = False
        self._yorum_modu_goster()
        self.yorum_label.markup = True
        self.yorum_label.text = (
            f'[color={RENKLER["kirmizi"]}]Yorum için yeterli coin yok. '
            f'Ana sayfadan coin kazanabilirsiniz.[/color]'
        )
        self.fal_btn.disabled = False

    def _fal_ac_devam(self):
        try:
            self._yorum_modu_goster()
            self._yorumu_goster()
            self._ai_tarot_yorum()
            self.fal_btn.disabled = False
            buton_metin_guncelle(self.fal_btn, tus_metin('tekrar'))
            self._arayuz_modu_guncelle()
        except Exception:
            print(traceback.format_exc(), flush=True)
            self._secim_hata()
        finally:
            self._calisiyor = False

    def _yorumu_goster(self):
        em = POZ_EMOJI.get(self.kart_adet, ['✨'] * self.kart_adet)
        poz = POZ_MAP.get(self.kart_adet, [f'Kart {i + 1}' for i in range(self.kart_adet)])

        y = f"[b][color={RENKLER['altin']}]🃏  TAROT YORUMUNUZ  🃏[/color][/b]\n\n"
        for i, (kart, durum) in enumerate(self.secilen):
            p = poz[i] if i < len(poz) else f'Kart {i + 1}'
            e = em[i] if i < len(em) else '✨'
            a = kart['ters'] if durum == 'Ters' else kart['anlam']
            c = RENKLER['yesil_parlak'] if durum == 'Düz' else RENKLER['kirmizi_acik']
            y += f"[b][color={RENKLER['mor_parlak']}]{e} {p}:[/color][/b] [b]{kart['isim']}[/b] "
            y += f"[color={c}]({durum})[/color]\n[color={RENKLER['gri_acik']}]{a}[/color]\n\n"

        y += f"[color={RENKLER['altin']}]💫 Kart Mesajı:[/color]\n"
        y += f"[color={RENKLER['pembe_acik']}]{random.choice([
            'Hayatınızda önemli değişimlerin eşiğindesiniz. Sezgilerinize güvenin.',
            'Geçmişi bırakın, gelecek size gülümsüyor.',
            'Aşk ve para sizi bekliyor.',
            'İç sesinizi dinleyin.',
            'Kariyerinizde büyük bir sıçrama yapmaya hazır olun!',
            'Evren size işaretler gönderiyor.',
        ])}[/color]\n\n"
        y += f"[color={RENKLER['gri']}]📚 Siz {self.kart_adet} kart seçtiniz[/color]"
        self.yorum_label.markup = True
        self.yorum_label.text = y
        self._son_temel_yorum = y

    def _ai_tarot_yorum(self):
        poz = POZ_MAP.get(self.kart_adet, [f'Kart {i + 1}' for i in range(self.kart_adet)])
        kartlar = []
        for i, (kart, durum) in enumerate(self.secilen):
            p = poz[i] if i < len(poz) else f'Kart {i + 1}'
            anlam = kart['ters'] if durum == 'Ters' else kart['anlam']
            kartlar.append({
                'pozisyon': p,
                'isim': kart['isim'],
                'durum': durum,
                'anlam': anlam,
            })

        self.yorum_label.text = self._son_temel_yorum + f"\n\n{yorum_bekle_markup()}"

        def _bitir(metin, ai_kullanildi, hata, kaynak=None, fotograf=False):
            try:
                self.yorum_label.text = (
                    yorum_sonuc_metni(
                        self._son_temel_yorum, metin, ai_kullanildi, hata, kaynak, fotograf,
                    )
                    + f"\n\n[color={RENKLER['gri']}]Siz {self.kart_adet} kart seçtiniz[/color]"
                )
            except Exception:
                print(traceback.format_exc(), flush=True)

        yorum_al('tarot', {'kartlar': kartlar}, _bitir, coin_dahil=False)
