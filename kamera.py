"""
FalımaBak - Fotoğraf seçme / kamera (Windows + Android).
Android: FileProvider kamera + sistem galeri seçici (READ_MEDIA_IMAGES yok).
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
_GALERI_ISTEK = 9002
_kamera_callback = None
_kamera_hedef = None
_kamera_mod = 'uri'
_galeri_callback = None
_activity_baglandi = False


def _foto_dir():
    if _android_mi():
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            if activity is not None:
                files_dir = str(activity.getFilesDir().getAbsolutePath())
                d = os.path.join(files_dir, 'user_photos')
                os.makedirs(d, exist_ok=True)
                return d
        except Exception:
            pass
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


def _ana_thread(fn, gecikme=0):
    Clock.schedule_once(lambda *_: fn(), gecikme)


def _android_mi():
    return (
        'ANDROID_ARGUMENT' in os.environ
        or 'ANDROID_ROOT' in os.environ
        or 'ANDROID_BOOTLOGO' in os.environ
    )


def _dil(k):
    try:
        from dil import t
        return t(k)
    except Exception:
        return k


def kamera_izni_iste(callback):
    if not _android_mi():
        _ana_thread(lambda: callback(True))
        return
    try:
        from android.permissions import request_permissions, Permission, check_permission

        if check_permission(Permission.CAMERA):
            _ana_thread(lambda: callback(True), 0.05)
            return

        def _sonuc(permissions, grants):
            def _bitir(*_):
                ok = False
                try:
                    if grants is not None and len(grants) > 0:
                        ok = all(bool(g) for g in grants)
                    if not ok:
                        ok = check_permission(Permission.CAMERA)
                except Exception:
                    ok = check_permission(Permission.CAMERA)
                callback(ok)

            _ana_thread(_bitir, 0.2)

        request_permissions([Permission.CAMERA], _sonuc)
    except Exception as e:
        print(f'Kamera izni: {e}', flush=True)
        _ana_thread(lambda: callback(True))


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
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    fos = FileOutputStream(yol)
    bitmap.compress(CompressFormat.JPEG, 90, fos)
    fos.flush()
    fos.close()


def _sonuc_gonder(cb, yol, hata=None):
    if yol and os.path.isfile(yol) and os.path.getsize(yol) > 0:
        _ana_thread(lambda p=yol: cb(os.path.normpath(p), None))
    elif hata:
        _ana_thread(lambda h=hata: cb(None, h))
    else:
        _ana_thread(lambda: cb(None, _dil('cam_fail')))


def _dosya_bekle(cb, yol, deneme=0):
    if yol and os.path.isfile(yol) and os.path.getsize(yol) > 0:
        _sonuc_gonder(cb, yol)
        return
    if deneme < 8:
        Clock.schedule_once(lambda *_: _dosya_bekle(cb, yol, deneme + 1), 0.25)
    else:
        _sonuc_gonder(cb, None)


def _intent_gorsel_uri(intent):
    """Galeri / photo picker sonucundan content URI al."""
    if intent is None:
        return None
    try:
        from jnius import autoclass
        uris = intent.getParcelableArrayListExtra('android.provider.extra.PICK_IMAGES_RESULT')
        if uris is not None and uris.size() > 0:
            ilk = uris.get(0)
            if ilk is not None:
                return str(ilk.toString())
    except Exception:
        pass
    uri = intent.getData()
    if uri is not None:
        return str(uri.toString())
    clip = intent.getClipData()
    if clip is not None and clip.getItemCount() > 0:
        item = clip.getItemAt(0)
        if item is not None and item.getUri() is not None:
            return str(item.getUri().toString())
    return None


def _intent_cozulebilir(activity, intent):
    try:
        from jnius import autoclass
        PackageManager = autoclass('android.content.pm.PackageManager')
        return intent.resolveActivity(activity.getPackageManager()) is not None
    except Exception:
        return False


def _galeri_intent_listesi(activity):
    """İzinsiz galeri — en uyumlu yöntemler önce (GET_CONTENT)."""
    from jnius import autoclass
    Intent = autoclass('android.content.Intent')
    MediaStore = autoclass('android.provider.MediaStore')
    Build = autoclass('android.os.Build')

    sira = []

    get_content = Intent(Intent.ACTION_GET_CONTENT)
    get_content.setType('image/*')
    get_content.addCategory(Intent.CATEGORY_OPENABLE)
    sira.append(Intent.createChooser(get_content, 'Fotoğraf seç'))

    try:
        if int(Build.VERSION.SDK_INT) >= 33:
            pick = Intent('android.provider.action.PICK_IMAGES')
            pick.putExtra('android.provider.extra.PICK_IMAGES_MAX', 1)
            if _intent_cozulebilir(activity, pick):
                sira.append(pick)
    except Exception:
        pass

    pick_one = Intent(Intent.ACTION_PICK)
    pick_one.setDataAndType(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, 'image/*')
    if _intent_cozulebilir(activity, pick_one):
        sira.append(pick_one)

    return sira


_galeri_intent_sira = []
_galeri_intent_idx = 0


def _galeri_sonraki_intent(activity):
    """Bir intent açılamazsa sıradakini dene (kullanıcı iptal ederse deneme)."""
    global _galeri_callback, _galeri_intent_sira, _galeri_intent_idx
    cb = _galeri_callback
    if not cb or _galeri_intent_idx >= len(_galeri_intent_sira):
        _galeri_callback = None
        if cb:
            _ana_thread(lambda: cb(None, _dil('cam_fail')))
        return
    intent = _galeri_intent_sira[_galeri_intent_idx]
    _galeri_intent_idx += 1

    def _ac(*_):
        try:
            activity.startActivityForResult(intent, _GALERI_ISTEK)
        except Exception as e:
            print(f'Galeri intent hatasi: {e}', flush=True)
            _galeri_sonraki_intent(activity)

    Clock.schedule_once(_ac, 0)


def _galeri_android_picker(callback):
    """Android fotoğraf seçici — READ_MEDIA_IMAGES gerekmez."""
    global _galeri_callback, _galeri_intent_sira, _galeri_intent_idx
    activity = None
    try:
        _activity_bagla()
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        if activity is None:
            raise RuntimeError('Activity yok')

        _galeri_callback = callback
        _galeri_intent_sira = _galeri_intent_listesi(activity)
        _galeri_intent_idx = 0
        if not _galeri_intent_sira:
            raise RuntimeError('Galeri intent yok')
        _galeri_sonraki_intent(activity)
    except Exception as e:
        print(f'Galeri picker: {e}', flush=True)
        _galeri_callback = None
        _ana_thread(lambda: callback(None, _dil('cam_fail')))


def _on_activity_result(request_code, result_code, intent):
    global _kamera_callback, _kamera_hedef, _kamera_mod, _galeri_callback

    if request_code == _GALERI_ISTEK:
        cb = _galeri_callback
        _galeri_callback = None
        if not cb:
            return
        try:
            from jnius import autoclass
            Activity = autoclass('android.app.Activity')
            if result_code != Activity.RESULT_OK:
                _sonuc_gonder(cb, None, _dil('cam_cancel'))
                return
            uri = _intent_gorsel_uri(intent)
            if uri:
                kayit = _kopyala(uri)
                if kayit:
                    _sonuc_gonder(cb, kayit)
                    return
            _sonuc_gonder(cb, None, _dil('cam_fail'))
        except Exception:
            print(traceback.format_exc(), flush=True)
            _sonuc_gonder(cb, None)
        return

    if request_code != _KAMERA_ISTEK or not _kamera_callback:
        return

    cb = _kamera_callback
    _kamera_callback = None
    yol = _kamera_hedef
    mod = _kamera_mod
    _kamera_hedef = None

    try:
        from jnius import autoclass
        Activity = autoclass('android.app.Activity')
        if result_code != Activity.RESULT_OK:
            _sonuc_gonder(cb, None, _dil('cam_cancel'))
            return

        if mod == 'uri' and yol:
            if os.path.isfile(yol) and os.path.getsize(yol) > 0:
                _sonuc_gonder(cb, yol)
                return
            _dosya_bekle(cb, yol)
            return

        if intent is not None:
            extras = intent.getExtras()
            if extras is not None:
                bitmap = extras.get('data')
                if bitmap is not None:
                    hedef = yol or os.path.join(
                        _foto_dir(),
                        f'cam_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg',
                    )
                    try:
                        _bitmap_kaydet(bitmap, hedef)
                        if os.path.getsize(hedef) > 0:
                            _sonuc_gonder(cb, hedef)
                            return
                    except Exception as e:
                        print(f'Bitmap kayıt: {e}', flush=True)

            uri = _intent_gorsel_uri(intent)
            if uri:
                kayit = _kopyala(uri)
                if kayit:
                    _sonuc_gonder(cb, kayit)
                    return

        _sonuc_gonder(cb, None)
    except Exception:
        print(traceback.format_exc(), flush=True)
        _sonuc_gonder(cb, None)


def kamera_hazirla():
    if _android_mi():
        _activity_bagla()


def uygulama_izinlerini_iste():
    kamera_hazirla()


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


def _galeri_masaustu(callback):
    def _islem():
        try:
            from tkinter import Tk, filedialog
            root = Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            yol = filedialog.askopenfilename(
                title='Fotoğraf Seç',
                filetypes=[('Resimler', '*.png *.jpg *.jpeg *.webp'), ('Tüm', '*.*')],
            )
            root.destroy()
            if not yol:
                _ana_thread(lambda: callback(None, 'Dosya seçilmedi'))
                return
            kayit = _kopyala(yol)
            _ana_thread(lambda: callback(kayit, None) if kayit else callback(None, 'Kopyalanamadı'))
        except Exception as e:
            _ana_thread(lambda: callback(None, str(e)))

    threading.Thread(target=_islem, daemon=True).start()


def galeriden_sec(callback):
    if _android_mi():
        _ana_thread(lambda: _galeri_android_picker(callback), 0.05)
    else:
        _galeri_masaustu(callback)


def _intent_uri_kamera(callback):
    """FileProvider ile tam çözünürlük."""
    global _kamera_callback, _kamera_hedef, _kamera_mod
    _activity_bagla()
    _kamera_callback = callback
    _kamera_mod = 'uri'

    from jnius import autoclass
    Intent = autoclass('android.content.Intent')
    MediaStore = autoclass('android.provider.MediaStore')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    File = autoclass('java.io.File')
    FileProvider = autoclass('androidx.core.content.FileProvider')
    activity = PythonActivity.mActivity

    fname = f'cam_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
    files_dir = activity.getFilesDir()
    photo_dir = File(files_dir, 'user_photos')
    photo_dir.mkdirs()
    photo_file = File(photo_dir, fname)
    _kamera_hedef = str(photo_file.getAbsolutePath())

    intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
    pkg = activity.getPackageName()
    uri = FileProvider.getUriForFile(activity, pkg + '.fileprovider', photo_file)
    intent.putExtra(MediaStore.EXTRA_OUTPUT, uri)
    intent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
    intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

    pm = activity.getPackageManager()
    PackageManager = autoclass('android.content.pm.PackageManager')
    liste = pm.queryIntentActivities(intent, PackageManager.MATCH_DEFAULT_ONLY)
    if liste is None or liste.size() == 0:
        raise RuntimeError('Kamera uygulaması yok')

    for i in range(liste.size()):
        ri = liste.get(i)
        activity.grantUriPermission(
            ri.activityInfo.packageName, uri,
            Intent.FLAG_GRANT_WRITE_URI_PERMISSION | Intent.FLAG_GRANT_READ_URI_PERMISSION,
        )

    activity.startActivityForResult(intent, _KAMERA_ISTEK)


def _intent_basit_kamera(callback):
    """Thumbnail modu — FileProvider gerektirmez."""
    global _kamera_callback, _kamera_hedef, _kamera_mod
    _activity_bagla()
    _kamera_callback = callback
    _kamera_mod = 'thumb'
    _kamera_hedef = os.path.join(
        _foto_dir(),
        f'cam_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg',
    )

    from jnius import autoclass
    Intent = autoclass('android.content.Intent')
    MediaStore = autoclass('android.provider.MediaStore')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    activity = PythonActivity.mActivity

    intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
    pm = activity.getPackageManager()
    PackageManager = autoclass('android.content.pm.PackageManager')
    if intent.resolveActivity(pm) is None:
        raise RuntimeError('Kamera yok')

    activity.startActivityForResult(intent, _KAMERA_ISTEK)


def _android_kamera_ac(callback):
    global _kamera_callback, _kamera_hedef
    try:
        _intent_uri_kamera(callback)
    except Exception as e1:
        print(f'URI kamera: {e1}', flush=True)
        _kamera_callback = None
        _kamera_hedef = None
        try:
            _intent_basit_kamera(callback)
        except Exception as e2:
            print(f'Basit kamera: {e2}', flush=True)
            _kamera_callback = None
            _kamera_hedef = None
            _ana_thread(lambda: callback(None, _dil('cam_fail')))


def _kamera_masaustu(callback):
    def _islem():
        try:
            import cv2
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not cap.isOpened():
                cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                _ana_thread(lambda: callback(None, 'Kamera bulunamadı'))
                return
            for _ in range(6):
                cap.read()
            ok, frame = cap.read()
            cap.release()
            if not ok or frame is None:
                _ana_thread(lambda: callback(None, 'Fotoğraf çekilemedi'))
                return
            yol = os.path.join(_foto_dir(), f'cam_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg')
            cv2.imwrite(yol, frame)
            _ana_thread(lambda: callback(os.path.normpath(yol), None))
        except ImportError:
            _ana_thread(lambda: callback(None, 'opencv-python gerekli'))
        except Exception as e:
            _ana_thread(lambda: callback(None, str(e)))

    threading.Thread(target=_islem, daemon=True).start()


def kameradan_cek(callback):
    if _android_mi():
        def _izinli(ok):
            if ok:
                _ana_thread(lambda: _android_kamera_ac(callback), 0.1)
            else:
                _ana_thread(lambda: callback(None, _dil('cam_denied')))

        kamera_izni_iste(_izinli)
    else:
        _kamera_masaustu(callback)
