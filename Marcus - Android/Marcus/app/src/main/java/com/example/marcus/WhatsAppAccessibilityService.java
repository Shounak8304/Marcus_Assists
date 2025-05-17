package com.example.marcus;

import android.accessibilityservice.AccessibilityService;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import java.util.List; // ✅ Add this import

public class WhatsAppAccessibilityService extends AccessibilityService {

    private static final String TAG = "WhatsAppAccessibility";

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (event.getPackageName() != null && event.getPackageName().equals("com.whatsapp")) {
            Log.d(TAG, "📲 WhatsApp opened. Checking for send button...");

            // Introduce a slight delay to allow WhatsApp UI to load
            new Handler(Looper.getMainLooper()).postDelayed(this::autoClickSendButton, 2000);
        }
    }

    private void autoClickSendButton() {
        AccessibilityNodeInfo rootNode = getRootInActiveWindow();
        if (rootNode == null) {
            Log.e(TAG, "❌ Root window is null. Cannot find send button.");
            return;
        }

        // Try finding the "Send" button by text
        List<AccessibilityNodeInfo> sendButtons = rootNode.findAccessibilityNodeInfosByText("Send");

        for (AccessibilityNodeInfo button : sendButtons) {
            if (button != null && button.isClickable()) {
                Log.d(TAG, "✅ Found 'Send' button. Clicking...");
                button.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                return;
            }
        }

        Log.e(TAG, "❌ Send button not found. Try using a different method.");
    }

    public void clickVoiceCallButton() {
        new Handler().postDelayed(() -> {
            AccessibilityNodeInfo rootNode = getRootInActiveWindow();
            if (rootNode == null) {
                Log.e(TAG, "❌ Root window is null. Retrying...");
                return;
            }

            List<AccessibilityNodeInfo> voiceCallButtons = rootNode.findAccessibilityNodeInfosByText("Voice call");
            for (AccessibilityNodeInfo button : voiceCallButtons) {
                if (button != null && button.isClickable()) {
                    Log.d(TAG, "✅ Found 'Voice Call' button. Clicking...");
                    button.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                    return;
                }
            }

            Log.e(TAG, "❌ Voice Call button not found. Retrying...");
        }, 3000); // Increased delay to 3 seconds
    }

    public void clickVideoCallButton() {
        new Handler().postDelayed(() -> {
            AccessibilityNodeInfo rootNode = getRootInActiveWindow();
            if (rootNode == null) {
                Log.e(TAG, "❌ Root window is null. Retrying...");
                return;
            }

            List<AccessibilityNodeInfo> videoCallButtons = rootNode.findAccessibilityNodeInfosByText("Video call");
            for (AccessibilityNodeInfo button : videoCallButtons) {
                if (button != null && button.isClickable()) {
                    Log.d(TAG, "✅ Found 'Video Call' button. Clicking...");
                    button.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                    return;
                }
            }

            Log.e(TAG, "❌ Video Call button not found. Retrying...");
        }, 3000); // Increased delay
    }

    @Override
    public void onInterrupt() {
        Log.e(TAG, "⚠️ Accessibility service interrupted.");
    }
}
