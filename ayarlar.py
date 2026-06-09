"""FalımaBak — Uygulama ayarları (premium kart düzeni)."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex
from kivy.metrics import dp

from theme import (
    RENKLER, SAFE_UST,
    metin_label, baslik_satir, siyah_buton, alt_nav_bar, ekran_icerik_sar,
    guvenli_textinput, kart_zemin_bagla,
)
from gecmis import kullanici_ismi, isim_guncelle, gecmis_temizle
from ai_yorum import config_kaydet, _ayar_yukle, gemini_key_kisa

_SURUM = '1.0.14'


def _ayar_karti(baslik, alt_baslik=None):
    kart = BoxLayout(
        orientation='vertical',
        size_hint_y=None,
        spacing=dp(10),
        padding=[dp(16), dp(14), dp(16), dp(14)],
    )
    kart_zemin_bagla(kart, radius=16)
    kart.add_widget(metin_label(
        baslik, font_size='16sp', bold=True, color=RENKLER['altin'],
        halign='left', size_hint_y=None, height=dp(22),
    ))
    if alt_baslik:
        kart.add_widget(metin_label(
            alt_baslik, font_size='11sp', color=RENKLER['gri_acik'],
            halign='left', size_hint_y=None, height=dp(32),
        ))
    return kart


class AyarlarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._kur()

    def _kur(self):
        ana = BoxLayout(orientation='vertical', padding=[dp(12), SAFE_UST, dp(12), 0], spacing=dp(12))
        ana.add_widget(baslik_satir('', 'Ayarlar', font_size='22sp', height=dp(40)))

        profil = _ayar_karti('Profil', 'Adınız yorumlarda kişiselleştirme için kullanılır.')
        self._isim_input = guvenli_textinput(hint_text='İsteğe bağlı')
        profil.add_widget(self._isim_input)
        profil.height = dp(130)
        ana.add_widget(profil)

        ai_kart = _ayar_karti(
            'Gelişmiş — Yapay zeka',
            'Boş bırakırsanız uygulama anahtarı veya cihaz içi yorum kullanılır.',
        )
        self._api_input = guvenli_textinput(
            hint_text='Gemini API anahtarı (isteğe bağlı)',
            password=True,
        )
        ai_kart.add_widget(self._api_input)
        ai_kart.add_widget(metin_label(
            'aistudio.google.com/apikey — AIzaSy ile başlayan anahtar.',
            font_size='10sp', color=RENKLER['gri_koyu'],
            size_hint_y=None, height=dp(28),
        ))
        ai_kart.height = dp(168)
        ana.add_widget(ai_kart)

        islem = _ayar_karti('Veri ve geçmiş')
        kaydet_btn = siyah_buton('Ayarları kaydet', vurgu=True, font_size='15sp')
        kaydet_btn.bind(on_press=self._kaydet)
        islem.add_widget(kaydet_btn)
        temizle_btn = siyah_buton('Fal geçmişini temizle', font_size='14sp')
        temizle_btn.bind(on_press=self._gecmis_temizle)
        islem.add_widget(temizle_btn)
        islem.height = dp(148)
        ana.add_widget(islem)

        self._mesaj = metin_label(
            '', font_size='13sp', color=RENKLER['yesil'],
            halign='center', size_hint_y=None, height=dp(28),
        )
        ana.add_widget(self._mesaj)

        ana.add_widget(BoxLayout(size_hint_y=1))
        ana.add_widget(metin_label(
            f'FalımaBak v{_SURUM} · Premium',
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
