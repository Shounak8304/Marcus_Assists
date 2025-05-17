package com.example.marcus;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.Button;
import android.widget.Toast;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

public class AccountActivity extends AppCompatActivity {

    private Button user1Button, user2Button, user3Button, editButton, deleteButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_account);

        user1Button = findViewById(R.id.user1Button);
        user2Button = findViewById(R.id.user2Button);
        user3Button = findViewById(R.id.user3Button);
        editButton = findViewById(R.id.editButton);
        deleteButton = findViewById(R.id.deleteButton);

        loadUserButtons();

        user1Button.setOnClickListener(v -> showUserDetails(1));
        user2Button.setOnClickListener(v -> showUserDetails(2));
        user3Button.setOnClickListener(v -> showUserDetails(3));

        editButton.setOnClickListener(v -> editUserDetails());
        deleteButton.setOnClickListener(v -> deleteUserDetails());
    }

    private void loadUserButtons() {
        SharedPreferences sharedPreferences = getSharedPreferences("user_prefs", Context.MODE_PRIVATE);
        int userCount = sharedPreferences.getInt("user_count", 0);

        if (userCount > 0) {
            user1Button.setText("User 1: " + sharedPreferences.getString("user1_name", "N/A"));
        }
        if (userCount > 1) {
            user2Button.setText("User 2: " + sharedPreferences.getString("user2_name", "N/A"));
        }
        if (userCount > 2) {
            user3Button.setText("User 3: " + sharedPreferences.getString("user3_name", "N/A"));
        }
    }

    private void showUserDetails(int userSlot) {
        SharedPreferences sharedPreferences = getSharedPreferences("user_prefs", Context.MODE_PRIVATE);
        String userDetails = sharedPreferences.getString("user" + userSlot + "_details", null);

        if (userDetails != null) {
            new AlertDialog.Builder(AccountActivity.this)
                    .setTitle("User " + userSlot + " Details")
                    .setMessage(userDetails)
                    .setPositiveButton(android.R.string.ok, null)
                    .show();
        } else {
            Toast.makeText(AccountActivity.this, "No user details found", Toast.LENGTH_SHORT).show();
        }
    }

    private void editUserDetails() {
        // Implement edit user details functionality
    }

    private void deleteUserDetails() {
        // Implement delete user details functionality
    }
}