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
    # Not: Android'de mesaj her tetiklemede Java receiver tarafından yeniden
    # seçilir; buradaki metin yalnızca ilk zamanlama içindir.
    ek = [
        'Bugün hiç fal açmadın! Kahveni hazırla, fincanını çevir.',
        'Yıldızlar seni çağırıyor — kısa bir fal molası?',
        'Bugünün mesajı fincanda veya kartlarda olabilir.',
        'Bir kahve, bir kart — FalımaBak hazır.',
        'Tarot kartları bugün sana ne söyler? Hadi bir çekiş yap.',
        'Avucundaki çizgiler bir hikâye anlatıyor. El falına bak!',
        'Günün falını kaçırma! Bir bakış her şeyi değiştirebilir.',
    ]
    try:
        from dil import t
        return t('notif_title'), random.choice(ek)
    except Exception:
        return 'FalımaBak', random.choice(ek)


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


def bildirim_sistem_acik_mi():
    """Telefon ayarlarında uygulama bildirimleri kapalı mı?"""
    if not _android_mi():
        return True
    try:
        from jnius import autoclass
        NotificationManager = autoclass('android.app.NotificationManager')
        context = _context()
        nm = context.getSystemService('notification')
        if nm is None:
            return True
        if hasattr(nm, 'areNotificationsEnabled'):
            return bool(nm.areNotificationsEnabled())
        return True
    except Exception:
        return True


def bildirim_izni_hazir_bekle(callback, deneme=0, max_deneme=25, baslangic_gecikme=0):
    """POST_NOTIFICATIONS izni ve sistem ayarı hazır olunca callback çağır."""
    if not _android_mi():
        if baslangic_gecikme > 0:
            from kivy.clock import Clock
            Clock.schedule_once(lambda *_: callback(), baslangic_gecikme)
        else:
            callback()
        return
    if bildirim_izni_var_mi() and bildirim_sistem_acik_mi():
        if baslangic_gecikme > 0 and deneme == 0:
            from kivy.clock import Clock
            Clock.schedule_once(lambda *_: callback(), baslangic_gecikme)
        else:
            callback()
        return
    if deneme >= max_deneme:
        print('Bildirim: izin/sistem hazir degil (zaman asimi)', flush=True)
        return
    from kivy.clock import Clock
    gecikme = baslangic_gecikme if deneme == 0 else 2.0
    Clock.schedule_once(
        lambda *_: bildirim_izni_hazir_bekle(
            callback, deneme + 1, max_deneme, baslangic_gecikme=0,
        ),
        gecikme,
    )


def bildirim_izni_iste():
    if not _android_mi():
        return
    try:
        from android import api_version
        if api_version.API_VERSION < 33:
            return
    except Exception:
        pass
    # 1) p4a'nin standart izin penceresi (en guvenilir yontem).
    try:
        from android.permissions import request_permissions
        request_permissions(['android.permission.POST_NOTIFICATIONS'])
        return
    except Exception as e:
        print(f'Bildirim izni (p4a): {e}', flush=True)
    # 2) Yedek: ActivityCompat ile dogrudan iste.
    try:
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


def pil_kisitlamasi_var_mi():
    """Telefon uygulamayı pil optimizasyonuna tabi tutuyor mu? (True = kısıtlı).

    Kısıtlıysa Android/OEM, arka plandaki hatırlatma alarmlarını öldürebilir.
    """
    if not _android_mi():
        return False
    try:
        from android import api_version
        if api_version.API_VERSION < 23:
            return False
    except Exception:
        pass
    try:
        context = _context()
        pm = context.getSystemService('power')
        if pm is None:
            return False
        return not pm.isIgnoringBatteryOptimizations(context.getPackageName())
    except Exception as e:
        print(f'Pil kisitlama kontrolu: {e}', flush=True)
        return False


def pil_optimizasyon_ayarlarini_ac():
    """Pil optimizasyonu muafiyeti için ayar ekranını açar (Play-güvenli, izin gerektirmez)."""
    if not _android_mi():
        return
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        Settings = autoclass('android.provider.Settings')
        Uri = autoclass('android.net.Uri')
        activity = PythonActivity.mActivity
        pkg = activity.getPackageName()
        # 1) Pil optimizasyonu listesi — kullanıcı FalımaBak'ı "kısıtlama yok" yapar.
        try:
            intent = Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS)
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            activity.startActivity(intent)
            return
        except Exception as e:
            print(f'Pil ayarı (liste): {e}', flush=True)
        # 2) Yedek: uygulama detay ayarları (oradan Pil → Kısıtlama yok).
        intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
        intent.setData(Uri.parse(f'package:{pkg}'))
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        activity.startActivity(intent)
    except Exception as e:
        print(f'Pil optimizasyon ayarı: {e}', flush=True)


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
    intent = Intent('org.kumar.falimabak.falimabak.ACTION_REMINDER')
    intent.setPackage(PAKET)
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


def _py_anlik_bildirim(baslik, mesaj):
    """Java cagrisi olmazsa saf jnius ile anlik bildirim goster."""
    from jnius import autoclass, cast
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    NotificationManager = autoclass('android.app.NotificationManager')
    NotificationBuilder = autoclass('android.app.Notification$Builder')
    BuildVersion = autoclass('android.os.Build$VERSION')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')

    context = PythonActivity.mActivity.getApplicationContext()
    nm = cast(
        'android.app.NotificationManager',
        context.getSystemService(Context.NOTIFICATION_SERVICE),
    )

    kanal_id = 'falimabak_hatirlatma'
    if BuildVersion.SDK_INT >= 26:
        NotificationChannel = autoclass('android.app.NotificationChannel')
        kanal = NotificationChannel(kanal_id, 'Hatırlatmalar', NotificationManager.IMPORTANCE_HIGH)
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

    try:
        ikon = context.getResources().getIdentifier('ic_notify', 'drawable', context.getPackageName())
        if not ikon:
            ikon = context.getApplicationInfo().icon
    except Exception:
        ikon = context.getApplicationInfo().icon

    builder.setSmallIcon(ikon)
    builder.setContentTitle(baslik)
    builder.setContentText(mesaj)
    builder.setContentIntent(pi)
    builder.setAutoCancel(True)
    nm.notify(9002, builder.build())


def bildirim_anlik_goster(mesaj=None):
    """Anlik onay bildirimi — bildirim acilinca/izin verilince."""
    if not _android_mi():
        return False
    if not bildirim_izni_var_mi():
        return False
    if not bildirim_sistem_acik_mi():
        return False
    baslik = 'FalımaBak'
    if not mesaj:
        mesaj = 'Hatırlatmalar açık! Fal zamanı geldiğinde seni uyaracağız.'
    try:
        from jnius import autoclass
        Receiver = autoclass('org.kumar.falimabak.falimabak.FalimabakAlarmReceiver')
        Receiver.showInstant(_context(), baslik, mesaj)
        return True
    except Exception as e:
        print(f'Anlik bildirim (Java): {e}', flush=True)
    try:
        _py_anlik_bildirim(baslik, mesaj)
        return True
    except Exception as e:
        print(f'Anlik bildirim (Python): {e}', flush=True)
        return False


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
    if not _android_mi():
        return
    bildirim_izni_iste()

    def _zamanla():
        if not bildirim_izni_var_mi():
            print('Bildirim: POST_NOTIFICATIONS izni yok', flush=True)
            return
        if not bildirim_sistem_acik_mi():
            print('Bildirim: sistem ayarlarinda kapali', flush=True)
            return
        bildirim_zamanla()

    bildirim_izni_hazir_bekle(_zamanla, baslangic_gecikme=1.0)


def bildirim_izinleri_kontrol():
    """İzin yoksa ayarlara yönlendir."""
    if not _android_mi():
        return
    if not bildirim_sistem_acik_mi() or not bildirim_izni_var_mi():
        bildirim_ayarlari_ac()
    elif not tam_alarm_izni_var_mi():
        tam_alarm_ayarlarini_ac()
