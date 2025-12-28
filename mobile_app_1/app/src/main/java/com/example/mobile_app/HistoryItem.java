package com.example.mobile_app;

public class HistoryItem {
    public long id;
    public long checkedAt;
    public double amt;
    public boolean isFraud;
    public double fraudProbability;
    public String category;
    public String gender;
    public String transactionTime;
    public Integer transactionDay;
    public String city;
    public Integer age;
    public String riskLevel;
    // Only stored when isFraud=true and backend returned AI explanation
    public String aiExplanation;
}
