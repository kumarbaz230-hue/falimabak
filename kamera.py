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


def _activity_bagla(zorla=False):
    global _activity_baglandi
    if not _android_mi():
        return
    if _activity_baglandi and not zorla:
        return
    try:
        from android import activity as android_activity
        android_activity.bind(on_activity_result=_on_activity_result)
        _activity_baglandi = True
        print('Activity result baglandi', flush=True)
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


def _galeri_sonuc_gonder(cb, yol=None, hata=None):
    if yol and os.path.isfile(yol) and os.path.getsize(yol) > 0:
        _ana_thread(lambda p=yol: cb(os.path.normpath(p), None))
    elif hata:
        _ana_thread(lambda h=hata: cb(None, h))
    else:
        _ana_thread(lambda: cb(None, _dil('galeri_fail')))


def _ui_thread(fn):
    try:
        from jnius import autoclass, PythonJavaClass, java_method
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        if activity is None:
            raise RuntimeError('activity yok')

        class _Run(PythonJavaClass):
            __javaclasses__ = ['java/lang/Runnable']

            @java_method('()V')
            def run(self):
                fn()

        activity.runOnUiThread(_Run())
    except Exception:
        try:
            from android.runnable import run_on_ui_thread

            @run_on_ui_thread
            def _wrap():
                fn()

            _wrap()
        except Exception:
            Clock.schedule_once(lambda *_: fn(), 0)


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


_GALERI_PAKETLER = (
    'com.miui.gallery',
    'com.google.android.apps.photos',
    'com.sec.android.gallery3d',
    'com.android.gallery3d',
    'com.coloros.gallery3d',
    'com.oneplus.gallery',
)


def _get_content_intent(Intent):
    intent = Intent(Intent.ACTION_GET_CONTENT)
    intent.setType('image/*')
    intent.addCategory(Intent.CATEGORY_OPENABLE)
    intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    return intent


def _galeri_intent_listesi(activity):
    """READ_MEDIA yok — Redmi/MIUI resolveActivity yalan soyler, filtre kullanma."""
    from jnius import autoclass
    Intent = autoclass('android.content.Intent')
    MediaStore = autoclass('android.provider.MediaStore')
    Build = autoclass('android.os.Build')

    sira = []
    seen = set()

    def ekle(intent, etiket):
        if etiket in seen:
            return
        seen.add(etiket)
        sira.append(intent)
        print(f'Galeri intent eklendi: {etiket}', flush=True)

    baslik = _dil('tus_galeri')
    if not baslik or baslik == 'tus_galeri':
        baslik = 'Fotoğraf seç'

    # MIUI/Redmi: chooser genelde tek calisan yol
    ekle(Intent.createChooser(_get_content_intent(Intent), baslik), 'chooser')
    ekle(_get_content_intent(Intent), 'get_content')

    open_doc = Intent(Intent.ACTION_OPEN_DOCUMENT)
    open_doc.setType('image/*')
    open_doc.addCategory(Intent.CATEGORY_OPENABLE)
    open_doc.addFlags(
        Intent.FLAG_GRANT_READ_URI_PERMISSION
        | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION,
    )
    ekle(open_doc, 'open_document')

    try:
        if int(Build.VERSION.SDK_INT) >= 33:
            pick = Intent('android.provider.action.PICK_IMAGES')
            pick.putExtra('android.provider.extra.PICK_IMAGES_MAX', 1)
            pick.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            ekle(pick, 'pick_images')
    except Exception:
        pass

    pick_one = Intent(Intent.ACTION_PICK)
    pick_one.setDataAndType(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, 'image/*')
    pick_one.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    ekle(pick_one, 'action_pick')

    for pkg in _GALERI_PAKETLER:
        try:
            pkg_intent = _get_content_intent(Intent)
            pkg_intent.setPackage(pkg)
            ekle(pkg_intent, f'pkg_{pkg}')
        except Exception:
            pass

    return sira


_galeri_intent_sira = []
_galeri_intent_idx = 0


def _galeri_sonraki_intent(activity):
    """Bir intent açılamazsa sıradakini dene."""
    global _galeri_callback, _galeri_intent_sira, _galeri_intent_idx
    cb = _galeri_callback
    if not cb or _galeri_intent_idx >= len(_galeri_intent_sira):
        _galeri_callback = None
        if cb:
            _galeri_sonuc_gonder(cb, hata=_dil('galeri_fail'))
        return
    intent = _galeri_intent_sira[_galeri_intent_idx]
    _galeri_intent_idx += 1

    def _ac():
        try:
            activity.startActivityForResult(intent, _GALERI_ISTEK)
        except Exception as e:
            print(f'Galeri intent hatasi: {e}', flush=True)
            _galeri_sonraki_intent(activity)

    _ui_thread(_ac)


def _galeri_android_picker(callback):
    """Android fotoğraf seçici — READ_MEDIA_IMAGES gerekmez."""
    global _galeri_callback, _galeri_intent_sira, _galeri_intent_idx
    activity = None
    try:
        _activity_bagla(zorla=True)
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        if activity is None:
            raise RuntimeError('Activity yok')

        _galeri_callback = callback
        _galeri_intent_sira = _galeri_intent_listesi(activity)
        _galeri_intent_idx = 0
        if not _galeri_intent_sira:
            raise RuntimeError('Galeri intent listesi bos')
        print(f'Galeri: {len(_galeri_intent_sira)} yontem hazir', flush=True)
        _galeri_sonraki_intent(activity)
    except Exception as e:
        print(f'Galeri picker: {e}', flush=True)
        _galeri_callback = None
        _galeri_sonuc_gonder(callback, hata=_dil('galeri_fail'))


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
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity

            if result_code != Activity.RESULT_OK:
                _galeri_sonuc_gonder(cb, hata=_dil('galeri_cancel'))
                return

            uri = _intent_gorsel_uri(intent)
            if uri:
                kayit = _kopyala(uri, intent)
                if kayit:
                    _galeri_sonuc_gonder(cb, yol=kayit)
                    return

            # Chooser/URI sorunu — sıradaki galeri yöntemini dene
            _galeri_callback = cb
            if activity is not None and _galeri_intent_idx < len(_galeri_intent_sira):
                print('Galeri: URI alinamadi, sonraki yontem deneniyor', flush=True)
                _galeri_sonraki_intent(activity)
                return

            _galeri_sonuc_gonder(cb, hata=_dil('galeri_fail'))
        except Exception:
            print(traceback.format_exc(), flush=True)
            _galeri_sonuc_gonder(cb, hata=_dil('galeri_fail'))
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


def _kopyala(kaynak, result_intent=None):
    if not kaynak:
        return None
    kaynak = str(kaynak).strip()
    if kaynak.startswith('file://'):
        kaynak = kaynak[7:]
    if kaynak.startswith('content://'):
        try:
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            resolver = context.getContentResolver()
            FileOutputStream = autoclass('java.io.FileOutputStream')
            uri = autoclass('android.net.Uri').parse(kaynak)

            if result_intent is not None:
                try:
                    flags = int(result_intent.getFlags())
                    read = int(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                    if flags & read:
                        try:
                            resolver.takePersistableUriPermission(uri, flags & read)
                        except Exception:
                            pass
                except Exception:
                    pass

            stream = resolver.openInputStream(uri)
            if stream is None:
                return None
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
            if os.path.getsize(hedef) > 0:
                return os.path.normpath(hedef)
            return None
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
