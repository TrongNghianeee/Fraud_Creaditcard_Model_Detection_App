package com.example.mobile_app;

import com.google.gson.annotations.SerializedName;

/**
 * Transaction Data Model - Updated for 4 fields only
 * Fields: amt, gender, category, transaction_time
 */
public class TransactionData {

    @SerializedName("amt")
    private Double amt;  // Số tiền (VND)

    @SerializedName("gender")
    private String gender;  // Giới tính (Nam/Nữ)

    @SerializedName("category")
    private String category;  // Loại giao dịch (Tiếng Việt)

    @SerializedName("transaction_time")
    private String transactionTime;  // Thời gian (HH:MM:SS)

    // Getters
    public Double getAmt() { return amt; }
    public String getGender() { return gender; }
    public String getCategory() { return category; }
    public String getTransactionTime() { return transactionTime; }

    // Setters
    public void setAmt(Double amt) { this.amt = amt; }
    public void setGender(String gender) { this.gender = gender; }
    public void setCategory(String category) { this.category = category; }
    public void setTransactionTime(String transactionTime) { this.transactionTime = transactionTime; }
}
