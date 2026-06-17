package org.kumar.falimabak.falimabak;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

import androidx.core.app.NotificationCompat;

import org.kivy.android.PythonActivity;

public class FalimabakAlarmReceiver extends BroadcastReceiver {
    private static final String CHANNEL_ID = "falimabak_hatirlatma";

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
        PendingIntent pi = PendingIntent.getActivity(context, 9001, launch, flags);

        int icon = context.getApplicationInfo().icon;
        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(icon)
            .setContentTitle(title)
            .setContentText(text)
            .setContentIntent(pi)
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT);

        nm.notify(9001, builder.build());
    }
}
