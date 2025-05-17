package com.example.marcus;

import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.util.Log;
import android.widget.Toast;


public class WhatsAppCallActivity {
    private Context context;

    public WhatsAppCallActivity(Context context) {
        if (context == null) {
            throw new IllegalArgumentException("Context cannot be null in WhatsAppCallActivity");
        }
        this.context = context;
    }

    public void makeVoiceCall(String contactName) {
        if (context == null) {
            Log.e("WhatsAppCallActivity", "❌ Context is null! Cannot make WhatsApp call.");
            return;
        }

        WhatsAppActivity whatsappActivity = new WhatsAppActivity(context);
        String phoneNumber = whatsappActivity.getContactNumber(contactName);

        if (phoneNumber == null) {
            Log.e("WhatsAppCallActivity", "❌ Contact not found: " + contactName);
            Toast.makeText(context, "❌ Contact not found: " + contactName, Toast.LENGTH_SHORT).show();
            return;
        }

        try {
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse("https://wa.me/" + phoneNumber));
            context.startActivity(intent);
            Log.d("WhatsAppCallActivity", "📞 WhatsApp Voice Call Started for: " + contactName);
        } catch (Exception e) {
            Log.e("WhatsAppCallActivity", "❌ Error making WhatsApp call: " + e.getMessage());
            Toast.makeText(context, "❌ Failed to make WhatsApp voice call!", Toast.LENGTH_SHORT).show();
        }
    }

    public void makeVideoCall(String contactName) {
        WhatsAppActivity whatsappActivity = new WhatsAppActivity(context);
        String phoneNumber = whatsappActivity.getContactNumber(contactName);

        if (phoneNumber == null) {
            Log.e("WhatsAppCallActivity", "❌ Contact not found: " + contactName);
            Toast.makeText(context, "❌ Contact not found: " + contactName, Toast.LENGTH_SHORT).show();
            return;
        }

        try {
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse("https://wa.me/" + phoneNumber));
            context.startActivity(intent);
            Log.d("WhatsAppCallActivity", "📹 WhatsApp Video Call Started for: " + contactName);

            new WhatsAppAccessibilityService().clickVideoCallButton();
        } catch (Exception e) {
            Log.e("WhatsAppCallActivity", "❌ Error making WhatsApp video call: " + e.getMessage());
            Toast.makeText(context, "❌ Failed to make WhatsApp video call!", Toast.LENGTH_SHORT).show();
        }
    }
}
