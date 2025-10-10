package com.example.mobile_app;

import java.util.concurrent.TimeUnit;

import okhttp3.OkHttpClient;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

/**
 * API Client - Singleton Retrofit instance
 */
public class ApiClient {

    // Flask server URL via ngrok
    // NGROK URL (works everywhere - WiFi, 4G, 5G)
    // Note: This URL changes every time you restart ngrok (Free plan)
    // Current ngrok URL: https://forgettable-prehistorically-leonard.ngrok-free.dev
    private static final String BASE_URL = "https://forgettable-prehistorically-leonard.ngrok-free.dev/";

    private static Retrofit retrofit = null;
    private static ApiService apiService = null;

    /**
     * Get Retrofit instance
     */
    public static Retrofit getRetrofitInstance() {
        if (retrofit == null) {
            // Logging interceptor for debugging
            HttpLoggingInterceptor loggingInterceptor = new HttpLoggingInterceptor();
            loggingInterceptor.setLevel(HttpLoggingInterceptor.Level.BODY);

            // OkHttpClient with timeout settings
            OkHttpClient okHttpClient = new OkHttpClient.Builder()
                    .connectTimeout(60, TimeUnit.SECONDS)
                    .readTimeout(60, TimeUnit.SECONDS)
                    .writeTimeout(60, TimeUnit.SECONDS)
                    .addInterceptor(loggingInterceptor)
                    .build();

            // Build Retrofit instance
            retrofit = new Retrofit.Builder()
                    .baseUrl(BASE_URL)
                    .client(okHttpClient)
                    .addConverterFactory(GsonConverterFactory.create())
                    .build();
        }
        return retrofit;
    }

    /**
     * Get API Service
     */
    public static ApiService getApiService() {
        if (apiService == null) {
            apiService = getRetrofitInstance().create(ApiService.class);
        }
        return apiService;
    }

    /**
     * Reset instance (useful for testing or changing BASE_URL)
     */
    public static void resetInstance() {
        retrofit = null;
        apiService = null;
    }
}
