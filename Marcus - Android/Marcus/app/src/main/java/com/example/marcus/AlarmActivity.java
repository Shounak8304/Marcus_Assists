package com.example.marcus;

import android.content.Context;
import android.content.Intent;
import android.provider.AlarmClock;
import android.util.Log;
import android.widget.Toast;

import java.util.Locale;

public class AlarmActivity {

    private Context context;

    public AlarmActivity(Context context) {
        this.context = context;
    }

    public void setAlarm(String timeInput) {
        try {
            String[] parts = timeInput.split(":| ");
            if (parts.length < 3) {
                Toast.makeText(context, "Invalid time format. Use 'set alarm for HH:MM AM/PM'", Toast.LENGTH_SHORT).show();
                return;
            }

            int hour = Integer.parseInt(parts[0]); // Extract hour
            int minute = Integer.parseInt(parts[1]); // Extract minute
            String amPm = parts[2].toLowerCase(Locale.ROOT);

            if (amPm.equals("pm") && hour < 12) {
                hour += 12; // Convert PM to 24-hour format
            } else if (amPm.equals("am") && hour == 12) {
                hour = 0; // Convert 12 AM to 0 (midnight)
            }

            Intent intent = new Intent(AlarmClock.ACTION_SET_ALARM);
            intent.putExtra(AlarmClock.EXTRA_HOUR, hour);
            intent.putExtra(AlarmClock.EXTRA_MINUTES, minute);
            intent.putExtra(AlarmClock.EXTRA_MESSAGE, "Marcus Alarm"); // Optional label
            intent.putExtra(AlarmClock.EXTRA_SKIP_UI, false); // Opens the Clock app

            if (intent.resolveActivity(context.getPackageManager()) != null) {
                context.startActivity(intent);
                Toast.makeText(context, "Alarm set for " + timeInput, Toast.LENGTH_SHORT).show();
                Log.d("AlarmActivity", "Alarm set for: " + timeInput);
            } else {
                Toast.makeText(context, "No Clock app found!", Toast.LENGTH_SHORT).show();
                Log.e("AlarmActivity", "Clock app not found!");
            }
        } catch (Exception e) {
            Log.e("AlarmActivity", "Error setting alarm", e);
            Toast.makeText(context, "Invalid time format. Use 'set alarm for HH:MM AM/PM'", Toast.LENGTH_SHORT).show();
        }
    }
}
