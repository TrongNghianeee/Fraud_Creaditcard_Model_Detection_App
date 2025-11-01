package com.example.mobile_app;

import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.Multipart;
import retrofit2.http.POST;
import retrofit2.http.Part;

/**
 * API Service - Retrofit interface (Updated for new APIs)
 */
public interface ApiService {

    /**
     * Extract and parse transaction from image (OCR + Gemini AI)
     * Returns 4 fields: amt, gender, category, transaction_time
     * 
     * @param file Image file (multipart)
     * @param language OCR language (default: "vie+eng")
     * @return API Response with transaction data (4 fields)
     */
    @Multipart
    @POST("api/preprocess/extract-and-parse")
    Call<ApiResponse> extractAndParse(
            @Part MultipartBody.Part file,
            @Part("language") RequestBody language
    );

    /**
     * Predict fraud based on 4 parameters (NEW API)
     * Input: amt (VND), gender (Nam/Nữ), category (VN), transaction_time (HH:MM:SS)
     *
     * @param request request body containing 4 fields
     * @return fraud prediction response
     */
    @POST("api/model/predict-fraud")
    Call<FraudResponse> predictFraud(@Body FraudRequest request);
}
