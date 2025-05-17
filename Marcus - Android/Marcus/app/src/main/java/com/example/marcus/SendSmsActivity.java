package com.example.marcus;

import android.content.Context;
import android.database.Cursor;
import android.provider.ContactsContract;
import android.telephony.SmsManager;
import android.util.Log;
import android.widget.Toast;

public class SendSmsActivity {

    private Context context;

    public SendSmsActivity(Context context) {
        this.context = context;
    }

    public void sendSms(String contactName, String message) {
        String phoneNumber = getPhoneNumber(contactName);

        if (phoneNumber != null && !phoneNumber.isEmpty()) {
            try {
                SmsManager smsManager = SmsManager.getDefault();
                smsManager.sendTextMessage(phoneNumber, null, message, null, null);
                Toast.makeText(context, "SMS sent to " + contactName, Toast.LENGTH_SHORT).show();
                Log.d("SendSmsActivity", "SMS sent to " + contactName + " at " + phoneNumber);
            } catch (Exception e) {
                Log.e("SendSmsActivity", "SMS sending failed", e);
                Toast.makeText(context, "SMS sending failed", Toast.LENGTH_SHORT).show();
            }
        } else {
            Toast.makeText(context, "Contact not found", Toast.LENGTH_SHORT).show();
            Log.d("SendSmsActivity", "Contact not found: " + contactName);
        }
    }

    private String getPhoneNumber(String contactName) {
        String phoneNumber = null;
        String trimmedContactName = contactName.trim().toLowerCase(); // Trim and convert to lower case
        Cursor cursor = context.getContentResolver().query(
                ContactsContract.Contacts.CONTENT_URI,
                null,
                "LOWER(" + ContactsContract.Contacts.DISPLAY_NAME + ") = ?",
                new String[]{trimmedContactName},
                null);

        if (cursor != null && cursor.moveToFirst()) {
            int contactIdIndex = cursor.getColumnIndex(ContactsContract.Contacts._ID);
            if (contactIdIndex != -1) {
                String contactId = cursor.getString(contactIdIndex);

                Cursor phones = context.getContentResolver().query(
                        ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                        null,
                        ContactsContract.CommonDataKinds.Phone.CONTACT_ID + " = ?",
                        new String[]{contactId},
                        null);

                if (phones != null && phones.moveToFirst()) {
                    int phoneNumberIndex = phones.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER);
                    if (phoneNumberIndex != -1) {
                        phoneNumber = phones.getString(phoneNumberIndex);
                    }
                    phones.close();
                }
            }
            cursor.close();
        }
        Log.d("SendSmsActivity", "Phone number for " + contactName + ": " + phoneNumber);
        return phoneNumber;
    }
}