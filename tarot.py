"""
🎴 Tarot Falı - v10.0 (Saf BoxLayout, size_hint_x=0.33)
- .kv YOK, saf Python
- 3 kart: BoxLayout horizontal + size_hint_x=0.33
- fit_mode='fill' ile görsel sığdırma
- ScrollView + size_hint_y=None + minimum_height
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.cache import Cache
import random
import os
import re
import unicodedata

from theme import (
    RENKLER, FON_ADI, tus_metin, fontlari_yukle, metin_label, gradient_arka_plan_ekle, ASSETS_DIR,
    tus_buton, baslik_satir, buton_metin_guncelle, yorum_bekle_markup, yorum_sonuc_metni,
    kaydirici_metin, SAFE_UST, SAFE_ALT, ekran_icerik_sar,
)
from ai_yorum import yorum_al

fontlari_yukle()

# ============================================================
#  YARDIMCILAR
# ============================================================
TR_MAP = str.maketrans({
    'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c',
    'İ': 'i', 'I': 'i', 'Ğ': 'g', 'Ü': 'u', 'Ş': 's', 'Ö': 'o', 'Ç': 'c',
})
_ALIASES = {
    'kilic_ikili': ('kilic_i_kili', 'kilic_2', 'swords_two'),
    'kilic_uclu': ('kilic_uclu', 'kilic_3', 'swords_three'),
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


def _eksik_resim_log(gorsel_yolu, kart_adi=None):
    """Terminalde eksik resim detayını net şekilde göster."""
    print('--- EKSİK RESİM DETAYI ---', flush=True)
    if kart_adi:
        print(f'Kart Adı: {kart_adi}', flush=True)
    print(f'Aranan Dosya Yolu: {gorsel_yolu}', flush=True)
    print('--------------------------', flush=True)


def kart_gorsel_yolu(kart_adi):
    """Kart görsel yolunu döndürür; bulunamazsa card_back.png'e düşer (asla None dönmez)."""
    for base in _dosya_adaylari(kart_adi):
        for ext in ('.png', '.jpg', '.jpeg', '.webp'):
            gorsel_yolu = os.path.normpath(os.path.join(ASSETS_DIR, base + ext))
            if os.path.exists(gorsel_yolu):
                return gorsel_yolu

    gorsel_yolu = os.path.normpath(os.path.join(ASSETS_DIR, sanitize(kart_adi) + '.png'))

    if os.path.exists(CARD_BACK):
        _eksik_resim_log(gorsel_yolu, kart_adi=kart_adi)
        return CARD_BACK

    _eksik_resim_log(gorsel_yolu, kart_adi=kart_adi)
    print(f'UYARI: Kart arkası da yok -> {CARD_BACK}', flush=True)
    return CARD_BACK


def kart_resmi_bul(adi):
    """Geriye dönük uyumluluk."""
    return kart_gorsel_yolu(adi)

def cache_temizle():
    try: Cache.remove('kv.image'); Cache.remove('kv.texture')
    except: pass

# ============================================================
#  78 KART
# ============================================================
def krt(s,e,a,t): return {'isim':s,'sembol':e,'anlam':a,'ters':t}
M = [('Soytarı','🎭','Macera, özgürlük','Saflık'),('Büyücü','🧙','Yaratıcılık','Manipülasyon'),
     ('Yüksek Rahibe','🔮','Sezgi, gizem','Sır saklama'),('İmparatoriçe','👸','Bereket, annelik','Bağımlılık'),
     ('İmparator','🤴','Otorite, disiplin','Zorbalık'),('Aziz','🙏','Bilgelik, gelenek','Dogmatizm'),
     ('Aşıklar','💑','Aşk, uyum','Uyumsuzluk'),('Savaş Arabası','🏎️','Zafer, kontrol','Kontrol kaybı'),
     ('Güç','🦁','Cesaret, içsel güç','Güçsüzlük'),('Azize','🧘','İç huzur, bilgelik','İzolasyon'),
     ('Şans Çarkı','🎡','Kader, şans','Engeller'),('Adalet','⚖️','Adalet, denge','Adaletsizlik'),
     ('Asılmış Adam','🙃','Fedakarlık, bekleyiş','Direnç'),('Ölüm','💀','Dönüşüm, yeniden doğuş','Değişime direnç'),
     ('Denge','⚖️','Denge, uyum','Dengesizlik'),('Şeytan','😈','Bağımlılık, kısıtlama','Özgürleşme'),
     ('Kule','🗼','Yıkım, ani değişim','Kaçış'),('Yıldız','⭐','Umut, ilham','Umutsuzluk'),
     ('Ay','🌙','Sezgi, gizem, korkular','Aydınlanma'),('Güneş','☀️','Mutluluk, başarı','Geçici'),
     ('Yargı','📯','Uyanış, yeniden doğuş','Şüphe'),('Dünya','🌍','Tamamlanma, başarı','Eksiklik')]
MAJOR = [krt(*x) for x in M]
WANDS = [krt(f'Değnek {s}',e,a,t) for s,e,a,t in [
    ('Ası','🔥','Başlangıç','Ertelenme'),('İkili','2️⃣','Planlama','Kötü plan'),('Üçlü','3️⃣','İlerleme','Engel'),
    ('Dörtlü','4️⃣','Kutlama','Geçici'),('Beşli','5️⃣','Mücadele','Kaçış'),('Altılı','6️⃣','Zafer','Kibir'),
    ('Yedili','7️⃣','Cesaret','Bunaltı'),('Sekizli','8️⃣','Haber','Gecikme'),('Dokuzlu','9️⃣','Azim','Tükenmişlik'),
    ('Onlu','🔟','Yük','Kurtulma'),('Vale','🤵','Keşif','Deneyimsiz'),('Şövalye','🏇','Tutku','Acele'),
    ('Kraliçe','👑','Cesaret','Kıskançlık'),('Kral','👑','Liderlik','Zorbalık')]]
CUPS = [krt(f'Kupa {s}',e,a,t) for s,e,a,t in [
    ('Ası','💧','Aşk başlangıç','Boşluk'),('İkili','2️⃣','İlişki','Ayrılık'),('Üçlü','3️⃣','Kutlama','Yalnızlık'),
    ('Dörtlü','4️⃣','Düşünce','Uyanış'),('Beşli','5️⃣','Kayıp','Kabul'),('Altılı','6️⃣','Anılar','Takılma'),
    ('Yedili','7️⃣','Hayaller','Odak'),('Sekizli','8️⃣','Kaçış','Korku'),('Dokuzlu','9️⃣','Bolluk','Tatminsizlik'),
    ('Onlu','🔟','Mutluluk','Kavga'),('Vale','🤵','Haber','Olgunlaşmamış'),('Şövalye','🏇','Teklif','H kırıklığı'),
    ('Kraliçe','👑','Şefkat','Kırılganlık'),('Kral','👑','Olgunluk','Baskı')]]
SWORDS = [krt(f'Kılıç {s}',e,a,t) for s,e,a,t in [
    ('Ası','⚔️','Netlik','Karışıklık'),('İkili','2️⃣','İkilem','Kararsızlık'),('Üçlü','3️⃣','Acı','İyileşme'),
    ('Dörtlü','4️⃣','Dinlenme','Tükenmişlik'),('Beşli','5️⃣','Çatışma','Uzlaşma'),('Altılı','6️⃣','Geçiş','Takılma'),
    ('Yedili','7️⃣','Kurnazlık','Vicdan'),('Sekizli','8️⃣','Korku','Özgürleşme'),('Dokuzlu','9️⃣','Kaygı','Umut'),
    ('Onlu','🔟','Çöküş','İyileşme'),('Vale','🤵','Fikir','Dedikodu'),('Şövalye','🏇','Hız','Acele'),
    ('Kraliçe','👑','İletişim','Soğukluk'),('Kral','👑','Adalet','Zorbalık')]]
PENTS = [krt(f'Tılsım {s}',e,a,t) for s,e,a,t in [
    ('Ası','💎','Fırsat','Kaçan'),('İkili','2️⃣','Denge','Dengesizlik'),('Üçlü','3️⃣','Beceri','Yetersizlik'),
    ('Dörtlü','4️⃣','Birikim','Cimrilik'),('Beşli','5️⃣','Zorluk','Yardım'),('Altılı','6️⃣','Paylaşım','Borç'),
    ('Yedili','7️⃣','Sabır','Sabırsızlık'),('Sekizli','8️⃣','Çalışma','Mükemmeliyetçi'),('Dokuzlu','9️⃣','Lüks','Harcama'),
    ('Onlu','🔟','Miras','Kavga'),('Vale','🤵','Çalışkan','Tembellik'),('Şövalye','🏇','Azim','Durgunluk'),
    ('Kraliçe','👑','Bereket','İhmal'),('Kral','👑','Başarı','Açgözlülük')]]
TUM_KARTLAR = MAJOR + WANDS + CUPS + SWORDS + PENTS


class TarotScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.secilen = []
        self.kart_adet = 3
        self._calisiyor = False
        Clock.schedule_once(lambda dt: self.kur(), 0)

    def kur(self):
        ana = BoxLayout(
            orientation='vertical',
            spacing=dp(6),
            padding=[dp(10), SAFE_UST, dp(10), SAFE_ALT],
        )

        ana.add_widget(baslik_satir('🃏', 'TAROT FALI', font_size='20sp', height=dp(32)))

        btsatir = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(46),
            spacing=dp(8),
        )
        gb = tus_buton('geri', font_size='13sp', size_hint_x=0.28)
        gb.bind(on_press=lambda x: setattr(self.manager, 'current', 'anasayfa'))
        btsatir.add_widget(gb)

        self.adet_btn = tus_buton('kart_adet', font_size='13sp', altin_yazi=True, size_hint_x=0.34)
        buton_metin_guncelle(self.adet_btn, f'{self.kart_adet} Kart')
        self.adet_btn.bind(on_press=self.adet_degistir)
        btsatir.add_widget(self.adet_btn)

        self.fal_btn = tus_buton('fal_ac', vurgu=True, size_hint_x=0.38)
        self.fal_btn.bind(on_press=self.fal_ac)
        btsatir.add_widget(self.fal_btn)
        ana.add_widget(btsatir)

        self.kart_satir = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(180),
            spacing=dp(10),
        )
        ana.add_widget(self.kart_satir)
        self._kart_placeholder_ekle(3)

        self.poz_satir = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(24),
            spacing=dp(10),
        )
        for _ in range(3):
            self.poz_satir.add_widget(
                metin_label('—', font_size='9sp', color=RENKLER['altin_parlak'], halign='center')
            )
        ana.add_widget(self.poz_satir)

        self.isim_satir = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(38),
            spacing=dp(6),
        )
        for _ in range(3):
            self.isim_satir.add_widget(
                metin_label('—', font_size='8sp', color=RENKLER['gri'], halign='center')
            )
        ana.add_widget(self.isim_satir)

        self.yorum_alani, self.yorum_label = kaydirici_metin(1)
        self.yorum_label.halign = 'left'
        self.yorum_label.text = (
            f'[b][color={RENKLER["gri_acik"]}]Fal başlatmak için\n"Fal Aç" butonuna tıklayın[/color][/b]'
        )
        ana.add_widget(self.yorum_alani)

        ekran_icerik_sar(self, ana)

    def _kart_placeholder_ekle(self, adet):
        """Boş kart slotları — Image her zaman geçerli source ile kilitli yerleşimde."""
        self.kart_satir.clear_widgets()
        pay = 1.0 / max(adet, 1)
        arka = CARD_BACK if os.path.exists(CARD_BACK) else ''
        for _ in range(adet):
            self.kart_satir.add_widget(
                Image(
                    source=arka,
                    size_hint=(pay, 1),
                    fit_mode='fill',
                    opacity=0.25,
                )
            )

    def _kart_image_olustur(self, gorsel_yolu, genislik_pay):
        """Tek kart Image — source doğrulanmış, layout kilitli."""
        if not gorsel_yolu or not os.path.exists(gorsel_yolu):
            _eksik_resim_log(gorsel_yolu or '(boş yol)')
            gorsel_yolu = CARD_BACK if os.path.exists(CARD_BACK) else gorsel_yolu

        img = Image(
            source='',
            size_hint=(genislik_pay, 1),
            fit_mode='fill',
        )
        img.source = gorsel_yolu
        img.reload()
        return img

    def adet_degistir(self, instance):
        if self.kart_adet == 3:
            self.kart_adet = 5
        elif self.kart_adet == 5:
            self.kart_adet = 1
        else:
            self.kart_adet = 3
        buton_metin_guncelle(self.adet_btn, f'{self.kart_adet} Kart')
        self._kart_placeholder_ekle(self.kart_adet)
        self.poz_satir.clear_widgets()
        for _ in range(self.kart_adet):
            self.poz_satir.add_widget(
                metin_label('—', font_size='9sp', color=RENKLER['altin_parlak'], halign='center')
            )
        self.isim_satir.clear_widgets()
        for _ in range(self.kart_adet):
            self.isim_satir.add_widget(metin_label('—', font_size='8sp', color=RENKLER['gri'], halign='center'))

    def fal_ac(self, instance):
        if self._calisiyor:
            return
        from fal_limit import yorum_baslat
        yorum_baslat('tarot', lambda: self._fal_ac_devam(instance))

    def _fal_ac_devam(self, instance):
        if self._calisiyor:
            return
        self._calisiyor = True
        buton_metin_guncelle(self.fal_btn, tus_metin('bekle')); self.fal_btn.disabled = True
        cache_temizle()

        sec = random.sample(TUM_KARTLAR, self.kart_adet)
        self.secilen = [(k, random.choice(['Düz','Ters'])) for k in sec]
        self._kartlari_goster()
        self._pozisyonlari_goster()
        self._isimleri_goster()
        self._yorumu_goster()
        self._ai_tarot_yorum()

        buton_metin_guncelle(self.fal_btn, tus_metin('tekrar')); self.fal_btn.disabled = False
        self._calisiyor = False

    def _kartlari_goster(self):
        """Seçilen kartların görsellerini yatay BoxLayout'a eşit genişlikte yerleştirir."""
        self.kart_satir.clear_widgets()
        self.kart_satir.height = dp(180)

        adet = len(self.secilen)
        genislik_pay = 1.0 / max(adet, 1)

        for i, (kart, _durum) in enumerate(self.secilen):
            gorsel_yolu = kart_gorsel_yolu(kart['isim'])
            img = self._kart_image_olustur(gorsel_yolu, genislik_pay)
            img.opacity = 0
            self.kart_satir.add_widget(img)

            anim = Animation(opacity=1, duration=0.35)
            Clock.schedule_once(lambda dt, a=anim, w=img: a.start(w), 0.05 * i)

    def _pozisyonlari_goster(self):
        """Kartların altındaki pozisyon etiketleri (Geçmiş / Şimdi / Gelecek)."""
        self.poz_satir.clear_widgets()
        poz_map = {
            1: ['✨ Kart'],
            3: ['🌅 Geçmiş', '🌞 Şimdi', '🌠 Gelecek'],
            5: ['🌅 Geçmiş', '🌞 Şimdi', '🌠 Gelecek', '💫 Etkiler', '🌟 Umut'],
        }
        etiketler = poz_map.get(self.kart_adet, [f'Kart {i + 1}' for i in range(self.kart_adet)])

        for i in range(len(self.secilen)):
            e = etiketler[i] if i < len(etiketler) else f'Kart {i + 1}'
            self.poz_satir.add_widget(
                metin_label(e, font_size='9sp', color=RENKLER['altin_parlak'], halign='center')
            )

    def _isimleri_goster(self):
        self.isim_satir.clear_widgets()
        for kart, durum in self.secilen:
            s = '🔴' if durum == 'Ters' else '🟢'
            c = RENKLER['kirmizi_acik'] if durum == 'Ters' else RENKLER['yesil_parlak']
            self.isim_satir.add_widget(metin_label(f'{s} {kart["isim"]}\n{durum}',
                font_size='7sp', bold=True, color=c))

    def _yorumu_goster(self):
        y = f"[b][color={RENKLER['altin']}]🃏  TAROT YORUMUNUZ  🃏[/color][/b]\n\n"
        pm = {1:['Kartınız'], 3:['Geçmiş','Şimdi','Gelecek'],
              5:['Geçmiş','Şimdi','Gelecek','Etkiler','Umut']}
        et = pm.get(self.kart_adet, [f'Kart {i+1}' for i in range(self.kart_adet)])
        for i, (kart, durum) in enumerate(self.secilen):
            p = et[i] if i < len(et) else f'Kart {i+1}'
            a = kart['ters'] if durum == 'Ters' else kart['anlam']
            c = RENKLER['yesil_parlak'] if durum == 'Düz' else RENKLER['kirmizi_acik']
            y += f"[b][color={RENKLER['mor_parlak']}]{p}:[/color][/b] {kart['sembol']} [b]{kart['isim']}[/b] "
            y += f"[color={c}]({durum})[/color]\n[color={RENKLER['gri_acik']}]{a}[/color]\n\n"
        y += f"[color={RENKLER['altin']}]💫 Kart Mesajı:[/color]\n"
        y += f"[color={RENKLER['pembe_acik']}]{random.choice(['Hayatınızda önemli değişimlerin eşiğindesiniz. Sezgilerinize güvenin.','Geçmişi bırakın, gelecek size gülümsüyor.','Aşk ve para sizi bekliyor.','İç sesinizi dinleyin.','Kariyerinizde büyük bir sıçrama yapmaya hazır olun!','Evren size işaretler gönderiyor.'])}[/color]\n\n"
        y += f"[color={RENKLER['gri']}]📚 78 karttan {self.kart_adet} kart çekildi[/color]"
        self.yorum_label.markup = True
        self.yorum_label.text = y
        self._son_temel_yorum = y

    def _ai_tarot_yorum(self):
        pm = {1: ['Kartınız'], 3: ['Geçmiş', 'Şimdi', 'Gelecek'],
              5: ['Geçmiş', 'Şimdi', 'Gelecek', 'Etkiler', 'Umut']}
        et = pm.get(self.kart_adet, [f'Kart {i + 1}' for i in range(self.kart_adet)])
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
                + f"\n\n[color={RENKLER['gri']}]78 karttan {self.kart_adet} kart çekildi[/color]"
            )

        yorum_al('tarot', {'kartlar': kartlar}, _bitir, coin_dahil=False)