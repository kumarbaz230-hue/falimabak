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

import org.kivy.android.PythonActivity;

public class FalimabakAlarmReceiver extends BroadcastReceiver {
    private static final String CHANNEL_ID = "falimabak_hatirlatma";
    private static final int ALARM_REQUEST = 9001;
    private static final long DEFAULT_INTERVAL_MS = 2L * 60L * 60L * 1000L;

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

        NotificationManager nm = (NotificationManager)
            context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm == null) {
            return;
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel ch = new NotificationChannel(
                CHANNEL_ID,
                "Hatırlatmalar",
                NotificationManager.IMPORTANCE_DEFAULT
            );
            nm.createNotificationChannel(ch);
        }

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
            .setPriority(NotificationCompat.PRIORITY_DEFAULT);

        nm.notify(ALARM_REQUEST, builder.build());

        if (intent.getBooleanExtra("reschedule", false)) {
            long intervalMs = intent.getLongExtra("interval_ms", DEFAULT_INTERVAL_MS);
            if (intervalMs < 60L * 60L * 1000L) {
                intervalMs = DEFAULT_INTERVAL_MS;
            }
            scheduleNext(context, title, text, intervalMs);
        }
    }

    private void scheduleNext(Context context, String title, String text, long intervalMs) {
        AlarmManager am = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        if (am == null) {
            return;
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
        long trigger = System.currentTimeMillis() + intervalMs;

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, trigger, pi);
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
            am.setExact(AlarmManager.RTC_WAKEUP, trigger, pi);
        } else {
            am.set(AlarmManager.RTC_WAKEUP, trigger, pi);
        }
    }
}
