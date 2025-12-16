package com.example.mobile_app;

import com.google.gson.annotations.SerializedName;

/**
 * Response model for fraud detection endpoint (NEW API)
 */
public class FraudResponse {

    @SerializedName("success")
    private boolean success;

    @SerializedName("error")
    private String error;

    @SerializedName("prediction")
    private FraudPrediction prediction;

    @SerializedName("input")
    private FraudInputData input;  // Converted input data

    public boolean isSuccess() {
        return success;
    }

    public String getError() {
        return error;
    }

    public FraudPrediction getPrediction() {
        return prediction;
    }

    public FraudInputData getInput() {
        return input;
    }

    /**
     * Inner class for converted input data
     */
    public static class FraudInputData {
        @SerializedName("amt_vnd")
        private double amtVnd;

        @SerializedName("amt_usd")
        private double amtUsd;

        @SerializedName("gender")
        private String gender;

        @SerializedName("category")
        private String category;

        @SerializedName("transaction_time")
        private String transactionTime;

    @SerializedName("transaction_hour")
    private Integer transactionHour;

    @SerializedName("transaction_day")
    private Integer transactionDay;

    @SerializedName("transaction_month")
    private Integer transactionMonth;

    @SerializedName("age")
    private Integer age;

    @SerializedName("city")
    private String city;

    @SerializedName("city_pop")
    private Long cityPop;

        public double getAmtVnd() { return amtVnd; }
        public double getAmtUsd() { return amtUsd; }
        public String getGender() { return gender; }
        public String getCategory() { return category; }
        public String getTransactionTime() { return transactionTime; }
        public Integer getTransactionHour() { return transactionHour; }
        public Integer getTransactionDay() { return transactionDay; }
        public Integer getTransactionMonth() { return transactionMonth; }
        public Integer getAge() { return age; }
        public String getCity() { return city; }
        public Long getCityPop() { return cityPop; }
    }
}
