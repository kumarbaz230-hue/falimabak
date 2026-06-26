package org.kumar.falimabak.falimabak;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/**
 * Telefon yeniden başlayınca hatırlatma alarmını yeniden kurar.
 */
public class FalimabakBootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent == null) {
            return;
        }
        String action = intent.getAction();
        if (Intent.ACTION_BOOT_COMPLETED.equals(action)
                || Intent.ACTION_MY_PACKAGE_REPLACED.equals(action)
                || "android.intent.action.QUICKBOOT_POWERON".equals(action)) {
            FalimabakAlarmReceiver.scheduleAlarm(
                context,
                "FalımaBak",
                "Bugün falına baktın mı? FalımaBak seni bekliyor.",
                FalimabakAlarmReceiver.DEFAULT_INTERVAL_MS,
                FalimabakAlarmReceiver.DEFAULT_FIRST_DELAY_MS
            );
        }
    }
}
