"""Periyodik fal hatırlatma bildirimleri (Android)."""

import os
import random

PAKET = 'org.kumar.falimabak.falimabak'
RECEIVER_SINIF = f'{PAKET}.FalimabakAlarmReceiver'
ALARM_REQUEST = 9001
ILK_GECIKME_DK = 15


def _android_mi():
    return (
        'ANDROID_ARGUMENT' in os.environ
        or 'ANDROID_ROOT' in os.environ
        or 'ANDROID_BOOTLOGO' in os.environ
    )


def _bildirim_metinleri():
    try:
        from dil import t
        baslik = t('notif_title')
        ek = [
            t('notif_body'),
            'Yıldızlar seni çağırıyor — kısa bir fal molası?',
            'Bugünün mesajı fincanda veya kartlarda olabilir.',
            'Bir kahve, bir kart — FalımaBak hazır.',
        ]
        return baslik, random.choice(ek)
    except Exception:
        return 'FalımaBak', 'Bugün falına baktın mı?'


def _aralik_ms():
    from gecmis import bildirim_aralik_saat_al
    saat = max(1, min(int(bildirim_aralik_saat_al()), 6))
    return saat * 60 * 60 * 1000


def _ilk_gecikme_ms():
    return ILK_GECIKME_DK * 60 * 1000


def _context():
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    return PythonActivity.mActivity.getApplicationContext()


def bildirim_izni_var_mi():
    if not _android_mi():
        return True
    try:
        from android import api_version
        if api_version.API_VERSION < 33:
            return True
        from jnius import autoclass
        ContextCompat = autoclass('androidx.core.content.ContextCompat')
        Manifest = autoclass('android.Manifest')
        PackageManager = autoclass('android.content.pm.PackageManager')
        context = _context()
        return ContextCompat.checkSelfPermission(
            context, Manifest.permission.POST_NOTIFICATIONS,
        ) == PackageManager.PERMISSION_GRANTED
    except Exception:
        return True


def bildirim_izni_iste():
    if not _android_mi():
        return
    try:
        from android import api_version
        if api_version.API_VERSION < 33:
            return
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        ActivityCompat = autoclass('androidx.core.app.ActivityCompat')
        Manifest = autoclass('android.Manifest')
        activity = PythonActivity.mActivity
        if ActivityCompat.checkSelfPermission(
            activity, Manifest.permission.POST_NOTIFICATIONS
        ) != 0:
            ActivityCompat.requestPermissions(
                activity, [Manifest.permission.POST_NOTIFICATIONS], 9100
            )
    except Exception as e:
        print(f'Bildirim izni: {e}', flush=True)


def bildirim_ayarlari_ac():
    """Uygulama bildirim ayarlarını aç."""
    if not _android_mi():
        return
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        Settings = autoclass('android.provider.Settings')
        activity = PythonActivity.mActivity
        pkg = activity.getPackageName()
        if hasattr(Settings, 'ACTION_APP_NOTIFICATION_SETTINGS'):
            intent = Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS)
            intent.putExtra(Settings.EXTRA_APP_PACKAGE, pkg)
        else:
            intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
            intent.setData(autoclass('android.net.Uri').parse(f'package:{pkg}'))
        activity.startActivity(intent)
    except Exception as e:
        print(f'Bildirim ayarları: {e}', flush=True)


def tam_alarm_izni_var_mi():
    if not _android_mi():
        return True
    try:
        from android import api_version
        if api_version.API_VERSION < 31:
            return True
        context = _context()
        am = context.getSystemService('alarm')
        return am.canScheduleExactAlarms()
    except Exception:
        return True


def tam_alarm_ayarlarini_ac():
    if not _android_mi() or tam_alarm_izni_var_mi():
        return
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        Settings = autoclass('android.provider.Settings')
        activity = PythonActivity.mActivity
        intent = Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM)
        intent.setData(
            autoclass('android.net.Uri').parse(f'package:{activity.getPackageName()}')
        )
        activity.startActivity(intent)
    except Exception as e:
        print(f'Tam alarm ayarı: {e}', flush=True)


def bildirim_iptal():
    if not _android_mi():
        return
    try:
        from jnius import autoclass
        Intent = autoclass('android.content.Intent')
        PendingIntent = autoclass('android.app.PendingIntent')
        ComponentName = autoclass('android.content.ComponentName')
        context = _context()
        intent = Intent()
        intent.setComponent(ComponentName(PAKET, RECEIVER_SINIF))
        pi = PendingIntent.getBroadcast(
            context, ALARM_REQUEST, intent,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE,
        )
        am = context.getSystemService('alarm')
        am.cancel(pi)
    except Exception as e:
        print(f'Bildirim iptal: {e}', flush=True)


def _java_zamanla(baslik, mesaj, aralik_ms, ilk_ms):
    from jnius import autoclass
    Receiver = autoclass('org.kumar.falimabak.falimabak.FalimabakAlarmReceiver')
    Receiver.scheduleAlarm(_context(), baslik, mesaj, int(aralik_ms), int(ilk_ms))


def _py_zamanla(baslik, mesaj, aralik_ms, ilk_ms):
    """Java çağrısı başarısız olursa yedek."""
    from datetime import datetime, timedelta
    from jnius import autoclass
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    AlarmManager = autoclass('android.app.AlarmManager')
    ComponentName = autoclass('android.content.ComponentName')
    context = _context()
    intent = Intent()
    intent.setComponent(ComponentName(PAKET, RECEIVER_SINIF))
    intent.putExtra('title', baslik)
    intent.putExtra('text', mesaj)
    intent.putExtra('interval_ms', int(aralik_ms))
    intent.putExtra('reschedule', True)
    pi = PendingIntent.getBroadcast(
        context, ALARM_REQUEST, intent,
        PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE,
    )
    am = context.getSystemService('alarm')
    trigger_ms = int((datetime.now() + timedelta(milliseconds=ilk_ms)).timestamp() * 1000)
    try:
        am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, trigger_ms, pi)
    except Exception:
        am.set(AlarmManager.RTC_WAKEUP, trigger_ms, pi)


def _py_test_bildirim(baslik, mesaj):
    """Java receiver yoksa saf jnius ile bildirim göster (yedek)."""
    from jnius import autoclass, cast
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    NotificationManager = autoclass('android.app.NotificationManager')
    NotificationBuilder = autoclass('android.app.Notification$Builder')
    BuildVersion = autoclass('android.os.Build$VERSION')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')

    activity = PythonActivity.mActivity
    context = activity.getApplicationContext()
    nm = cast(
        'android.app.NotificationManager',
        context.getSystemService(Context.NOTIFICATION_SERVICE),
    )

    kanal_id = 'falimabak_hatirlatma'
    if BuildVersion.SDK_INT >= 26:
        NotificationChannel = autoclass('android.app.NotificationChannel')
        kanal = NotificationChannel(
            kanal_id, 'Hatırlatmalar', NotificationManager.IMPORTANCE_HIGH,
        )
        kanal.setDescription('Fal hatırlatmaları')
        kanal.enableVibration(True)
        nm.createNotificationChannel(kanal)
        builder = NotificationBuilder(context, kanal_id)
    else:
        builder = NotificationBuilder(context)

    launch = Intent(context, PythonActivity)
    launch.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP)
    flags = PendingIntent.FLAG_UPDATE_CURRENT
    if BuildVersion.SDK_INT >= 23:
        flags |= PendingIntent.FLAG_IMMUTABLE
    pi = PendingIntent.getActivity(context, 9002, launch, flags)

    ikon = context.getApplicationInfo().icon
    builder.setSmallIcon(ikon)
    builder.setContentTitle(baslik)
    builder.setContentText(mesaj)
    builder.setContentIntent(pi)
    builder.setAutoCancel(True)
    nm.notify(9002, builder.build())


def bildirim_test_goster():
    """Anında test bildirimi — Ayarlar'dan."""
    if not _android_mi():
        return False, 'Sadece Android'
    # Android 13+ izni yoksa önce runtime izin penceresini göster.
    if not bildirim_izni_var_mi():
        bildirim_izni_iste()
        return False, 'Bildirim izni gerekli — izni verip tekrar deneyin'

    baslik = 'FalımaBak'
    mesaj = 'Hatırlatmalar çalışıyor! Periyodik fallar yolda.'
    java_hata = None
    try:
        from jnius import autoclass
        Receiver = autoclass('org.kumar.falimabak.falimabak.FalimabakAlarmReceiver')
        Receiver.showTestNotification(_context(), baslik, mesaj)
        return True, None
    except Exception as e:
        java_hata = e
        print(f'Bildirim test (Java): {e}', flush=True)

    # Java receiver APK'da yoksa saf jnius ile dene.
    try:
        _py_test_bildirim(baslik, mesaj)
        return True, None
    except Exception as e:
        print(f'Bildirim test (Python): {e}', flush=True)
        return False, str(java_hata or e)


def bildirim_zamanla():
    from gecmis import bildirim_acik_al
    if not bildirim_acik_al():
        bildirim_iptal()
        return
    if not _android_mi():
        return
    baslik, mesaj = _bildirim_metinleri()
    aralik_ms = _aralik_ms()
    ilk_ms = _ilk_gecikme_ms()
    try:
        _java_zamanla(baslik, mesaj, aralik_ms, ilk_ms)
    except Exception as e:
        print(f'Bildirim Java zamanla hatasi: {e}', flush=True)
        try:
            _py_zamanla(baslik, mesaj, aralik_ms, ilk_ms)
        except Exception as e2:
            print(f'Bildirim Python zamanla hatasi: {e2}', flush=True)
            return
    izin = 'OK' if bildirim_izni_var_mi() else 'YOK'
    alarm = 'OK' if tam_alarm_izni_var_mi() else 'YOK'
    print(
        f'Bildirim planlandi: ilk={ILK_GECIKME_DK}dk, '
        f'aralik={aralik_ms // 3600000}saat, izin={izin}, tam_alarm={alarm}',
        flush=True,
    )
    if not bildirim_izni_var_mi():
        print('Bildirim: POST_NOTIFICATIONS izni yok', flush=True)
    if not tam_alarm_izni_var_mi():
        tam_alarm_ayarlarini_ac()


def bildirim_baslat():
    from gecmis import bildirim_acik_al
    if not bildirim_acik_al():
        bildirim_iptal()
        return
    bildirim_izni_iste()
    bildirim_zamanla()


def bildirim_izinleri_kontrol():
    """İzin yoksa ayarlara yönlendir."""
    if not _android_mi():
        return
    if not bildirim_izni_var_mi():
        bildirim_ayarlari_ac()
    elif not tam_alarm_izni_var_mi():
        tam_alarm_ayarlarini_ac()
