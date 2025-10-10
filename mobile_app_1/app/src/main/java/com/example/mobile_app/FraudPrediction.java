package com.example.mobile_app;

import com.google.gson.annotations.SerializedName;

/**
 * Model representing fraud prediction details.
 */
public class FraudPrediction {

    @SerializedName("is_fraud")
    private boolean isFraud;

    @SerializedName("fraud_probability")
    private double fraudProbability;

    @SerializedName("confidence")
    private String confidence;

    @SerializedName("risk_level")
    private String riskLevel;

    public boolean isFraud() {
        return isFraud;
    }

    public double getFraudProbability() {
        return fraudProbability;
    }

    public String getConfidence() {
        return confidence;
    }

    public String getRiskLevel() {
        return riskLevel;
    }
}
