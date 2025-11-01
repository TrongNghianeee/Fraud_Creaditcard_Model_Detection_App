package com.example.mobile_app;

import android.graphics.Color;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import androidx.cardview.widget.CardView;
import java.text.DecimalFormat;
import java.util.Locale;

public class FraudResultActivity extends AppCompatActivity {
    private static final String TAG = "FraudResultActivity";
    
    private CardView cvFraudStatus;
    private TextView tvFraudIcon;
    private TextView tvFraudStatus;
    private TextView tvFraudProbability;
    private TextView tvRiskLevel;
    private TextView tvConvertedInfo;
    private TextView tvRecommendation;
    private Button btnBackToForm;
    
    private final DecimalFormat decimalFormat = new DecimalFormat("#,###");

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_fraud_result);
        
        initViews();
        loadResultData();
        setupListeners();
    }
    
    private void initViews() {
        cvFraudStatus = findViewById(R.id.cvFraudStatus);
        tvFraudIcon = findViewById(R.id.tvFraudIcon);
        tvFraudStatus = findViewById(R.id.tvFraudStatus);
        tvFraudProbability = findViewById(R.id.tvFraudProbability);
        tvRiskLevel = findViewById(R.id.tvRiskLevel);
        tvConvertedInfo = findViewById(R.id.tvConvertedInfo);
        tvRecommendation = findViewById(R.id.tvRecommendation);
        btnBackToForm = findViewById(R.id.btnBackToForm);
    }
    
    private void loadResultData() {
        // Get data from intent
        boolean isFraud = getIntent().getBooleanExtra("is_fraud", false);
        double fraudProb = getIntent().getDoubleExtra("fraud_probability", 0.0);
        String riskLevel = getIntent().getStringExtra("risk_level");
        String confidence = getIntent().getStringExtra("confidence");
        
        double amtVnd = getIntent().getDoubleExtra("amt_vnd", 0.0);
        double amtUsd = getIntent().getDoubleExtra("amt_usd", 0.0);
        String gender = getIntent().getStringExtra("gender");
        String category = getIntent().getStringExtra("category");
        String transactionTime = getIntent().getStringExtra("transaction_time");
        
        // Set fraud status with color coding
        if (isFraud) {
            tvFraudIcon.setText("⚠");
            tvFraudIcon.setTextColor(Color.parseColor("#C62828"));
            tvFraudStatus.setText("CẢNH BÁO: GIAO DỊCH NGHI NGỜ!");
            tvFraudStatus.setTextColor(Color.parseColor("#C62828"));
            cvFraudStatus.setCardBackgroundColor(Color.parseColor("#FFEBEE"));
        } else {
            tvFraudIcon.setText("✓");
            tvFraudIcon.setTextColor(Color.parseColor("#2E7D32"));
            tvFraudStatus.setText("GIAO DỊCH AN TOÀN");
            tvFraudStatus.setTextColor(Color.parseColor("#2E7D32"));
            cvFraudStatus.setCardBackgroundColor(Color.parseColor("#E8F5E9"));
        }
        
        // Set probability
        String probText = String.format(Locale.getDefault(), "%.1f%%", fraudProb * 100);
        tvFraudProbability.setText(probText);
        
        // Set risk level
        tvRiskLevel.setText(riskLevel != null ? riskLevel : "Không xác định");
        
        // Set converted info
        StringBuilder convertedInfo = new StringBuilder();
        if (amtVnd > 0) {
            convertedInfo.append(String.format(Locale.getDefault(), "Số tiền: %.0f VND (%.2f USD)\n", amtVnd, amtUsd));
        }
        if (gender != null && !gender.isEmpty()) {
            convertedInfo.append("Giới tính: ").append(gender).append("\n");
        }
        if (category != null && !category.isEmpty()) {
            convertedInfo.append("Loại giao dịch: ").append(category).append("\n");
        }
        if (transactionTime != null && !transactionTime.isEmpty()) {
            convertedInfo.append("Thời gian: ").append(transactionTime);
        }
        
        if (convertedInfo.length() > 0) {
            tvConvertedInfo.setText(convertedInfo.toString());
        } else {
            tvConvertedInfo.setText("Không có thông tin");
        }
        
        // Set recommendation based on fraud status and risk level
        String recommendation;
        if (isFraud) {
            if ("HIGH".equalsIgnoreCase(riskLevel)) {
                recommendation = "Cảnh báo: Giao dịch có nguy cơ cao! Nên từ chối hoặc kiểm tra kỹ.";
            } else if ("MEDIUM".equalsIgnoreCase(riskLevel)) {
                recommendation = "Lưu ý: Giao dịch có nguy cơ trung bình. Nên xác minh thêm.";
            } else {
                recommendation = "Giao dịch nghi ngờ. Nên theo dõi và xác minh.";
            }
        } else {
            recommendation = "Giao dịch được xác nhận an toàn. Có thể tiến hành bình thường.";
        }
        
        tvRecommendation.setText(recommendation);
    }
    
    private void setupListeners() {
        btnBackToForm.setOnClickListener(v -> finish());
    }
}
