package com.example.mobile_app;

import com.google.gson.annotations.SerializedName;

/**
 * Transaction Data Model - Updated to include full parsed fields
 * Fields: amt, gender, category, transaction_time, transaction_day, city, age
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

    @SerializedName("transaction_day")
    private Integer transactionDay; // 0-6

    @SerializedName("city")
    private String city; // tỉnh/thành (viết thường, không dấu)

    @SerializedName("age")
    private Integer age; // 18-100

    // Getters
    public Double getAmt() { return amt; }
    public String getGender() { return gender; }
    public String getCategory() { return category; }
    public String getTransactionTime() { return transactionTime; }
    public Integer getTransactionDay() { return transactionDay; }
    public String getCity() { return city; }
    public Integer getAge() { return age; }

    // Setters
    public void setAmt(Double amt) { this.amt = amt; }
    public void setGender(String gender) { this.gender = gender; }
    public void setCategory(String category) { this.category = category; }
    public void setTransactionTime(String transactionTime) { this.transactionTime = transactionTime; }
    public void setTransactionDay(Integer transactionDay) { this.transactionDay = transactionDay; }
    public void setCity(String city) { this.city = city; }
    public void setAge(Integer age) { this.age = age; }
}
