package com.example.marcus;

import android.Manifest;
import android.accessibilityservice.AccessibilityService;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.bluetooth.BluetoothAdapter;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.MediaStore;
import android.provider.Settings;
import android.text.TextUtils;
import android.util.Log;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.app.NotificationCompat;
import androidx.core.content.ContextCompat;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;

import java.net.URI;
import java.net.URISyntaxException;

public class MainActivity extends AppCompatActivity implements WebSocketClientManager.WebSocketConnectionListener {


    private static final int REQUEST_BLUETOOTH_PERMISSIONS = 2;
    private static final int REQUEST_OVERLAY_PERMISSION = 3;
    private static final int REQUEST_CAMERA_PERMISSION = 4;
    private static final int REQUEST_READ_CONTACTS_PERMISSION = 5;
    private static final int REQUEST_SEND_SMS_PERMISSION = 6;
    private static final int REQUEST_CALL_PHONE_PERMISSION = 7;
    private static final int REQUEST_ANSWER_PHONE_CALLS_PERMISSION = 8;
    private static final int LOCATION_PERMISSION_REQUEST_CODE = 1001;
    private static final int BLUETOOTH_PERMISSION_REQUEST_CODE = 1002;
    private static final String SERVER_URI = "ws://4.213.152.184:9001";
    private static final String CHANNEL_ID = "MarcusChannel";
    private static final String TAG = "MainActivity";
    private WebSocketClient webSocketClient;
    private NotificationManager notificationManager;
    private OpenAppActivity openAppActivity;
    private SendSmsActivity sendSmsActivity;
    private CallActivity callActivity;
    private WhatsAppCallActivity whatsAppCallActivity;
    private StatusBarActivity statusBarActivity;
    private SendEmailActivity sendEmailActivity;
    private FlashlightActivity flashlightActivity;
    private BluetoothActivity bluetoothActivity;
    private SpotifyAccessibilityService spotifyActivity;
    public static boolean isCallOngoing = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        notificationManager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        createNotificationChannel();
        checkAndRequestAccessibilityService();
        requestLocationPermission();

        openAppActivity = new OpenAppActivity(this);
        sendSmsActivity = new SendSmsActivity(this);
        callActivity = new CallActivity(this);
        whatsAppCallActivity = new WhatsAppCallActivity(this);
        statusBarActivity = new StatusBarActivity(this);
        sendEmailActivity = new SendEmailActivity();
        flashlightActivity = new FlashlightActivity(this);
        bluetoothActivity = new BluetoothActivity(this);
        spotifyActivity = new SpotifyAccessibilityService();


        BluetoothAdapter bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

        // Request necessary permissions
        requestNecessaryPermissions();

        if (!Settings.canDrawOverlays(this)) {
            Intent intent = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                    Uri.parse("package:" + getPackageName()));
            startActivityForResult(intent, REQUEST_OVERLAY_PERMISSION);
        } else {
            startFloatingService();
            minimizeApp();
        }

        connectWebSocket();
    }

    private void requestNecessaryPermissions() {
        // Request permissions for contacts, SMS, camera, etc.
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_CONTACTS) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.READ_CONTACTS}, REQUEST_READ_CONTACTS_PERMISSION);
        }

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.SEND_SMS) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.SEND_SMS}, REQUEST_SEND_SMS_PERMISSION);
        }

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CALL_PHONE) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.CALL_PHONE}, REQUEST_CALL_PHONE_PERMISSION);
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.BLUETOOTH_CONNECT}, REQUEST_BLUETOOTH_PERMISSIONS);
            }
        }

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.CAMERA}, REQUEST_CAMERA_PERMISSION);
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.ANSWER_PHONE_CALLS) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.ANSWER_PHONE_CALLS}, REQUEST_ANSWER_PHONE_CALLS_PERMISSION);
            }
        }
    }

    private void requestLocationPermission() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED ||
                ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {

            ActivityCompat.requestPermissions(this, new String[]{
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION
            }, LOCATION_PERMISSION_REQUEST_CODE);
        }
    }

    private void requestBluetoothPermission() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.BLUETOOTH_CONNECT}, BLUETOOTH_PERMISSION_REQUEST_CODE);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

        if (grantResults.length > 0) {
            switch (requestCode) {
                case LOCATION_PERMISSION_REQUEST_CODE:
                    if (grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                        Toast.makeText(this, "Location Permission Granted", Toast.LENGTH_SHORT).show();
                    } else {
                        Toast.makeText(this, "Location Permission Denied", Toast.LENGTH_SHORT).show();
                    }
                    break;

                case BLUETOOTH_PERMISSION_REQUEST_CODE:
                    if (grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                        Toast.makeText(this, "Bluetooth Permission Granted", Toast.LENGTH_SHORT).show();
                    } else {
                        Toast.makeText(this, "Bluetooth Permission Denied", Toast.LENGTH_SHORT).show();
                    }
                    break;

                // You can add other permission requests here similarly.
            }
        }
    }

    private void startFloatingService() {
        Intent intent = new Intent(MainActivity.this, FloatingService.class);
        startService(intent);
    }

    private void minimizeApp() {
        Intent startMain = new Intent(Intent.ACTION_MAIN);
        startMain.addCategory(Intent.CATEGORY_HOME);
        startMain.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(startMain);
    }

    private void connectWebSocket() {
        WebSocketClientManager manager = WebSocketClientManager.getInstance();
        manager.setWebSocketConnectionListener(this);  // ✅ Set self as listener
        manager.connect();
    }

    @Override
    public void onConnected() {
        Log.d("WebSocket", "Connected to server");
    }

    @Override
    public void onCommandReceived(String command) {
        runOnUiThread(() -> {
            Log.d("COMMAND_DISPATCH", "Command received via manager: " + command);
            handleCommand(command);  // ✅ Use your existing handler
        });
    }


    private void handleCommand(String command) {
        runOnUiThread(() -> {
            Log.d("COMMAND_HANDLER", "Received command: [" + command + "]");

            if (command.toLowerCase().startsWith("open ")) {
                String appName = command.substring(5).trim();
                Log.d("MainActivity", "Opening app: " + appName);
                openAppActivity.openApp(appName);
            } else if (command.toLowerCase().startsWith("sms ")) {

                if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_CONTACTS)
                        != PackageManager.PERMISSION_GRANTED) {
                    Toast.makeText(this, "Please grant contact permission for SMS feature", Toast.LENGTH_SHORT).show();
                    ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.READ_CONTACTS}, 101);
                    return;
                }

                String[] parts = command.split(" that ", 2);
                if (parts.length == 2) {
                    String contactName = parts[0].substring(4).trim();
                    String message = parts[1].trim();
                    Log.d("MainActivity", "Parsed command - Contact: " + contactName + ", Message: " + message);
                    sendSmsActivity.sendSms(contactName, message);
                } else {
                    Toast.makeText(this, "Invalid SMS command format", Toast.LENGTH_SHORT).show();
                }

            } else if (command.toLowerCase().startsWith("call ")) {
                if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_CONTACTS)
                        != PackageManager.PERMISSION_GRANTED) {
                    Toast.makeText(this, "Please grant contact permission for calling", Toast.LENGTH_SHORT).show();
                    ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.READ_CONTACTS}, 102);
                    return;
                }

                String contactName = command.substring(5).trim();
                Log.d("MainActivity", "Parsed command - Contact: " + contactName);
                callActivity.makeCall(contactName);

            } else if (command.equalsIgnoreCase("end call")) {
                Log.d("MainActivity", "Ending call");
                callActivity.endCall();

            } else if (command.equalsIgnoreCase("put on speaker")) {
                Log.d("MainActivity", "Turning speakerphone on");
                callActivity.toggleSpeakerphone(true);

            } else if (command.equalsIgnoreCase("turn off speaker")) {
                Log.d("MainActivity", "Turning speakerphone off");
                callActivity.toggleSpeakerphone(false);

            } else if (command.equalsIgnoreCase("on mobile data")) {
                Log.d("MainActivity", "Turning on mobile data");
                statusBarActivity.setMobileDataEnabled(true);

            } else if (command.equalsIgnoreCase("off mobile data")) {
                Log.d("MainActivity", "Turning off mobile data");
                statusBarActivity.setMobileDataEnabled(false);

            } else if (command.equalsIgnoreCase("on bluetooth")) {
                Log.d("MainActivity", "Turning ON Bluetooth");
                bluetoothActivity.turnOnBluetooth();

            } else if (command.equalsIgnoreCase("off bluetooth")) {
                Log.d("MainActivity", "Turning OFF Bluetooth");
                bluetoothActivity.turnOffBluetooth();

            } else if (command.toLowerCase().startsWith("whatsapp ")) {
                String[] parts = command.split(" that ", 2);
                if (parts.length == 2) {
                    String contactName = parts[0].substring(9).trim();
                    String message = parts[1].trim();
                    Log.d("MainActivity", "Sending WhatsApp message - Contact: " + contactName + ", Message: " + message);
                    new WhatsAppActivity(this).sendWhatsAppMessage(contactName, message);
                } else {
                    Toast.makeText(this, "Invalid WhatsApp command format. Use: 'whatsapp [contact] that [message]'", Toast.LENGTH_SHORT).show();
                }

            } else if (command.toLowerCase().startsWith("email ")) {
                try {
                    String[] parts = command.substring(6).split(" subject ", 2);
                    if (parts.length == 2) {
                        String recipient = parts[0].trim().replaceAll("\\s", "");
                        String subjectAndBody = parts[1].trim();
                        String subject = "", body = "";

                        if (subjectAndBody.contains(" body ")) {
                            String[] subParts = subjectAndBody.split(" body ", 2);
                            subject = subParts[0].trim();
                            body = subParts[1].trim();
                        } else {
                            subject = subjectAndBody;
                        }

                        Log.d("MainActivity", "Parsed email - To: " + recipient + ", Subject: " + subject + ", Body: " + body);
                        sendEmailActivity.sendEmail(recipient, subject, body);
                    } else {
                        Toast.makeText(this, "Invalid email format! Use: email [recipient] subject [subject] body [message]", Toast.LENGTH_SHORT).show();
                    }
                } catch (Exception e) {
                    Log.e("MainActivity", "Error processing email command", e);
                }

            } else if (command.toLowerCase().startsWith("navigate to ")) {
                String destination = command.substring(12).trim();
                Log.d("MainActivity", "Navigating to: " + destination);
                new GoogleMapsActivity(this).navigateTo(destination);

            } else if (command.toLowerCase().startsWith("set alarm for ")) {
                String time = command.substring(14).trim();
                Log.d("MainActivity", "Setting alarm for: " + time);
                new AlarmActivity(this).setAlarm(time);

            } else if (command.equalsIgnoreCase("play ringtone")) {
                Log.d("MainActivity", "Playing default ringtone");
                new RingtoneActivity(this).playRingtone();

            } else if (command.equalsIgnoreCase("stop ringtone")) {
                Log.d("MainActivity", "Stopping ringtone");
                new RingtoneActivity(this).stopRingtone();

            } else if (command.toLowerCase().startsWith("voice call ")) {
                String contactName = command.substring(11).replace(" on whatsapp", "").trim();
                Log.d("MainActivity", "Making WhatsApp Voice Call to: " + contactName);
                new WhatsAppCallActivity(this).makeVoiceCall(contactName);

            } else if (command.toLowerCase().startsWith("video call ")) {
                String contactName = command.substring(11).replace(" on whatsapp", "").trim();
                Log.d("MainActivity", "Making WhatsApp Video Call to: " + contactName);
                new WhatsAppCallActivity(this).makeVideoCall(contactName);

            } else if (command.equalsIgnoreCase("on the flash")) {
                Log.d("MainActivity", "Turning ON the flashlight");
                flashlightActivity.turnOnFlash();

            } else if (command.equalsIgnoreCase("off the flash")) {
                Log.d("MainActivity", "Turning OFF the flashlight");
                flashlightActivity.turnOffFlash();

            } else if (command.equalsIgnoreCase("play music")) {
                Log.d("MainActivity", "Playing music on Spotify");
                spotifyActivity.openSpotifyAndPlay(this);
            } else if (command.equalsIgnoreCase("click photo")) {
                Log.d("MainActivity", "Opening Camera to click photo");
                Intent intent = new Intent(this, CameraActivity.class);
                startActivity(intent);
            } else {
                openAppActivity.handleCommand(command);
            }

            showNotification("Command executed: " + command);
        });
    }

    private void checkAndRequestAccessibilityService() {
        if (!isAccessibilityServiceEnabled(SpeakerAccessibilityService.class)) {
            Intent intent = new Intent(android.provider.Settings.ACTION_ACCESSIBILITY_SETTINGS);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
            Toast.makeText(this, "Enable 'Marcus Speaker Service' in Accessibility Settings", Toast.LENGTH_LONG).show();
        }
    }

    private boolean isAccessibilityServiceEnabled(Class<? extends AccessibilityService> service) {
        String serviceId = getPackageName() + "/" + service.getName();
        TextUtils.SimpleStringSplitter splitter = new TextUtils.SimpleStringSplitter(':');

        String enabledServices = Settings.Secure.getString(getContentResolver(), Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);
        if (enabledServices != null) {
            splitter.setString(enabledServices);
            while (splitter.hasNext()) {
                if (splitter.next().equalsIgnoreCase(serviceId)) {
                    return true;
                }
            }
        }

        return Settings.Secure.getInt(getContentResolver(), Settings.Secure.ACCESSIBILITY_ENABLED, 0) == 1;
    }

    public void showNotification(String message) {
        Notification notification = new NotificationCompat.Builder(this, CHANNEL_ID)
                .setContentTitle("Marcus Assists")
                .setContentText(message)
                .setSmallIcon(R.drawable.ic_notification)
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .build();
        notificationManager.notify(1, notification);
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            CharSequence name = "Marcus Channel";
            String description = "Channel for Marcus notifications";
            int importance = NotificationManager.IMPORTANCE_HIGH;
            NotificationChannel channel = new NotificationChannel(CHANNEL_ID, name, importance);
            channel.setDescription(description);
            notificationManager.createNotificationChannel(channel);
        }
    }
}