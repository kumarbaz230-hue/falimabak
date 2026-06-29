package org.kumar.falimabak.falimabak;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;

import com.google.android.play.core.review.ReviewInfo;
import com.google.android.play.core.review.ReviewManager;
import com.google.android.play.core.review.ReviewManagerFactory;

/**
 * Play Store değerlendirme — önce uygulama içi diyalog, olmazsa mağaza sayfası.
 */
public class PlayReviewHelper {
    private static final String PAKET = "org.kumar.falimabak.falimabak";
    private static final String WEB_URL =
        "https://play.google.com/store/apps/details?id=" + PAKET;

    /** Google In-App Review diyalogunu dene (uygulamadan çıkmadan). */
    public static boolean tryInAppReview(Activity activity) {
        if (activity == null) {
            return false;
        }
        try {
            ReviewManager manager = ReviewManagerFactory.create(activity);
            manager.requestReviewFlow().addOnCompleteListener(task -> {
                if (!task.isSuccessful()) {
                    return;
                }
                ReviewInfo info = task.getResult();
                manager.launchReviewFlow(activity, info);
            });
            return true;
        } catch (Throwable ignored) {
            return false;
        }
    }

    /** Harici Play Store / tarayıcı sayfasını aç. */
    public static boolean openStoreListing(Activity activity) {
        if (activity == null) {
            return false;
        }
        try {
            Intent market = new Intent(
                Intent.ACTION_VIEW,
                Uri.parse("market://details?id=" + PAKET)
            );
            market.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            activity.startActivity(market);
            return true;
        } catch (ActivityNotFoundException ignored) {
            // Play Store yok — web sayfası
        } catch (Throwable ignored) {
        }
        try {
            Intent web = new Intent(Intent.ACTION_VIEW, Uri.parse(WEB_URL));
            web.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            activity.startActivity(web);
            return true;
        } catch (Throwable ignored) {
            return false;
        }
    }
}
