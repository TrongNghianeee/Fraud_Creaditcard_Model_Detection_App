package com.example.mobile_app;

import com.google.gson.annotations.SerializedName;

/**
 * Request payload for fraud detection endpoint (NEW API)
 * 4 parameters: amt, gender, category, transaction_time
 */
public class FraudRequest {

    @SerializedName("amt")
    private final double amt;  // Số tiền VND

    @SerializedName("gender")
    private final String gender;  // Giới tính (Nam/Nữ)

    @SerializedName("category")
    private final String category;  // Loại giao dịch (Tiếng Việt)

    @SerializedName("transaction_time")
    private final String transactionTime;  // Thời gian (HH:MM:SS)

    public FraudRequest(double amt, String gender, String category, String transactionTime) {
        this.amt = amt;
        this.gender = gender;
        this.category = category;
        this.transactionTime = transactionTime;
    }

    public double getAmt() {
        return amt;
    }

    public String getGender() {
        return gender;
    }

    public String getCategory() {
        return category;
    }

    public String getTransactionTime() {
        return transactionTime;
    }
}
