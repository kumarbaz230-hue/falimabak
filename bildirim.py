"""Periyodik fal hatırlatma bildirimleri (Android)."""

import os
import random

PAKET = 'org.kumar.falimabak.falimabak'
RECEIVER_SINIF = f'{PAKET}.FalimabakAlarmReceiver'
ALARM_REQUEST = 9001
ILK_GECIKME_DK = 30


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
        govde = t('notif_body')
        ek = [
            t('notif_body'),
            'Yıldızlar seni çağırıyor — kısa bir fal molası?',
            'Bugünün mesajı fincanda veya kartlarda olabilir.',
            'Bir kahve, bir kart — FalımaBak hazır.',
        ]
        if len(ek) > 1:
            govde = random.choice(ek)
        return baslik, govde
    except Exception:
        return 'FalımaBak', 'Bugün falına baktın mı?'


def _aralik_ms():
    from gecmis import bildirim_aralik_saat_al
    saat = max(1, min(int(bildirim_aralik_saat_al()), 6))
    return saat * 60 * 60 * 1000


def _ilk_gecikme_ms():
    return ILK_GECIKME_DK * 60 * 1000


def bildirim_izni_var_mi():
    if not _android_mi():
        return True
    try:
        from android import api_version
        if api_version.API_VERSION < 33:
            return True
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        ContextCompat = autoclass('androidx.core.content.ContextCompat')
        Manifest = autoclass('android.Manifest')
        PackageManager = autoclass('android.content.pm.PackageManager')
        context = PythonActivity.mActivity.getApplicationContext()
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


def tam_alarm_izni_var_mi():
    if not _android_mi():
        return True
    try:
        from android import api_version
        if api_version.API_VERSION < 31:
            return True
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        AlarmManager = autoclass('android.app.AlarmManager')
        context = PythonActivity.mActivity.getApplicationContext()
        am = context.getSystemService('alarm')
        return am.canScheduleExactAlarms()
    except Exception:
        return True


def tam_alarm_ayarlarini_ac():
    """Android 12+ tam alarm izni kapalıysa ayarlara yönlendir."""
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
            autoclass('android.net.Uri').parse(
                f'package:{activity.getPackageName()}'
            )
        )
        activity.startActivity(intent)
    except Exception as e:
        print(f'Tam alarm ayarı: {e}', flush=True)


def bildirim_iptal():
    if not _android_mi():
        return
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        PendingIntent = autoclass('android.app.PendingIntent')
        ComponentName = autoclass('android.content.ComponentName')
        activity = PythonActivity.mActivity
        context = activity.getApplicationContext()
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


def bildirim_zamanla():
    from gecmis import bildirim_acik_al
    if not bildirim_acik_al():
        bildirim_iptal()
        return
    if not _android_mi():
        return
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        FalimabakAlarmReceiver = autoclass(
            'org.kumar.falimabak.falimabak.FalimabakAlarmReceiver'
        )
        context = PythonActivity.mActivity.getApplicationContext()
        baslik, mesaj = _bildirim_metinleri()
        aralik_ms = _aralik_ms()
        ilk_ms = _ilk_gecikme_ms()
        FalimabakAlarmReceiver.scheduleAlarm(
            context, baslik, mesaj, aralik_ms, ilk_ms,
        )
        izin = 'OK' if bildirim_izni_var_mi() else 'YOK'
        alarm = 'OK' if tam_alarm_izni_var_mi() else 'YOK'
        print(
            f'Bildirim planlandi: ilk={ILK_GECIKME_DK}dk sonra, '
            f'aralik={aralik_ms // 3600000}saat, izin={izin}, tam_alarm={alarm}',
            flush=True,
        )
        if not tam_alarm_izni_var_mi():
            tam_alarm_ayarlarini_ac()
    except Exception as e:
        print(f'Bildirim zamanla: {e}', flush=True)


def bildirim_baslat():
    """Uygulama açılışında veya arka plana giderken hatırlatmayı planla."""
    from gecmis import bildirim_acik_al
    if not bildirim_acik_al():
        bildirim_iptal()
        return
    bildirim_izni_iste()
    bildirim_zamanla()
