"""
✨ Diğer Fallar Modülü
İskambil Falı, Çiçek Falı, Nazar Falı, El Falı
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
import random

from ai_yorum import yorum_al
from theme import (
    TUS, tus_buton, siyah_buton, baslik_satir, buton_metin_guncelle,
    yorum_bekle_markup, foto_fal_sonuc, diger_fal_buton, emoji_temizle,
)

RENKLER = {
    'arka_plan': '#1a0a2e',
    'altin': '#ffd700',
    'mor': '#9b59b6',
    'mor_koyu': '#6c3483',
    'beyaz': '#ffffff',
    'gri_acik': '#e0e0e0',
    'yesil': '#2ecc71',
    'kirmizi': '#e74c3c',
    'turuncu': '#f39c12',
    'pembe': '#e91e90',
    'pembe_acik': '#ff80ab',
    'lacivert': '#1a237e',
    'mavi_acik': '#64B5F6',
}

# İskambil kağıdı anlamları
ISKAMBIL_KARTLARI = [
    {'isim': 'Kupa Ası', 'anlam': 'Aşk ve mutluluk kapınızda. Yeni bir ilişki başlangıcı.', 'sembol': '🃏❤️'},
    {'isim': 'Kupa Kızı', 'anlam': 'Sevgi dolu bir kadın hayatınıza girecek.', 'sembol': '👩❤️'},
    {'isim': 'Kupa Papazı', 'anlam': 'Duygusal ve sadık bir erkek figürü.', 'sembol': '👨❤️'},
    {'isim': 'Kupa Vale', 'anlam': 'İyi haberler getiren genç bir arkadaş.', 'sembol': '🧑❤️'},
    {'isim': 'Karo Ası', 'anlam': 'Maddi kazanç ve yeni iş fırsatı.', 'sembol': '🃏💎'},
    {'isim': 'Karo Kızı', 'anlam': 'Zeki ve başarılı bir kadın iş hayatınızda.', 'sembol': '👩💼'},
    {'isim': 'Karo Papazı', 'anlam': 'Güçlü bir iş ortağı veya patron.', 'sembol': '👨💼'},
    {'isim': 'Karo Vale', 'anlam': 'Genç bir iş arkadaşından yardım.', 'sembol': '🧑💼'},
    {'isim': 'Maça Ası', 'anlam': 'Zorlukların üstesinden gelme gücü.', 'sembol': '🃏♠️'},
    {'isim': 'Maça Kızı', 'anlam': 'Dikkatli olmanız gereken bir kadın.', 'sembol': '👩⚔️'},
    {'isim': 'Maça Papazı', 'anlam': 'Otoriter ve güçlü bir erkek figürü.', 'sembol': '👨⚔️'},
    {'isim': 'Maça Vale', 'anlam': 'Genç bir rakip veya rekabet.', 'sembol': '🧑⚔️'},
    {'isim': 'Sinek Ası', 'anlam': 'Yeni fikirler ve başarılı projeler.', 'sembol': '🃏♣️'},
    {'isim': 'Sinek Kızı', 'anlam': 'Yaratıcı ve yardımsever bir kadın.', 'sembol': '👩🍀'},
    {'isim': 'Sinek Papazı', 'anlam': 'Bilge ve tecrübeli bir danışman.', 'sembol': '👨🍀'},
    {'isim': 'Sinek Vale', 'anlam': 'Genç bir arkadaştan güzel haber.', 'sembol': '🧑🍀'},
]

# Çiçek falı anlamları
CICEK_FALI = [
    {'isim': 'Gül 🌹', 'anlam': 'Büyük bir aşk ve tutku sizi bekliyor. Romantik günler yakın.'},
    {'isim': 'Papatya 🌼', 'anlam': 'Saflık ve masumiyet. Temiz bir sayfa açma zamanı.'},
    {'isim': 'Lale 🌷', 'anlam': 'Bolluk ve bereket. Maddi konularda şanslı dönem.'},
    {'isim': 'Orkide 🏵️', 'anlam': 'Gizem ve zarafet. Özel biriyle tanışacaksınız.'},
    {'isim': 'Ayçiçeği 🌻', 'anlam': 'Mutluluk ve pozitif enerji. Yüzünüz gülecek.'},
    {'isim': 'Menekşe 💜', 'anlam': 'Sadakat ve güven. Dostluklarınız güçlenecek.'},
    {'isim': 'Karanfil 🌸', 'anlam': 'Saygı ve hayranlık. İş hayatında başarı.'},
    {'isim': 'Zambak 💮', 'anlam': 'Saflık ve yeniden doğuş. Ruhsal arınma zamanı.'},
    {'isim': 'Nergis 🌺', 'anlam': 'Kendine güven ve başarı. Yeteneklerinizi keşfedin.'},
    {'isim': 'Sümbül 🏵️', 'anlam': 'Spor ve sağlık. Yeni bir spora başlama zamanı.'},
    {'isim': 'Kiraz Çiçeği 🌸', 'anlam': 'Güzellik ve geçicilik. Anın tadını çıkarın.'},
    {'isim': 'Nilüfer 🪷', 'anlam': 'Ruhsal aydınlanma ve iç huzur. Meditasyon zamanı.'},
    {'isim': 'Lavanta 💐', 'anlam': 'Huzur ve sakinlik. Stresli dönem sona eriyor.'},
    {'isim': 'Yasemin 🌼', 'anlam': 'Romantizm ve duygusallık. Aşk hayatınız hareketleniyor.'},
]

# El falı çizgi anlamları
EL_FALI = [
    {'isim': 'Hayat Çizgisi', 'anlam': 'Uzun ve sağlıklı bir yaşam sizi bekliyor. Canlılığınız yüksek.'},
    {'isim': 'Kader Çizgisi', 'anlam': 'Kariyerinizde büyük başarılar elde edeceksiniz.'},
    {'isim': 'Kalp Çizgisi', 'anlam': 'Aşk hayatınızda derin ve anlamlı bir ilişki sizi bekliyor.'},
    {'isim': 'Akıl Çizgisi', 'anlam': 'Zekanız ve analitik düşünceniz sayesinde her sorunu çözeceksiniz.'},
    {'isim': 'Güneş Çizgisi', 'anlam': 'Yaratıcı yeteneklerinizle tanınacak ve takdir edileceksiniz.'},
    {'isim': 'Sezgi Çizgisi', 'anlam': 'İçgüdüleriniz çok kuvvetli. Sezgilerinize güvenin.'},
    {'isim': 'Merkür Çizgisi', 'anlam': 'İletişim yeteneğiniz sayesinde iş hayatında yükseleceksiniz.'},
    {'isim': 'Evlilik Çizgisi', 'anlam': 'Yakın zamanda önemli bir ilişki kararı alacaksınız.'},
    {'isim': 'Çocuk Çizgisi', 'anlam': 'Aile hayatınızda mutlu haberler sizi bekliyor.'},
    {'isim': 'Para Çizgisi', 'anlam': 'Maddi konularda şanslı bir dönem. Yatırım zamanı.'},
    {'isim': 'Sağlık Çizgisi', 'anlam': 'Sağlığınız yerinde. Düzenli spor yapmaya devam edin.'},
    {'isim': 'Yolculuk Çizgisi', 'anlam': 'Yakında güzel bir seyahat sizi bekliyor.'},
]

# Nazar falı
NAZAR_YORUMLARI = [
    "Nazar boncuğunuz parlıyor! Kötü enerjilerden korunuyorsunuz.",
    "Bu hafta nazara karşı dikkatli olun. Başarılarınız kıskanılabilir.",
    "Nazar boncuğunuzu yanınızda taşıyın. Sizi koruyacak.",
    "Enerjiniz çok yüksek! Olumlu düşünceleriniz gerçekleşiyor.",
    "Birileri sizi kıskanıyor olabilir. Tedbirli olun.",
    "Nazar boncuğunuz kırıldıysa, sizi büyük bir kazadan korumuş demektir.",
    "Pozitif enerjiniz etrafa yayılıyor. Herkes sizi seviyor.",
    "Mavi renk size şans getirecek. Mavi tonları kullanın.",
    "Göz değmesine karşı dikkatli olun. Özellikle yeni başlangıçlarda.",
    "Nazar duası okuyun ve korunduğunuzu hissedin.",
    "İç huzurunuzu koruyun. Dış etkenler sizi etkilemesin.",
    "Nazar boncuğu görmek size şans getirecek.",
]


class DigerFallarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        with self.canvas.before:
            Color(*get_color_from_hex(RENKLER['arka_plan']))
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._guncelle_rect, pos=self._guncelle_rect)
        
        ana_layout = BoxLayout(orientation='vertical', spacing=10, padding=15)
        
        from kivy.metrics import dp
        ana_layout.add_widget(baslik_satir('', 'DİĞER FALLAR', font_size='24sp', height=dp(44)))
        
        # Fal türü seçimi
        fal_turu_layout = GridLayout(cols=2, spacing=10, size_hint=(1, 0.2))
        
        fal_turleri = [
            ('İskambil', 'iskambil'),
            ('Çiçek Falı', 'cicek'),
            ('Nazar Falı', 'nazar'),
        ]
        
        for text, fal_type in fal_turleri:
            btn = diger_fal_buton(text, fal_type, vurgu=True, font_size='13sp')
            btn.bind(on_press=lambda x, ft=fal_type: self.fal_sec(ft))
            fal_turu_layout.add_widget(btn)
        
        ana_layout.add_widget(fal_turu_layout)
        
        # Fal sonucu alanı
        self.sonuc_alani = ScrollView(size_hint=(1, 0.55))
        self.sonuc_label = Label(
            text='[b][color={}]Yukarıdan bir fal türü seçin![/color][/b]'.format(RENKLER['gri_acik']),
            font_size='16sp',
            color=get_color_from_hex(RENKLER['beyaz']),
            size_hint_y=None,
            halign='center',
            valign='top',
            text_size=(380, None),
            markup=True,
            padding=(10, 10)
        )
        self.sonuc_label.bind(texture_size=self.sonuc_label.setter('size'))
        self.sonuc_alani.add_widget(self.sonuc_label)
        
        ana_layout.add_widget(self.sonuc_alani)
        
        # Butonlar
        buton_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.08),
            spacing=10
        )
        
        self.tekrar_buton = tus_buton('tekrar', vurgu=True, font_size='14sp')
        self.tekrar_buton.bind(on_press=self.tekrar_bak)
        self.tekrar_buton.disabled = True
        
        geri_buton = tus_buton('geri', font_size='13sp')
        geri_buton.bind(on_press=lambda x: setattr(self.manager, 'current', 'anasayfa'))
        
        buton_layout.add_widget(self.tekrar_buton)
        buton_layout.add_widget(geri_buton)
        
        ana_layout.add_widget(buton_layout)
        
        self.add_widget(ana_layout)
    
    def _guncelle_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def _fal_baslat(self, veri):
        from fal_limit import yorum_baslat
        yorum_baslat('diger', lambda: self._fal_baslat_devam(veri))

    def _fal_baslat_devam(self, veri):
        self.sonuc_label.markup = True
        self.sonuc_label.text = yorum_bekle_markup()
        self.tekrar_buton.disabled = True

        def _bitir(metin, ai_kullanildi, hata, kaynak=None, fotograf=False):
            self.sonuc_label.markup = True
            if hata and not metin:
                self.sonuc_label.text = (
                    f"[color={RENKLER['kirmizi']}]{emoji_temizle(hata)}[/color]"
                )
            else:
                self.sonuc_label.text = foto_fal_sonuc(metin, hata)
            self.tekrar_buton.disabled = False

        yorum_al('diger', veri, _bitir, coin_dahil=False)

    def fal_sec(self, fal_type):
        """Seçilen fal türüne göre fal bak"""
        self.fal_turu = fal_type
        
        if fal_type == 'iskambil':
            self.iskambil_fali()
        elif fal_type == 'cicek':
            self.cicek_fali()
        elif fal_type == 'nazar':
            self.nazar_fali()
        
        self.tekrar_buton.disabled = False
    
    def tekrar_bak(self, instance):
        """Aynı fal türünü tekrar bak"""
        if hasattr(self, 'fal_turu'):
            self.fal_sec(self.fal_turu)
    
    def iskambil_fali(self):
        """İskambil falı — premium cihaz yorumu."""
        secilen = random.sample(ISKAMBIL_KARTLARI, 3)
        pozisyonlar = ['Geçmiş', 'Şu An', 'Gelecek']
        kartlar = [
            {'isim': k['isim'], 'anlam': k['anlam'], 'pozisyon': p}
            for k, p in zip(secilen, pozisyonlar)
        ]
        self._fal_baslat({'alt_tip': 'iskambil', 'tur': 'İskambil Falı', 'kartlar': kartlar})

    def cicek_fali(self):
        """Çiçek falı — premium cihaz yorumu."""
        secilen = random.sample(CICEK_FALI, random.randint(2, 4))
        cicekler = [{'isim': c['isim'], 'anlam': c['anlam']} for c in secilen]
        self._fal_baslat({'alt_tip': 'cicek', 'tur': 'Çiçek Falı', 'cicekler': cicekler})

    def nazar_fali(self):
        """Nazar falı — premium cihaz yorumu."""
        self._fal_baslat({'alt_tip': 'nazar', 'tur': 'Nazar Falı'})