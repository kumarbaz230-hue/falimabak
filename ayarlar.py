"""FalımaBak — Ayarlar (dil + profil)."""

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.utils import get_color_from_hex
from kivy.metrics import dp

from theme import (
    RENKLER, SAFE_UST, APP_SURUM,
    metin_label, baslik_satir, siyah_buton, alt_nav_bar, ekran_icerik_sar,
    guvenli_textinput, kart_zemin_bagla, klavye_kaydir_bagla,
)
from gecmis import (
    kullanici_ismi, isim_guncelle, gecmis_temizle, dil_al, muzik_acik_al, muzik_seviye_al,
    bildirim_acik_al, bildirim_acik_kaydet,
)
from dil import t, dil_listesi, dil_etiket, dil_degistir

_SURUM = APP_SURUM


def _ayar_karti(baslik, alt_baslik=None):
    kart = BoxLayout(
        orientation='vertical',
        size_hint_y=None,
        spacing=dp(10),
        padding=[dp(16), dp(16), dp(16), dp(16)],
    )
    kart_zemin_bagla(kart, radius=16)
    kart.add_widget(metin_label(
        baslik, font_size='16sp', bold=True, color=RENKLER['altin'],
        halign='left', size_hint_y=None, height=dp(24),
    ))
    if alt_baslik:
        alt = metin_label(
            alt_baslik, font_size='11sp', color=RENKLER['gri_acik'],
            halign='left', size_hint_y=None, height=dp(36),
        )

        def _alt_yukseklik(inst, *_):
            if inst.width > dp(8):
                inst.text_size = (inst.width, None)
                inst.height = max(inst.texture_size[1], dp(18))

        alt.bind(width=_alt_yukseklik, texture_size=_alt_yukseklik)
        kart.add_widget(alt)
    kart.bind(minimum_height=kart.setter('height'))
    return kart


class AyarlarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._kur()

    def _kur(self):
        ana = BoxLayout(orientation='vertical', padding=[dp(12), SAFE_UST, dp(12), 0], spacing=dp(8))

        kaydir = ScrollView(
            size_hint_y=1,
            do_scroll_x=False,
            bar_width=dp(3),
            bar_color=get_color_from_hex(RENKLER['mor_parlak']),
            bar_inactive_color=get_color_from_hex(RENKLER['kart_kenar']),
        )
        icerik = BoxLayout(
            orientation='vertical',
            spacing=dp(16),
            size_hint_y=None,
            padding=[0, 0, 0, dp(16)],
        )
        icerik.bind(minimum_height=icerik.setter('height'))

        icerik.add_widget(baslik_satir('', t('settings_title'), font_size='22sp', height=dp(40)))

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
        icerik.add_widget(dil_kart)

        profil = _ayar_karti(t('settings_profile'), t('settings_profile_hint'))
        self._isim_input = guvenli_textinput(hint_text=t('settings_name_hint'))
        profil.add_widget(self._isim_input)
        icerik.add_widget(profil)

        islem = _ayar_karti(t('settings_data'))
        kaydet_btn = siyah_buton(t('settings_save'), vurgu=True, font_size='15sp')
        kaydet_btn.bind(on_press=self._kaydet)
        islem.add_widget(kaydet_btn)
        temizle_btn = siyah_buton(t('settings_clear'), font_size='14sp')
        temizle_btn.bind(on_press=self._gecmis_temizle)
        islem.add_widget(temizle_btn)
        icerik.add_widget(islem)

        bildirim_kart = _ayar_karti(t('settings_notif'), t('settings_notif_hint'))
        from kivy.uix.checkbox import CheckBox
        bildirim_satir = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        self._bildirim_check = CheckBox(
            active=bildirim_acik_al(),
            size_hint_x=None,
            width=dp(40),
            color=get_color_from_hex(RENKLER['altin']),
        )
        self._bildirim_check.bind(active=self._bildirim_degisti)
        bildirim_satir.add_widget(self._bildirim_check)
        bildirim_etiket = metin_label(
            t('settings_notif_on'), font_size='14sp', color=RENKLER['beyaz'],
            halign='left', valign='middle', size_hint_x=1,
        )
        bildirim_satir.add_widget(bildirim_etiket)
        bildirim_kart.add_widget(bildirim_satir)
        icerik.add_widget(bildirim_kart)

        hukuk = _ayar_karti(t('settings_legal'), t('settings_legal_hint'))
        gizlilik_btn = siyah_buton(t('settings_privacy'), font_size='14sp')
        gizlilik_btn.bind(on_press=self._gizlilik_ac)
        hukuk.add_widget(gizlilik_btn)
        deger_btn = siyah_buton(t('settings_rate'), vurgu=True, font_size='14sp')
        deger_btn.bind(on_press=self._degerlendir)
        hukuk.add_widget(deger_btn)
        rate_ipucu = metin_label(
            t('settings_rate_hint'), font_size='11sp', color=RENKLER['gri_acik'],
            halign='left', size_hint_y=None, height=dp(32),
        )
        rate_ipucu.bind(texture_size=lambda i, v: setattr(i, 'height', max(v[1], dp(24))))
        hukuk.add_widget(rate_ipucu)
        icerik.add_widget(hukuk)

        yardim = _ayar_karti(t('settings_help'), t('settings_help_hint'))
        faq = metin_label(
            t('settings_faq'), font_size='11sp', color=RENKLER['gri_acik'],
            halign='left', size_hint_y=None,
        )
        faq.bind(texture_size=lambda i, v: setattr(i, 'height', max(v[1], dp(80))))
        yardim.add_widget(faq)
        icerik.add_widget(yardim)

        muzik_kart = _ayar_karti(t('settings_music'), t('settings_music_hint'))
        self._muzik_btn = siyah_buton(t('settings_music_off'), font_size='14sp')
        self._muzik_btn.bind(on_press=self._muzik_toggle)
        muzik_kart.add_widget(self._muzik_btn)

        from kivy.uix.slider import Slider
        self._muzik_slider = Slider(
            min=0, max=100,
            value=int(muzik_seviye_al() * 100),
            size_hint_y=None, height=dp(36),
        )
        self._muzik_slider.bind(on_value=self._muzik_seviye_degisti)

        ses_satir = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        azalt = siyah_buton('−', font_size='20sp')
        azalt.size_hint_x = None
        azalt.width = dp(52)
        azalt.bind(on_press=self._muzik_seviye_azalt)
        artir = siyah_buton('+', font_size='20sp')
        artir.size_hint_x = None
        artir.width = dp(52)
        artir.bind(on_press=self._muzik_seviye_artir)
        self._muzik_yuzde = metin_label(
            '', font_size='12sp', bold=True, color=RENKLER['altin'],
            halign='center', valign='middle',
        )
        ses_satir.add_widget(azalt)
        ses_satir.add_widget(self._muzik_yuzde)
        ses_satir.add_widget(artir)

        muzik_kart.add_widget(metin_label(
            t('settings_volume'), font_size='11sp', color=RENKLER['gri_acik'],
            halign='left', size_hint_y=None, height=dp(18),
        ))
        muzik_kart.add_widget(self._muzik_slider)
        muzik_kart.add_widget(ses_satir)
        icerik.add_widget(muzik_kart)

        self._mesaj = metin_label(
            '', font_size='13sp', color=RENKLER['yesil'],
            halign='center', size_hint_y=None, height=dp(28),
        )
        icerik.add_widget(self._mesaj)

        icerik.add_widget(metin_label(
            f'FalımaBak v{_SURUM}',
            font_size='10sp', color=RENKLER['gri_koyu'],
            halign='center', size_hint_y=None, height=dp(18),
        ))

        kaydir.add_widget(icerik)
        self._kaydir = kaydir
        ana.add_widget(kaydir)

        try:
            from reklam import reklam_alani_bosluk
            ana.add_widget(reklam_alani_bosluk())
        except Exception:
            pass
        ana.add_widget(alt_nav_bar('ayarlar', on_sec=self._nav))
        ekran_icerik_sar(self, ana)
        klavye_kaydir_bagla(self._kaydir, self._isim_input)

    def on_enter(self, *_):
        self._yukle()

    def _yukle(self):
        self._isim_input.text = kullanici_ismi()
        self._dil_spinner.text = dil_etiket(dil_al())
        self._mesaj.text = ''
        self._bildirim_check.active = bildirim_acik_al()
        self._slider_guncelle(muzik_seviye_al() * 100, ses_uygula=False)
        self._muzik_btn_guncelle()
        try:
            from muzik import muzik_acik_mi, muzik_uygula
            if muzik_acik_mi():
                muzik_uygula()
        except Exception:
            pass

    def _slider_guncelle(self, deger, ses_uygula=True):
        self._muzik_slider.unbind(on_value=self._muzik_seviye_degisti)
        deger = max(0, min(100, int(deger)))
        self._muzik_slider.value = deger
        self._muzik_yuzde.text = f'%{deger}'
        self._muzik_slider.bind(on_value=self._muzik_seviye_degisti)
        if ses_uygula:
            from muzik import muzik_seviye_ayarla
            muzik_seviye_ayarla(deger / 100.0)

    def _muzik_btn_guncelle(self):
        acik = muzik_acik_al()
        self._muzik_btn.text = t('settings_music_on') if acik else t('settings_music_off')

    def _muzik_toggle(self, *_):
        from muzik import muzik_ac_kapat, muzik_acik_mi
        muzik_ac_kapat(not muzik_acik_mi())
        self._muzik_btn_guncelle()

    def _muzik_seviye_degisti(self, _, deger):
        self._slider_guncelle(deger)

    def _muzik_seviye_azalt(self, *_):
        self._slider_guncelle(self._muzik_slider.value - 10)

    def _muzik_seviye_artir(self, *_):
        self._slider_guncelle(self._muzik_slider.value + 10)

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

    def _gizlilik_ac(self, *_):
        try:
            from reklam import gizlilik_ac
            gizlilik_ac(self.manager)
        except Exception:
            if self.manager and 'gizlilik' in self.manager.screen_names:
                self.manager.current = 'gizlilik'

    def _bildirim_degisti(self, _, acik):
        bildirim_acik_kaydet(acik)
        try:
            from bildirim import (
                bildirim_baslat, bildirim_iptal, bildirim_izinleri_kontrol,
                bildirim_anlik_goster,
            )
            if acik:
                bildirim_baslat()
                bildirim_izinleri_kontrol()
                # Açar açmaz anlık onay bildirimi — kullanıcı çalıştığını görsün.
                from kivy.clock import Clock
                Clock.schedule_once(lambda *_: bildirim_anlik_goster(), 0.6)
                self._mesaj.text = t('settings_notif_on_msg')
            else:
                bildirim_iptal()
                self._mesaj.text = t('settings_notif_off_msg')
            self._mesaj.color = get_color_from_hex(RENKLER['yesil'])
        except Exception:
            pass

    def _degerlendir(self, *_):
        # Dokunma olayı bitsin; Play Store geçişi hemen geri dönmesin diye kısa gecikme.
        from kivy.clock import Clock
        Clock.schedule_once(lambda *_: self._degerlendir_ac(), 0.2)

    def _degerlendir_ac(self):
        try:
            from play_store import magaza_degerlendir_odullu
            from coin import DEGERLENDIRME_COIN
            from coin_ui import coin_ui_yenile
            acildi, verildi, _ = magaza_degerlendir_odullu()
            if not acildi:
                self._mesaj.text = t('settings_rate_fail')
                self._mesaj.color = get_color_from_hex(RENKLER['kirmizi'])
                return
            if verildi:
                coin_ui_yenile()
                self._mesaj.text = t('settings_rate_reward', coin=DEGERLENDIRME_COIN)
            else:
                self._mesaj.text = t('settings_rate_done')
            self._mesaj.color = get_color_from_hex(RENKLER['yesil'])
        except Exception:
            pass

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
