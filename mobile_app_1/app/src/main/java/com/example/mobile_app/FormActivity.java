package com.example.mobile_app;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.Spinner;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import java.text.DecimalFormat;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class FormActivity extends AppCompatActivity {
    private static final String TAG = "FormActivity";

    private EditText etAmount;
    private Spinner spGender;
    private Spinner spCategory;
    private EditText etTransactionTime;
    private Button btnFraudCheck;
    private ProgressBar progressFraud;
    private Button btnBack;

    private final DecimalFormat decimalFormat = new DecimalFormat("#,###");

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Log.d(TAG, "FormActivity onCreate() started");
        
        setContentView(R.layout.activity_form);
        Log.d(TAG, "Layout set successfully");
        
        initializeViews();
        Log.d(TAG, "Views initialized successfully");
        
        loadTransactionData();
        Log.d(TAG, "Transaction data loaded successfully");
        
        setupListeners();
        Log.d(TAG, "Listeners setup successfully");
    }

    private void initializeViews() {
        etAmount = findViewById(R.id.etAmount);
        spGender = findViewById(R.id.spGender);
        spCategory = findViewById(R.id.spCategory);
        etTransactionTime = findViewById(R.id.etTransactionTime);
        btnFraudCheck = findViewById(R.id.btnFraudCheck);
        progressFraud = findViewById(R.id.progressFraud);
        btnBack = findViewById(R.id.btnBack);
    }

    private void loadTransactionData() {
        try {
            String amt = getIntent().getStringExtra("amt");
            String gender = getIntent().getStringExtra("gender");
            String category = getIntent().getStringExtra("category");
            String transactionTime = getIntent().getStringExtra("transaction_time");
            
            Log.d(TAG, "Intent extras - amt: " + amt + ", gender: " + gender +
                    ", category: " + category + ", transaction_time: " + transactionTime);
            
            if (amt != null && !amt.isEmpty()) {
                etAmount.setText(amt);
                Log.d(TAG, "Set amount: " + amt);
            }
            
            if (gender != null && !gender.isEmpty()) {
                String[] genderOptions = getResources().getStringArray(R.array.gender_options);
                for (int i = 0; i < genderOptions.length; i++) {
                    if (genderOptions[i].equalsIgnoreCase(gender)) {
                        spGender.setSelection(i);
                        Log.d(TAG, "Set gender selection to position: " + i + " (" + gender + ")");
                        break;
                    }
                }
            }
            
            if (category != null && !category.isEmpty()) {
                String[] categoryOptions = getResources().getStringArray(R.array.category_options);
                for (int i = 0; i < categoryOptions.length; i++) {
                    if (categoryOptions[i].equalsIgnoreCase(category)) {
                        spCategory.setSelection(i);
                        Log.d(TAG, "Set category selection to position: " + i + " (" + category + ")");
                        break;
                    }
                }
            }
            
            if (transactionTime != null && !transactionTime.isEmpty()) {
                etTransactionTime.setText(transactionTime);
                Log.d(TAG, "Set transaction time: " + transactionTime);
            }
            
            Log.d(TAG, "loadTransactionData() completed successfully");
        } catch (Exception e) {
            Log.e(TAG, "Error loading transaction data", e);
            Toast.makeText(this, "Lỗi khi tải dữ liệu giao dịch", Toast.LENGTH_SHORT).show();
        }
    }

    private void setupListeners() {
        btnFraudCheck.setOnClickListener(v -> analyzeFraud());
        btnBack.setOnClickListener(v -> finish());
    }

    private void analyzeFraud() {
        if (!validateInputs()) return;

        String amtStr = etAmount.getText().toString().trim().replace(",", "");
        String gender = spGender.getSelectedItem().toString();
        String category = spCategory.getSelectedItem().toString();
        String transactionTime = etTransactionTime.getText().toString().trim();

        Log.d(TAG, "Analyzing fraud - amt: " + amtStr + ", gender: " + gender + 
                ", category: " + category + ", time: " + transactionTime);

        double amt;
        try {
            amt = Double.parseDouble(amtStr);
        } catch (NumberFormatException e) {
            Toast.makeText(this, "Số tiền không hợp lệ", Toast.LENGTH_SHORT).show();
            return;
        }

        showLoading();

        FraudRequest request = new FraudRequest(amt, gender, category, transactionTime);
        Call<FraudResponse> call = ApiClient.getApiService().predictFraud(request);

        call.enqueue(new Callback<FraudResponse>() {
            @Override
            public void onResponse(Call<FraudResponse> call, Response<FraudResponse> response) {
                hideLoading();
                
                if (response.isSuccessful() && response.body() != null) {
                    Log.d(TAG, "Fraud analysis successful");
                    navigateToResultActivity(response.body());
                } else {
                    Log.e(TAG, "Fraud analysis failed with code: " + response.code());
                    Toast.makeText(FormActivity.this, "Lỗi: " + response.code(), Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<FraudResponse> call, Throwable t) {
                hideLoading();
                Log.e(TAG, "Fraud analysis failed", t);
                Toast.makeText(FormActivity.this, "Lỗi kết nối: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void navigateToResultActivity(FraudResponse response) {
        Intent intent = new Intent(this, FraudResultActivity.class);
        FraudPrediction prediction = response.getPrediction();
        FraudResponse.FraudInputData input = response.getInput();
        
        if (prediction != null) {
            intent.putExtra("is_fraud", prediction.isFraud());
            intent.putExtra("fraud_probability", prediction.getFraudProbability());
            intent.putExtra("confidence", prediction.getConfidence());
            intent.putExtra("risk_level", prediction.getRiskLevel());
        }
        
        if (input != null) {
            intent.putExtra("amt_vnd", input.getAmtVnd());
            intent.putExtra("amt_usd", input.getAmtUsd());
            intent.putExtra("gender", input.getGender());
            intent.putExtra("category", input.getCategory());
            intent.putExtra("transaction_time", input.getTransactionTime());
        }
        
        startActivity(intent);
    }

    private boolean validateInputs() {
        String amtStr = etAmount.getText().toString().trim();
        String gender = spGender.getSelectedItem().toString();
        String category = spCategory.getSelectedItem().toString();
        String transactionTime = etTransactionTime.getText().toString().trim();

        if (amtStr.isEmpty()) {
            Toast.makeText(this, "Vui lòng nhập số tiền", Toast.LENGTH_SHORT).show();
            return false;
        }

        if (category.equals("Chọn loại giao dịch")) {
            Toast.makeText(this, "Vui lòng chọn loại giao dịch", Toast.LENGTH_SHORT).show();
            return false;
        }

        if (transactionTime.isEmpty()) {
            Toast.makeText(this, "Vui lòng nhập thời gian giao dịch", Toast.LENGTH_SHORT).show();
            return false;
        }

        return true;
    }

    private void showLoading() {
        progressFraud.setVisibility(android.view.View.VISIBLE);
        btnFraudCheck.setEnabled(false);
    }

    private void hideLoading() {
        progressFraud.setVisibility(android.view.View.GONE);
        btnFraudCheck.setEnabled(true);
    }
}