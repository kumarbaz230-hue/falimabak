"""
🎴 Tarot Falı — interaktif kart seçimi
Kapalı kartlara dokun → çevir → yorum al
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.cache import Cache
import random
import os
import re
import unicodedata

from theme import (
    RENKLER, tus_metin, fontlari_yukle, metin_label, ASSETS_DIR,
    tus_buton, baslik_satir, buton_metin_guncelle, yorum_bekle_markup, yorum_sonuc_metni,
    kaydirici_metin, SAFE_UST, SAFE_ALT, ekran_icerik_sar, yorum_panel_baslik,
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

DESTE_GOSTER = 9


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
            gorsel_yolu = os.path.normpath(os.path.join(ASSETS_DIR, base + ext))
            if os.path.exists(gorsel_yolu):
                return gorsel_yolu
    if os.path.exists(CARD_BACK):
        return CARD_BACK
    return CARD_BACK


def cache_temizle():
    try:
        Cache.remove('kv.image')
        Cache.remove('kv.texture')
    except Exception:
        pass


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

POZ_MAP = {
    1: ['✨ Kart'],
    3: ['🌅 Geçmiş', '🌞 Şimdi', '🌠 Gelecek'],
    5: ['🌅 Geçmiş', '🌞 Şimdi', '🌠 Gelecek', '💫 Etkiler', '🌟 Umut'],
}


class TiklanabilirKart(ButtonBehavior, RelativeLayout):
    """Kapalı tarot kartı — dokununca çevrilir."""

    def __init__(self, kart, durum, tikla_cb, genislik=None, **kwargs):
        super().__init__(
            size_hint=(None, 1),
            width=genislik or dp(74),
            **kwargs,
        )
        self.kart = kart
        self.durum = durum
        self.tikla_cb = tikla_cb
        self.acik = False
        self.secildi = False

        arka = CARD_BACK if os.path.exists(CARD_BACK) else ''
        on = kart_gorsel_yolu(kart['isim'])

        self._arka = Image(source=arka, size_hint=(1, 1), fit_mode='fill')
        self._on = Image(source=on, size_hint=(1, 1), fit_mode='fill', opacity=0)
        if durum == 'Ters':
            self._on.angle = 180

        self.add_widget(self._arka)
        self.add_widget(self._on)

    def on_press(self):
        if self.secildi or self.acik or self.disabled:
            return
        self.tikla_cb(self)

    def cevir(self, bitti=None):
        if self.acik:
            return
        self.acik = True
        self.secildi = True
        anim_arka = Animation(opacity=0, duration=0.2)
        anim_on = Animation(opacity=1, duration=0.2)

        def _on_goster(*_):
            anim_on.start(self._on)
            if bitti:
                Clock.schedule_once(lambda *_: bitti(), 0.22)

        anim_arka.bind(on_complete=lambda *_: _on_goster())
        anim_arka.start(self._arka)

    def pasif_yap(self):
        self.disabled = True
        Animation(opacity=0.35, duration=0.15).start(self)


class TarotScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.secilen = []
        self.kart_adet = 3
        self._calisiyor = False
        self._mod = 'secim'
        self._deste_veri = []
        self._kart_widgetlari = []
        Clock.schedule_once(lambda *_: self.kur(), 0)

    def kur(self):
        ana = BoxLayout(
            orientation='vertical',
            spacing=dp(4),
            padding=[dp(10), SAFE_UST, dp(10), SAFE_ALT],
        )

        ana.add_widget(baslik_satir('🃏', 'TAROT FALI', font_size='20sp', height=dp(32)))

        btsatir = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            spacing=dp(8),
        )
        gb = tus_buton('geri', font_size='13sp', size_hint_x=0.28)
        gb.bind(on_press=lambda *_: setattr(self.manager, 'current', 'anasayfa'))
        btsatir.add_widget(gb)

        self.adet_btn = tus_buton('kart_adet', font_size='13sp', altin_yazi=True, size_hint_x=0.34)
        buton_metin_guncelle(self.adet_btn, f'{self.kart_adet} Kart')
        self.adet_btn.bind(on_press=self.adet_degistir)
        btsatir.add_widget(self.adet_btn)

        self.fal_btn = tus_buton('tekrar', font_size='13sp', size_hint_x=0.38)
        self.fal_btn.bind(on_press=self._yeni_desteye_basla)
        self.fal_btn.disabled = True
        btsatir.add_widget(self.fal_btn)
        ana.add_widget(btsatir)

        self._durum = metin_label(
            '', font_size='12sp', color=RENKLER['altin_parlak'],
            halign='center', size_hint_y=None, height=dp(22),
        )
        ana.add_widget(self._durum)

        self.deste_scroll = ScrollView(
            size_hint_y=None,
            height=dp(158),
            do_scroll_x=True,
            do_scroll_y=False,
            bar_width=0,
        )
        self.deste_satir = BoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            spacing=dp(8),
            padding=[dp(6), dp(4)],
        )
        self.deste_satir.bind(minimum_width=self.deste_satir.setter('width'))
        self.deste_scroll.add_widget(self.deste_satir)
        ana.add_widget(self.deste_scroll)

        self.kart_satir = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(0),
            spacing=dp(8),
        )
        ana.add_widget(self.kart_satir)

        self.poz_satir = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(0),
            spacing=dp(8),
        )
        ana.add_widget(self.poz_satir)

        self.isim_satir = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(0),
            spacing=dp(4),
        )
        ana.add_widget(self.isim_satir)

        ana.add_widget(yorum_panel_baslik('Tarot yorumunuz'))
        self.yorum_alani, self.yorum_label = kaydirici_metin(1)
        self.yorum_label.halign = 'left'
        ana.add_widget(self.yorum_alani)

        ekran_icerik_sar(self, ana)
        self._yeni_desteye_basla()

    def _talimat_metni(self):
        return (
            f'[b][color={RENKLER["altin"]}]Kapalı kartlara dokunun[/color][/b]\n'
            f'[color={RENKLER["gri_acik"]}]Üstten {self.kart_adet} kart seçin. '
            f'Seçtiğiniz kartlar döner, ardından yorumunuz hazırlanır.[/color]'
        )

    def _durum_guncelle(self):
        n = len(self.secilen)
        if self._mod == 'secim':
            self._durum.text = f'{n} / {self.kart_adet} kart seçildi'
        elif self._mod == 'yorum':
            self._durum.text = 'Kartlarınız açıldı ✦'

    def _yeni_desteye_basla(self, *_):
        if self._calisiyor:
            return
        cache_temizle()
        self._mod = 'secim'
        self.secilen = []
        self._calisiyor = False
        self.fal_btn.disabled = True
        buton_metin_guncelle(self.adet_btn, f'{self.kart_adet} Kart')
        self.adet_btn.disabled = False

        self.kart_satir.height = dp(0)
        self.kart_satir.clear_widgets()
        self.poz_satir.height = dp(0)
        self.poz_satir.clear_widgets()
        self.isim_satir.height = dp(0)
        self.isim_satir.clear_widgets()

        self.deste_scroll.opacity = 1
        self.deste_scroll.disabled = False
        self.deste_scroll.height = dp(158)

        self.yorum_label.markup = True
        self.yorum_label.text = self._talimat_metni()
        self._deste_hazirla()
        self._deste_goster()
        self._durum_guncelle()

    def _deste_hazirla(self):
        havuz = random.sample(TUM_KARTLAR, min(DESTE_GOSTER, len(TUM_KARTLAR)))
        self._deste_veri = [(k, random.choice(['Düz', 'Ters'])) for k in havuz]

    def _deste_goster(self):
        self.deste_satir.clear_widgets()
        self._kart_widgetlari = []
        for kart, durum in self._deste_veri:
            w = TiklanabilirKart(kart, durum, self._kart_tiklandi)
            self._kart_widgetlari.append(w)
            self.deste_satir.add_widget(w)

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

        self.secilen.append((widget.kart, widget.durum))

        def _devam():
            self._durum_guncelle()
            if len(self.secilen) >= self.kart_adet:
                self._secim_tamam()

        widget.cevir(bitti=_devam)

    def _secim_tamam(self):
        self._calisiyor = True
        self.adet_btn.disabled = True
        for w in self._kart_widgetlari:
            if not w.secildi:
                w.pasif_yap()

        Clock.schedule_once(lambda *_: self._yorum_baslat(), 0.35)

    def _yorum_baslat(self):
        from fal_limit import yorum_baslat
        yorum_baslat('tarot', self._fal_ac_devam)

    def _fal_ac_devam(self):
        self._mod = 'yorum'
        self._secilen_satirlari_goster()
        Animation(height=0, opacity=0, duration=0.25).start(self.deste_scroll)
        self._yorumu_goster()
        self._ai_tarot_yorum()
        self.fal_btn.disabled = False
        buton_metin_guncelle(self.fal_btn, tus_metin('tekrar'))
        self._calisiyor = False
        self._durum_guncelle()

    def _secilen_satirlari_goster(self):
        adet = len(self.secilen)
        pay = 1.0 / max(adet, 1)

        self.kart_satir.height = dp(118)
        self.kart_satir.clear_widgets()
        for kart, durum in self.secilen:
            img = Image(
                source=kart_gorsel_yolu(kart['isim']),
                size_hint=(pay, 1),
                fit_mode='fill',
                angle=180 if durum == 'Ters' else 0,
            )
            self.kart_satir.add_widget(img)

        etiketler = POZ_MAP.get(self.kart_adet, [f'Kart {i + 1}' for i in range(adet)])
        self.poz_satir.height = dp(20)
        self.poz_satir.clear_widgets()
        for i in range(adet):
            e = etiketler[i] if i < len(etiketler) else f'Kart {i + 1}'
            self.poz_satir.add_widget(
                metin_label(e, font_size='9sp', color=RENKLER['altin_parlak'], halign='center')
            )

        self.isim_satir.height = dp(32)
        self.isim_satir.clear_widgets()
        for kart, durum in self.secilen:
            s = '🔴' if durum == 'Ters' else '🟢'
            c = RENKLER['kirmizi_acik'] if durum == 'Ters' else RENKLER['yesil_parlak']
            self.isim_satir.add_widget(metin_label(
                f'{s} {kart["isim"]}\n{durum}',
                font_size='7sp', bold=True, color=c, halign='center',
            ))

    def _yorumu_goster(self):
        y = f"[b][color={RENKLER['altin']}]🃏  TAROT YORUMUNUZ  🃏[/color][/b]\n\n"
        et = POZ_MAP.get(self.kart_adet, [f'Kart {i + 1}' for i in range(self.kart_adet)])
        for i, (kart, durum) in enumerate(self.secilen):
            p = et[i] if i < len(et) else f'Kart {i + 1}'
            a = kart['ters'] if durum == 'Ters' else kart['anlam']
            c = RENKLER['yesil_parlak'] if durum == 'Düz' else RENKLER['kirmizi_acik']
            y += f"[b][color={RENKLER['mor_parlak']}]{p}:[/color][/b] {kart['sembol']} [b]{kart['isim']}[/b] "
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
        et = POZ_MAP.get(self.kart_adet, [f'Kart {i + 1}' for i in range(self.kart_adet)])
        kartlar = []
        for i, (kart, durum) in enumerate(self.secilen):
            p = et[i] if i < len(et) else f'Kart {i + 1}'
            anlam = kart['ters'] if durum == 'Ters' else kart['anlam']
            kartlar.append({
                'pozisyon': p,
                'isim': kart['isim'],
                'durum': durum,
                'anlam': anlam,
            })

        self.yorum_label.text = self._son_temel_yorum + f"\n\n{yorum_bekle_markup()}"

        def _bitir(metin, ai_kullanildi, hata, kaynak=None, fotograf=False):
            self.yorum_label.text = (
                yorum_sonuc_metni(
                    self._son_temel_yorum, metin, ai_kullanildi, hata, kaynak, fotograf,
                )
                + f"\n\n[color={RENKLER['gri']}]Siz {self.kart_adet} kart seçtiniz[/color]"
            )

        yorum_al('tarot', {'kartlar': kartlar}, _bitir, coin_dahil=False)
