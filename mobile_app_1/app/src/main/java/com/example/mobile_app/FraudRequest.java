package com.example.mobile_app;

import com.google.gson.annotations.SerializedName;

/**
 * Request payload for fraud detection endpoint.
 */
public class FraudRequest {

    @SerializedName("amount_usd")
    private final double amountUsd;

    @SerializedName("amount_vnd")
    private final Double amountVnd;

    public FraudRequest(double amountUsd, Double amountVnd) {
        this.amountUsd = amountUsd;
        this.amountVnd = amountVnd;
    }

    public double getAmountUsd() {
        return amountUsd;
    }

    public Double getAmountVnd() {
        return amountVnd;
    }
}
