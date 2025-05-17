package com.example.marcus;

import android.accessibilityservice.AccessibilityService;
import android.util.Log;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

import java.util.List;

public class SpeakerAccessibilityService extends AccessibilityService {
    private static SpeakerAccessibilityService instance;

    public static SpeakerAccessibilityService getInstance() {
        return instance;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        instance = this;
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        // Not needed for our case
    }

    @Override
    public void onInterrupt() {
        // Not needed for our case
    }

    public void clickSpeakerButton() {
        AccessibilityNodeInfo rootNode = getRootInActiveWindow();
        if (rootNode == null) {
            Log.e("SpeakerService", "No active window found!");
            return;
        }

        List<AccessibilityNodeInfo> speakerButtons = rootNode.findAccessibilityNodeInfosByText("Speaker");
        for (AccessibilityNodeInfo node : speakerButtons) {
            if (node.isClickable()) {
                node.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                Log.d("SpeakerService", "Clicked Speaker Button via Accessibility Service");
                return;
            }
        }
        Log.e("SpeakerService", "Speaker button not found!");
    }
}
