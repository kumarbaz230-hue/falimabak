"""FalımaBak — uygulama içi gizlilik politikası (internet gerekmez)."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

from theme import (
    RENKLER, SAFE_UST, SAFE_ALT,
    metin_label, siyah_buton, ekran_icerik_sar, baslik_satir,
)


def _gizlilik_metni():
    from dil import t
    return t('privacy_body')


class GizlilikScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from dil import t
        ana = BoxLayout(orientation='vertical', padding=[dp(12), SAFE_UST, dp(12), SAFE_ALT], spacing=dp(10))
        ana.add_widget(baslik_satir('', t('privacy_title'), font_size='22sp', height=dp(40)))

        kaydir = ScrollView(size_hint_y=1, do_scroll_x=False, bar_width=dp(3),
            bar_color=get_color_from_hex(RENKLER['mor_parlak']))
        govde = BoxLayout(orientation='vertical', size_hint_y=None, padding=[dp(4), dp(8)])
        govde.bind(minimum_height=govde.setter('height'))
        lbl = metin_label(
            _gizlilik_metni(),
            font_size='12sp',
            color=RENKLER['gri_acik'],
            halign='left',
            size_hint_y=None,
        )
        lbl.bind(texture_size=lambda inst, val: setattr(inst, 'height', max(val[1], dp(200))))
        govde.add_widget(lbl)
        kaydir.add_widget(govde)
        ana.add_widget(kaydir)

        geri = siyah_buton(t('tus_geri'), font_size='14sp', size_hint_y=None, height=dp(48))
        geri.bind(on_press=lambda *_: setattr(self.manager, 'current', 'ayarlar'))
        ana.add_widget(geri)
        ekran_icerik_sar(self, ana)

    def on_enter(self, *_):
        for w in self.walk():
            if hasattr(w, 'text') and len(getattr(w, 'text', '')) > 80:
                w.text = _gizlilik_metni()
                break
