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
    private TextView tvRecommendation;
    private CardView cvAiExplanation;
    private TextView tvAiExplanation;
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
        tvRecommendation = findViewById(R.id.tvRecommendation);
        cvAiExplanation = findViewById(R.id.cvAiExplanation);
        tvAiExplanation = findViewById(R.id.tvAiExplanation);
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
        int transactionHour = getIntent().getIntExtra("transaction_hour", -1);
        int transactionDay = getIntent().getIntExtra("transaction_day", -1);
        int transactionMonth = getIntent().getIntExtra("transaction_month", -1);
        int age = getIntent().getIntExtra("age", -1);
        String city = getIntent().getStringExtra("city");
        long cityPop = getIntent().getLongExtra("city_pop", 0L);

        String aiExplanation = getIntent().getStringExtra("ai_explanation");
        boolean aiExplanationSuccess = getIntent().getBooleanExtra("ai_explanation_success", true);
        String aiExplanationError = getIntent().getStringExtra("ai_explanation_error");
        
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
        
        // Transaction converted info is intentionally hidden on this screen (mobile UX)
        
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

        // Show AI explanation only when fraud=true and explanation exists (or show error if attempted)
        if (isFraud) {
            if (aiExplanation != null && !aiExplanation.trim().isEmpty()) {
                cvAiExplanation.setVisibility(android.view.View.VISIBLE);
                tvAiExplanation.setText(aiExplanation);
            } else if (!aiExplanationSuccess) {
                cvAiExplanation.setVisibility(android.view.View.VISIBLE);
                String msg = (aiExplanationError != null && !aiExplanationError.trim().isEmpty())
                        ? ("Không thể tạo giải thích AI: " + aiExplanationError)
                        : "Không thể tạo giải thích AI";
                tvAiExplanation.setText(msg);
            } else {
                cvAiExplanation.setVisibility(android.view.View.GONE);
            }
        } else {
            cvAiExplanation.setVisibility(android.view.View.GONE);
        }
    }
    
    private void setupListeners() {
        btnBackToForm.setOnClickListener(v -> finish());
    }
}
