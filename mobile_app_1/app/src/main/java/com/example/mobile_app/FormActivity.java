package com.example.mobile_app;

import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import java.text.DecimalFormat;

/**
 * Form Activity - Display transaction results
 */
public class FormActivity extends AppCompatActivity {

    // UI Components
    private TextView tvSenderName;
    private TextView tvReceiverName;
    private TextView tvAmountVnd;
    private TextView tvAmountUsd;
    private TextView tvTime;
    private TextView tvDate;
    private TextView tvTransactionContent;
    private TextView tvSenderBank;
    private TextView tvReceiverBank;
    private TextView tvTransactionId;
    private TextView tvTransactionFee;
    private TextView tvOcrConfidence;
    private TextView tvProcessingTime;
    private Button btnBack;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_form);

        // Initialize views
        initViews();

        // Load data from Intent
        loadTransactionData();

        // Setup back button
        btnBack.setOnClickListener(v -> finish());
    }

    /**
     * Initialize all UI components
     */
    private void initViews() {
        tvSenderName = findViewById(R.id.tvSenderName);
        tvReceiverName = findViewById(R.id.tvReceiverName);
        tvAmountVnd = findViewById(R.id.tvAmountVnd);
        tvAmountUsd = findViewById(R.id.tvAmountUsd);
        tvTime = findViewById(R.id.tvTime);
        tvDate = findViewById(R.id.tvDate);
        tvTransactionContent = findViewById(R.id.tvTransactionContent);
        tvSenderBank = findViewById(R.id.tvSenderBank);
        tvReceiverBank = findViewById(R.id.tvReceiverBank);
        tvTransactionId = findViewById(R.id.tvTransactionId);
        tvTransactionFee = findViewById(R.id.tvTransactionFee);
        tvOcrConfidence = findViewById(R.id.tvOcrConfidence);
        tvProcessingTime = findViewById(R.id.tvProcessingTime);
        btnBack = findViewById(R.id.btnBack);
    }

    /**
     * Load transaction data from Intent extras
     */
    private void loadTransactionData() {
        Bundle extras = getIntent().getExtras();
        if (extras != null) {
            // Basic information
            tvSenderName.setText(formatValue(extras.getString("sender_name")));
            tvReceiverName.setText(formatValue(extras.getString("receiver_name")));
            
            // Amount with formatting
            String amountVnd = extras.getString("amount_vnd");
            String amountUsd = extras.getString("amount_usd");
            tvAmountVnd.setText(formatCurrency(amountVnd, "VND"));
            tvAmountUsd.setText(formatCurrency(amountUsd, "USD"));
            
            // Date and time
            tvTime.setText(formatValue(extras.getString("time")));
            tvDate.setText(formatValue(extras.getString("date")));
            
            // Transaction details
            tvTransactionContent.setText(formatValue(extras.getString("transaction_content")));
            tvSenderBank.setText(formatValue(extras.getString("sender_bank")));
            tvReceiverBank.setText(formatValue(extras.getString("receiver_bank")));
            tvTransactionId.setText(formatValue(extras.getString("transaction_id")));
            tvTransactionFee.setText(formatCurrency(extras.getString("transaction_fee"), "VND"));
            
            // OCR metadata
            String confidence = extras.getString("ocr_confidence");
            String processingTime = extras.getString("processing_time");
            tvOcrConfidence.setText(confidence != null ? confidence + "%" : "N/A");
            tvProcessingTime.setText(processingTime != null ? processingTime + "s" : "N/A");
        }
    }

    /**
     * Format value - handle null/empty
     */
    private String formatValue(String value) {
        if (value == null || value.trim().isEmpty() || value.equalsIgnoreCase("null")) {
            return "Không có thông tin";
        }
        return value;
    }

    /**
     * Format currency with proper thousand separator
     */
    private String formatCurrency(String amount, String currency) {
        if (amount == null || amount.trim().isEmpty() || amount.equalsIgnoreCase("null")) {
            return "0 " + currency;
        }
        
        try {
            // Remove any existing formatting
            String cleaned = amount.replaceAll("[^0-9.]", "");
            double value = Double.parseDouble(cleaned);
            
            // Format with thousand separator
            DecimalFormat formatter = new DecimalFormat("#,###.##");
            return formatter.format(value) + " " + currency;
        } catch (NumberFormatException e) {
            return amount + " " + currency;
        }
    }
}
