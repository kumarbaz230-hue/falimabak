package org.kumar.falimabak.falimabak;

import android.app.AlarmManager;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

import androidx.core.app.NotificationCompat;
import androidx.core.content.ContextCompat;

import org.kivy.android.PythonActivity;

import java.util.Random;

public class FalimabakAlarmReceiver extends BroadcastReceiver {
    public static final String CHANNEL_ID = "falimabak_hatirlatma";
    public static final int ALARM_REQUEST = 9001;
    public static final int TEST_NOTIFY_ID = 9002;
    public static final long DEFAULT_INTERVAL_MS = 2L * 60L * 60L * 1000L;
    public static final long DEFAULT_FIRST_DELAY_MS = 15L * 60L * 1000L;

    // Fal ile ilgili çeşitli hatırlatma mesajları — her bildirimde rastgele seçilir.
    private static final String[] FAL_MESAJLARI = {
        "Bugün hiç fal açmadın! Kahveni hazırla, fincanını çevir.",
        "Yıldızlar seni çağırıyor — kısa bir fal molası?",
        "Bugünün mesajı fincanda veya kartlarda olabilir.",
        "Bir kahve, bir kart — FalımaBak hazır.",
        "Merak etme, falına bakmak için her zaman geç değil.",
        "Tarot kartları bugün sana ne söyler? Hadi bir çekiş yap.",
        "Avucundaki çizgiler bir hikâye anlatıyor. El falına bak!",
        "Kahve telven bugün şanslı bir işaret taşıyor olabilir.",
        "Burç yorumun hazır — bugün seni neler bekliyor?",
        "Rüyanı mı gördün? Anlamını FalımaBak'ta keşfet.",
        "Günün falını kaçırma! Bir bakış her şeyi değiştirebilir.",
        "FalımaBak seni özledi — bugünkü kaderine göz at."
    };

    private static String pickMessage() {
        int i = new Random().nextInt(FAL_MESAJLARI.length);
        return FAL_MESAJLARI[i];
    }

    /** Anında bildirim — uygulama izni verince/açınca onay icin (Python'dan cagrilir). */
    public static void showInstant(Context context, String title, String text) {
        if (context == null || !canNotify(context)) {
            return;
        }
        if (title == null || title.isEmpty()) {
            title = "FalımaBak";
        }
        if (text == null || text.isEmpty()) {
            text = pickMessage();
        }
        showNotification(context, title, text, TEST_NOTIFY_ID);
    }

    /** Bildirim icin guvenli kucuk ikon: once ic_notify, olmazsa uygulama ikonu. */
    private static int resolveSmallIcon(Context context) {
        try {
            int id = context.getResources().getIdentifier(
                "ic_notify", "drawable", context.getPackageName()
            );
            if (id != 0) {
                return id;
            }
        } catch (Throwable ignored) {
        }
        try {
            return context.getApplicationInfo().icon;
        } catch (Throwable ignored) {
            return android.R.drawable.ic_dialog_info;
        }
    }

    @Override
    public void onReceive(Context context, Intent intent) {
        String title = intent.getStringExtra("title");
        if (title == null || title.isEmpty()) {
            title = "FalımaBak";
        }
        // Her tetiklemede taze/çeşitli mesaj seç (uygulama kapalı olsa bile çalışır).
        String text = pickMessage();

        long intervalMs = intent.getLongExtra("interval_ms", DEFAULT_INTERVAL_MS);
        if (intervalMs < 60L * 60L * 1000L) {
            intervalMs = DEFAULT_INTERVAL_MS;
        }

        if (!canNotify(context)) {
            scheduleAlarm(context, title, text, intervalMs, intervalMs);
            return;
        }

        showNotification(context, title, text, ALARM_REQUEST);

        // setAlarmClock tek seferlik olduğu için her seferinde yeniden zamanla.
        scheduleAlarm(context, title, text, intervalMs, intervalMs);
    }

    private static void showNotification(Context context, String title, String text, int notifyId) {
        NotificationManager nm = (NotificationManager)
            context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm == null) {
            return;
        }

        ensureChannel(nm);

        Intent launch = new Intent(context, PythonActivity.class);
        launch.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        int flags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            flags |= PendingIntent.FLAG_IMMUTABLE;
        }
        PendingIntent pi = PendingIntent.getActivity(context, notifyId, launch, flags);

        int icon = resolveSmallIcon(context);
        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(icon)
            .setContentTitle(title)
            .setContentText(text)
            .setStyle(new NotificationCompat.BigTextStyle().bigText(text))
            .setContentIntent(pi)
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setDefaults(NotificationCompat.DEFAULT_ALL);

        try {
            nm.notify(notifyId, builder.build());
        } catch (Throwable e) {
            // Ikon vb. bir sorun olursa sistem ikonuyla tekrar dene.
            builder.setSmallIcon(android.R.drawable.ic_dialog_info);
            try {
                nm.notify(notifyId, builder.build());
            } catch (Throwable ignored) {
            }
        }
    }

    public static void scheduleAlarm(
        Context context,
        String title,
        String text,
        long intervalMs,
        long delayMs
    ) {
        AlarmManager am = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        if (am == null) {
            return;
        }
        if (intervalMs < 60L * 60L * 1000L) {
            intervalMs = DEFAULT_INTERVAL_MS;
        }
        if (delayMs < 60L * 1000L) {
            delayMs = DEFAULT_FIRST_DELAY_MS;
        }

        Intent next = new Intent();
        next.setComponent(new ComponentName(context, FalimabakAlarmReceiver.class));
        next.putExtra("title", title);
        next.putExtra("text", text);
        next.putExtra("interval_ms", intervalMs);
        next.putExtra("reschedule", true);

        int flags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            flags |= PendingIntent.FLAG_IMMUTABLE;
        }
        PendingIntent alarmPi = PendingIntent.getBroadcast(context, ALARM_REQUEST, next, flags);
        long trigger = System.currentTimeMillis() + delayMs;

        Intent show = new Intent(context, PythonActivity.class);
        show.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent showPi = PendingIntent.getActivity(context, ALARM_REQUEST + 100, show, flags);

        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                AlarmManager.AlarmClockInfo info =
                    new AlarmManager.AlarmClockInfo(trigger, showPi);
                am.setAlarmClock(info, alarmPi);
            } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, trigger, alarmPi);
            } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
                am.setExact(AlarmManager.RTC_WAKEUP, trigger, alarmPi);
            } else {
                am.set(AlarmManager.RTC_WAKEUP, trigger, alarmPi);
            }
        } catch (SecurityException e) {
            try {
                am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, trigger, alarmPi);
            } catch (Exception ignored) {
            }
        }
    }

    private static boolean canNotify(Context context) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) {
            return true;
        }
        return ContextCompat.checkSelfPermission(
            context, android.Manifest.permission.POST_NOTIFICATIONS
        ) == android.content.pm.PackageManager.PERMISSION_GRANTED;
    }

    private static void ensureChannel(NotificationManager nm) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
            return;
        }
        NotificationChannel ch = new NotificationChannel(
            CHANNEL_ID,
            "Hatırlatmalar",
            NotificationManager.IMPORTANCE_HIGH
        );
        ch.setDescription("Fal hatırlatmaları");
        ch.enableVibration(true);
        nm.createNotificationChannel(ch);
    }
}
