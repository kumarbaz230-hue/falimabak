"""FalımaBak — Ayarlar ekranı (Gemini API key + AI modu)."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.utils import get_color_from_hex
from kivy.metrics import dp

from theme import (
    RENKLER, FON_ADI, SAFE_UST, SAFE_ALT,
    metin_label, baslik_satir, siyah_buton, alt_nav_bar, ekran_icerik_sar,
)
from ai_yorum import _ayar_yukle, config_kaydet, gemini_key_kisa, bulut_ai_hazir_mi, ai_durum_metni


class AyarlarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._kur()

    def _kur(self):
        ana = BoxLayout(orientation='vertical', padding=[dp(12), SAFE_UST, dp(12), 0], spacing=dp(10))
        ana.add_widget(baslik_satir('⚙️', 'Ayarlar', font_size='22sp', height=dp(40)))

        ana.add_widget(metin_label(
            'Gemini API Key',
            font_size='15sp', bold=True, color=RENKLER['altin'],
            size_hint_y=None, height=dp(24),
        ))
        ana.add_widget(metin_label(
            'Google AI Studio\'dan aldığın anahtarı yapıştır.\n'
            'Key sadece telefonunda saklanır; GitHub\'a gitmez.',
            font_size='12sp', color=RENKLER['gri_acik'],
            size_hint_y=None, height=dp(44),
        ))

        self._key_input = TextInput(
            hint_text='AQ.... veya AIzaSy....',
            font_name=FON_ADI,
            font_size='14sp',
            multiline=False,
            password=True,
            size_hint_y=None,
            height=dp(46),
            padding=[dp(12), dp(12)],
            background_color=get_color_from_hex(RENKLER['kart_arka']),
            foreground_color=get_color_from_hex(RENKLER['beyaz']),
            hint_text_color=get_color_from_hex(RENKLER['gri']),
        )
        ana.add_widget(self._key_input)

        self._durum = metin_label(
            '', font_size='12sp', color=RENKLER['gri'],
            size_hint_y=None, height=dp(22),
        )
        ana.add_widget(self._durum)

        ana.add_widget(metin_label(
            'AI Modu',
            font_size='15sp', bold=True, color=RENKLER['altin'],
            size_hint_y=None, height=dp(24),
        ))
        self._mod_spinner = Spinner(
            text='otomatik',
            values=('otomatik', 'gemini', 'offline'),
            size_hint_y=None,
            height=dp(44),
            background_color=get_color_from_hex(RENKLER['kart_arka_cam']),
            color=get_color_from_hex(RENKLER['beyaz']),
            font_name=FON_ADI,
            font_size='14sp',
        )
        ana.add_widget(self._mod_spinner)

        ana.add_widget(metin_label(
            'otomatik = bulut varsa Gemini, yoksa hazır yorum\n'
            'gemini = sadece bulut | offline = sadece hazır yorum',
            font_size='11sp', color=RENKLER['gri_koyu'],
            size_hint_y=None, height=dp(36),
        ))

        kaydet_btn = siyah_buton('Kaydet', vurgu=True, font_size='15sp')
        kaydet_btn.bind(on_press=self._kaydet)
        ana.add_widget(kaydet_btn)

        self._mesaj = metin_label(
            '', font_size='13sp', color=RENKLER['yesil'],
            halign='center', size_hint_y=None, height=dp(28),
        )
        ana.add_widget(self._mesaj)

        ana.add_widget(BoxLayout(size_hint_y=1))
        ana.add_widget(alt_nav_bar('ayarlar', on_sec=self._nav))
        ekran_icerik_sar(self, ana)

    def on_enter(self, *_):
        self._yukle()

    def _yukle(self):
        ayar = _ayar_yukle()
        self._key_input.text = ''
        key_var = ayar.get('gemini_api_key', '')
        if key_var:
            self._durum.text = f'Mevcut key: {gemini_key_kisa(ayar)}'
            self._durum.color = get_color_from_hex(RENKLER['yesil'])
        else:
            self._durum.text = 'Henüz API key girilmedi'
            self._durum.color = get_color_from_hex(RENKLER['turuncu'])
        mod = (ayar.get('ai_mod') or 'otomatik').lower()
        if mod in self._mod_spinner.values:
            self._mod_spinner.text = mod
        self._mesaj.text = ai_durum_metni() if bulut_ai_hazir_mi() else 'Bulut AI için key gerekli'

    def _kaydet(self, *_):
        guncelle = {'ai_mod': self._mod_spinner.text.strip().lower()}
        yeni_key = self._key_input.text.strip()
        if yeni_key:
            guncelle['gemini_api_key'] = yeni_key
        if config_kaydet(guncelle):
            self._mesaj.text = '✓ Ayarlar kaydedildi'
            self._mesaj.color = get_color_from_hex(RENKLER['yesil'])
            self._yukle()
        else:
            self._mesaj.text = 'Kayıt başarısız'
            self._mesaj.color = get_color_from_hex(RENKLER['kirmizi'])

    def _nav(self, hedef):
        if not self.manager:
            return
        if hedef == 'anasayfa':
            self.manager.current = 'anasayfa'
        elif hedef == 'gecmis':
            self.manager.current = 'gecmis'
