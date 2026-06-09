"""FalımaBak — Ayarlar (dil + profil)."""

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.utils import get_color_from_hex
from kivy.metrics import dp

from theme import (
    RENKLER, SAFE_UST,
    metin_label, baslik_satir, siyah_buton, alt_nav_bar, ekran_icerik_sar,
    guvenli_textinput, kart_zemin_bagla,
)
from gecmis import kullanici_ismi, isim_guncelle, gecmis_temizle, dil_al
from dil import t, dil_listesi, dil_etiket, dil_degistir

_SURUM = '1.0.17'


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
        ana.add_widget(baslik_satir('', t('settings_title'), font_size='22sp', height=dp(40)))

        dil_kart = _ayar_karti(t('settings_lang'), t('settings_lang_hint'))
        self._dil_spinner = Spinner(
            text=dil_etiket(dil_al()),
            values=[etik for _, etik in dil_listesi()],
            size_hint_y=None,
            height=dp(44),
            background_color=get_color_from_hex(RENKLER['kart_arka_cam']),
            color=get_color_from_hex(RENKLER['beyaz']),
        )
        dil_kart.add_widget(self._dil_spinner)
        dil_kart.height = dp(130)
        ana.add_widget(dil_kart)

        profil = _ayar_karti(t('settings_profile'), t('settings_profile_hint'))
        self._isim_input = guvenli_textinput(hint_text=t('settings_name_hint'))
        profil.add_widget(self._isim_input)
        profil.height = dp(130)
        ana.add_widget(profil)

        islem = _ayar_karti(t('settings_data'))
        kaydet_btn = siyah_buton(t('settings_save'), vurgu=True, font_size='15sp')
        kaydet_btn.bind(on_press=self._kaydet)
        islem.add_widget(kaydet_btn)
        temizle_btn = siyah_buton(t('settings_clear'), font_size='14sp')
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
            f'FalımaBak v{_SURUM}',
            font_size='10sp', color=RENKLER['gri_koyu'],
            halign='center', size_hint_y=None, height=dp(18),
        ))
        ana.add_widget(alt_nav_bar('ayarlar', on_sec=self._nav))
        ekran_icerik_sar(self, ana)

    def on_enter(self, *_):
        self._yukle()

    def _yukle(self):
        self._isim_input.text = kullanici_ismi()
        self._dil_spinner.text = dil_etiket(dil_al())
        self._mesaj.text = ''

    def _secili_dil_kodu(self):
        etik = self._dil_spinner.text
        for kod, label in dil_listesi():
            if label == etik:
                return kod
        return dil_al()

    def _kaydet(self, *_):
        eski_dil = dil_al()
        yeni = self._secili_dil_kodu()
        dil_degistir(yeni)
        isim_guncelle(self._isim_input.text.strip())
        self._mesaj.text = t('settings_saved')
        self._mesaj.color = get_color_from_hex(RENKLER['yesil'])
        if yeni != eski_dil:
            app = App.get_running_app()
            if app and hasattr(app, 'ekranlari_yenile_dil'):
                app.ekranlari_yenile_dil()

    def _gecmis_temizle(self, *_):
        if gecmis_temizle():
            self._mesaj.text = t('settings_cleared')
            self._mesaj.color = get_color_from_hex(RENKLER['yesil'])
        else:
            self._mesaj.text = t('settings_clear_fail')
            self._mesaj.color = get_color_from_hex(RENKLER['kirmizi'])

    def _nav(self, hedef):
        if not self.manager:
            return
        if hedef == 'anasayfa':
            self.manager.current = 'anasayfa'
        elif hedef == 'gecmis':
            self.manager.current = 'gecmis'
