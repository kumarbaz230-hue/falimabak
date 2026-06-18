"""Periyodik fal hatırlatma bildirimleri (Android)."""

import os

PAKET = 'org.kumar.falimabak.falimabak'
RECEIVER_SINIF = f'{PAKET}.FalimabakAlarmReceiver'
ALARM_REQUEST = 9001
BILDIRIM_ARALIK_SAAT = 2


def _android_mi():
    return (
        'ANDROID_ARGUMENT' in os.environ
        or 'ANDROID_ROOT' in os.environ
        or 'ANDROID_BOOTLOGO' in os.environ
    )


def _bildirim_metinleri():
    try:
        from dil import t
        return t('notif_title'), t('notif_body')
    except Exception:
        return 'FalımaBak', 'Bugün falına baktın mı?'


def _aralik_ms():
    from gecmis import bildirim_aralik_saat_al
    saat = max(1, min(int(bildirim_aralik_saat_al()), 6))
    return saat * 60 * 60 * 1000


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
        from datetime import datetime, timedelta
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        PendingIntent = autoclass('android.app.PendingIntent')
        AlarmManager = autoclass('android.app.AlarmManager')
        ComponentName = autoclass('android.content.ComponentName')
        activity = PythonActivity.mActivity
        context = activity.getApplicationContext()

        baslik, mesaj = _bildirim_metinleri()
        aralik_ms = _aralik_ms()
        aralik_saat = aralik_ms // (60 * 60 * 1000)

        now = datetime.now()
        hedef = now + timedelta(hours=aralik_saat)

        intent = Intent()
        intent.setComponent(ComponentName(PAKET, RECEIVER_SINIF))
        intent.putExtra('title', baslik)
        intent.putExtra('text', mesaj)
        intent.putExtra('interval_ms', aralik_ms)
        intent.putExtra('reschedule', True)
        pi = PendingIntent.getBroadcast(
            context, ALARM_REQUEST, intent,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE,
        )
        am = context.getSystemService('alarm')
        trigger_ms = int(hedef.timestamp() * 1000)
        if hasattr(AlarmManager, 'setExactAndAllowWhileIdle'):
            am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, trigger_ms, pi)
        elif hasattr(AlarmManager, 'setExact'):
            am.setExact(AlarmManager.RTC_WAKEUP, trigger_ms, pi)
        else:
            am.set(AlarmManager.RTC_WAKEUP, trigger_ms, pi)
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
