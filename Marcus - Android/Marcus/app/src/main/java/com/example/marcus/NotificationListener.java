package com.example.marcus;

import android.app.Notification;
import android.content.Context;
import android.os.Bundle;
import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;
import android.util.Log;

import java.net.URI;
import java.net.URISyntaxException;
import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;

public class NotificationListener extends NotificationListenerService {
    private static final String TAG = "NotificationListener";
    private static final String SERVER_URI = "ws://4.213.152.184:9001";  // Change this if needed

    private WebSocketClient webSocketClient;

    @Override
    public void onCreate() {
        super.onCreate();
        connectWebSocket();
    }

    private void connectWebSocket() {
        try {
            webSocketClient = new WebSocketClient(new URI(SERVER_URI)) {
                @Override
                public void onOpen(ServerHandshake handshakedata) {
                    Log.i(TAG, "WebSocket Connected");
                }

                @Override
                public void onMessage(String message) {
                    Log.i(TAG, "Message from server: " + message);
                }

                @Override
                public void onClose(int code, String reason, boolean remote) {
                    Log.i(TAG, "WebSocket Disconnected: " + reason);
                }

                @Override
                public void onError(Exception ex) {
                    Log.e(TAG, "WebSocket Error: " + ex.getMessage());
                }
            };
            webSocketClient.connect();
        } catch (URISyntaxException e) {
            Log.e(TAG, "WebSocket URI Error: " + e.getMessage());
        }
    }

    @Override
    public void onNotificationPosted(StatusBarNotification sbn) {
        String packageName = sbn.getPackageName();

        // Ignore notifications from your own app
        if (packageName.equals("com.example.marcus")) {
            return;
        }

        // Extract notification title and content
        Bundle extras = sbn.getNotification().extras;
        String notificationTitle = extras.getString(Notification.EXTRA_TITLE);
        String notificationText = extras.getCharSequence(Notification.EXTRA_TEXT) != null ?
                extras.getCharSequence(Notification.EXTRA_TEXT).toString() :
                "New Notification";

        Log.d(TAG, "Notification from: " + packageName + " - " + notificationTitle + ": " + notificationText);

        // 📌 **Detect Call Ongoing Status**
        if (packageName.equals("com.samsung.android.incallui")) {  // Call UI package
            if (notificationTitle != null && notificationTitle.contains("Call") &&
                    notificationText != null && notificationText.contains("On-going call")) {
                MainActivity.isCallOngoing = true;  // Mark call as active
                Log.d(TAG, "📞 Ongoing call detected via notification.");
            }
        }

        // Send the notification to WebSocket server
        if (webSocketClient != null && webSocketClient.isOpen()) {
            webSocketClient.send("🔔 Notification from " + packageName + " - " + notificationTitle + ": " + notificationText);
        }
    }


    @Override
    public void onNotificationRemoved(StatusBarNotification sbn) {
        Log.d(TAG, "Notification Removed: " + sbn.getPackageName());
    }
}
