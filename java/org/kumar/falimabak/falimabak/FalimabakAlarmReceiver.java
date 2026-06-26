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

public class FalimabakAlarmReceiver extends BroadcastReceiver {
    public static final String CHANNEL_ID = "falimabak_hatirlatma";
    public static final int ALARM_REQUEST = 9001;
    public static final long DEFAULT_INTERVAL_MS = 2L * 60L * 60L * 1000L;
    public static final long DEFAULT_FIRST_DELAY_MS = 30L * 60L * 1000L;

    @Override
    public void onReceive(Context context, Intent intent) {
        String title = intent.getStringExtra("title");
        String text = intent.getStringExtra("text");
        if (title == null || title.isEmpty()) {
            title = "FalımaBak";
        }
        if (text == null || text.isEmpty()) {
            text = "Bugün falına baktın mı?";
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(
                    context, android.Manifest.permission.POST_NOTIFICATIONS
                ) != android.content.pm.PackageManager.PERMISSION_GRANTED) {
                long intervalMs = intent.getLongExtra("interval_ms", DEFAULT_INTERVAL_MS);
                if (intervalMs < 60L * 60L * 1000L) {
                    intervalMs = DEFAULT_INTERVAL_MS;
                }
                scheduleAlarm(context, title, text, intervalMs, intervalMs);
                return;
            }
        }

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
        PendingIntent pi = PendingIntent.getActivity(context, ALARM_REQUEST, launch, flags);

        int icon = context.getApplicationInfo().icon;
        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(icon)
            .setContentTitle(title)
            .setContentText(text)
            .setContentIntent(pi)
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setDefaults(NotificationCompat.DEFAULT_ALL);

        nm.notify(ALARM_REQUEST, builder.build());

        if (intent.getBooleanExtra("reschedule", false)) {
            long intervalMs = intent.getLongExtra("interval_ms", DEFAULT_INTERVAL_MS);
            if (intervalMs < 60L * 60L * 1000L) {
                intervalMs = DEFAULT_INTERVAL_MS;
            }
            scheduleAlarm(context, title, text, intervalMs, intervalMs);
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
        if (delayMs < 5L * 60L * 1000L) {
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
        PendingIntent pi = PendingIntent.getBroadcast(context, ALARM_REQUEST, next, flags);
        long trigger = System.currentTimeMillis() + delayMs;

        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                if (am.canScheduleExactAlarms()) {
                    am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, trigger, pi);
                } else {
                    am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, trigger, pi);
                }
            } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, trigger, pi);
            } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
                am.setExact(AlarmManager.RTC_WAKEUP, trigger, pi);
            } else {
                am.set(AlarmManager.RTC_WAKEUP, trigger, pi);
            }
        } catch (SecurityException e) {
            am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, trigger, pi);
        }
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
