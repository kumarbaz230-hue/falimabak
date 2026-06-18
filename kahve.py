"""
☕ Kahve Falı Modülü - Kamera Entegrasyonlu
Kullanıcı kahve fincanını fotoğraflar, uygulama yorumlar!
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.utils import get_color_from_hex
from kivy.animation import Animation, Sequence
from kivy.clock import Clock
from kivy.metrics import dp
import random

from theme import (
    RENKLER, tus_metin, yorum_bekle_metin, fontlari_yukle, metin_label,
    tus_buton, baslik_satir, buton_metin_guncelle,
    kaydirici_metin, FotoKutucukPanel, yorum_bekle_markup, foto_fal_sonuc,
    SAFE_UST, SAFE_ALT, ekran_icerik_sar, yorum_panel_baslik,
)
from kamera import galeriden_sec, kameradan_cek, galeri_aktif
from ai_yorum import yorum_al

fontlari_yukle()

RENKLER = {
    'arka_plan': '#0d0221',
    'arka_plan2': '#150534',
    'kart_arka': '#1a0a3e',
    'kart_kenar': '#2d1b69',
    'altin': '#ffd700',
    'altin_parlak': '#ffec6e',
    'mor_parlak': '#b388ff',
    'mor': '#7c4dff',
    'mor_koyu': '#4a148c',
    'beyaz': '#ffffff',
    'gri_acik': '#e0e0e0',
    'gri': '#9e9e9e',
    'yesil': '#00e676',
    'kirmizi': '#ff1744',
    'turuncu': '#ff9100',
    'pembe': '#e040fb',
    'pembe_acik': '#ff80ab',
    'lacivert': '#0d47a1',
    'mavi_acik': '#40c4ff',
    'mavi_parlak': '#00e5ff',
    'kahve': '#6d4c41',
    'kahve_acik': '#a1887f',
    'sutlu': '#d7ccc8',
    'krem': '#ffcc80',
}

# Kahve falı şekilleri - ZENGİN VERİTABANI
KAHVE_SEKILLERI = [
    # AŞK & İLİŞKİ
    {'isim': 'Göz 👁️', 'kategori': 'Aşk', 'pozitif': 'Birisi size derinden aşık! Gözlerini sizden alamıyor.',
     'negatif': 'Kıskançlık duyan biri var. Dikkatli olun, nazar değebilir.'},
    {'isim': 'Kalp ❤️', 'kategori': 'Aşk', 'pozitif': 'Kocaman bir aşk kapınızda! Yeni bir ilişkiye hazır olun.',
     'negatif': 'Aşk hayatınızda geçici bir kriz olabilir. Sabırlı olun.'},
    {'isim': 'Yüzük 💍', 'kategori': 'Aşk', 'pozitif': 'EVLİLİK HABERİ GELİYOR! Parmakta yüzük görmeye hazır olun.',
     'negatif': 'İlişkinizde bir karar vermeniz gerekiyor. Acele etmeyin.'},
    {'isim': 'Kuğu 🦢', 'kategori': 'Aşk', 'pozitif': 'Sonsuz aşk ve sadakat. Ruh eşinizi buldunuz!',
     'negatif': 'Bir ilişkide fedakarlık yapmanız gerekebilir.'},
    {'isim': 'Gül 🌹', 'kategori': 'Aşk', 'pozitif': 'Romantik bir sürpriz sizi bekliyor. Çiçekler ve tatlı sözler!',
     'negatif': 'Bir hayal kırıklığı yaşayabilirsiniz. Gerçekçi olun.'},
    
    # PARA & KARİYER
    {'isim': 'Para 💰', 'kategori': 'Para', 'pozitif': 'Beklenmedik PARA! Miras, ikramiye veya zam kapıda.',
     'negatif': 'Maddi konularda dikkat! Gereksiz harcamalardan kaçının.'},
    {'isim': 'Balık 🐟', 'kategori': 'Para', 'pozitif': 'BOLLUK ve BEREKET! Para akışınız hızlanıyor.',
     'negatif': 'Bir yatırımınız risk altında. Uzman görüşü alın.'},
    {'isim': 'At Nalı 🍀', 'kategori': 'Para', 'pozitif': 'ŞANS peşinizi bırakmıyor! Piyango veya şans oyunları.',
     'negatif': 'Şansa güvenmeyin, kendi yeteneklerinize güvenin.'},
    {'isim': 'Merdiven 🪜', 'kategori': 'Kariyer', 'pozitif': 'Kariyerinizde YÜKSELİŞ! Terfi veya yeni iş teklifi.',
     'negatif': 'Yükselmek için daha çok çalışmanız gerekiyor.'},
    {'isim': 'Kitap 📖', 'kategori': 'Kariyer', 'pozitif': 'Yeni bilgiler size başarı getirecek. Eğitim zamanı!',
     'negatif': 'Bir sınav veya görüşmede zorlanabilirsiniz. İyi hazırlanın.'},
    
    # SAĞLIK & ŞİFA
    {'isim': 'Ağaç 🌳', 'kategori': 'Sağlık', 'pozitif': 'SAĞLIK ve uzun ömür! Enerjiniz yerinde, hayat dolu.',
     'negatif': 'Sağlığınıza dikkat! Kontrol zamanı geldi.'},
    {'isim': 'Yıldız ⭐', 'kategori': 'Sağlık', 'pozitif': 'ŞİFA enerjisi! Hastalık varsa geçecek, sağlık yerine gelecek.',
     'negatif': 'Yorgunluk ve stres sizi etkiliyor. Dinlenin.'},
    {'isim': 'Güneş ☀️', 'kategori': 'Sağlık', 'pozitif': 'ENERJİ ve canlılık! Kendinizi çok iyi hissedeceksiniz.',
     'negatif': 'Aşırı güneşe dikkat! Sağlığınızı koruyun.'},
    {'isim': 'Ay 🌙', 'kategori': 'Sağlık', 'pozitif': 'İç huzur ve dinginlik. Ruhsal şifa zamanı.',
     'negatif': 'Uyku düzeninize dikkat edin. Uykusuzluk sorun olabilir.'},
    
    # YOLCULUK & HABER
    {'isim': 'Uçak ✈️', 'kategori': 'Seyahat', 'pozitif': 'SEYAHAT vakti! Yurt dışı veya uzak bir şehre gideceksiniz.',
     'negatif': 'Seyahat planlarınız ertelenebilir. Alternatif düşünün.'},
    {'isim': 'Gemi ⛵', 'kategori': 'Seyahat', 'pozitif': 'Keyifli bir deniz yolculuğu veya tatil sizi bekliyor.',
     'negatif': 'Duygusal dalgalanmalar yaşayabilirsiniz. Dengenizi koruyun.'},
    {'isim': 'Kuş 🐦', 'kategori': 'Haber', 'pozitif': 'MÜJDE! Uzaktan güzel bir haber alacaksınız.',
     'negatif': 'Bir haber sizi üzebilir. Doğrulamasını yapın.'},
    {'isim': 'Mektup ✉️', 'kategori': 'Haber', 'pozitif': 'ÖNEMLİ bir yazılı haber! İş teklifi veya davet.',
     'negatif': 'Bir yazışmada sorun çıkabilir. Dikkatli olun.'},
    
    # İNSANLAR & DOSTLAR
    {'isim': 'Köpek 🐕', 'kategori': 'Dostluk', 'pozitif': 'SADAKAT! Gerçek dostunuz yanınızda, güvenin.',
     'negatif': 'Bir arkadaşlıkta hayal kırıklığı yaşayabilirsiniz.'},
    {'isim': 'Kedi 🐱', 'kategori': 'Dostluk', 'pozitif': 'BAĞIMSIZLIK! Yeni bir dostluk özgürlük getirecek.',
     'negatif': 'Güvendiğiniz bir kişi sizi şaşırtabilir.'},
    {'isim': 'Fil 🐘', 'kategori': 'Dostluk', 'pozitif': 'BİLGELİK! Tecrübeli bir dost size yol gösterecek.',
     'negatif': 'Aşırı inatçılık sorun yaratabilir. Esnek olun.'},
    {'isim': 'Kelebek 🦋', 'kategori': 'Dostluk', 'pozitif': 'DÖNÜŞÜM! Yeni dostluklar hayatınızı renklendirecek.',
     'negatif': 'Geçici arkadaşlıklara fazla güvenmeyin.'},
    
    # DİĞER ÖNEMLİ SEMBOLLER
    {'isim': 'Ev 🏠', 'kategori': 'Aile', 'pozitif': 'AİLE içinde huzur ve mutluluk! Güzel günler sizi bekliyor.',
     'negatif': 'Ev içinde bir anlaşmazlık olabilir. Sakin olun.'},
    {'isim': 'Bebek 👶', 'kategori': 'Aile', 'pozitif': 'MUTLU HABER! Aileye yeni bir üye katılabilir.',
     'negatif': 'Bir sorumluluk sizi zorlayabilir. Hazırlıklı olun.'},
    {'isim': 'Yol 🛤️', 'kategori': 'Hayat', 'pozitif': 'YENİ BAŞLANGIÇ! Hayatınızda yeni bir yol açılıyor.',
     'negatif': 'Bir seçim yapmanız gerekiyor ve kararsızsınız.'},
    {'isim': 'Kale 🏰', 'kategori': 'Hayat', 'pozitif': 'KORUNMA ve güvenlik. Hiçbir şeyden korkmayın!',
     'negatif': 'Kendinizi kısıtlanmış hissedebilirsiniz. Özgürlüğünüzü arayın.'},
    {'isim': 'Çiçek 🌸', 'kategori': 'Hayat', 'pozitif': 'GÜZEL GÜNLER! Hayatınız çiçek gibi açacak.',
     'negatif': 'Kısa süreli bir üzüntü, ardından mutluluk.'},
    {'isim': 'Yılan 🐍', 'kategori': 'Uyarı', 'pozitif': 'DÖNÜŞÜM! Eski sorunlardan kurtulup yenileneceksiniz.',
     'negatif': 'DİKKAT! Çevrenizde size zarar vermek isteyen biri olabilir.'},
    {'isim': 'Ejderha 🐉', 'kategori': 'Güç', 'pozitif': 'İÇSEL GÜÇ! Büyük engelleri aşacak güce sahipsiniz.',
     'negatif': 'Öfkenizi kontrol edin. Aşırı hırs sorun yaratabilir.'},
    {'isim': 'Kılıç ⚔️', 'kategori': 'Mücadele', 'pozitif': 'ADALET yerini bulacak. Doğru olan kazanacak.',
     'negatif': 'Bir kavgadan veya anlaşmazlıktan uzak durun.'},
    {'isim': 'Anahtar 🔑', 'kategori': 'Çözüm', 'pozitif': 'ÇÖZÜM! Her şeyin anahtarı elinizde. Sorun bitecek.',
     'negatif': 'Bir sırrı açıklamakta zorlanabilirsiniz.'},
    {'isim': 'Köprü 🌉', 'kategori': 'Bağlantı', 'pozitif': 'BAĞLANTI! Yeni insanlarla tanışacak, köprüler kuracaksınız.',
     'negatif': 'Bir ilişkide kopma noktasına gelebilirsiniz.'},
    {'isim': 'Dağ ⛰️', 'kategori': 'Engel', 'pozitif': 'ZİRVE! Büyük bir başarıya ulaşacak, dağın tepesini göreceksiniz.',
     'negatif': 'Önünüzde aşılması gereken zorlu bir engel var. Vazgeçmeyin!'},
]

# Profesyonel yorumlar
GENEL_YORUMLAR = [
    "🌸 FALINIZDA MUHTEŞEM SEMBOLLER VAR! Önünüzdeki dönemde aşk, para ve mutluluk sizi bekliyor. Hayatınızda yeni bir sayfa açılıyor! 🌸",
    "🌟 YILDIZLAR SİZE GÜLÜMSÜYOR! Bu hafta çok şanslısınız. Beklenmedik güzel haberler alacak, yüzünüz gülecek. Hazır olun! 🌟",
    "⚡ ENERJİNİZ ÇOK YÜKSEK! Pozitif düşünceleriniz gerçeğe dönüşüyor. Sezgilerinize güvenin, sizi doğru yola yönlendirecek. ⚡",
    "💫 FIRSATLAR AYAKLARINIZA GELİYOR! Kaçırmayın, değerlendirin. Özellikle iş ve kariyer konularında şanslı bir dönemdesiniz. 💫",
    "🌈 GÖKKUŞAĞININ DİĞER UCUNDA MUTLULUK SİZİ BEKLİYOR! Zor günler geride kalıyor. Aydınlık bir gelecek sizi bekliyor. 🌈",
    "🔮 SEZGİLERİNİZ ÇOK KUVVETLENİYOR! Rüyalarınıza dikkat edin. İç sesiniz size önemli mesajlar veriyor. Dinleyin! 🔮",
    "💜 AŞK HAYATINIZDA HAREKETLİ GÜNLER! Kalbinizi açın, sevgiye izin verin. Doğru kişi çok yakında karşınıza çıkacak. 💜",
    "💰 BOLLUK VE BEREKET ZAMANI! Maddi konularda rahatlayacaksınız. Yeni gelir kapıları açılıyor. Akıllıca harcayın. 💰",
    "🌿 SAĞLIĞINIZA DİKKAT!! Vücudunuz size sinyaller gönderiyor. Spor, sağlıklı beslenme ve dinlenme zamanı. 🌿",
    "🤝 SOSYAL ÇEVREMİZ GENİŞLİYOR! Yeni insanlarla tanışacak, güzel dostluklar kuracaksınız. Davetleri geri çevirmeyin. 🤝",
    "🎯 HEDEFLERİNİZE ODAKLANIN! Başarı için gerekli tüm yeteneklere sahipsiniz. İnanın ve çalışın, kazanacaksınız. 🎯",
    "🌺 İÇSEL HURUZA ULAŞMA ZAMANI! Meditasyon, yoga ve doğa yürüyüşleri size iyi gelecek. Ruhunuzu dinlendirin. 🌺",
    "🎭 BİR SÜRPRİZ SİZİ BEKLİYOR! Ne olduğunu söylemeyelim ama güzel bir sürpriz olacak. Heyecanlanmaya hazır olun! 🎭",
    "⭐ ŞANS PEŞİNİZİ BIRAKMIYOR! Bu hafta deneyeceğiniz her şey başarılı olacak. Şans oyunlarında bir şans verin! ⭐",
    "🦋 DÖNÜŞÜM VE YENİLENME! Eski alışkanlıklarınızı bırakma zamanı. Yeni bir siz doğuyor. Değişime açık olun! 🦋",
    "🏆 BAŞARI KAPIDA! Emeklerinizin karşılığını alacaksınız. Terfi, zam veya ödül sizi bekliyor olabilir. 🏆",
]

KAHVE_FOTO_SLOT = [
    {'anahtar': 'fincan_ic1', 'baslik': 'Fincan İçi 1', 'ikon_metin': '1'},
    {'anahtar': 'fincan_ic2', 'baslik': 'Fincan İçi 2', 'ikon_metin': '2'},
    {'anahtar': 'tabak', 'baslik': 'Tabak', 'ikon_metin': 'T'},
]


class KahveScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        ana_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            padding=[dp(12), SAFE_UST, dp(12), SAFE_ALT],
        )

        ana_layout.add_widget(baslik_satir('☕', 'KAHVE FALI', font_size='24sp', height=dp(44)))

        ana_layout.add_widget(metin_label(
            'Fincan içini 2 kez + tabağı fotoğraflayın. Kutuya dokunup kamera ile çekin.',
            font_size='12sp',
            color=RENKLER['gri_acik'],
            halign='center',
            size_hint_y=None,
            height=dp(36),
        ))

        self.foto_panel = FotoKutucukPanel(KAHVE_FOTO_SLOT, yukseklik=dp(128))
        ana_layout.add_widget(self.foto_panel)

        kamera_btn_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8),
        )

        if galeri_aktif():
            galeri_btn = tus_buton('galeri', font_size='13sp')
            galeri_btn.bind(on_press=lambda *_: galeriden_sec(self._foto_sonuc))
            kamera_btn_layout.add_widget(galeri_btn)

        kamera_btn = tus_buton('kamera', vurgu=True, font_size='13sp')
        kamera_btn.bind(on_press=lambda *_: kameradan_cek(self._foto_sonuc))
        kamera_btn_layout.add_widget(kamera_btn)
        ana_layout.add_widget(kamera_btn_layout)

        buton_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8),
        )

        self.fal_buton = tus_buton('yorumla', vurgu=True, font_size='15sp')
        self.fal_buton.bind(on_press=self.fal_yorumla)

        geri_buton = tus_buton('geri', font_size='13sp')
        geri_buton.bind(on_press=lambda x: setattr(self.manager, 'current', 'anasayfa'))

        buton_layout.add_widget(self.fal_buton)
        buton_layout.add_widget(geri_buton)
        ana_layout.add_widget(buton_layout)

        self.sekiller_alani, self.sekiller_label = kaydirici_metin(1)
        self.sekiller_alani.size_hint_y = None
        self.sekiller_alani.height = dp(56)
        self.sekiller_label.halign = 'center'
        ana_layout.add_widget(self.sekiller_alani)

        ana_layout.add_widget(yorum_panel_baslik('Fal yorumunuz'))
        self.yorum_alani, self.yorum_label = kaydirici_metin(1)
        self.yorum_label.halign = 'left'
        ana_layout.add_widget(self.yorum_alani)

        ekran_icerik_sar(self, ana_layout)
    
    def _foto_sonuc(self, yol, hata):
        if hata:
            self.yorum_label.markup = True
            self.yorum_label.text = f"[color={RENKLER['kirmizi']}]{hata}[/color]"
            return

        self.foto_panel.fotograf_ekle(yol)
        self.flas_efekti()
    
    def flas_efekti(self):
        """Flaş efekti"""
        flash = FloatLayout(size_hint=(1, 1))
        with flash.canvas:
            Color(1, 1, 1, 1)
            Rectangle(size=self.size, pos=self.pos)
        self.add_widget(flash)
        anim = Animation(opacity=0, duration=0.3)
        anim.start(flash)
        Clock.schedule_once(lambda dt: self.remove_widget(flash) if flash in self.children else None, 0.3)
    
    def fal_yorumla(self, instance):
        """Kahve falını yorumla — fotoğraflar doğrulanır ve yorumlanır."""
        if not self.foto_panel.tamam_mi():
            eksik = ', '.join(self.foto_panel.eksik_basliklar())
            self.yorum_label.markup = True
            self.yorum_label.text = (
                f"[color={RENKLER['kirmizi']}]Eksik fotoğraflar: {eksik}[/color]\n"
                f"[color={RENKLER['gri_acik']}]Her kutuya dokunup kamera ile fotoğraf çekin.[/color]"
            )
            return

        foto_veri = self.foto_panel.tum_veri()
        from foto_analiz import fotolar_dogrula
        ok, hata, _ = fotolar_dogrula(
            'kahve',
            foto_veri.get('foto_yollari'),
            foto_veri.get('foto_aciklamalari'),
        )
        if not ok:
            self.yorum_label.markup = True
            self.yorum_label.text = foto_fal_sonuc(None, hata)
            return

        from fal_limit import yorum_baslat
        yorum_baslat('kahve', lambda: self._fal_yorumla_devam(instance))

    def _fal_yorumla_devam(self, instance):
        self.sekiller_label.text = ''
        self.yorum_label.markup = True
        self.yorum_label.text = yorum_bekle_markup()
        buton_metin_guncelle(self.fal_buton, yorum_bekle_metin())
        self.fal_buton.disabled = True

        def _ai_bitir(metin, ai_kullanildi, hata, kaynak=None, fotograf=False):
            self.yorum_label.text = foto_fal_sonuc(metin, hata)
            buton_metin_guncelle(self.fal_buton, tus_metin('tekrar'))
            self.fal_buton.disabled = False

        foto_veri = self.foto_panel.tum_veri()
        yorum_al('kahve', foto_veri, _ai_bitir, coin_dahil=False)