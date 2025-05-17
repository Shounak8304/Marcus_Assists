package com.example.marcus;

import android.bluetooth.BluetoothAdapter;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.util.Log;
import android.widget.Toast;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

public class BluetoothActivity {
    private final BluetoothAdapter bluetoothAdapter;
    private final Context context;

    public BluetoothActivity(Context context) {
        this.context = context;
        bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
    }

    public void turnOnBluetooth() {
        if (bluetoothAdapter == null) {
            Toast.makeText(context, "Bluetooth not supported on this device", Toast.LENGTH_SHORT).show();
            return;
        }

        // Check Bluetooth permissions for Android 12+ (API 31+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S &&
                ContextCompat.checkSelfPermission(context, android.Manifest.permission.BLUETOOTH_CONNECT)
                        != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(
                    (MainActivity) context,
                    new String[]{android.Manifest.permission.BLUETOOTH_CONNECT},
                    1
            );
            return;
        }

        if (!bluetoothAdapter.isEnabled()) {
            // Request the user to enable Bluetooth (Required for Android 10+)
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            enableBtIntent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(enableBtIntent);
            Toast.makeText(context, "Requesting to turn ON Bluetooth...", Toast.LENGTH_SHORT).show();
            Log.d("BluetoothActivity", "Bluetooth enable request sent.");
        } else {
            Toast.makeText(context, "Bluetooth is already ON", Toast.LENGTH_SHORT).show();
        }
    }

    public void turnOffBluetooth() {
        if (bluetoothAdapter == null) {
            Toast.makeText(context, "Bluetooth not supported on this device", Toast.LENGTH_SHORT).show();
            return;
        }

        // Check Bluetooth permissions for Android 12+ (API 31+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S &&
                ContextCompat.checkSelfPermission(context, android.Manifest.permission.BLUETOOTH_CONNECT)
                        != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(
                    (MainActivity) context,
                    new String[]{android.Manifest.permission.BLUETOOTH_CONNECT},
                    1
            );
            return;
        }

        if (bluetoothAdapter.isEnabled()) {
            bluetoothAdapter.disable();
            Toast.makeText(context, "Turning off Bluetooth...", Toast.LENGTH_SHORT).show();
            Log.d("BluetoothActivity", "Bluetooth turned OFF");
        } else {
            Toast.makeText(context, "Bluetooth is already OFF", Toast.LENGTH_SHORT).show();
        }
    }
}
