"""FalımaBak — Uygulama ayarları."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex
from kivy.metrics import dp

from theme import (
    RENKLER, SAFE_UST, SAFE_ALT,
    metin_label, baslik_satir, siyah_buton, alt_nav_bar, ekran_icerik_sar,
    guvenli_textinput,
)
from gecmis import kullanici_ismi, isim_guncelle, gecmis_temizle
from ai_yorum import config_kaydet, _ayar_yukle, gemini_key_kisa


class AyarlarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._kur()

    def _kur(self):
        ana = BoxLayout(orientation='vertical', padding=[dp(12), SAFE_UST, dp(12), 0], spacing=dp(10))
        ana.add_widget(baslik_satir('', 'Ayarlar', font_size='22sp', height=dp(40)))

        ana.add_widget(metin_label(
            'Adınız',
            font_size='15sp', bold=True, color=RENKLER['altin'],
            size_hint_y=None, height=dp(24),
        ))
        self._isim_input = guvenli_textinput(hint_text='İsteğe bağlı — yorumlarda kullanılır')
        ana.add_widget(self._isim_input)

        ana.add_widget(metin_label(
            'Yapay zeka anahtarı (isteğe bağlı)',
            font_size='15sp', bold=True, color=RENKLER['altin'],
            size_hint_y=None, height=dp(24),
        ))
        self._api_input = guvenli_textinput(
            hint_text='Boş bırakılırsa uygulama anahtarı kullanılır',
            password=True,
        )
        ana.add_widget(self._api_input)
        ana.add_widget(metin_label(
            'AI çalışmazsa aistudio.google.com/apikey adresinden AIzaSy ile başlayan key alıp buraya yapıştırın.',
            font_size='11sp', color=RENKLER['gri_acik'],
            size_hint_y=None, height=dp(36),
        ))

        kaydet_btn = siyah_buton('Kaydet', vurgu=True, font_size='15sp')
        kaydet_btn.bind(on_press=self._kaydet)
        ana.add_widget(kaydet_btn)

        temizle_btn = siyah_buton('Fal geçmişini temizle', font_size='14sp')
        temizle_btn.bind(on_press=self._gecmis_temizle)
        ana.add_widget(temizle_btn)

        self._mesaj = metin_label(
            '', font_size='13sp', color=RENKLER['yesil'],
            halign='center', size_hint_y=None, height=dp(28),
        )
        ana.add_widget(self._mesaj)

        ana.add_widget(BoxLayout(size_hint_y=1))
        ana.add_widget(metin_label(
            'FalımaBak v1.0.12',
            font_size='10sp', color=RENKLER['gri_koyu'],
            halign='center', size_hint_y=None, height=dp(18),
        ))
        ana.add_widget(alt_nav_bar('ayarlar', on_sec=self._nav))
        ekran_icerik_sar(self, ana)

    def on_enter(self, *_):
        self._yukle()

    def _yukle(self):
        self._isim_input.text = kullanici_ismi()
        ayar = _ayar_yukle()
        mevcut = (ayar.get('gemini_api_key') or '').strip()
        self._api_input.text = mevcut
        kisa = gemini_key_kisa(ayar)
        if kisa and not mevcut:
            self._api_input.hint_text = f'Uygulama anahtarı aktif ({kisa})'
        self._mesaj.text = ''

    def _kaydet(self, *_):
        isim = self._isim_input.text.strip()
        isim_guncelle(isim)
        api = self._api_input.text.strip()
        config_kaydet({'gemini_api_key': api})
        self._mesaj.text = 'Ayarlar kaydedildi'
        self._mesaj.color = get_color_from_hex(RENKLER['yesil'])

    def _gecmis_temizle(self, *_):
        if gecmis_temizle():
            self._mesaj.text = 'Fal geçmişi temizlendi'
            self._mesaj.color = get_color_from_hex(RENKLER['yesil'])
        else:
            self._mesaj.text = 'Temizleme başarısız'
            self._mesaj.color = get_color_from_hex(RENKLER['kirmizi'])

    def _nav(self, hedef):
        if not self.manager:
            return
        if hedef == 'anasayfa':
            self.manager.current = 'anasayfa'
        elif hedef == 'gecmis':
            self.manager.current = 'gecmis'
