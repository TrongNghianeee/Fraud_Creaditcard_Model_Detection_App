package com.example.mobile_app;

import com.google.gson.annotations.SerializedName;

/**
 * Transaction Data Model
 */
public class TransactionData {

    @SerializedName("sender_name")
    private String senderName;

    @SerializedName("receiver_name")
    private String receiverName;

    @SerializedName("amount_vnd")
    private String amountVnd;

    @SerializedName("amount_usd")
    private String amountUsd;

    @SerializedName("time")
    private String time;

    @SerializedName("date")
    private String date;

    @SerializedName("transaction_content")
    private String transactionContent;

    @SerializedName("sender_bank")
    private String senderBank;

    @SerializedName("receiver_bank")
    private String receiverBank;

    @SerializedName("transaction_id")
    private String transactionId;

    @SerializedName("transaction_fee")
    private String transactionFee;

    // Getters
    public String getSenderName() { return senderName; }
    public String getReceiverName() { return receiverName; }
    public String getAmountVnd() { return amountVnd; }
    public String getAmountUsd() { return amountUsd; }
    public String getTime() { return time; }
    public String getDate() { return date; }
    public String getTransactionContent() { return transactionContent; }
    public String getSenderBank() { return senderBank; }
    public String getReceiverBank() { return receiverBank; }
    public String getTransactionId() { return transactionId; }
    public String getTransactionFee() { return transactionFee; }

    // Setters
    public void setSenderName(String senderName) { this.senderName = senderName; }
    public void setReceiverName(String receiverName) { this.receiverName = receiverName; }
    public void setAmountVnd(String amountVnd) { this.amountVnd = amountVnd; }
    public void setAmountUsd(String amountUsd) { this.amountUsd = amountUsd; }
    public void setTime(String time) { this.time = time; }
    public void setDate(String date) { this.date = date; }
    public void setTransactionContent(String transactionContent) { this.transactionContent = transactionContent; }
    public void setSenderBank(String senderBank) { this.senderBank = senderBank; }
    public void setReceiverBank(String receiverBank) { this.receiverBank = receiverBank; }
    public void setTransactionId(String transactionId) { this.transactionId = transactionId; }
    public void setTransactionFee(String transactionFee) { this.transactionFee = transactionFee; }
}
