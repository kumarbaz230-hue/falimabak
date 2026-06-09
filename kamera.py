"""
FalımaBak - Fotoğraf seçme / kamera (Windows + Android).
"""

import os
import shutil
import threading
import traceback
from datetime import datetime

from kivy.clock import Clock

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_FOTO_DIR = os.path.join(BASE_DIR, 'user_photos')


def _foto_dir():
    if _android_mi():
        try:
            from kivy.app import App
            app = App.get_running_app()
            if app and app.user_data_dir:
                d = os.path.join(app.user_data_dir, 'user_photos')
                os.makedirs(d, exist_ok=True)
                return d
        except Exception:
            pass
    os.makedirs(_DEFAULT_FOTO_DIR, exist_ok=True)
    return _DEFAULT_FOTO_DIR


def _ana_thread(fn):
    Clock.schedule_once(lambda *_: fn(), 0)


def _android_mi():
    return (
        'ANDROID_ARGUMENT' in os.environ
        or 'ANDROID_ROOT' in os.environ
        or 'ANDROID_BOOTLOGO' in os.environ
    )


def kamera_izni_iste(callback):
    """Android runtime kamera izni."""
    if not _android_mi():
        callback(True)
        return
    try:
        from android.permissions import request_permissions, Permission, check_permission

        if check_permission(Permission.CAMERA):
            callback(True)
            return

        def _sonuc(permissions, grants):
            callback(bool(grants and grants[0]))

        request_permissions([Permission.CAMERA], _sonuc)
    except Exception as e:
        print(f'Kamera izni: {e}', flush=True)
        callback(True)


def uygulama_izinlerini_iste():
    """Açılışta kamera iznini önceden iste."""
    if not _android_mi():
        return

    def _cb(ok):
        print(f'Kamera izni: {"verildi" if ok else "reddedildi"}', flush=True)

    kamera_izni_iste(_cb)


def _kopyala(kaynak):
    if not kaynak:
        return None
    kaynak = str(kaynak).strip()
    if kaynak.startswith('file://'):
        kaynak = kaynak[7:]
    if kaynak.startswith('content://'):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            resolver = context.getContentResolver()
            FileOutputStream = autoclass('java.io.FileOutputStream')
            uri = autoclass('android.net.Uri').parse(kaynak)
            stream = resolver.openInputStream(uri)
            hedef = os.path.join(
                _foto_dir(),
                f'foto_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg',
            )
            out = FileOutputStream(hedef)
            buf = bytearray(8192)
            while True:
                n = stream.read(buf)
                if n <= 0:
                    break
                out.write(bytes(buf[:n]))
            stream.close()
            out.close()
            return os.path.normpath(hedef)
        except Exception as e:
            print(f'content:// kopyalama: {e}', flush=True)
            return None
    if not os.path.isfile(kaynak):
        return None
    ext = os.path.splitext(kaynak)[1].lower() or '.jpg'
    hedef = os.path.join(
        _foto_dir(),
        f'foto_{datetime.now().strftime("%Y%m%d_%H%M%S")}{ext}',
    )
    try:
        shutil.copy2(kaynak, hedef)
        return os.path.normpath(hedef)
    except Exception as e:
        print(f'Foto kopyalama: {e}', flush=True)
        return None


def _galeri_plyer(callback):
    try:
        from plyer import filechooser

        def _secildi(dosyalar):
            try:
                if not dosyalar:
                    _ana_thread(lambda: callback(None, 'Dosya seçilmedi'))
                    return
                kayit = _kopyala(dosyalar[0])
                if kayit:
                    _ana_thread(lambda: callback(kayit, None))
                else:
                    _ana_thread(lambda: callback(None, 'Fotoğraf kopyalanamadı'))
            except Exception:
                print(traceback.format_exc(), flush=True)
                _ana_thread(lambda: callback(None, 'Galeri hatası'))

        filechooser.open_file(
            on_selection=_secildi,
            filters=['*.png', '*.jpg', '*.jpeg', '*.webp', '*.bmp'],
        )
    except Exception as e:
        print(f'Galeri plyer: {e}', flush=True)
        _ana_thread(lambda: callback(None, 'Galeri açılamadı'))


def _galeri_masaustu(callback):
    def _islem():
        try:
            from tkinter import Tk, filedialog

            root = Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            yol = filedialog.askopenfilename(
                title='Fotoğraf Seç',
                filetypes=[
                    ('Resimler', '*.png *.jpg *.jpeg *.webp *.bmp'),
                    ('Tüm dosyalar', '*.*'),
                ],
            )
            root.destroy()
            if not yol:
                _ana_thread(lambda: callback(None, 'Dosya seçilmedi'))
                return
            kayit = _kopyala(yol)
            _ana_thread(lambda: callback(kayit, None) if kayit else callback(None, 'Fotoğraf kopyalanamadı'))
        except Exception as e:
            _ana_thread(lambda: callback(None, str(e)))

    threading.Thread(target=_islem, daemon=True).start()


def galeriden_sec(callback):
    if _android_mi():
        Clock.schedule_once(lambda *_: _galeri_plyer(callback), 0)
    else:
        _galeri_masaustu(callback)


def _kamera_plyer(callback):
    try:
        from plyer import camera

        klasor = _foto_dir()
        os.makedirs(klasor, exist_ok=True)
        yol = os.path.join(
            klasor,
            f'cam_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg',
        )
        open(yol, 'ab').close()

        def _bitti(ok):
            try:
                if ok and os.path.isfile(yol) and os.path.getsize(yol) > 0:
                    _ana_thread(lambda: callback(os.path.normpath(yol), None))
                else:
                    _ana_thread(lambda: callback(None, 'Fotoğraf çekilmedi'))
            except Exception:
                _ana_thread(lambda: callback(None, 'Kamera hatası'))

        camera.take_picture(filename=yol, on_complete=_bitti)
    except Exception as e:
        print(f'Kamera plyer: {e}', flush=True)
        _ana_thread(lambda: callback(None, 'Kamera açılamadı. Ayarlardan kamera iznini açın.'))


def _kamera_masaustu(callback):
    def _islem():
        try:
            import cv2

            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not cap.isOpened():
                cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                _ana_thread(lambda: callback(None, 'Kamera bulunamadı. Galeriden seçmeyi deneyin.'))
                return

            for _ in range(8):
                cap.read()

            ok, frame = cap.read()
            cap.release()

            if not ok or frame is None:
                _ana_thread(lambda: callback(None, 'Fotoğraf çekilemedi'))
                return

            yol = os.path.join(
                _foto_dir(),
                f'cam_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg',
            )
            cv2.imwrite(yol, frame)
            _ana_thread(lambda: callback(os.path.normpath(yol), None))
        except ImportError:
            _ana_thread(
                lambda: callback(
                    None,
                    'Kamera için: py -3 -m pip install opencv-python',
                )
            )
        except Exception as e:
            _ana_thread(lambda: callback(None, str(e)))

    threading.Thread(target=_islem, daemon=True).start()


def kameradan_cek(callback):
    if _android_mi():
        def _izinli(ok):
            if ok:
                Clock.schedule_once(lambda *_: _kamera_plyer(callback), 0)
            else:
                _ana_thread(lambda: callback(
                    None,
                    'Kamera izni kapalı. Telefon Ayarları > Uygulamalar > FalımaBak > İzinler',
                ))

        kamera_izni_iste(_izinli)
    else:
        _kamera_masaustu(callback)
