"""FalımaBak — Uygulama ayarları (API key kullanıcıdan istenmez)."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.utils import get_color_from_hex
from kivy.metrics import dp

from theme import (
    RENKLER, SAFE_UST, SAFE_ALT,
    metin_label, baslik_satir, siyah_buton, alt_nav_bar, ekran_icerik_sar,
    guvenli_textinput,
)
from ai_yorum import _ayar_yukle, config_kaydet, bulut_ai_hazir_mi, ai_durum_metni
from gecmis import kullanici_ismi, isim_guncelle, gecmis_temizle


class AyarlarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._kur()

    def _kur(self):
        ana = BoxLayout(orientation='vertical', padding=[dp(12), SAFE_UST, dp(12), 0], spacing=dp(10))
        ana.add_widget(baslik_satir('', 'Ayarlar', font_size='22sp', height=dp(40)))

        ana.add_widget(metin_label(
            'FalımaBak Yorumlama',
            font_size='15sp', bold=True, color=RENKLER['altin'],
            size_hint_y=None, height=dp(24),
        ))
        self._ai_durum = metin_label(
            '', font_size='12sp', color=RENKLER['gri_acik'],
            size_hint_y=None, height=dp(40),
        )
        ana.add_widget(self._ai_durum)

        ana.add_widget(metin_label(
            'Adınız',
            font_size='15sp', bold=True, color=RENKLER['altin'],
            size_hint_y=None, height=dp(24),
        ))
        self._isim_input = guvenli_textinput(hint_text='İsteğe bağlı — yorumlarda kullanılır')
        ana.add_widget(self._isim_input)

        ana.add_widget(metin_label(
            'Yorum tercihi',
            font_size='15sp', bold=True, color=RENKLER['altin'],
            size_hint_y=None, height=dp(24),
        ))
        self._mod_spinner = Spinner(
            text='otomatik',
            values=('otomatik', 'offline'),
            size_hint_y=None,
            height=dp(44),
            background_color=get_color_from_hex(RENKLER['kart_arka_cam']),
            color=get_color_from_hex(RENKLER['beyaz']),
            font_size='14sp',
        )
        ana.add_widget(self._mod_spinner)
        ana.add_widget(metin_label(
            'otomatik = yapay zeka yorumu | offline = sadece hazır yorum',
            font_size='11sp', color=RENKLER['gri_koyu'],
            size_hint_y=None, height=dp(32),
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
            'FalımaBak v1.0.7 · Bulut AI',
            font_size='10sp', color=RENKLER['gri_koyu'],
            halign='center', size_hint_y=None, height=dp(18),
        ))
        ana.add_widget(alt_nav_bar('ayarlar', on_sec=self._nav))
        ekran_icerik_sar(self, ana)

    def on_enter(self, *_):
        self._yukle()

    def _yukle(self):
        ayar = _ayar_yukle()
        self._isim_input.text = kullanici_ismi()
        mod = (ayar.get('ai_mod') or 'otomatik').lower()
        if mod == 'gemini':
            mod = 'otomatik'
        if mod in self._mod_spinner.values:
            self._mod_spinner.text = mod
        if bulut_ai_hazir_mi():
            self._ai_durum.text = f'{ai_durum_metni()}\nYapay zeka yorumları aktif.'
            self._ai_durum.color = get_color_from_hex(RENKLER['yesil'])
        else:
            self._ai_durum.text = 'Bulut yapay zeka şu an kullanılamıyor.\nHazır yorumlar gösterilir.'
            self._ai_durum.color = get_color_from_hex(RENKLER['turuncu'])
        self._mesaj.text = ''

    def _kaydet(self, *_):
        mod = self._mod_spinner.text.strip().lower()
        guncelle = {'ai_mod': mod, 'ai_aktif': mod != 'offline'}
        isim = self._isim_input.text.strip()
        if isim:
            isim_guncelle(isim)
        elif not isim:
            isim_guncelle('')
        if config_kaydet(guncelle):
            self._mesaj.text = 'Ayarlar kaydedildi'
            self._mesaj.color = get_color_from_hex(RENKLER['yesil'])
            self._yukle()
        else:
            self._mesaj.text = 'Kayıt başarısız'
            self._mesaj.color = get_color_from_hex(RENKLER['kirmizi'])

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
