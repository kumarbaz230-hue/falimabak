"""Burç Eşleşmesi — iki kişinin doğum tarihine göre burç uyumu + AI yorum."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.metrics import dp

from astroloji import BURCLAR
from ai_yorum import yorum_al
from theme import (
    RENKLER, SAFE_UST, SAFE_ALT, EKRAN_UST,
    metin_label, guvenli_textinput, tus_buton, baslik_satir,
    buton_metin_guncelle, ekran_icerik_sar, kaydirici_metin,
    yorum_bekle_metin, yorum_sonuc_metni, tus_metin, fontlari_yukle,
    fal_form_duz, yorum_panel_baslik,
)

fontlari_yukle()

_INP_H = dp(42)


def _burc_bul(gun, ay):
    if (ay == 3 and gun >= 21) or (ay == 4 and gun <= 19):
        return 'Koç'
    if (ay == 4 and gun >= 20) or (ay == 5 and gun <= 20):
        return 'Boğa'
    if (ay == 5 and gun >= 21) or (ay == 6 and gun <= 20):
        return 'İkizler'
    if (ay == 6 and gun >= 21) or (ay == 7 and gun <= 22):
        return 'Yengeç'
    if (ay == 7 and gun >= 23) or (ay == 8 and gun <= 22):
        return 'Aslan'
    if (ay == 8 and gun >= 23) or (ay == 9 and gun <= 22):
        return 'Başak'
    if (ay == 9 and gun >= 23) or (ay == 10 and gun <= 22):
        return 'Terazi'
    if (ay == 10 and gun >= 23) or (ay == 11 and gun <= 21):
        return 'Akrep'
    if (ay == 11 and gun >= 22) or (ay == 12 and gun <= 21):
        return 'Yay'
    if (ay == 12 and gun >= 22) or (ay == 1 and gun <= 19):
        return 'Oğlak'
    if (ay == 1 and gun >= 20) or (ay == 2 and gun <= 18):
        return 'Kova'
    return 'Balık'


def _tarih_gecerli(gun, ay, yil):
    if yil < 1900 or yil > 2100 or ay < 1 or ay > 12 or gun < 1 or gun > 31:
        return False
    if ay in (4, 6, 9, 11) and gun > 30:
        return False
    if ay == 2:
        artik = (yil % 4 == 0 and yil % 100 != 0) or (yil % 400 == 0)
        if gun > (29 if artik else 28):
            return False
    return True


def _uyum_skoru(burc1, burc2):
    if burc1 == burc2:
        return 78
    e1 = BURCLAR[burc1]['element']
    e2 = BURCLAR[burc2]['element']
    tablo = {
        ('Ateş', 'Ateş'): 82, ('Ateş', 'Hava'): 90, ('Ateş', 'Toprak'): 52, ('Ateş', 'Su'): 46,
        ('Toprak', 'Toprak'): 80, ('Toprak', 'Su'): 70, ('Toprak', 'Hava'): 48,
        ('Hava', 'Hava'): 88, ('Hava', 'Su'): 74,
        ('Su', 'Su'): 84,
    }
    return tablo.get((e1, e2), tablo.get((e2, e1), 62))


def _temel_sonuc(burc1, burc2, skor, isim1, isim2):
    b1, b2 = BURCLAR[burc1], BURCLAR[burc2]
    ad1 = isim1 or 'Kişi 1'
    ad2 = isim2 or 'Kişi 2'
    yildiz = '★' * (skor // 20) + '☆' * (5 - skor // 20)
    return (
        f"[b][color={RENKLER['altin']}]💞 Burç Uyumu: %{skor} {yildiz}[/color][/b]\n\n"
        f"[b]{ad1}[/b] — {burc1} {b1['sembol']} ({b1['element']})\n"
        f"[b]{ad2}[/b] — {burc2} {b2['sembol']} ({b2['element']})\n\n"
        f"[color={RENKLER['gri_acik']}]Element uyumu ve burç dinamikleri "
        f"FalımaBak tarafından yorumlanıyor…[/color]"
    )


class BurcEslesmeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._kur()

    def _tarih_satiri(self):
        from dil import t
        satir = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=_INP_H,
            spacing=dp(6),
        )
        g = guvenli_textinput(
            hint_text=t('burc_gun'), input_filter='int',
            size_hint_x=0.28, height=_INP_H,
        )
        a = guvenli_textinput(
            hint_text=t('burc_ay'), input_filter='int',
            size_hint_x=0.28, height=_INP_H,
        )
        y = guvenli_textinput(
            hint_text=t('burc_yil'), input_filter='int',
            size_hint_x=0.44, height=_INP_H,
        )
        satir.add_widget(g)
        satir.add_widget(a)
        satir.add_widget(y)
        return satir, g, a, y

    def _kur(self):
        from dil import t
        ana = BoxLayout(
            orientation='vertical',
            padding=[dp(12), EKRAN_UST, dp(12), SAFE_ALT],
            spacing=dp(6),
        )
        ana.add_widget(baslik_satir('💞', t('burc_eslesme_title'), font_size='22sp', height=dp(36)))

        form_panel, govde = fal_form_duz()

        govde.add_widget(metin_label(
            t('burc_kisi1'), font_size='13sp', bold=True, color=RENKLER['pembe_acik'],
            halign='left', size_hint_y=None, height=dp(18),
        ))
        self._isim1 = guvenli_textinput(
            hint_text=t('burc_isim1'), height=_INP_H,
        )
        govde.add_widget(self._isim1)
        govde.add_widget(metin_label(
            t('burc_dogum_tarihi'), font_size='11sp', color=RENKLER['gri_acik'],
            halign='left', size_hint_y=None, height=dp(16),
        ))
        t1, self._g1, self._a1, self._y1 = self._tarih_satiri()
        govde.add_widget(t1)

        govde.add_widget(Widget(size_hint_y=None, height=dp(6)))

        govde.add_widget(metin_label(
            t('burc_kisi2'), font_size='13sp', bold=True, color=RENKLER['mavi_acik'],
            halign='left', size_hint_y=None, height=dp(18),
        ))
        self._isim2 = guvenli_textinput(
            hint_text=t('burc_isim2'), height=_INP_H,
        )
        govde.add_widget(self._isim2)
        govde.add_widget(metin_label(
            t('burc_dogum_tarihi'), font_size='11sp', color=RENKLER['gri_acik'],
            halign='left', size_hint_y=None, height=dp(16),
        ))
        t2, self._g2, self._a2, self._y2 = self._tarih_satiri()
        govde.add_widget(t2)

        ana.add_widget(form_panel)

        self._durum = metin_label(
            '', font_size='12sp', color=RENKLER['kirmizi'],
            halign='left', markup=True, size_hint_y=None, height=dp(18),
        )
        ana.add_widget(self._durum)

        ana.add_widget(yorum_panel_baslik('Uyum yorumu'))
        self._yorum_alani, self._yorum_label = kaydirici_metin(1)
        self._yorum_label.text = (
            f'[color={RENKLER["gri_acik"]}]İki kişinin doğum tarihini girip '
            f'"Eşleştir"e basın.[/color]'
        )
        self._yorum_label.markup = True
        ana.add_widget(self._yorum_alani)

        btn = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(46), spacing=dp(8))
        self._esles_btn = tus_buton('burc_esles', vurgu=True, font_size='14sp')
        self._esles_btn.bind(on_press=self._eslestir)
        geri = tus_buton('geri', font_size='14sp')
        geri.bind(on_press=lambda *_: setattr(self.manager, 'current', 'anasayfa'))
        btn.add_widget(self._esles_btn)
        btn.add_widget(geri)
        ana.add_widget(btn)

        ekran_icerik_sar(self, ana)

    def _parse_tarih(self, g_in, a_in, y_in):
        g, a, y = g_in.text.strip(), a_in.text.strip(), y_in.text.strip()
        if not g or not a or not y:
            return None, 'burc_hata_bos'
        try:
            gun, ay, yil = int(g), int(a), int(y)
        except ValueError:
            return None, 'burc_hata_sayi'
        if not _tarih_gecerli(gun, ay, yil):
            return None, 'burc_hata_tarih'
        return (gun, ay, yil, _burc_bul(gun, ay)), None

    def _eslestir(self, *_):
        from dil import t
        t1, err1 = self._parse_tarih(self._g1, self._a1, self._y1)
        t2, err2 = self._parse_tarih(self._g2, self._a2, self._y2)
        if err1 or err2:
            kod = err1 or err2
            self._durum.text = f"[color={RENKLER['kirmizi']}]{t(kod)}[/color]"
            self._yorum_label.text = ''
            return

        self._durum.text = ''
        gun1, ay1, yil1, burc1 = t1
        gun2, ay2, yil2, burc2 = t2
        isim1 = self._isim1.text.strip()
        isim2 = self._isim2.text.strip()
        skor = _uyum_skoru(burc1, burc2)

        temel = _temel_sonuc(burc1, burc2, skor, isim1, isim2)
        self._son_temel = temel
        self._yorum_label.text = yorum_bekle_metin()
        buton_metin_guncelle(self._esles_btn, yorum_bekle_metin())
        self._esles_btn.disabled = True

        veri = {
            'burc1': burc1,
            'burc2': burc2,
            'dogum1': f'{gun1:02d}.{ay1:02d}.{yil1}',
            'dogum2': f'{gun2:02d}.{ay2:02d}.{yil2}',
            'isim1': isim1 or t('burc_kisi1'),
            'isim2': isim2 or t('burc_kisi2'),
            'skor': skor,
        }

        def _bitir(metin, ai_kullanildi, hata, kaynak=None, fotograf=False):
            self._yorum_label.text = yorum_sonuc_metni(
                self._son_temel, metin, ai_kullanildi, hata, kaynak, fotograf,
            )
            buton_metin_guncelle(self._esles_btn, tus_metin('tekrar'))
            self._esles_btn.disabled = False

        yorum_al('burc_eslesme', veri, _bitir)
