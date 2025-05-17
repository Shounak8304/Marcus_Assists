package com.example.marcus;

import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.util.Log;
import android.widget.Toast;

public class GoogleMapsActivity {
    private static final String TAG = "GoogleMapsActivity";
    private Context context;

    public GoogleMapsActivity(Context ctx) {
        this.context = ctx;
    }

    public void navigateTo(String destination) {
        Log.d(TAG, "Navigating to: " + destination);
        openGoogleMapsSearch(destination);
    }

    private void openGoogleMapsSearch(String destination) {
        Log.d(TAG, "Opening Google Maps with search for: " + destination);

        Uri gmmIntentUri = Uri.parse("geo:0,0?q=" + Uri.encode(destination));  // Search mode
        Intent mapIntent = new Intent(Intent.ACTION_VIEW, gmmIntentUri);
        mapIntent.setPackage("com.google.android.apps.maps");

        if (mapIntent.resolveActivity(context.getPackageManager()) != null) {
            context.startActivity(mapIntent);
        } else {
            Toast.makeText(context, "Google Maps not installed!", Toast.LENGTH_SHORT).show();
        }
    }
}
