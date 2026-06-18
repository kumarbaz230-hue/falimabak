"""
⭐ Yıldız Falı (Astroloji) Modülü - Düzeltilmiş Versiyon
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
import random
from datetime import date

from ai_yorum import yorum_al
from theme import (
    RENKLER, SAFE_UST, SAFE_ALT,
    tus_metin, yorum_bekle_metin, tus_buton, baslik_satir, buton_metin_guncelle,
    yorum_sonuc_metni, metin_label, guvenli_textinput, ekran_icerik_sar,
    kaydirici_metin, fontlari_yukle,
    fal_form_duz, yorum_panel_baslik,
)

fontlari_yukle()

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
        ana_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(4),
            padding=[dp(12), SAFE_UST, dp(12), SAFE_ALT],
        )
        ana_layout.add_widget(baslik_satir('🌟', 'YILDIZ FALI', font_size='24sp', height=dp(36)))

        form_panel, govde = fal_form_duz()

        govde.add_widget(metin_label(
            'Doğum tarihinizi girin — burcunuzu öğrenin!',
            font_size='12sp', color=RENKLER['mavi_acik'],
            halign='left', size_hint_y=None, height=dp(28),
        ))

        self.gun_input = guvenli_textinput(
            hint_text='Gün', input_filter='int', size_hint_x=0.28, height=dp(42),
        )
        self.ay_input = guvenli_textinput(
            hint_text='Ay', input_filter='int', size_hint_x=0.28, height=dp(42),
        )
        self.yil_input = guvenli_textinput(
            hint_text='Yıl', input_filter='int', size_hint_x=0.44, height=dp(42),
        )
        tarih_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(42),
            spacing=dp(8),
        )
        tarih_layout.add_widget(self.gun_input)
        tarih_layout.add_widget(self.ay_input)
        tarih_layout.add_widget(self.yil_input)
        govde.add_widget(tarih_layout)

        ana_layout.add_widget(form_panel)

        ana_layout.add_widget(yorum_panel_baslik('Burç yorumunuz'))
        self.yorum_alani, self.yorum_label = kaydirici_metin(1)
        self.yorum_label.text = (
            f'[b][color={RENKLER["gri_acik"]}]Doğum tarihinizi girip\n'
            f'"Falıma Bak" butonuna tıklayın![/color][/b]'
        )
        self.yorum_label.markup = True
        ana_layout.add_widget(self.yorum_alani)

        buton_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(46),
            spacing=dp(8),
        )
        self.fal_buton = tus_buton('fal_bak', vurgu=True, font_size='15sp')
        self.fal_buton.bind(on_press=self.fal_bak)
        geri_buton = tus_buton('geri', font_size='13sp')
        geri_buton.bind(on_press=lambda x: setattr(self.manager, 'current', 'anasayfa'))
        buton_layout.add_widget(self.fal_buton)
        buton_layout.add_widget(geri_buton)
        ana_layout.add_widget(buton_layout)

        ekran_icerik_sar(self, ana_layout)
    
    def fal_bak(self, instance):
        """Doğum tarihine göre burç ve yorum göster"""
        try:
            gun_text = self.gun_input.text.strip()
            ay_text = self.ay_input.text.strip()
            yil_text = self.yil_input.text.strip()
            
            if not gun_text or not ay_text or not yil_text:
                self.yorum_label.markup = True
                self.yorum_label.text = f"[color={RENKLER['kirmizi']}]Lütfen tüm alanları doldurun![/color]"
                return
            
            gun = int(gun_text)
            ay = int(ay_text)
            yil = int(yil_text)
            
            if not self.tarih_kontrol(gun, ay, yil):
                self.yorum_label.markup = True
                self.yorum_label.text = f"[color={RENKLER['kirmizi']}]Geçersiz tarih! Lütfen geçerli bir tarih girin.[/color]"
                return

            from fal_limit import yorum_baslat
            yorum_baslat('astroloji', lambda: self._fal_bak_devam(gun, ay, yil))
            
        except ValueError:
            self.yorum_label.markup = True
            self.yorum_label.text = f"[color={RENKLER['kirmizi']}]Lütfen sayısal değerler girin![/color]"
        except Exception as e:
            self.yorum_label.markup = True
            self.yorum_label.text = f"[color={RENKLER['kirmizi']}]Hata: {str(e)}[/color]"

    def _fal_bak_devam(self, gun, ay, yil):
        burc_adi = self.burc_bul(gun, ay)
        burc = BURCLAR[burc_adi]
        yorumlar = BURC_YORUMLARI[burc_adi]

        sonuc = f"{burc['sembol']} [b]BURCUNUZ: {burc_adi}[/b] {burc['sembol']}\n"
        sonuc += f"Element: {burc['element']}  |  Gezegen: {burc['gezegen']}\n"
        sonuc += f"{burc['tarih']}\n\n"

        yorum = f"[b][color={RENKLER['altin']}]⭐ {burc_adi} BURCU YORUMU ⭐[/color][/b]\n\n"
        yorum = sonuc + yorum
        secilen_yorum = random.choice(yorumlar)
        yorum += f"[color={RENKLER['mavi_acik']}]{secilen_yorum}[/color]\n\n"

        sansli_sayi = random.randint(1, 100)
        yorum += f"[b][color={RENKLER['altin']}]🍀 Şanslı Sayın: [color={RENKLER['yesil']}]{sansli_sayi}[/color][/color][/b]\n\n"
        yorum += f"[b][color={RENKLER['altin']}]💫 Günün Tavsiyesi:[/color][/b]\n"
        tavsiyeler = [
            "Bugün sezgilerinize güvenin! İç sesiniz sizi doğru yönlendirecek.",
            "Yeni insanlarla tanışmak için harika bir gün. Sosyal olun!",
            "Maddi konularda dikkatli kararlar alın. Acele etmeyin.",
            "Ailenizle vakit geçirin. Onlar size iyi gelecek.",
            "Kendinize zaman ayırın. Bir hobi edinin.",
            "Spor yapın ve sağlıklı beslenin. Vücudunuza iyi bakın.",
            "Meditasyon yapın. Zihninizi dinlendirin.",
            "Sevdiklerinize sürpriz yapın! Mutluluk paylaştıkça büyür.",
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
        }, _ai_bitir, coin_dahil=False)