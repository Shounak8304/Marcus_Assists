package com.example.marcus;

import android.app.ActivityManager;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.os.Build;
import android.util.Log;
import android.widget.Toast;

import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

public class OpenAppActivity {
    private static final String TAG = "OpenAppActivity";
    private Context context;
    private Map<String, String> installedApps;

    public OpenAppActivity(Context context) {
        this.context = context;
        cacheInstalledApps();
    }

    // Cache all installed apps
    private void cacheInstalledApps() {
        installedApps = new HashMap<>();
        PackageManager pm = context.getPackageManager();
        List<ApplicationInfo> apps = pm.getInstalledApplications(PackageManager.GET_META_DATA);

        for (ApplicationInfo app : apps) {
            String label = pm.getApplicationLabel(app).toString().toLowerCase(Locale.ROOT).trim();
            installedApps.put(label, app.packageName);
        }
    }

    // Handle the command received (either open or close)
    public void handleCommand(String command) {
        if (command != null) {
            String appName = command.toLowerCase(Locale.ROOT).trim();

            // Check for specific command for remote desktop (e.g., webshare desktop)
            if (command.equalsIgnoreCase("webcare desktop")) {
                openApp("remote desktop");  // Assuming the app is named "remote desktop" (or adjust as needed)
            } else if (command.startsWith("open ")) {
                openApp(appName.substring(5).trim()); // Open app command
            } else if (command.startsWith("close ")) {
                closeApp(appName.substring(6).trim()); // Close app command
            } else {
                Toast.makeText(context, "Unknown command: " + command, Toast.LENGTH_SHORT).show();
            }
        }
    }

    public void openApp(String appName) {
        if (installedApps.isEmpty()) {
            cacheInstalledApps();
        }

        String packageName = installedApps.get(appName.toLowerCase(Locale.ROOT).trim());

        if (packageName != null) {
            // Try to open the app
            openAppByPackage(packageName);
        } else {
            // Fuzzy match if exact match not found
            packageName = fuzzyMatchAppName(appName);
            if (packageName != null) {
                openAppByPackage(packageName);
            } else {
                Toast.makeText(context, "App not found: " + appName, Toast.LENGTH_SHORT).show();
            }
        }
    }

    // Close the specified app
    private void closeApp(String appName) {
        if (installedApps.isEmpty()) {
            cacheInstalledApps(); // Cache apps if not already done
        }

        String packageName = installedApps.get(appName);

        if (packageName != null) {
            // Attempt to close the app using ActivityManager
            closeAppByPackage(packageName);
        } else {
            // Fuzzy match if exact match not found
            packageName = fuzzyMatchAppName(appName);
            if (packageName != null) {
                closeAppByPackage(packageName);
            } else {
                Toast.makeText(context, "App not found: " + appName, Toast.LENGTH_SHORT).show();
            }
        }
    }

    // Fuzzy match app name
    private String fuzzyMatchAppName(String appName) {
        for (String label : installedApps.keySet()) {
            if (label.contains(appName) || appName.contains(label)) {
                return installedApps.get(label);
            }
        }
        return null;
    }

    // Open the app by package name
    private void openAppByPackage(String packageName) {
        try {
            Intent launchIntent = context.getPackageManager().getLaunchIntentForPackage(packageName);
            if (launchIntent != null) {
                launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                context.startActivity(launchIntent);
            } else {
                Toast.makeText(context, "Unable to launch app.", Toast.LENGTH_SHORT).show();
            }
        } catch (Exception e) {
            Toast.makeText(context, "Error opening app.", Toast.LENGTH_SHORT).show();
            Log.e(TAG, "Error opening app: " + e.getMessage());
        }
    }

    // Close the app by package name using ActivityManager
    private void closeAppByPackage(String packageName) {
        try {
            ActivityManager am = (ActivityManager) context.getSystemService(Context.ACTIVITY_SERVICE);

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                // For Android Lollipop and above, use finishAndRemoveTask
                List<ActivityManager.AppTask> tasks = am.getAppTasks();
                boolean foundApp = false;

                for (ActivityManager.AppTask task : tasks) {
                    String taskPackageName = task.getTaskInfo().baseActivity.getPackageName();
                    if (taskPackageName.equals(packageName)) {
                        foundApp = true;
                        task.finishAndRemoveTask(); // Attempt to close the app
                        Log.d(TAG, "Successfully closed the app: " + packageName);
                        Toast.makeText(context, "App closed: " + packageName, Toast.LENGTH_SHORT).show();
                        return;
                    }
                }

                // If app is not found running in the task list, log the state
                if (!foundApp) {
                    Log.d(TAG, "App not found in the task list or cannot be force stopped due to Android restrictions.");
                    Toast.makeText(context, "Unable to close app: " + packageName, Toast.LENGTH_SHORT).show();
                }
            } else {
                // For older Android versions, use killBackgroundProcesses
                am.killBackgroundProcesses(packageName);
                Log.d(TAG, "Attempted to kill the background process of: " + packageName);
                Toast.makeText(context, "App closed: " + packageName, Toast.LENGTH_SHORT).show();
            }
        } catch (Exception e) {
            Log.e(TAG, "Error closing app: " + e.getMessage());
            Toast.makeText(context, "Error closing app.", Toast.LENGTH_SHORT).show();
        }
    }
}
