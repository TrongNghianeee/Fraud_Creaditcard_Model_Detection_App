package com.example.mobile_app;

import com.google.gson.annotations.SerializedName;

/**
 * Response model for fraud detection endpoint.
 */
public class FraudResponse {

    @SerializedName("success")
    private boolean success;

    @SerializedName("error")
    private String error;

    @SerializedName("amount_usd")
    private Double amountUsd;

    @SerializedName("prediction")
    private FraudPrediction prediction;

    public boolean isSuccess() {
        return success;
    }

    public String getError() {
        return error;
    }

    public Double getAmountUsd() {
        return amountUsd;
    }

    public FraudPrediction getPrediction() {
        return prediction;
    }
}
