package com.example.marcus;

import android.Manifest;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.util.Base64;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Set;
import java.util.UUID;
import java.util.Arrays;

public class OptionsActivity extends AppCompatActivity {

    private static final UUID MY_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");
    private static final String ESP32_DEVICE_NAME = "ESP32_MIC";
    private static final int REQUEST_BT_PERMISSIONS = 1;

    private BluetoothAdapter bluetoothAdapter;
    private BluetoothSocket bluetoothSocket;
    private ConnectedThread connectedThread;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_options);

        Button accountButton = findViewById(R.id.accountButton);
        Button logoutButton = findViewById(R.id.logoutButton);
        Button instructionButton = findViewById(R.id.instructionButton);
        Button closeButton = findViewById(R.id.closeButton);
        Button bluetoothButton = findViewById(R.id.bluetoothButton);

        bluetoothButton.setOnClickListener(v -> {
            if (checkBluetoothPermissions()) {
                connectToESP32();
            }
        });

        accountButton.setOnClickListener(v -> startActivity(new android.content.Intent(this, AccountActivity.class)));
        logoutButton.setOnClickListener(v -> Toast.makeText(this, "Logout clicked", Toast.LENGTH_SHORT).show());
        instructionButton.setOnClickListener(v -> startActivity(new android.content.Intent(this, InstructionsActivity.class)));
        closeButton.setOnClickListener(v -> finish());
    }

    private boolean checkBluetoothPermissions() {
        String[] permissions = {
                Manifest.permission.BLUETOOTH,
                Manifest.permission.BLUETOOTH_ADMIN,
                Manifest.permission.BLUETOOTH_CONNECT,
                Manifest.permission.BLUETOOTH_SCAN
        };

        boolean allGranted = true;
        for (String permission : permissions) {
            if (ActivityCompat.checkSelfPermission(this, permission) != PackageManager.PERMISSION_GRANTED) {
                allGranted = false;
                break;
            }
        }

        if (!allGranted) {
            ActivityCompat.requestPermissions(this, permissions, REQUEST_BT_PERMISSIONS);
            return false;
        }

        return true;
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions,
                                           @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_BT_PERMISSIONS) {
            if (checkBluetoothPermissions()) {
                connectToESP32();
            } else {
                Toast.makeText(this, "Bluetooth permissions are required", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void connectToESP32() {
        bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        if (bluetoothAdapter == null) {
            Toast.makeText(this, "Bluetooth not supported", Toast.LENGTH_SHORT).show();
            return;
        }

        if (!bluetoothAdapter.isEnabled()) {
            Toast.makeText(this, "Please enable Bluetooth", Toast.LENGTH_SHORT).show();
            return;
        }

        Set<BluetoothDevice> pairedDevices = bluetoothAdapter.getBondedDevices();
        BluetoothDevice foundDevice = null;

        for (BluetoothDevice device : pairedDevices) {
            if (device.getName() != null && device.getName().equals(ESP32_DEVICE_NAME)) {
                foundDevice = device;
                break;
            }
        }

        if (foundDevice == null) {
            Toast.makeText(this, "ESP32 not paired", Toast.LENGTH_SHORT).show();
            return;
        }

        final BluetoothDevice esp32Device = foundDevice; // ✅ Now it's final

        Toast.makeText(this, "Connecting to ESP32...", Toast.LENGTH_SHORT).show();

        new Thread(() -> {
            try {
                bluetoothSocket = esp32Device.createInsecureRfcommSocketToServiceRecord(MY_UUID);
                bluetoothSocket.connect();

                connectedThread = new ConnectedThread(bluetoothSocket);
                connectedThread.start();

                runOnUiThread(() -> Toast.makeText(this, "Connected to ESP32", Toast.LENGTH_SHORT).show());

            } catch (IOException e) {
                runOnUiThread(() -> Toast.makeText(this, "Connection failed: " + e.getMessage(), Toast.LENGTH_SHORT).show());
                e.printStackTrace();
            }
        }).start();
    }

    private class ConnectedThread extends Thread {
        private final InputStream mmInStream;
        private boolean isRunning = true;
        private final byte[] buffer = new byte[1024];

        public ConnectedThread(BluetoothSocket socket) {
            InputStream tmpIn = null;
            try {
                tmpIn = socket.getInputStream();
            } catch (IOException e) {
                e.printStackTrace();
            }
            mmInStream = tmpIn;
        }

        @Override
        public void run() {
            ByteArrayOutputStream audioBuffer = new ByteArrayOutputStream();
            int sampleRate = 8000;
            int bytesPerSample = 2; // For PCM 16-bit
            int durationInSeconds = 5;
            int targetBufferSize = sampleRate * bytesPerSample * durationInSeconds;

            while (isRunning) {
                try {
                    int bytes = mmInStream.read(buffer);
                    if (bytes > 0) {
                        audioBuffer.write(buffer, 0, bytes);

                        if (audioBuffer.size() >= targetBufferSize) {
                            byte[] audioChunk = audioBuffer.toByteArray();
                            audioBuffer.reset(); // Clear buffer after sending

                            sendAudioToServer(audioChunk);  // Send using existing helper
                        }
                    }
                } catch (IOException e) {
                    Log.e("BT_READ", "Error reading input", e);
                    isRunning = false;
                    closeSocket();
                }
            }

            // Final flush
            if (audioBuffer.size() > 0) {
                sendAudioToServer(audioBuffer.toByteArray());
            }
        }

        public void cancel() {
            isRunning = false;
            closeSocket();
        }

        private void closeSocket() {
            try {
                if (mmInStream != null) mmInStream.close();
                if (bluetoothSocket != null) bluetoothSocket.close();
            } catch (IOException e) {
                Log.e("BT_CLOSE", "Error closing socket", e);
            }
        }
    }

    // Function to send audio to server (Base64 encoding included)
    private void sendAudioToServer(byte[] audioData) {
        try {
            // Convert the audio to Base64
            String base64Audio = Base64.encodeToString(audioData, Base64.NO_WRAP);
            String message = "AUDIO_BASE64:" + base64Audio;

            // Send audio data to the server via WebSocket
            WebSocketClientManager manager = WebSocketClientManager.getInstance();
            if (manager.getWebSocketClient() != null && manager.getWebSocketClient().isOpen()) {
                manager.sendCommand(message);  // Send the Base64 audio to the server
                Log.d("BT_FORWARD", "Sent audio to server (" + audioData.length + " bytes)");
            } else {
                Log.w("BT_FORWARD", "WebSocket not connected");
            }
        } catch (Exception e) {
            Log.e("SEND_AUDIO", "Error sending audio to server", e);
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (connectedThread != null) {
            connectedThread.cancel();
        }
    }
}
