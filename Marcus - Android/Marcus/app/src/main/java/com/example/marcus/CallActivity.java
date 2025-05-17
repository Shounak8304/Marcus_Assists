package com.example.marcus;

import android.Manifest;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.media.AudioManager;
import android.net.Uri;
import android.os.Build;
import android.os.Handler;
import android.provider.ContactsContract;
import android.provider.Settings;
import android.telecom.Call;
import android.telecom.TelecomManager;
import android.text.TextUtils;
import android.util.Log;
import android.view.accessibility.AccessibilityNodeInfo;
import android.widget.Toast;

import androidx.annotation.RequiresApi;
import androidx.core.app.ActivityCompat;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;

public class CallActivity {
    private static final String TAG = "CallActivity";
    private Context context;
    private TelecomManager telecomManager;
    private AudioManager audioManager;

    public CallActivity(Context context) {
        this.context = context;
        this.telecomManager = (TelecomManager) context.getSystemService(Context.TELECOM_SERVICE);
        this.audioManager = (AudioManager) context.getSystemService(Context.AUDIO_SERVICE);
    }

    // 📞 **Make a Call with Fuzzy Contact Matching**
    public void makeCall(String contactName) {
        String bestMatch = getClosestMatchingContact(contactName);
        if (bestMatch != null) {
            String phoneNumber = getPhoneNumber(bestMatch);
            if (phoneNumber != null) {
                Intent callIntent = new Intent(Intent.ACTION_CALL);
                callIntent.setData(Uri.parse("tel:" + phoneNumber));
                callIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);

                if (ActivityCompat.checkSelfPermission(context, Manifest.permission.CALL_PHONE) == PackageManager.PERMISSION_GRANTED) {
                    context.startActivity(callIntent);
                    Toast.makeText(context, "Calling " + bestMatch, Toast.LENGTH_SHORT).show();
                    Log.d(TAG, "Calling " + bestMatch + " at " + phoneNumber);
                } else {
                    Toast.makeText(context, "Call permission required!", Toast.LENGTH_SHORT).show();
                }
            }
        } else {
            Toast.makeText(context, "No close match found", Toast.LENGTH_SHORT).show();
        }
    }

    // 🔊 **Enable Speakerphone Only If Call is Active**
    public void enableSpeakerIfCallActive() {
        Call activeCall = getActiveCall();

        if (activeCall == null) {
            Log.e(TAG, "No active call detected, cannot toggle speaker.");
            Toast.makeText(context, "No active call detected!", Toast.LENGTH_SHORT).show();
            return;
        }

        // If an active call is detected, enable the speaker
        toggleSpeakerphone(true);
    }

    public void toggleSpeakerphone(boolean turnOn) {
        if (audioManager == null) {
            Log.e(TAG, "AudioManager is NULL!");
            Toast.makeText(context, "AudioManager unavailable", Toast.LENGTH_SHORT).show();
            return;
        }

        Log.d(TAG, "Attempting to set speakerphone " + (turnOn ? "ON" : "OFF"));

        // Step 1: Set audio mode to IN_COMMUNICATION
        audioManager.setMode(AudioManager.MODE_IN_COMMUNICATION);

        // Step 2: Toggle the speakerphone
        audioManager.setSpeakerphoneOn(turnOn);

        // Step 3: Delay and verify if the state changed
        new Handler().postDelayed(() -> {
            boolean isNowOn = audioManager.isSpeakerphoneOn();
            Log.d(TAG, "Final speaker state: " + (isNowOn ? "ON" : "OFF"));

            if (isNowOn == turnOn) {
                Toast.makeText(context, "Speakerphone " + (turnOn ? "ON" : "OFF"), Toast.LENGTH_SHORT).show();
                Log.d(TAG, "Speakerphone " + (turnOn ? "ON" : "OFF") + " successfully set.");
            } else {
                Log.e(TAG, "Speakerphone toggle failed! Trying Accessibility Service...");

                // Step 4: Check Accessibility Service
                SpeakerAccessibilityService service = SpeakerAccessibilityService.getInstance();
                if (service != null) {
                    Log.d(TAG, "Attempting to toggle speaker via Accessibility Service...");
                    service.clickSpeakerButton();  // Simulates clicking the speaker button
                } else {
                    Log.e(TAG, "Accessibility Service is not running!");
                    Toast.makeText(context, "Enable 'Marcus Speaker Service' in Accessibility Settings", Toast.LENGTH_LONG).show();
                }
            }
        }, 1000);
    }


    private boolean isAccessibilityServiceEnabled(Class<? extends android.accessibilityservice.AccessibilityService> service) {
        String serviceId = context.getPackageName() + "/" + service.getName();
        TextUtils.SimpleStringSplitter splitter = new TextUtils.SimpleStringSplitter(':');

        String enabledServices = Settings.Secure.getString(context.getContentResolver(), Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);
        if (enabledServices != null) {
            splitter.setString(enabledServices);
            while (splitter.hasNext()) {
                if (splitter.next().equalsIgnoreCase(serviceId)) {
                    return true;
                }
            }
        }

        return Settings.Secure.getInt(context.getContentResolver(), Settings.Secure.ACCESSIBILITY_ENABLED, 0) == 1;
    }


    // ❌ **End Call**
    public void endCall() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            if (telecomManager != null) {
                try {
                    telecomManager.endCall();
                    Toast.makeText(context, "Call ended", Toast.LENGTH_SHORT).show();
                    Log.d(TAG, "Call ended successfully");
                } catch (SecurityException e) {
                    Log.e(TAG, "Call end failed. Permission issue?", e);
                }
            }
        } else {
            try {
                Method method = telecomManager.getClass().getDeclaredMethod("endCall");
                method.setAccessible(true);
                method.invoke(telecomManager);
                Toast.makeText(context, "Call ended", Toast.LENGTH_SHORT).show();
            } catch (Exception e) {
                Log.e(TAG, "Failed to end call", e);
            }
        }
    }

    // 🔍 **Detect Active Call**
    @RequiresApi(api = Build.VERSION_CODES.M)
    private Call getActiveCall() {
        MyInCallService inCallService = MyInCallService.getInstance();
        if (inCallService != null) {
            for (Call call : inCallService.getCallList()) {
                int state = call.getState();
                if (state == Call.STATE_ACTIVE || state == Call.STATE_DIALING ||
                        state == Call.STATE_RINGING || state == Call.STATE_CONNECTING) {
                    Log.d(TAG, "Active call detected: " + call);
                    return call;
                }
            }
        }
        Log.e(TAG, "No active call detected from TelecomManager.");
        return null;
    }

    // ☎ Get phone number from contact name
    private String getPhoneNumber(String contactName) {
        String phoneNumber = null;
        Cursor cursor = context.getContentResolver().query(
                ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                new String[]{ContactsContract.CommonDataKinds.Phone.NUMBER},
                ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME + " = ?",
                new String[]{contactName},
                null);

        if (cursor != null && cursor.moveToFirst()) {
            phoneNumber = cursor.getString(cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER));
            cursor.close();
        }

        return phoneNumber;
    }


    // 🔍 **Fuzzy Matching for Contact Name**
    private String getClosestMatchingContact(String inputName) {
        List<String> contacts = getAllContactNames();
        if (contacts.isEmpty()) return null;

        String bestMatch = null;
        int minDistance = Integer.MAX_VALUE;
        int threshold = 3;

        for (String contact : contacts) {
            int distance = levenshteinDistance(inputName.toLowerCase(), contact.toLowerCase());
            if (distance < minDistance) {
                minDistance = distance;
                bestMatch = contact;
            }
        }
        return (minDistance <= threshold) ? bestMatch : null;
    }

    // 🔠 **Levenshtein Distance Algorithm**
    private int levenshteinDistance(String s1, String s2) {
        int[][] dp = new int[s1.length() + 1][s2.length() + 1];

        for (int i = 0; i <= s1.length(); i++) {
            for (int j = 0; j <= s2.length(); j++) {
                if (i == 0) {
                    dp[i][j] = j;
                } else if (j == 0) {
                    dp[i][j] = i;
                } else {
                    int cost = (s1.charAt(i - 1) == s2.charAt(j - 1)) ? 0 : 1;
                    dp[i][j] = Math.min(Math.min(
                                    dp[i - 1][j] + 1,
                                    dp[i][j - 1] + 1),
                            dp[i - 1][j - 1] + cost);
                }
            }
        }
        return dp[s1.length()][s2.length()];
    }

    // 📜 **Retrieve Contacts**
    private List<String> getAllContactNames() {
        List<String> contacts = new ArrayList<>();
        Cursor cursor = context.getContentResolver().query(
                ContactsContract.Contacts.CONTENT_URI,
                new String[]{ContactsContract.Contacts.DISPLAY_NAME},
                null, null, null);

        if (cursor != null) {
            while (cursor.moveToNext()) {
                String displayName = cursor.getString(cursor.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME));
                if (displayName != null) contacts.add(displayName);
            }
            cursor.close();
        }
        return contacts;
    }
}
