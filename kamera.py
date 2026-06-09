"""
FalımaBak - Fotoğraf seçme / kamera (Windows + Android).
Android'de sistem kamera uygulaması (Intent) kullanılır — plyer çoğu cihazda çalışmaz.
"""

import os
import shutil
import threading
import traceback
from datetime import datetime

from kivy.clock import Clock

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_FOTO_DIR = os.path.join(BASE_DIR, 'user_photos')

_KAMERA_ISTEK = 9001
_kamera_callback = None
_kamera_hedef = None
_activity_baglandi = False


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


def _activity_bagla():
    global _activity_baglandi
    if _activity_baglandi or not _android_mi():
        return
    try:
        from android import activity as android_activity
        android_activity.bind(on_activity_result=_on_activity_result)
        _activity_baglandi = True
    except Exception as e:
        print(f'Kamera activity bind: {e}', flush=True)


def _bitmap_kaydet(bitmap, yol):
    from jnius import autoclass
    CompressFormat = autoclass('android.graphics.Bitmap$CompressFormat')
    FileOutputStream = autoclass('java.io.FileOutputStream')
    fos = FileOutputStream(yol)
    bitmap.compress(CompressFormat.JPEG, 92, fos)
    fos.flush()
    fos.close()


def _on_activity_result(request_code, result_code, intent):
    global _kamera_callback, _kamera_hedef
    if request_code != _KAMERA_ISTEK or not _kamera_callback:
        return

    cb = _kamera_callback
    _kamera_callback = None
    yol = _kamera_hedef
    _kamera_hedef = None

    try:
        from jnius import autoclass
        Activity = autoclass('android.app.Activity')
        if result_code != Activity.RESULT_OK:
            _ana_thread(lambda: cb(None, 'Fotoğraf çekilmedi'))
            return

        if yol and os.path.isfile(yol) and os.path.getsize(yol) > 0:
            _ana_thread(lambda p=yol: cb(os.path.normpath(p), None))
            return

        if intent is not None:
            uri = intent.getData()
            if uri is not None:
                kayit = _kopyala(str(uri.toString()))
                if kayit:
                    _ana_thread(lambda p=kayit: cb(p, None))
                    return

            extras = intent.getExtras()
            if extras is not None:
                bitmap = extras.get('data')
                if bitmap is not None and yol:
                    try:
                        os.makedirs(os.path.dirname(yol), exist_ok=True)
                        _bitmap_kaydet(bitmap, yol)
                        if os.path.getsize(yol) > 0:
                            _ana_thread(lambda p=yol: cb(os.path.normpath(p), None))
                            return
                    except Exception as e:
                        print(f'Kamera bitmap kayıt: {e}', flush=True)

        _ana_thread(lambda: cb(None, 'Kamera fotoğrafı alınamadı. Galeriden seçmeyi deneyin.'))
    except Exception:
        print(traceback.format_exc(), flush=True)
        _ana_thread(lambda: cb(None, 'Kamera hatası'))


def uygulama_izinlerini_iste():
    """Açılışta kamera iznini önceden iste ve activity callback bağla."""
    if not _android_mi():
        return
    _activity_bagla()

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


def _kamera_android_intent(callback):
    """Sistem kamera uygulamasını aç (Android Intent)."""
    global _kamera_callback, _kamera_hedef
    _activity_bagla()
    _kamera_callback = callback
    try:
        from jnius import autoclass
        Intent = autoclass('android.content.Intent')
        MediaStore = autoclass('android.provider.MediaStore')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity

        klasor = _foto_dir()
        os.makedirs(klasor, exist_ok=True)
        _kamera_hedef = os.path.join(
            klasor,
            f'cam_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg',
        )

        intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)

        try:
            File = autoclass('java.io.File')
            FileProvider = autoclass('androidx.core.content.FileProvider')
            pkg = activity.getPackageName()
            photo_file = File(_kamera_hedef)
            parent = photo_file.getParentFile()
            if parent is not None:
                parent.mkdirs()
            uri = FileProvider.getUriForFile(activity, pkg + '.fileprovider', photo_file)
            intent.putExtra(MediaStore.EXTRA_OUTPUT, uri)
            intent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        except Exception as e:
            print(f'FileProvider atlandı (thumbnail modu): {e}', flush=True)

        pm = activity.getPackageManager()
        if intent.resolveActivity(pm) is None:
            _kamera_callback = None
            _kamera_hedef = None
            _ana_thread(lambda: callback(None, 'Bu cihazda kamera uygulaması bulunamadı'))
            return

        activity.startActivityForResult(intent, _KAMERA_ISTEK)
    except Exception as e:
        print(f'Kamera intent: {e}', flush=True)
        print(traceback.format_exc(), flush=True)
        _kamera_callback = None
        _kamera_hedef = None
        _kamera_plyer(callback)


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
        _ana_thread(lambda: callback(None, 'Kamera açılamadı. Galeriden seçmeyi deneyin.'))


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
                Clock.schedule_once(lambda *_: _kamera_android_intent(callback), 0)
            else:
                _ana_thread(lambda: callback(
                    None,
                    'Kamera izni kapalı. Telefon Ayarları > Uygulamalar > FalımaBak > İzinler',
                ))

        kamera_izni_iste(_izinli)
    else:
        _kamera_masaustu(callback)
