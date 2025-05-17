package com.example.marcus;

import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.provider.ContactsContract;
import android.util.Log;
import android.widget.Toast;

import org.apache.commons.text.similarity.LevenshteinDistance;

import java.util.HashMap;
import java.util.Map;

public class WhatsAppActivity {
    private Context context;

    public WhatsAppActivity(Context context) {
        this.context = context;
    }

    public void sendWhatsAppMessage(String contactName, String message) {
        String phoneNumber = getContactNumber(contactName);

        if (phoneNumber == null) {
            Log.e("WhatsAppActivity", "❌ Contact not found: " + contactName);
            Toast.makeText(context, "❌ Contact not found: " + contactName, Toast.LENGTH_SHORT).show();
            return;
        }

        try {
            String encodedMessage = Uri.encode(message);
            Intent intent = new Intent(Intent.ACTION_VIEW);
            intent.setData(Uri.parse("https://api.whatsapp.com/send?phone=" + phoneNumber + "&text=" + encodedMessage));
            context.startActivity(intent);
            Log.d("WhatsAppActivity", "📩 WhatsApp chat opened for: " + contactName + " (" + phoneNumber + ") -> " + message);
        } catch (Exception e) {
            Log.e("WhatsAppActivity", "❌ Error opening WhatsApp: " + e.getMessage());
            Toast.makeText(context, "❌ Failed to open WhatsApp!", Toast.LENGTH_SHORT).show();
        }
    }

    public String getContactNumber(String inputName) {
        inputName = inputName.toLowerCase().replace("on whatsapp", "").trim(); // Ensure name is clean
        Map<String, String> contactsMap = getAllContacts();
        return findBestMatch(inputName, contactsMap);
    }

    private Map<String, String> getAllContacts() {
        Map<String, String> contactsMap = new HashMap<>();
        Uri uri = ContactsContract.CommonDataKinds.Phone.CONTENT_URI;
        String[] projection = {ContactsContract.CommonDataKinds.Phone.NUMBER, ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME};

        Cursor cursor = context.getContentResolver().query(uri, projection, null, null, null);
        if (cursor != null) {
            while (cursor.moveToNext()) {
                String name = cursor.getString(1).toLowerCase();
                String number = cursor.getString(0);
                contactsMap.put(name, number);
            }
            cursor.close();
        }
        return contactsMap;
    }

    private String findBestMatch(String inputName, Map<String, String> contactsMap) {
        LevenshteinDistance levenshtein = new LevenshteinDistance();
        String bestMatch = null;
        int lowestDistance = Integer.MAX_VALUE;
        int threshold = 3;

        for (String contactName : contactsMap.keySet()) {
            int distance = levenshtein.apply(inputName, contactName);
            if (distance < lowestDistance) {
                lowestDistance = distance;
                bestMatch = contactName;
            }
        }

        if (bestMatch != null && lowestDistance <= threshold) {
            Log.d("WhatsAppActivity", "✅ Best match: " + bestMatch + " with distance " + lowestDistance);
            return contactsMap.get(bestMatch);
        }

        Log.e("WhatsAppActivity", "❌ No close match found for: " + inputName);
        return null;
    }
}
