"""
👐 El Falı Modülü - Kamera Entegrasyonlu
Kullanıcı elini fotoğraflar, yapay zeka çizgileri okur!
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse, Line
from kivy.utils import get_color_from_hex
from kivy.animation import Animation, Sequence
from kivy.clock import Clock
from kivy.metrics import dp
import random

from theme import (
    RENKLER, TUS, YORUM_BEKLE, fontlari_yukle, metin_label,
    tus_buton, baslik_satir, buton_metin_guncelle, yorum_baslik, yorum_durum_notu,
    kaydirici_metin, FotoKutucukPanel,
)
from kamera import galeriden_sec, kameradan_cek
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
    'ten': '#ffccbc',
}

# El falı çizgi veritabanı (24 farklı çizgi)
EL_CIZGILERI = [
    {
        'isim': 'Hayat Çizgisi',
        'ikon': '🌿',
        'pozitif': 'Uzun ve sağlıklı bir yaşam süreceksiniz! Enerjiniz yüksek, hastalıklara karşı dirençlisiniz.',
        'negatif': 'Sağlığınıza daha fazla dikkat etmelisiniz. Düzenli check-up yaptırın.',
        'ipucu': 'Baş parmağınızın etrafındaki kavis'
    },
    {
        'isim': 'Kader Çizgisi',
        'ikon': '⭐',
        'pozitif': 'Büyük başarılara imza atacaksınız! Kariyerinizde beklenmedik yükseliş.',
        'negatif': 'Kariyerinizde bazı engeller olabilir. Sabırlı olun, başarı gelecek.',
        'ipucu': 'Orta parmaktan bileğe doğru'
    },
    {
        'isim': 'Kalp Çizgisi',
        'ikon': '💖',
        'pozitif': 'Büyük bir aşk yaşayacaksınız! Kalbiniz sevgiyle dolu.',
        'negatif': 'Aşk hayatınızda dikkatli olun. Yanlış kişilere güvenmeyin.',
        'ipucu': 'Serçe parmak altından işaret parmağına'
    },
    {
        'isim': 'Akıl Çizgisi',
        'ikon': '🧠',
        'pozitif': 'Zekanız ve analitik düşüncenizle herkesi şaşırtacaksınız!',
        'negatif': 'Aşırı düşünmekten karar veremiyorsunuz. Biraz rahatlayın.',
        'ipucu': 'İşaret parmağından avuç içine'
    },
    {
        'isim': 'Güneş Çizgisi',
        'ikon': '☀️',
        'pozitif': 'Yeteneklerinizle herkesin hayranlığını kazanacaksınız!',
        'negatif': 'Kendinizi göstermekten çekiniyorsunuz. Cesur olun!',
        'ipucu': 'Yüzük parmağına doğru'
    },
    {
        'isim': 'Sezgi Çizgisi',
        'ikon': '🔮',
        'pozitif': 'Sezgileriniz çok güçlü! Medyumluk yeteneğiniz var.',
        'negatif': 'İç sesinizi dinlemiyorsunuz. Sezgilerinize güvenin.',
        'ipucu': 'Avuç kenarında kavis'
    },
    {
        'isim': 'Evlilik Çizgisi',
        'ikon': '💍',
        'pozitif': 'EVLİLİK HABERİ GELİYOR! Parmakta yüzük göreceksiniz.',
        'negatif': 'İlişkinizde bir kriz olabilir. Sabır ve anlayış gösterin.',
        'ipucu': 'Serçe parmak altında yatay'
    },
    {
        'isim': 'Para Çizgisi',
        'ikon': '💰',
        'pozitif': 'BÜYÜK PARA! Beklenmedik bir miras veya yatırım kazancı.',
        'negatif': 'Maddi konularda dikkatli olun. Gereksiz harcamalardan kaçının.',
        'ipucu': 'Kalp ve akıl çizgisi arası'
    },
    {
        'isim': 'Sağlık Çizgisi',
        'ikon': '🏥',
        'pozitif': 'Sağlığınız yerinde! Spor ve sağlıklı yaşam size iyi geliyor.',
        'negatif': 'Sağlık sorunlarına karşı dikkatli olun. Düzenli beslenin.',
        'ipucu': 'Küçük parmak altından bileğe'
    },
    {
        'isim': 'Yolculuk Çizgisi',
        'ikon': '✈️',
        'pozitif': 'HARİKA BİR SEYAHAT! Yurt dışı veya egzotik bir tatil sizi bekliyor.',
        'negatif': 'Seyahat planlarınız ertelenebilir. Alternatif tarihler düşünün.',
        'ipucu': 'Avuç içi altında yatay'
    },
    {
        'isim': 'Merkür Çizgisi',
        'ikon': '📢',
        'pozitif': 'İletişim yeteneğinizle iş hayatında fırtınalar estireceksiniz!',
        'negatif': 'Yanlış anlaşılmalara karşı dikkatli olun. Sözlerinizi seçin.',
        'ipucu': 'Küçük parmak altında'
    },
    {
        'isim': 'Çocuk Çizgisi',
        'ikon': '👶',
        'pozitif': 'Aileye yeni bir üye katılabilir! Müjdeli haber yakında.',
        'negatif': 'Çocuk sahibi olma konusunda biraz daha bekleyebilirsiniz.',
        'ipucu': 'Evlilik çizgisinden yukarı'
    },
    {
        'isim': 'Bileklik Çizgisi',
        'ikon': '📿',
        'pozitif': 'Uzun ömür ve sağlık! Bileklik çizginiz ne kadar belirginse şans o kadar büyük.',
        'negatif': 'Enerjiniz düşük. Dinlenmeye ve iyi beslenmeye özen gösterin.',
        'ipucu': 'Bilekteki yatay çizgiler'
    },
    {
        'isim': 'Satürn Çizgisi',
        'ikon': '🪐',
        'pozitif': 'Kariyerinizde disiplin ve başarı! Uzun vadeli hedeflerinize ulaşacaksınız.',
        'negatif': 'Aşırı sorumluluk sizi yoruyor. Biraz eğlenmeyi unutmayın.',
        'ipucu': 'Orta parmak altında dikey'
    },
    {
        'isim': 'Apollon Çizgisi',
        'ikon': '🎭',
        'pozitif': 'Yaratıcılık ve sanat! Yeteneklerinizle herkesi büyüleyeceksiniz.',
        'negatif': 'Yaratıcılığınız bloke olmuş. Yeni ilham kaynakları arayın.',
        'ipucu': 'Yüzük parmağına doğru yükselen'
    },
    {
        'isim': 'Venüs Çizgisi',
        'ikon': '💕',
        'pozitif': 'Aşk ve çekicilik! Karşı cins üzerinde büyük etki bırakıyorsunuz.',
        'negatif': 'Aşık olmaktan korkuyorsunuz. Kalbinizi açmaya cesaret edin.',
        'ipucu': 'Baş parmak çevresinde'
    },
    {
        'isim': 'Mars Çizgisi',
        'ikon': '⚔️',
        'pozitif': 'Cesaret ve savaşçı ruh! Her engeli aşacak güce sahipsiniz.',
        'negatif': 'Öfkenizi kontrol etmeyi öğrenmelisiniz. Sakin kalın.',
        'ipucu': 'Avuç içi ortasında'
    },
    {
        'isim': 'Ay Çizgisi',
        'ikon': '🌙',
        'pozitif': 'İç huzur ve maneviyat! Meditasyon size çok iyi gelecek.',
        'negatif': 'Rüyalarınız size mesaj veriyor. Dikkatle dinleyin.',
        'ipucu': 'Avuç kenarında aşağı'
    },
]

# El tipleri
EL_TIPLERI = [
    {
        'tip': 'Hava Eli 🖐️',
        'ozellik': 'Kare avuç, uzun parmaklar',
        'karakter': 'Zeki, iletişimci, meraklı, yaratıcı',
        'meslek': 'Yazar, sanatçı, öğretmen, mucit'
    },
    {
        'tip': 'Ateş Eli 🔥',
        'ozellik': 'Uzun avuç, kısa parmaklar',
        'karakter': 'Cesur, enerjik, lider, maceracı',
        'meslek': 'Girişimci, yönetici, cerrah, pilot'
    },
    {
        'tip': 'Toprak Eli 🌍',
        'ozellik': 'Kare avuç, kısa parmaklar',
        'karakter': 'Sabırlı, güvenilir, pratik, çalışkan',
        'meslek': 'Mühendis, doktor, çiftçi, mimar'
    },
    {
        'tip': 'Su Eli 💧',
        'ozellik': 'Uzun avuç, ince parmaklar',
        'karakter': 'Sezgisel, duygusal, empatik, sanatçı',
        'meslek': 'Psikolog, müzisyen, şair, ressam'
    }
]

EL_FOTO_SLOT = [
    {'anahtar': 'avuc_ici', 'baslik': 'Avuç İçi', 'ikon': '🖐️'},
    {'anahtar': 'el_disi', 'baslik': 'El Dışı', 'ikon': '✋'},
]


class ElFaliScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        with self.canvas.before:
            Color(*get_color_from_hex(RENKLER['arka_plan']))
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._guncelle_rect, pos=self._guncelle_rect)
            
        ana_layout = BoxLayout(orientation='vertical', spacing=6, padding=10)
        
        ana_layout.add_widget(baslik_satir('✋', 'EL FALI', font_size='24sp', height=dp(44)))
        
        ana_layout.add_widget(metin_label(
            'Avuç içi ve el dışı fotoğrafı ekleyin. Kutuya dokunup galeri/kamera ile yükleyin.',
            font_size='12sp',
            color=RENKLER['gri_acik'],
            halign='center',
            size_hint_y=None,
            height=dp(36),
        ))

        self.foto_panel = FotoKutucukPanel(EL_FOTO_SLOT, yukseklik=dp(128))
        ana_layout.add_widget(self.foto_panel)

        btn_layout1 = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.08),
            spacing=8,
        )

        galeri_btn = tus_buton('galeri', font_size='13sp')
        galeri_btn.bind(on_press=lambda *_: galeriden_sec(self._foto_sonuc))

        kamera_btn = tus_buton('kamera', vurgu=True, font_size='13sp')
        kamera_btn.bind(on_press=lambda *_: kameradan_cek(self._foto_sonuc))

        self.fal_bak_btn = tus_buton('fal_bak', vurgu=True, font_size='13sp')
        self.fal_bak_btn.bind(on_press=self.fal_bak)
        
        btn_layout1.add_widget(galeri_btn)
        btn_layout1.add_widget(kamera_btn)
        btn_layout1.add_widget(self.fal_bak_btn)
        ana_layout.add_widget(btn_layout1)
        
        self.sonuc_alani, self.sonuc_label = kaydirici_metin(0.48)
        self.sonuc_label.halign = 'left'
        self.sonuc_label.text = (
            f'[b][color={RENKLER["gri_acik"]}]👐 Avuç içi + el dışı fotoğrafı ekleyin,\n'
            f'sonra el falı yorumunuzu alın![/color][/b]'
        )
        ana_layout.add_widget(self.sonuc_alani)
        
        # ALT BUTONLAR
        btn_layout2 = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.07),
            spacing=8
        )
        
        geri_buton = tus_buton('geri', font_size='13sp')
        geri_buton.bind(on_press=lambda x: setattr(self.manager, 'current', 'anasayfa'))
        
        btn_layout2.add_widget(geri_buton)
        ana_layout.add_widget(btn_layout2)
        
        self.add_widget(ana_layout)
    
    def _guncelle_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
    
    def _foto_sonuc(self, yol, hata):
        if hata:
            self.sonuc_label.markup = True
            self.sonuc_label.text = f"[color={RENKLER['kirmizi']}]❌ {hata}[/color]"
            return

        self.foto_panel.fotograf_ekle(yol)
        self.flas_yap()
    
    def flas_yap(self):
        """Flash efekti"""
        flash = FloatLayout(size_hint=(1, 1))
        with flash.canvas:
            Color(1, 1, 1, 1)
            Rectangle(size=self.size, pos=self.pos)
        self.add_widget(flash)
        anim = Animation(opacity=0, duration=0.2)
        anim.start(flash)
        Clock.schedule_once(lambda dt: self.remove_widget(flash) if flash in self.children else None, 0.2)
    
    def fal_bak(self, instance):
        """El falı yorumu"""
        if not self.foto_panel.tamam_mi():
            eksik = ', '.join(self.foto_panel.eksik_basliklar())
            self.sonuc_label.markup = True
            self.sonuc_label.text = (
                f"[color={RENKLER['kirmizi']}]Eksik fotoğraflar: {eksik}[/color]\n"
                f"[color={RENKLER['gri_acik']}]Her kutuya dokunup galeri veya kamera ile ekleyin.[/color]"
            )
            return
        
        # Animasyon
        anim = Sequence(
            Animation(opacity=0.5, duration=0.15),
            Animation(opacity=1, duration=0.25)
        )
        anim.start(self.sonuc_alani)
        
        # El tipi belirle
        el_tipi = random.choice(EL_TIPLERI)
        
        # Rastgele çizgiler seç (5-7 tane)
        secilen_sayisi = random.randint(5, 7)
        secilen_cizgiler = random.sample(EL_CIZGILERI, secilen_sayisi)
        
        # Sonuç oluştur
        sonuc = f"[b][color={RENKLER['altin']}]👐 EL FALINIZ HAZIR! 👐[/color][/b]\n\n"
        
        # El tipi
        sonuc += f"[b][color={RENKLER['pembe']}]📋 EL TİPİNİZ:[/color][/b]\n"
        sonuc += f"[color={RENKLER['altin']}]{el_tipi['tip']}[/color]\n"
        sonuc += f"[color={RENKLER['gri_acik']}]{el_tipi['ozellik']}[/color]\n"
        sonuc += f"Karakter: [color={RENKLER['gri_acik']}]{el_tipi['karakter']}[/color]\n"
        sonuc += f"Meslek: [color={RENKLER['gri_acik']}]{el_tipi['meslek']}[/color]\n\n"
        
        # Çizgiler
        sonuc += f"[b][color={RENKLER['altin']}]✋ ÇİZGİ ANALİZİ:[/color][/b]\n\n"
        
        for cizgi in secilen_cizgiler:
            durum = random.choice(['Pozitif', 'Negatif'])
            yorum = cizgi['pozitif'] if durum == 'Pozitif' else cizgi['negatif']
            renk = RENKLER['yesil'] if durum == 'Pozitif' else RENKLER['kirmizi']
            
            sonuc += f"[color={renk}]{cizgi['ikon']} [b]{cizgi['isim']}[/b] - ({durum})[/color]\n"
            sonuc += f"[color={RENKLER['gri_acik']}]{yorum}[/color]\n"
            sonuc += f"[i][color={RENKLER['mor_parlak']}]📍 {cizgi['ipucu']}[/color][/i]\n\n"
        
        # Genel yorum
        sonuc += f"[b][color={RENKLER['altin']}]💫 GENEL DEĞERLENDİRME:[/color][/b]\n"
        
        genel_yorumlar = [
            f"{el_tipi['tip']} tipine sahipsiniz. {el_tipi['karakter']} bir karakteriniz var. Size en uygun meslekler: {el_tipi['meslek']}.",
            "Elinizdeki çizgiler çok net ve belirgin. Hayatta ne istediğinizi biliyorsunuz!",
            "Avuç içinizdeki çizgiler karmaşık değil, bu sizin kararlı yapınızı gösteriyor.",
            "Çizgileriniz derin ve uzun. Uzun ve başarılı bir yaşam sizi bekliyor.",
            "Eliniz sıcak ve yumuşak. Duygusal ve sevgi dolu bir insansınız.",
            "Parmaklarınızın uzunluğu sanatsal yeteneklerinize işaret ediyor.",
            "Baş parmağınızın şekli güçlü bir iradeye sahip olduğunuzu gösteriyor."
        ]
        sonuc += f"[color={RENKLER['gri_acik']}]{random.choice(genel_yorumlar)}[/color]\n\n"
        
        sonuc += f"[b][color={RENKLER['altin']}]🔢 ŞANSLI SAYINIZ:[/color][/b] "
        sonuc += f"[color={RENKLER['yesil']}]{random.randint(1, 100)}[/color]"
        
        self.sonuc_label.markup = True
        self.sonuc_label.text = sonuc
        self._son_elfali_yorum = sonuc
        buton_metin_guncelle(self.fal_bak_btn, YORUM_BEKLE)
        self.fal_bak_btn.disabled = True

        def _ai_bitir(metin, ai_kullanildi, hata, kaynak=None, fotograf=False):
            baslik = yorum_baslik(ai_kullanildi, kaynak, fotograf)
            renk = RENKLER['pembe_acik'] if ai_kullanildi else RENKLER['gri_acik']
            self.sonuc_label.text = (
                self._son_elfali_yorum
                + f"\n\n[b][color={RENKLER['altin']}]» {baslik}[/color][/b]\n"
                + f"[color={renk}]{metin}[/color]"
                + yorum_durum_notu(hata, ai_kullanildi)
            )
            buton_metin_guncelle(self.fal_bak_btn, TUS['tekrar'])
            self.fal_bak_btn.disabled = False

        foto_veri = self.foto_panel.tum_veri()
        yorum_al('elfali', {
            'el_tipi': el_tipi['tip'],
            'cizgiler': [c['isim'] for c in secilen_cizgiler],
            **foto_veri,
        }, _ai_bitir)