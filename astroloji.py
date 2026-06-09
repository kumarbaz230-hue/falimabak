"""
⭐ Yıldız Falı (Astroloji) Modülü - Düzeltilmiş Versiyon
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.metrics import dp
import random
from datetime import date

from ai_yorum import yorum_al
from theme import tus_metin, yorum_bekle_metin, tus_buton, baslik_satir, buton_metin_guncelle, yorum_sonuc_metni

RENKLER = {
    'arka_plan': '#0d0221',
    'altin': '#ffd700',
    'mor': '#7c4dff',
    'mor_parlak': '#b388ff',
    'mor_koyu': '#4a148c',
    'beyaz': '#ffffff',
    'gri_acik': '#e0e0e0',
    'yesil': '#00e676',
    'kirmizi': '#ff1744',
    'lacivert': '#0d47a1',
    'mavi_acik': '#40c4ff',
    'pembe_acik': '#ff80ab',
    'yesil_parlak': '#69f0ae',
}

# Burç bilgileri (doğru tarih aralıklarıyla)
BURCLAR = {
    'Koç':     {'tarih': '21 Mart - 19 Nisan',     'element': 'Ateş',   'gezegen': 'Mars',   'sembol': '🐏'},
    'Boğa':    {'tarih': '20 Nisan - 20 Mayıs',    'element': 'Toprak', 'gezegen': 'Venüs',  'sembol': '🐂'},
    'İkizler': {'tarih': '21 Mayıs - 20 Haziran',  'element': 'Hava',   'gezegen': 'Merkür', 'sembol': '👯'},
    'Yengeç':  {'tarih': '21 Haziran - 22 Temmuz', 'element': 'Su',     'gezegen': 'Ay',     'sembol': '🦀'},
    'Aslan':   {'tarih': '23 Temmuz - 22 Ağustos', 'element': 'Ateş',   'gezegen': 'Güneş',  'sembol': '🦁'},
    'Başak':   {'tarih': '23 Ağustos - 22 Eylül',  'element': 'Toprak', 'gezegen': 'Merkür', 'sembol': '👩‍🌾'},
    'Terazi':  {'tarih': '23 Eylül - 22 Ekim',     'element': 'Hava',   'gezegen': 'Venüs',  'sembol': '⚖️'},
    'Akrep':   {'tarih': '23 Ekim - 21 Kasım',     'element': 'Su',     'gezegen': 'Plüton', 'sembol': '🦂'},
    'Yay':     {'tarih': '22 Kasım - 21 Aralık',   'element': 'Ateş',   'gezegen': 'Jüpiter','sembol': '🏹'},
    'Oğlak':   {'tarih': '22 Aralık - 19 Ocak',    'element': 'Toprak', 'gezegen': 'Satürn', 'sembol': '🐐'},
    'Kova':    {'tarih': '20 Ocak - 18 Şubat',     'element': 'Hava',   'gezegen': 'Uranüs', 'sembol': '🏺'},
    'Balık':   {'tarih': '19 Şubat - 20 Mart',     'element': 'Su',     'gezegen': 'Neptün', 'sembol': '🐟'},
}

# Burç yorumları
BURC_YORUMLARI = {
    'Koç': [
        "Enerjiniz yüksek! Yeni başlangıçlar için harika bir zaman.",
        "Aşk hayatınızda hareketli günler sizi bekliyor. Cesur olun!",
        "Kariyerinizde önemli fırsatlar kapınızı çalıyor.",
        "Sosyal çevreniz genişliyor. Yeni dostluklar kurun.",
        "Maddi konularda şanslı bir dönemdesiniz.",
    ],
    'Boğa': [
        "Sabrınızın meyvelerini toplama zamanı! Emekleriniz karşılık buluyor.",
        "Aşkta istikrar ve güven arıyorsunuz. Doğru kişi yakında çıkacak.",
        "Maddi konularda rahat bir dönem. Bütçenizi dengede tutun.",
        "Doğayla iç içe zaman geçirin, size iyi gelecek.",
        "Yeni bir hobi edinmek için harika bir zaman.",
    ],
    'İkizler': [
        "İletişim yeteneğinizle herkesi etkiliyorsunuz!",
        "Yeni bilgiler öğrenmek için mükemmel bir dönem.",
        "Sosyal çevrenizde popüler olacaksınız.",
        "Aşk hayatınızda sürpriz gelişmeler olabilir.",
        "Fikirlerinizi paylaşmaktan çekinmeyin.",
    ],
    'Yengeç': [
        "Duygularınızın sesini dinleyin. İçgüdüleriniz sizi doğru yönlendirecek.",
        "Aile bağlarınız güçleniyor. Sevdiklerinizle vakit geçirin.",
        "Aşk hayatınızda romantik bir dönem başlıyor.",
        "Geçmişten gelen bir konu kapanacak.",
        "Ev dekorasyonu veya taşınma gündeme gelebilir.",
    ],
    'Aslan': [
        "Sahne sizin! Yeteneklerinizi gösterme zamanı geldi.",
        "Liderlik vasfınız ön plana çıkıyor.",
        "Aşk hayatınızda tutkulu günler sizi bekliyor.",
        "Kendinize güvenin ve hedeflerinizin peşinden gidin.",
        "Yeni bir projede başrol oynayabilirsiniz.",
    ],
    'Başak': [
        "Analitik zekanız sayesinde her sorunu çözüyorsunuz!",
        "Sağlığınıza dikkat etmeniz gereken bir dönemdesiniz.",
        "İş hayatınızda verimliliğiniz artıyor.",
        "Aşkta mükemmeliyetçiliğinizi biraz kenara bırakın.",
        "Yeni bir düzen kurma zamanı.",
    ],
    'Terazi': [
        "Denge ve uyum sizin anahtar kelimeleriniz!",
        "İlişkilerde şanslı bir dönem. Evlilik gündemde olabilir.",
        "Sanatsal faaliyetler size iyi gelecek.",
        "Yeni bir ortaklık veya iş birliği fırsatı doğabilir.",
        "Sosyal adalet konularında sesinizi duyuracaksınız.",
    ],
    'Akrep': [
        "Sezgileriniz çok kuvvetli. İç sesinize güvenin!",
        "Gizli kalmış bir gerçek ortaya çıkabilir.",
        "Finansal konularda dönüşüm zamanı.",
        "Aşk hayatınızda derin ve tutkulu bir dönem.",
        "Kişisel gelişiminiz için önemli adımlar atacaksınız.",
    ],
    'Yay': [
        "Macera ve keşif zamanı! Yeni yerler göreceksiniz.",
        "Yurt dışı bağlantılı işler gündeme gelebilir.",
        "Felsefi konulara ilginiz artıyor.",
        "Aşk hayatınızda özgürlüğünüzü koruyun.",
        "Eğitim hayatınızda önemli gelişmeler olabilir.",
    ],
    'Oğlak': [
        "Hedeflerinize emin adımlarla ilerliyorsunuz. Başarı kaçınılmaz!",
        "Kariyerinizde yükselme zamanı. Terfi alabilirsiniz.",
        "Maddi konularda sağlam adımlar atıyorsunuz.",
        "Sorumluluklarınız artıyor ama üstesinden geleceksiniz.",
        "Aşk hayatınızda daha ciddi adımlar atma zamanı.",
    ],
    'Kova': [
        "Yaratıcı fikirlerinizle herkesi şaşırtıyorsunuz!",
        "Teknoloji ve inovasyon konularında başarılı olacaksınız.",
        "Arkadaş çevrenizde popüler ve etkili olacaksınız.",
        "Aşkta sıra dışı deneyimler yaşayabilirsiniz.",
        "Toplumsal konularda sesinizi duyuracaksınız.",
    ],
    'Balık': [
        "Hayal gücünüz sınır tanımıyor! Sanatsal yeteneklerinizi konuşturun.",
        "Rüyalarınıza dikkat edin. Önemli mesajlar alabilirsiniz.",
        "Empati yeteneğiniz sayesinde herkes size güveniyor.",
        "Aşk hayatınızda romantik bir dönem.",
        "Meditasyon size iyi gelecek. İç huzuru bulacaksınız.",
    ]
}

class AstrolojiScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def burc_bul(self, gun, ay):
        """Doğru burç hesaplama"""
        if (ay == 3 and gun >= 21) or (ay == 4 and gun <= 19):
            return 'Koç'
        elif (ay == 4 and gun >= 20) or (ay == 5 and gun <= 20):
            return 'Boğa'
        elif (ay == 5 and gun >= 21) or (ay == 6 and gun <= 20):
            return 'İkizler'
        elif (ay == 6 and gun >= 21) or (ay == 7 and gun <= 22):
            return 'Yengeç'
        elif (ay == 7 and gun >= 23) or (ay == 8 and gun <= 22):
            return 'Aslan'
        elif (ay == 8 and gun >= 23) or (ay == 9 and gun <= 22):
            return 'Başak'
        elif (ay == 9 and gun >= 23) or (ay == 10 and gun <= 22):
            return 'Terazi'
        elif (ay == 10 and gun >= 23) or (ay == 11 and gun <= 21):
            return 'Akrep'
        elif (ay == 11 and gun >= 22) or (ay == 12 and gun <= 21):
            return 'Yay'
        elif (ay == 12 and gun >= 22) or (ay == 1 and gun <= 19):
            return 'Oğlak'
        elif (ay == 1 and gun >= 20) or (ay == 2 and gun <= 18):
            return 'Kova'
        else:
            return 'Balık'
    
    def tarih_kontrol(self, gun, ay, yil):
        """Geçerli tarih kontrolü"""
        if yil < 1900 or yil > 2100:
            return False
        if ay < 1 or ay > 12:
            return False
        if gun < 1 or gun > 31:
            return False
        # 30 gün olan aylar
        if ay in [4, 6, 9, 11] and gun > 30:
            return False
        # Şubat kontrolü
        if ay == 2:
            # Artık yıl kontrolü
            artik = (yil % 4 == 0 and yil % 100 != 0) or (yil % 400 == 0)
            if gun > (29 if artik else 28):
                return False
        return True
    
    def build_ui(self):
        with self.canvas.before:
            Color(*get_color_from_hex(RENKLER['arka_plan']))
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._guncelle_rect, pos=self._guncelle_rect)
            
        ana_layout = BoxLayout(orientation='vertical', spacing=8, padding=[12, 10, 12, 10])
        
        ana_layout.add_widget(baslik_satir('🌟', 'YILDIZ FALI', font_size='24sp', height=dp(44)))
        
        # Giriş alanı
        giris = FloatLayout(size_hint=(1, 0.25))
        with giris.canvas:
            Color(*get_color_from_hex(RENKLER['lacivert']), 0.3)
            RoundedRectangle(pos=(15, 5), size=(giris.width-30, giris.height-10), radius=[15])
        
        aciklama = Label(
            text='Doğum tarihinizi girin\nburcunuzu ve yorumunuzu öğrenin!',
            font_size='15sp',
            color=get_color_from_hex(RENKLER['mavi_acik']),
            pos_hint={'center_x': 0.5, 'center_y': 0.75},
            halign='center'
        )
        giris.add_widget(aciklama)
        
        tarih_layout = BoxLayout(
            orientation='horizontal', 
            spacing=8,
            pos_hint={'center_x': 0.5, 'center_y': 0.35},
            size_hint=(0.9, 0.35)
        )
        
        self.gun_input = TextInput(
            hint_text='Gün',
            text='',
            font_size='18sp',
            multiline=False,
            input_filter='int',
            size_hint=(0.3, 1),
            background_color=get_color_from_hex(RENKLER['mor_koyu']),
            foreground_color=get_color_from_hex(RENKLER['beyaz']),
            hint_text_color=get_color_from_hex(RENKLER['gri_acik'])
        )
        
        self.ay_input = TextInput(
            hint_text='Ay',
            text='',
            font_size='18sp',
            multiline=False,
            input_filter='int',
            size_hint=(0.3, 1),
            background_color=get_color_from_hex(RENKLER['mor_koyu']),
            foreground_color=get_color_from_hex(RENKLER['beyaz']),
            hint_text_color=get_color_from_hex(RENKLER['gri_acik'])
        )
        
        self.yil_input = TextInput(
            hint_text='Yıl',
            text='',
            font_size='18sp',
            multiline=False,
            input_filter='int',
            size_hint=(0.4, 1),
            background_color=get_color_from_hex(RENKLER['mor_koyu']),
            foreground_color=get_color_from_hex(RENKLER['beyaz']),
            hint_text_color=get_color_from_hex(RENKLER['gri_acik'])
        )
        
        tarih_layout.add_widget(self.gun_input)
        tarih_layout.add_widget(self.ay_input)
        tarih_layout.add_widget(self.yil_input)
        giris.add_widget(tarih_layout)
        
        ana_layout.add_widget(giris)
        
        # Burç sonucu
        self.sonuc_layout = BoxLayout(size_hint=(1, 0.12))
        self.sonuc_label = Label(
            text='',
            font_size='17sp',
            color=get_color_from_hex(RENKLER['beyaz']),
            halign='center',
            markup=True
        )
        self.sonuc_layout.add_widget(self.sonuc_label)
        ana_layout.add_widget(self.sonuc_layout)
        
        # Butonlar
        buton_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.08),
            spacing=8
        )
        
        self.fal_buton = tus_buton('fal_bak', vurgu=True, font_size='15sp')
        self.fal_buton.bind(on_press=self.fal_bak)
        
        geri_buton = tus_buton('geri', font_size='13sp')
        geri_buton.bind(on_press=lambda x: setattr(self.manager, 'current', 'anasayfa'))
        
        buton_layout.add_widget(self.fal_buton)
        buton_layout.add_widget(geri_buton)
        ana_layout.add_widget(buton_layout)
        
        # Yorum alanı
        self.yorum_alani = ScrollView(size_hint=(1, 0.4))
        self.yorum_label = Label(
            text='[b][color={}]Doğum tarihinizi girip\n"Falıma Bak" butonuna tıklayın![/color][/b]'.format(RENKLER['gri_acik']),
            font_size='14sp',
            color=get_color_from_hex(RENKLER['beyaz']),
            size_hint_y=None,
            halign='center',
            valign='top',
            text_size=(370, None),
            markup=True,
            padding=(8, 8)
        )
        self.yorum_label.bind(texture_size=self.yorum_label.setter('size'))
        self.yorum_alani.add_widget(self.yorum_label)
        ana_layout.add_widget(self.yorum_alani)
        
        self.add_widget(ana_layout)
    
    def _guncelle_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
    
    def fal_bak(self, instance):
        """Doğum tarihine göre burç ve yorum göster"""
        try:
            gun_text = self.gun_input.text.strip()
            ay_text = self.ay_input.text.strip()
            yil_text = self.yil_input.text.strip()
            
            if not gun_text or not ay_text or not yil_text:
                self.sonuc_label.markup = True
                self.sonuc_label.text = f"[color={RENKLER['kirmizi']}]❌ Lütfen tüm alanları doldurun![/color]"
                self.yorum_label.text = ''
                return
            
            gun = int(gun_text)
            ay = int(ay_text)
            yil = int(yil_text)
            
            if not self.tarih_kontrol(gun, ay, yil):
                self.sonuc_label.markup = True
                self.sonuc_label.text = f"[color={RENKLER['kirmizi']}]❌ Geçersiz tarih! Lütfen\ngeçerli bir tarih girin.[/color]"
                self.yorum_label.text = ''
                return
            
            burc_adi = self.burc_bul(gun, ay)
            burc = BURCLAR[burc_adi]
            yorumlar = BURC_YORUMLARI[burc_adi]
            
            # Burç sonucu
            sonuc = f"{burc['sembol']} [b]BURCUNUZ: {burc_adi}[/b] {burc['sembol']}\n"
            sonuc += f"Element: {burc['element']}  |  Gezegen: {burc['gezegen']}\n"
            sonuc += f"{burc['tarih']}"
            
            self.sonuc_label.markup = True
            self.sonuc_label.text = sonuc
            
            # Detaylı yorum
            yorum = f"[b][color={RENKLER['altin']}]⭐ {burc_adi} BURCU YORUMU ⭐[/color][/b]\n\n"
            
            secilen_yorum = random.choice(yorumlar)
            yorum += f"[color={RENKLER['mavi_acik']}]{secilen_yorum}[/color]\n\n"
            
            # Şanslı sayı
            sansli_sayi = random.randint(1, 100)
            yorum += f"[b][color={RENKLER['altin']}]🍀 Şanslı Sayın: [color={RENKLER['yesil']}]{sansli_sayi}[/color][/color][/b]\n\n"
            
            # Günlük tavsiye
            yorum += f"[b][color={RENKLER['altin']}]💫 Günün Tavsiyesi:[/color][/b]\n"
            tavsiyeler = [
                "Bugün sezgilerinize güvenin! İç sesiniz sizi doğru yönlendirecek.",
                "Yeni insanlarla tanışmak için harika bir gün. Sosyal olun!",
                "Maddi konularda dikkatli kararlar alın. Acele etmeyin.",
                "Ailenizle vakit geçirin. Onlar size iyi gelecek.",
                "Kendinize zaman ayırın. Bir hobi edinin.",
                "Spor yapın ve sağlıklı beslenin. Vücudunuza iyi bakın.",
                "Meditasyon yapın. Zihninizi dinlendirin.",
                "Sevdiklerinize sürpriz yapın! Mutluluk paylaştıkça büyür."
            ]
            yorum += f"[color={RENKLER['gri_acik']}]{random.choice(tavsiyeler)}[/color]\n\n"
            
            yorum += f"[color={RENKLER['altin']}]📅 {date.today().strftime('%d.%m.%Y')}[/color]"
            
            self.yorum_label.markup = True
            self.yorum_label.text = yorum
            self._son_astro_yorum = yorum
            buton_metin_guncelle(self.fal_buton, yorum_bekle_metin())
            self.fal_buton.disabled = True

            def _ai_bitir(metin, ai_kullanildi, hata, kaynak=None, fotograf=False):
                self.yorum_label.text = yorum_sonuc_metni(
                    self._son_astro_yorum, metin, ai_kullanildi, hata, kaynak, fotograf,
                )
                buton_metin_guncelle(self.fal_buton, tus_metin('tekrar'))
                self.fal_buton.disabled = False

            yorum_al('astroloji', {
                'burc': burc_adi,
                'dogum': f'{gun:02d}.{ay:02d}.{yil}',
            }, _ai_bitir)
            
        except ValueError:
            self.sonuc_label.markup = True
            self.sonuc_label.text = f"[color={RENKLER['kirmizi']}]❌ Lütfen sayısal değerler girin![/color]"
            self.yorum_label.text = ''
        except Exception as e:
            self.sonuc_label.markup = True
            self.sonuc_label.text = f"[color={RENKLER['kirmizi']}]❌ Hata: {str(e)}[/color]"
            self.yorum_label.text = ''