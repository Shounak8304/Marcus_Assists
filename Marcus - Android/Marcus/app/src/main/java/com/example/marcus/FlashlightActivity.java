package com.example.marcus;

import android.content.Context;
import android.hardware.camera2.CameraAccessException;
import android.hardware.camera2.CameraManager;
import android.os.Build;
import android.util.Log;

public class FlashlightActivity {

    private final CameraManager cameraManager;
    private String cameraId;

    public FlashlightActivity(Context context) {
        cameraManager = (CameraManager) context.getSystemService(Context.CAMERA_SERVICE);
        try {
            if (cameraManager != null) {
                cameraId = cameraManager.getCameraIdList()[0]; // Get the first camera ID
            }
        } catch (CameraAccessException e) {
            Log.e("FlashlightActivity", "Error accessing camera", e);
        }
    }

    public void turnOnFlash() {
        setFlashlightState(true);
    }

    public void turnOffFlash() {
        setFlashlightState(false);
    }

    private void setFlashlightState(boolean state) {
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                cameraManager.setTorchMode(cameraId, state);
                Log.d("FlashlightActivity", "Flashlight " + (state ? "ON" : "OFF"));
            }
        } catch (CameraAccessException e) {
            Log.e("FlashlightActivity", "Error toggling flashlight", e);
        }
    }
}
