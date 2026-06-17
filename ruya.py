"""Rüya Tabiri — kullanıcının rüyasını FalımaBak yorumlar."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp

from ai_yorum import _yorum_al_calistir
from fal_limit import yorum_baslat
from theme import (
    RENKLER, SAFE_UST, SAFE_ALT,
    metin_label, guvenli_textinput, tus_buton, baslik_satir,
    buton_metin_guncelle, ekran_icerik_sar, kaydirici_metin,
    yorum_bekle_metin, yorum_sonuc_metni, tus_metin, fontlari_yukle,
    klavye_kaydir_bagla,
)

fontlari_yukle()

MIN_UZUNLUK = 15


def _ruya_ozet(metin):
    temiz = ' '.join((metin or '').split())
    if len(temiz) <= 90:
        return temiz
    return temiz[:87] + '…'


class RuyaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._kur()

    def _kur(self):
        from dil import t
        ana = BoxLayout(
            orientation='vertical',
            padding=[dp(12), SAFE_UST, dp(12), SAFE_ALT],
            spacing=dp(8),
        )
        ana.add_widget(baslik_satir('🌙', t('ruya_title'), font_size='22sp', height=dp(40)))

        aciklama = metin_label(
            t('ruya_aciklama'),
            font_size='12sp', color=RENKLER['gri_acik'],
            halign='left', size_hint_y=None,
        )
        aciklama.bind(texture_size=lambda i, v: setattr(i, 'height', max(v[1], dp(36))))
        ana.add_widget(aciklama)

        ana.add_widget(metin_label(
            t('ruya_input_label'),
            font_size='13sp', bold=True, color=RENKLER['mor'],
            halign='left', size_hint_y=None, height=dp(20),
        ))
        self._ruya_input = guvenli_textinput(
            hint_text=t('ruya_input_hint'),
            multiline=True,
            size_hint_y=None,
            height=dp(120),
        )
        ana.add_widget(self._ruya_input)

        self._durum = metin_label(
            '', font_size='13sp', color=RENKLER['beyaz'],
            halign='left', markup=True, size_hint_y=None, height=dp(24),
        )
        self._durum.bind(texture_size=lambda i, v: setattr(i, 'height', max(v[1], dp(24))))
        ana.add_widget(self._durum)

        self._yorum_alani, self._yorum_label = kaydirici_metin(1)
        ana.add_widget(self._yorum_alani)

        btn = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8))
        self._yorum_btn = tus_buton('ruya_tabir', vurgu=True, font_size='14sp')
        self._yorum_btn.bind(on_press=self._tabir_et)
        geri = tus_buton('geri', font_size='14sp')
        geri.bind(on_press=lambda *_: setattr(self.manager, 'current', 'anasayfa'))
        btn.add_widget(self._yorum_btn)
        btn.add_widget(geri)
        ana.add_widget(btn)

        ekran_icerik_sar(self, ana)
        klavye_kaydir_bagla(None, ana, self._ruya_input)

    def _tabir_et(self, *_):
        from dil import t
        metin = (self._ruya_input.text or '').strip()
        if len(metin) < MIN_UZUNLUK:
            self._durum.text = f"[color={RENKLER['kirmizi']}]{t('ruya_hata_kisa')}[/color]"
            self._yorum_label.text = ''
            return

        yorum_baslat('ruya', lambda: self._tabir_devam(metin))

    def _tabir_devam(self, metin):
        from dil import t
        ozet = _ruya_ozet(metin)
        self._son_temel = (
            f"[b][color={RENKLER['altin']}]🌙 {t('ruya_ozet_baslik')}[/color][/b]\n\n"
            f"[color={RENKLER['mavi_acik']}]\"{ozet}\"[/color]\n\n"
            f"[color={RENKLER['gri_acik']}]{t('ruya_yorumlaniyor')}[/color]"
        )
        self._durum.text = ''
        self._yorum_label.text = yorum_bekle_metin()
        buton_metin_guncelle(self._yorum_btn, yorum_bekle_metin())
        self._yorum_btn.disabled = True

        veri = {'ruya': metin, 'ozet': ozet}

        def _bitir(metin, ai_kullanildi, hata, kaynak=None, fotograf=False):
            self._yorum_label.text = yorum_sonuc_metni(
                self._son_temel, metin, ai_kullanildi, hata, kaynak, fotograf,
            )
            buton_metin_guncelle(self._yorum_btn, tus_metin('tekrar'))
            self._yorum_btn.disabled = False

        _yorum_al_calistir('ruya', veri, _bitir)
