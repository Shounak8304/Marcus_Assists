package com.example.marcus;

import android.accessibilityservice.AccessibilityService;
import android.content.Context;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import android.content.Intent;
import android.util.Log;

public class SpotifyAccessibilityService extends AccessibilityService {
    private static final String SPOTIFY_PACKAGE = "com.spotify.music";
    private static final String TAG = "SpotifyAccessibility";

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        Log.d(TAG, "Accessibility Event: " + event.getEventType() + " - " + event.getClassName());
        if (event.getPackageName() != null && event.getPackageName().toString().equals(SPOTIFY_PACKAGE)) {
            Log.d(TAG, "Spotify opened, checking for play button...");
            performPlayAction();
        }
    }


    private void performPlayAction() {
        AccessibilityNodeInfo rootNode = getRootInActiveWindow();
        if (rootNode == null) return;

        for (AccessibilityNodeInfo node : rootNode.findAccessibilityNodeInfosByText("Play")) {
            if (node.isClickable()) {
                Log.d(TAG, "Play button found, clicking...");
                node.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                return;
            }
        }

        // Try alternative text labels
        for (AccessibilityNodeInfo node : rootNode.findAccessibilityNodeInfosByText("▶")) {
            if (node.isClickable()) {
                Log.d(TAG, "Play icon found, clicking...");
                node.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                return;
            }
        }

        Log.d(TAG, "Play button not found!");
    }


    public void openSpotifyAndPlay(Context context) {
        Intent intent = context.getPackageManager().getLaunchIntentForPackage(SPOTIFY_PACKAGE);
        if (intent != null) {
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(intent);
        } else {
            Log.e(TAG, "Spotify is not installed");
        }
    }


    @Override
    public void onInterrupt() {}
}
