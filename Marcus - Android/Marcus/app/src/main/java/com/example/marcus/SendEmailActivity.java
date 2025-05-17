package com.example.marcus;

import android.util.Log;
import java.util.Properties;
import javax.mail.Authenticator;
import javax.mail.Message;
import javax.mail.MessagingException;
import javax.mail.PasswordAuthentication;
import javax.mail.Session;
import javax.mail.Transport;
import javax.mail.internet.InternetAddress;
import javax.mail.internet.MimeMessage;

public class SendEmailActivity {
    private static final String TAG = "SendEmailActivity";
    private static final String SMTP_HOST = "smtp.gmail.com"; // SMTP Server
    private static final String SMTP_PORT = "587"; // SMTP Port
    private static final String EMAIL_SENDER = "your_email@gmail.com"; // Your Email
    private static final String EMAIL_PASSWORD = "your_app_password"; // App Password

    public void sendEmail(String recipient, String subject, String body) {
        // Remove spaces from email before passing it into the thread
        final String cleanRecipient = recipient.replaceAll("\\s", "");

        Log.d(TAG, "Sending email to: " + cleanRecipient);

        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    Properties props = new Properties();
                    props.put("mail.smtp.auth", "true");
                    props.put("mail.smtp.starttls.enable", "true");
                    props.put("mail.smtp.host", SMTP_HOST);
                    props.put("mail.smtp.port", SMTP_PORT);

                    Session session = Session.getInstance(props, new Authenticator() {
                        @Override
                        protected PasswordAuthentication getPasswordAuthentication() {
                            return new PasswordAuthentication(EMAIL_SENDER, EMAIL_PASSWORD);
                        }
                    });

                    Message message = new MimeMessage(session);
                    message.setFrom(new InternetAddress(EMAIL_SENDER));
                    message.setRecipients(Message.RecipientType.TO, InternetAddress.parse(cleanRecipient));
                    message.setSubject(subject);
                    message.setText(body);

                    Transport.send(message);
                    Log.d(TAG, "Email sent successfully.");
                } catch (MessagingException e) {
                    Log.e(TAG, "Failed to send email", e);
                }
            }
        }).start();
    }
}
