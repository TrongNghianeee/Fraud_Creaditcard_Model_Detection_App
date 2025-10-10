package com.example.mobile_app;

import android.graphics.Color;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import java.text.DecimalFormat;
import java.util.Locale;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * Form Activity - Display transaction results
 */
public class FormActivity extends AppCompatActivity {

    // UI Components
    private EditText etSenderName;
    private EditText etReceiverName;
    private EditText etAmountVnd;
    private EditText etAmountUsd;
    private EditText etTime;
    private EditText etDate;
    private EditText etTransactionContent;
    private EditText etSenderBank;
    private EditText etReceiverBank;
    private EditText etTransactionId;
    private EditText etTransactionFee;
    private Button btnFraudCheck;
    private ProgressBar progressFraud;
    private LinearLayout layoutFraudResult;
    private TextView tvFraudStatus;
    private TextView tvFraudProbability;
    private TextView tvFraudRecommendation;
    private Button btnBack;

    private final DecimalFormat decimalFormat = new DecimalFormat("0.####################");

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_form);

        decimalFormat.setGroupingUsed(false);

        // Initialize views
        initViews();

        // Load data from Intent
        loadTransactionData();

        // Setup back button
        btnBack.setOnClickListener(v -> finish());

        // Fraud analysis button
        btnFraudCheck.setOnClickListener(v -> analyzeFraud(true));

    }

    /**
     * Initialize all UI components
     */
    private void initViews() {
        etSenderName = findViewById(R.id.etSenderName);
        etReceiverName = findViewById(R.id.etReceiverName);
        etAmountVnd = findViewById(R.id.etAmountVnd);
        etAmountUsd = findViewById(R.id.etAmountUsd);
        etTime = findViewById(R.id.etTime);
        etDate = findViewById(R.id.etDate);
        etTransactionContent = findViewById(R.id.etTransactionContent);
        etSenderBank = findViewById(R.id.etSenderBank);
        etReceiverBank = findViewById(R.id.etReceiverBank);
        etTransactionId = findViewById(R.id.etTransactionId);
        etTransactionFee = findViewById(R.id.etTransactionFee);
        btnFraudCheck = findViewById(R.id.btnFraudCheck);
        progressFraud = findViewById(R.id.progressFraud);
        layoutFraudResult = findViewById(R.id.layoutFraudResult);
        tvFraudStatus = findViewById(R.id.tvFraudStatus);
        tvFraudProbability = findViewById(R.id.tvFraudProbability);
        tvFraudRecommendation = findViewById(R.id.tvFraudRecommendation);
        btnBack = findViewById(R.id.btnBack);
        layoutFraudResult.setVisibility(View.GONE);
        progressFraud.setVisibility(View.GONE);

        etAmountUsd.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) { }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                layoutFraudResult.setVisibility(View.GONE);
            }

            @Override
            public void afterTextChanged(Editable s) { }
        });
    }

    /**
     * Load transaction data from Intent extras
     */
    private void loadTransactionData() {
        Bundle extras = getIntent().getExtras();
        if (extras != null) {
            // Basic information
            setEditTextValue(etSenderName, extras.getString("sender_name"));
            setEditTextValue(etReceiverName, extras.getString("receiver_name"));

            // Amounts (strip currency symbols)
            setEditTextAmount(etAmountVnd, extras.getString("amount_vnd"));
            setEditTextAmount(etAmountUsd, extras.getString("amount_usd"));

            // Date and time
            setEditTextValue(etTime, extras.getString("time"));
            setEditTextValue(etDate, extras.getString("date"));

            // Transaction details
            setEditTextValue(etTransactionContent, extras.getString("transaction_content"));
            setEditTextValue(etSenderBank, extras.getString("sender_bank"));
            setEditTextValue(etReceiverBank, extras.getString("receiver_bank"));
            setEditTextValue(etTransactionId, extras.getString("transaction_id"));
            setEditTextAmount(etTransactionFee, extras.getString("transaction_fee"));

        }
    }

    private void setEditTextValue(EditText editText, String value) {
        if (value == null || value.trim().isEmpty() || value.equalsIgnoreCase("null")) {
            editText.setText("");
        } else {
            editText.setText(value.trim());
        }
    }

    private void setEditTextAmount(EditText editText, String value) {
        Double parsed = parseAmount(value);
        if (parsed == null) {
            setEditTextValue(editText, value);
        } else {
            editText.setText(formatForInput(parsed));
        }
    }

    private String formatForInput(Double value) {
        if (value == null) {
            return "";
        }
        String formatted = decimalFormat.format(value);
        // Remove trailing .0 if present
        if (formatted.contains(".") && formatted.endsWith("0")) {
            formatted = formatted.replaceAll("0+$", "").replaceAll("\\.$", "");
        }
        return formatted;
    }

    private Double parseAmount(String raw) {
        if (raw == null) {
            return null;
        }

        String trimmed = raw.trim();
        if (trimmed.isEmpty() || trimmed.equalsIgnoreCase("null")) {
            return null;
        }

        // Remove currency symbols and letters
        String cleaned = trimmed.replaceAll("[A-Za-zđĐ₫$€£¥₱₫]", "").trim();
        if (cleaned.isEmpty()) {
            return null;
        }

        boolean hasComma = cleaned.contains(",");
        boolean hasDot = cleaned.contains(".");
        String normalized = cleaned.replace(" ", "");

        if (hasComma && hasDot) {
            int lastComma = normalized.lastIndexOf(',');
            int lastDot = normalized.lastIndexOf('.');
            if (lastComma > lastDot) {
                normalized = normalized.replace(".", "").replace(',', '.');
            } else {
                normalized = normalized.replace(",", "");
            }
        } else if (hasComma) {
            normalized = normalized.replace(',', '.');
        }

        normalized = normalized.replaceAll("[^0-9.\\-]", "");

        int dotIndex = normalized.indexOf('.');
        if (dotIndex != -1) {
            int nextDot = normalized.indexOf('.', dotIndex + 1);
            if (nextDot != -1) {
                String integerPart = normalized.substring(0, nextDot).replace(".", "");
                String decimalPart = normalized.substring(nextDot + 1);
                normalized = integerPart + (decimalPart.isEmpty() ? "" : "." + decimalPart);
            }
        }

        boolean negative = normalized.startsWith("-");
        normalized = normalized.replace("-", "");
        if (negative) {
            normalized = "-" + normalized;
        }

        try {
            return Double.parseDouble(normalized);
        } catch (NumberFormatException e) {
            return null;
        }
    }

    private void analyzeFraud(boolean showValidationMessage) {
        Double amountUsd = parseAmount(etAmountUsd.getText().toString());
        Double amountVnd = parseAmount(etAmountVnd.getText().toString());

        if (amountUsd == null || amountUsd < 0) {
            if (showValidationMessage) {
                Toast.makeText(this, "Vui lòng nhập số tiền USD hợp lệ để phân tích.", Toast.LENGTH_SHORT).show();
            }
            layoutFraudResult.setVisibility(View.GONE);
            return;
        }

        showFraudLoading(true);

        ApiService apiService = ApiClient.getApiService();
        FraudRequest request = new FraudRequest(amountUsd, amountVnd);

        apiService.predictFromAmount(request).enqueue(new Callback<FraudResponse>() {
            @Override
            public void onResponse(Call<FraudResponse> call, Response<FraudResponse> response) {
                showFraudLoading(false);

                if (!response.isSuccessful() || response.body() == null) {
                    if (showValidationMessage) {
                        Toast.makeText(FormActivity.this, "Không thể phân tích fraud. Mã " + response.code(), Toast.LENGTH_SHORT).show();
                    }
                    layoutFraudResult.setVisibility(View.GONE);
                    return;
                }

                FraudResponse fraudResponse = response.body();
                if (!fraudResponse.isSuccess() || fraudResponse.getPrediction() == null) {
                    if (showValidationMessage) {
                        String message = fraudResponse.getError() != null ? fraudResponse.getError() : "Không nhận được kết quả phân tích.";
                        Toast.makeText(FormActivity.this, message, Toast.LENGTH_SHORT).show();
                    }
                    layoutFraudResult.setVisibility(View.GONE);
                    return;
                }

                updateFraudResult(fraudResponse.getPrediction());
            }

            @Override
            public void onFailure(Call<FraudResponse> call, Throwable t) {
                showFraudLoading(false);
                if (showValidationMessage) {
                    Toast.makeText(FormActivity.this, "Lỗi kết nối: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                }
                layoutFraudResult.setVisibility(View.GONE);
            }
        });
    }

    private void showFraudLoading(boolean loading) {
        progressFraud.setVisibility(loading ? View.VISIBLE : View.GONE);
        btnFraudCheck.setEnabled(!loading);
        if (loading) {
            layoutFraudResult.setVisibility(View.GONE);
        }
    }

    private void updateFraudResult(FraudPrediction prediction) {
        layoutFraudResult.setVisibility(View.VISIBLE);

        double probabilityPercent = prediction.getFraudProbability() * 100.0;
        tvFraudProbability.setText(String.format(Locale.getDefault(), "Tỷ lệ Fraud: %.2f%%", probabilityPercent));

        String riskLevel = prediction.getRiskLevel() != null ? prediction.getRiskLevel().toLowerCase(Locale.ROOT) : "";
        String statusText;
        String recommendation;
        int statusColor;
        int detailColor;
        int backgroundColor;

        switch (riskLevel) {
            case "very_low":
                statusText = "AN TOÀN";
                recommendation = "Giao dịch an toàn, có thể tiếp tục.";
                statusColor = Color.parseColor("#2e7d32");
                detailColor = Color.parseColor("#1b5e20");
                backgroundColor = Color.parseColor("#e8f5e9");
                break;
            case "low":
                statusText = "RỦI RO THẤP";
                recommendation = "Rủi ro thấp, nên tiếp tục theo dõi.";
                statusColor = Color.parseColor("#0277bd");
                detailColor = Color.parseColor("#01579b");
                backgroundColor = Color.parseColor("#e1f5fe");
                break;
            case "high":
                statusText = "RỦI RO CAO";
                recommendation = "Cân nhắc từ chối hoặc kiểm tra kỹ.";
                statusColor = Color.parseColor("#c62828");
                detailColor = Color.parseColor("#b71c1c");
                backgroundColor = Color.parseColor("#fdecea");
                break;
            case "very_high":
                statusText = "RỦI RO RẤT CAO";
                recommendation = "Khuyến nghị từ chối ngay lập tức.";
                statusColor = Color.parseColor("#7f0000");
                detailColor = Color.parseColor("#7f0000");
                backgroundColor = Color.parseColor("#ffebee");
                break;
            case "medium":
            default:
                statusText = prediction.isFraud() ? "RỦI RO" : "TRUNG LẬP";
                recommendation = prediction.isFraud() ? "Kiểm tra kỹ trước khi chấp nhận." : "Tiếp tục theo dõi giao dịch.";
                statusColor = Color.parseColor("#ef6c00");
                detailColor = Color.parseColor("#d84315");
                backgroundColor = Color.parseColor("#fff3e0");
                break;
        }

        tvFraudStatus.setText(statusText);
        tvFraudStatus.setTextColor(statusColor);
        tvFraudProbability.setTextColor(detailColor);
        tvFraudRecommendation.setText("Khuyến nghị: " + recommendation);
        tvFraudRecommendation.setTextColor(detailColor);
        layoutFraudResult.setBackgroundColor(backgroundColor);
    }
}
