"""Fal başlatma — coin harcama."""

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex

from coin import FAL_MALIYET, SINIRSIZ_TIPLER, coin_harca, fal_izinli, fal_ucretsiz
from theme import RENKLER, metin_label, siyah_buton

TIP_ETIKET = {
    'tarot': 'Tarot',
    'kahve': 'Kahve',
    'astroloji': 'Astroloji',
    'elfali': 'El Falı',
    'diger': 'Diğer Fallar',
    'burc_eslesme': 'Burç Eşleşmesi',
    'ruya': 'Rüya Tabiri',
}


def fal_durumu(tip):
    from coin import coin_miktar
    if fal_ucretsiz(tip):
        return {'sinirsiz': True, 'kalan': 99, 'coin': coin_miktar()}
    return {
        'sinirsiz': False,
        'kalan': coin_miktar() // FAL_MALIYET,
        'coin': coin_miktar(),
        'maliyet': FAL_MALIYET,
    }


def fal_kullanildi_kaydet(tip):
    """Coin yorum_baslat anında düşülür; burada ek işlem yok."""
    return


def fal_basarisiz_iade(tip):
    """Fal tamamlanmadıysa (hata / geçersiz foto) coin iade."""
    if fal_ucretsiz(tip):
        return
    try:
        from coin import coin_iade
        coin_iade(FAL_MALIYET)
        from coin_ui import coin_ui_yenile
        coin_ui_yenile()
    except Exception:
        pass


def yorum_baslat(tip, devam_fn):
    if not fal_izinli(tip):
        _coin_yetersiz_popup(tip)
        return
    if not fal_ucretsiz(tip):
        if not coin_harca(FAL_MALIYET):
            _coin_yetersiz_popup(tip)
            return
        try:
            from coin_ui import coin_ui_yenile
            coin_ui_yenile()
        except Exception:
            pass
    devam_fn()


def _coin_yetersiz_popup(tip):
    from dil import t
    from coin_ui import coin_popup_goster

    etiket = TIP_ETIKET.get(tip, tip)
    icerik = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
    icerik.add_widget(metin_label(
        t('coin_fal_need', tip=etiket, cost=FAL_MALIYET),
        font_size='13sp', color=RENKLER['beyaz'],
        halign='center', size_hint_y=None, height=dp(64),
    ))
    btn_satir = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
    iptal = siyah_buton(t('limit_no'), font_size='14sp')
    coin_btn = siyah_buton(t('coin_get_coins'), vurgu=True, font_size='14sp')
    btn_satir.add_widget(iptal)
    btn_satir.add_widget(coin_btn)
    icerik.add_widget(btn_satir)

    popup = Popup(
        title=t('coin_title'),
        content=icerik,
        size_hint=(0.88, None),
        height=dp(190),
        separator_color=get_color_from_hex(RENKLER['altin']),
        title_color=get_color_from_hex(RENKLER['altin']),
        auto_dismiss=False,
    )

    def _kapat(*_):
        popup.dismiss()

    def _coin(*_):
        _kapat()
        Clock.schedule_once(lambda *_: coin_popup_goster(), 0.1)

    iptal.bind(on_press=_kapat)
    coin_btn.bind(on_press=_coin)
    popup.open()
