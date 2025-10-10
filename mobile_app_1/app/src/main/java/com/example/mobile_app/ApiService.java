package com.example.mobile_app;

import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import retrofit2.Call;
import retrofit2.http.Multipart;
import retrofit2.http.POST;
import retrofit2.http.Part;

/**
 * API Service - Retrofit interface
 */
public interface ApiService {

    /**
     * Extract and parse transaction from image
     * 
     * @param file Image file (multipart)
     * @param language OCR language (default: "vie+eng")
     * @return API Response with transaction data
     */
    @Multipart
    @POST("api/preprocess/extract-and-parse")
    Call<ApiResponse> extractAndParse(
            @Part MultipartBody.Part file,
            @Part("language") RequestBody language
    );
}
