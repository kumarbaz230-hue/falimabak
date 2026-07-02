package org.kumar.falimabak.falimabak;

import android.content.Context;
import android.content.SharedPreferences;

import com.google.android.play.core.appupdate.AppUpdateManager;
import com.google.android.play.core.appupdate.AppUpdateManagerFactory;
import com.google.android.play.core.install.model.UpdateAvailability;

/**
 * Play Store'da yeni sürüm varsa tek seferlik güncelleme bildirimi.
 * Sunucu/FCM gerekmez — Google Play App Update API kullanır.
 */
public class PlayUpdateHelper {
    private static final String PREFS = "falimabak_guncelleme";
    private static final String KEY_LAST_NOTIFY = "last_notify_vc";

    private static int getVersionCode(Context ctx) {
        try {
            return ctx.getPackageManager()
                .getPackageInfo(ctx.getPackageName(), 0).versionCode;
        } catch (Throwable ignored) {
            return 0;
        }
    }

    /**
     * Play'de kurulu sürümden yeni bir sürüm varsa bildirim göster (sürüm başına bir kez).
     */
    public static void checkAndNotify(Context context, String title, String message) {
        if (context == null) {
            return;
        }
        Context app = context.getApplicationContext();
        AppUpdateManager manager = AppUpdateManagerFactory.create(app);
        manager.getAppUpdateInfo().addOnSuccessListener(info -> {
            try {
                if (info.updateAvailability() != UpdateAvailability.UPDATE_AVAILABLE) {
                    return;
                }
                int available = info.availableVersionCode();
                int installed = getVersionCode(app);
                if (available <= installed) {
                    return;
                }
                SharedPreferences prefs = app.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
                int lastNotified = prefs.getInt(KEY_LAST_NOTIFY, 0);
                if (available == lastNotified) {
                    return;
                }
                prefs.edit().putInt(KEY_LAST_NOTIFY, available).apply();
                FalimabakAlarmReceiver.showGuncelleme(app, title, message);
            } catch (Throwable ignored) {
            }
        });
    }
}
