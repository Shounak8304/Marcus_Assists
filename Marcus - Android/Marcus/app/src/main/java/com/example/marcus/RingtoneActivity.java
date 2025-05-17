package com.example.marcus;

import android.content.Context;
import android.media.Ringtone;
import android.media.RingtoneManager;
import android.net.Uri;
import android.util.Log;

public class RingtoneActivity {
    private Context context;
    private Ringtone ringtone;

    public RingtoneActivity(Context context) {
        this.context = context;
    }

    public void playRingtone() {
        try {
            Uri ringtoneUri = RingtoneManager.getActualDefaultRingtoneUri(context, RingtoneManager.TYPE_RINGTONE);
            if (ringtoneUri != null) {
                ringtone = RingtoneManager.getRingtone(context, ringtoneUri);
                if (ringtone != null) {
                    ringtone.play();
                    Log.d("RingtoneActivity", "🔊 Playing default ringtone...");
                } else {
                    Log.e("RingtoneActivity", "⚠️ Ringtone is null.");
                }
            } else {
                Log.e("RingtoneActivity", "⚠️ No default ringtone found.");
            }
        } catch (Exception e) {
            Log.e("RingtoneActivity", "❌ Error playing ringtone: " + e.getMessage());
        }
    }

    public void stopRingtone() {
        if (ringtone != null && ringtone.isPlaying()) {
            ringtone.stop();
            Log.d("RingtoneActivity", "🔇 Ringtone stopped.");
        }
    }
}
