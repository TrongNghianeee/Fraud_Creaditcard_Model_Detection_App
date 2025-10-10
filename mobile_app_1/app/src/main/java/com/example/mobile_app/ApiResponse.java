package com.example.mobile_app;

import com.google.gson.annotations.SerializedName;

/**
 * API Response Model
 */
public class ApiResponse {

    @SerializedName("success")
    private boolean success;

    @SerializedName("transaction")
    private TransactionData transaction;

    @SerializedName("ocr_confidence")
    private String ocrConfidence;

    @SerializedName("processing_time")
    private String processingTime;

    @SerializedName("ai_parsing_success")
    private boolean aiParsingSuccess;

    @SerializedName("ai_error")
    private String aiError;

    @SerializedName("error")
    private String error;

    // Getters
    public boolean isSuccess() { return success; }
    public TransactionData getTransaction() { return transaction; }
    public String getOcrConfidence() { return ocrConfidence; }
    public String getProcessingTime() { return processingTime; }
    public boolean isAiParsingSuccess() { return aiParsingSuccess; }
    public String getAiError() { return aiError; }
    public String getError() { return error; }

    // Setters
    public void setSuccess(boolean success) { this.success = success; }
    public void setTransaction(TransactionData transaction) { this.transaction = transaction; }
    public void setOcrConfidence(String ocrConfidence) { this.ocrConfidence = ocrConfidence; }
    public void setProcessingTime(String processingTime) { this.processingTime = processingTime; }
    public void setAiParsingSuccess(boolean aiParsingSuccess) { this.aiParsingSuccess = aiParsingSuccess; }
    public void setAiError(String aiError) { this.aiError = aiError; }
    public void setError(String error) { this.error = error; }
}
