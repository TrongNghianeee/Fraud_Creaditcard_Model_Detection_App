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
    private Double ocrConfidence;  // Changed to Double to accept number from backend

    @SerializedName("processing_time")
    private Double processingTime;  // Changed to Double to accept number from backend

    @SerializedName("ai_parsing_success")
    private boolean aiParsingSuccess;

    @SerializedName("ai_error")
    private String aiError;
    
    @SerializedName("ocr_text")
    private String ocrText;  // OCR text when AI parsing fails

    @SerializedName("error")
    private String error;

    // Getters
    public boolean isSuccess() { return success; }
    public TransactionData getTransaction() { return transaction; }
    public String getOcrConfidence() { 
        return ocrConfidence != null ? String.valueOf(ocrConfidence) : "0"; 
    }
    public String getProcessingTime() { 
        return processingTime != null ? String.valueOf(processingTime) : "0"; 
    }
    public boolean isAiParsingSuccess() { return aiParsingSuccess; }
    public String getAiError() { return aiError; }
    public String getOcrText() { return ocrText; }
    public String getError() { return error; }

    // Setters
    public void setSuccess(boolean success) { this.success = success; }
    public void setTransaction(TransactionData transaction) { this.transaction = transaction; }
    public void setOcrConfidence(Double ocrConfidence) { this.ocrConfidence = ocrConfidence; }
    public void setProcessingTime(Double processingTime) { this.processingTime = processingTime; }
    public void setAiParsingSuccess(boolean aiParsingSuccess) { this.aiParsingSuccess = aiParsingSuccess; }
    public void setAiError(String aiError) { this.aiError = aiError; }
    public void setOcrText(String ocrText) { this.ocrText = ocrText; }
    public void setError(String error) { this.error = error; }
}
