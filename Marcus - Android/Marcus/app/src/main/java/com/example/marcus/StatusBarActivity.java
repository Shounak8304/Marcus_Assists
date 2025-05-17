package com.example.marcus;

import android.bluetooth.BluetoothAdapter;
import android.content.Context;
import android.util.Log;
import android.widget.Toast;

import java.io.DataOutputStream;

public class StatusBarActivity {

    private Context context;
    private BluetoothAdapter bluetoothAdapter;

    public StatusBarActivity(Context context) {
        this.context = context;
        this.bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
    }

    // Method to toggle mobile data
    public void setMobileDataEnabled(boolean enabled) {
        try {
            // Execute shell command to toggle mobile data
            String command = enabled ? "svc data enable" : "svc data disable";
            Process su = Runtime.getRuntime().exec("su");
            DataOutputStream os = new DataOutputStream(su.getOutputStream());
            os.writeBytes(command + "\n");
            os.writeBytes("exit\n");
            os.flush();
            os.close();
            su.waitFor();
            Log.d("StatusBarActivity", "Mobile data toggled: " + (enabled ? "ON" : "OFF"));
            Toast.makeText(context, "Mobile data " + (enabled ? "enabled" : "disabled"), Toast.LENGTH_SHORT).show();
        } catch (Exception e) {
            Log.e("StatusBarActivity", "Failed to toggle mobile data", e);
            Toast.makeText(context, "Failed to toggle mobile data", Toast.LENGTH_SHORT).show();
        }
    }

    // Method to toggle Bluetooth
    public void setBluetoothEnabled(boolean enabled) {
        if (bluetoothAdapter == null) {
            // Device does not support Bluetooth
            Toast.makeText(context, "Bluetooth is not supported on this device", Toast.LENGTH_SHORT).show();
            return;
        }

        if (enabled) {
            if (!bluetoothAdapter.isEnabled()) {
                boolean success = bluetoothAdapter.enable();
                Toast.makeText(context, "Bluetooth is being enabled", Toast.LENGTH_SHORT).show();
                Log.d("StatusBarActivity", "Turning on Bluetooth, success: " + success);
            } else {
                Toast.makeText(context, "Bluetooth is already enabled", Toast.LENGTH_SHORT).show();
            }
        } else {
            if (bluetoothAdapter.isEnabled()) {
                boolean success = bluetoothAdapter.disable();
                Toast.makeText(context, "Bluetooth is being disabled", Toast.LENGTH_SHORT).show();
                Log.d("StatusBarActivity", "Turning off Bluetooth, success: " + success);
            } else {
                Toast.makeText(context, "Bluetooth is already disabled", Toast.LENGTH_SHORT).show();
            }
        }
    }
}