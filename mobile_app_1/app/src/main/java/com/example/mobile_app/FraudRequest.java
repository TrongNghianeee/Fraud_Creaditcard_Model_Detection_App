package com.example.mobile_app;

import com.google.gson.annotations.SerializedName;

/**
 * Request payload for fraud detection endpoint (UPDATED)
 * Now includes: amt, gender, category, transaction_hour, transaction_day, age, city, city_pop
 */
public class FraudRequest {

    @SerializedName("amt")
    private final double amt;  // Số tiền VND

    @SerializedName("gender")
    private final String gender;  // Giới tính (Nam/Nữ)

    @SerializedName("category")
    private final String category;  // Loại giao dịch (Tiếng Việt)

    @SerializedName("transaction_hour")
    private final int transactionHour;  // Giờ giao dịch (0-23)

    @SerializedName("transaction_day")
    private final int transactionDay;   // Ngày trong tuần (0-6)

    @SerializedName("age")
    private final int age;              // Tuổi (18-100)

    @SerializedName("city")
    private final String city;          // Tên tỉnh/thành (viết thường, không dấu)

    @SerializedName("city_pop")
    private final long cityPop;         // Dân số tỉnh/thành

    public FraudRequest(double amt, String gender, String category, int transactionHour, int transactionDay, int age, String city, long cityPop) {
        this.amt = amt;
        this.gender = gender;
        this.category = category;
        this.transactionHour = transactionHour;
        this.transactionDay = transactionDay;
        this.age = age;
        this.city = city;
        this.cityPop = cityPop;
    }

    public double getAmt() { return amt; }
    public String getGender() { return gender; }
    public String getCategory() { return category; }
    public int getTransactionHour() { return transactionHour; }
    public int getTransactionDay() { return transactionDay; }
    public int getAge() { return age; }
    public String getCity() { return city; }
    public long getCityPop() { return cityPop; }
}
