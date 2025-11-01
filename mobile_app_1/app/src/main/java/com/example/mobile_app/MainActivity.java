package com.example.mobile_app;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.provider.OpenableColumns;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;

import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * Main Activity - Upload and scan transaction image
 */
public class MainActivity extends AppCompatActivity {

    private static final String TAG = "MainActivity";
    private static final int PERMISSION_REQUEST_CODE = 100;

    // UI Components
    private ImageView imagePreview;
    private TextView textPlaceholder;
    private Button btnUpload;
    private Button btnAnalyze;
    private Button btnViewResults;
    private ProgressBar progressBar;
    private TextView textStatus;

    // Selected image URI
    private Uri selectedImageUri;
    
    // Extracted data from OCR
    private String extractedAmt;
    private String extractedGender;
    private String extractedCategory;
    private String extractedTransactionTime;

    // Activity launcher for image picker
    private ActivityResultLauncher<Intent> imagePickerLauncher;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Initialize UI components
        initViews();

        // Setup image picker launcher
        setupImagePickerLauncher();

        // Request permissions
        checkPermissions();

        // Setup click listeners
        setupClickListeners();
    }

    /**
     * Initialize all UI components
     */
    private void initViews() {
        imagePreview = findViewById(R.id.imagePreview);
        textPlaceholder = findViewById(R.id.textPlaceholder);
        btnUpload = findViewById(R.id.btnUpload);
        btnAnalyze = findViewById(R.id.btnAnalyze);
        btnViewResults = findViewById(R.id.btnViewResults);
        progressBar = findViewById(R.id.progressBar);
        textStatus = findViewById(R.id.textStatus);

        // Initially disable buttons
        btnAnalyze.setEnabled(false);
        btnViewResults.setEnabled(false);
    }

    /**
     * Setup image picker result launcher
     */
    private void setupImagePickerLauncher() {
        imagePickerLauncher = registerForActivityResult(
                new ActivityResultContracts.StartActivityForResult(),
                result -> {
                    if (result.getResultCode() == Activity.RESULT_OK) {
                        Intent data = result.getData();
                        if (data != null && data.getData() != null) {
                            selectedImageUri = data.getData();
                            displayImage(selectedImageUri);
                            btnAnalyze.setEnabled(true);
                            textStatus.setText("Ảnh đã sẵn sàng. Nhấn 'Phân tích giao dịch'");
                        }
                    }
                }
        );
    }

    /**
     * Setup button click listeners
     */
    private void setupClickListeners() {
        btnUpload.setOnClickListener(v -> openImagePicker());
        btnAnalyze.setOnClickListener(v -> uploadAndScan());
        btnViewResults.setOnClickListener(v -> navigateToFormActivity());
    }

    /**
     * Check and request necessary permissions
     */
    private void checkPermissions() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.READ_EXTERNAL_STORAGE},
                    PERMISSION_REQUEST_CODE);
        }
    }

    /**
     * Open image picker
     */
    private void openImagePicker() {
        Intent intent = new Intent(Intent.ACTION_PICK);
        intent.setType("image/*");
        imagePickerLauncher.launch(intent);
    }

    /**
     * Display selected image in ImageView
     */
    private void displayImage(Uri imageUri) {
        try {
            InputStream inputStream = getContentResolver().openInputStream(imageUri);
            Bitmap bitmap = BitmapFactory.decodeStream(inputStream);
            imagePreview.setImageBitmap(bitmap);
            imagePreview.setVisibility(View.VISIBLE);
            textPlaceholder.setVisibility(View.GONE);
        } catch (IOException e) {
            Log.e(TAG, "Error loading image: " + e.getMessage());
            Toast.makeText(this, "Lỗi khi tải ảnh", Toast.LENGTH_SHORT).show();
            textPlaceholder.setVisibility(View.VISIBLE);
        }
    }

    /**
     * Upload image and scan transaction
     */
    private void uploadAndScan() {
        if (selectedImageUri == null) {
            Toast.makeText(this, "Vui lòng chọn ảnh trước", Toast.LENGTH_SHORT).show();
            textPlaceholder.setVisibility(View.VISIBLE);
            return;
        }

        // Show loading
        showLoading(true);
        textStatus.setText("Đang xử lý... Bước 1/2: OCR");

        try {
            // Convert URI to File
            File imageFile = getFileFromUri(selectedImageUri);
            
            // Create RequestBody for file
            RequestBody requestFile = RequestBody.create(
                    MediaType.parse(getContentResolver().getType(selectedImageUri)),
                    imageFile
            );

            // Create MultipartBody.Part
            MultipartBody.Part body = MultipartBody.Part.createFormData(
                    "file",
                    imageFile.getName(),
                    requestFile
            );

            // Create RequestBody for language parameter
            RequestBody language = RequestBody.create(
                    MediaType.parse("text/plain"),
                    "vie+eng"
            );

            // Call API
            ApiService apiService = ApiClient.getApiService();
            Call<ApiResponse> call = apiService.extractAndParse(body, language);

            call.enqueue(new Callback<ApiResponse>() {
                @Override
                public void onResponse(Call<ApiResponse> call, Response<ApiResponse> response) {
                    showLoading(false);
                    
                    Log.d(TAG, "API Response received - Code: " + response.code());

                    try {
                        if (response.isSuccessful() && response.body() != null) {
                            ApiResponse apiResponse = response.body();
                            
                            Log.d(TAG, "Response body received - success: " + apiResponse.isSuccess());
                            Log.d(TAG, "AI parsing success: " + apiResponse.isAiParsingSuccess());
                            Log.d(TAG, "Transaction is null: " + (apiResponse.getTransaction() == null));

                            if (apiResponse.isSuccess() && apiResponse.isAiParsingSuccess()) {
                                // Success - navigate to FormActivity
                                Log.d(TAG, "CASE 1: Both OCR and AI parsing succeeded");
                                textStatus.setText("✓ Phân tích thành công!");
                                
                                // Save extracted data and enable "View Results" button
                                saveExtractedData(apiResponse);
                                btnViewResults.setEnabled(true);
                                
                                navigateToFormActivity(apiResponse);
                            } else if (apiResponse.isSuccess()) {
                                // OCR success but AI parsing failed - still allow user to continue
                                Log.d(TAG, "CASE 2: OCR succeeded, AI parsing failed");
                                String errorMsg = "OCR thành công nhưng AI không thể phân tích. Bạn có thể nhập thủ công.";
                                textStatus.setText(errorMsg);
                                Toast.makeText(MainActivity.this, errorMsg, Toast.LENGTH_LONG).show();
                                
                                // Log AI error for debugging
                                if (apiResponse.getAiError() != null) {
                                    Log.e(TAG, "AI parsing error: " + apiResponse.getAiError());
                                }
                                if (apiResponse.getOcrText() != null) {
                                    Log.d(TAG, "OCR text extracted: " + apiResponse.getOcrText());
                                }
                                
                                // Save extracted data and enable "View Results" button
                                saveExtractedData(apiResponse);
                                btnViewResults.setEnabled(true);
                                
                                // Still navigate to FormActivity for manual input
                                navigateToFormActivity(apiResponse);
                            } else {
                                // Both failed
                                Log.d(TAG, "CASE 3: Both OCR and AI parsing failed");
                                String errorMsg = apiResponse.getError() != null ?
                                        apiResponse.getError() : "Có lỗi xảy ra";
                                textStatus.setText("✗ " + errorMsg);
                                Toast.makeText(MainActivity.this, errorMsg, Toast.LENGTH_LONG).show();
                            }
                        } else {
                            Log.e(TAG, "Response not successful or body is null");
                            textStatus.setText("✗ Lỗi kết nối API");
                            Toast.makeText(MainActivity.this,
                                    "Lỗi: " + response.code(), Toast.LENGTH_SHORT).show();
                        }
                    } catch (Exception e) {
                        Log.e(TAG, "CRASH in onResponse: " + e.getMessage(), e);
                        Toast.makeText(MainActivity.this, 
                                "Lỗi xử lý response: " + e.getMessage(), Toast.LENGTH_LONG).show();
                        textStatus.setText("✗ Lỗi xử lý dữ liệu");
                    }
                }

                @Override
                public void onFailure(Call<ApiResponse> call, Throwable t) {
                    showLoading(false);
                    textStatus.setText("✗ Không thể kết nối đến server");
                    Toast.makeText(MainActivity.this,
                            "Lỗi kết nối: " + t.getMessage(), Toast.LENGTH_LONG).show();
                    Log.e(TAG, "API Error: " + t.getMessage(), t);
                }
            });

        } catch (IOException e) {
            showLoading(false);
            textStatus.setText("✗ Lỗi đọc file ảnh");
            Toast.makeText(this, "Lỗi: " + e.getMessage(), Toast.LENGTH_SHORT).show();
            Log.e(TAG, "File error: " + e.getMessage(), e);
        }
    }

    /**
     * Convert URI to File
     */
    private File getFileFromUri(Uri uri) throws IOException {
        InputStream inputStream = getContentResolver().openInputStream(uri);
        String fileName = getFileName(uri);
        
        File tempFile = new File(getCacheDir(), fileName);
        FileOutputStream outputStream = new FileOutputStream(tempFile);

        byte[] buffer = new byte[4096];
        int bytesRead;
        while ((bytesRead = inputStream.read(buffer)) != -1) {
            outputStream.write(buffer, 0, bytesRead);
        }

        outputStream.close();
        inputStream.close();

        return tempFile;
    }

    /**
     * Get file name from URI
     */
    private String getFileName(Uri uri) {
        String result = null;
        if (uri.getScheme().equals("content")) {
            Cursor cursor = getContentResolver().query(uri, null, null, null, null);
            try {
                if (cursor != null && cursor.moveToFirst()) {
                    int index = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                    if (index != -1) {
                        result = cursor.getString(index);
                    }
                }
            } finally {
                if (cursor != null) {
                    cursor.close();
                }
            }
        }
        if (result == null) {
            result = uri.getPath();
            int cut = result.lastIndexOf('/');
            if (cut != -1) {
                result = result.substring(cut + 1);
            }
        }
        return result;
    }

    /**
     * Show/hide loading indicator
     */
    private void showLoading(boolean show) {
        progressBar.setVisibility(show ? View.VISIBLE : View.GONE);
        btnAnalyze.setEnabled(!show);
        btnUpload.setEnabled(!show);
    }

    /**
     * Save extracted data for later use
     */
    private void saveExtractedData(ApiResponse apiResponse) {
        TransactionData transaction = apiResponse.getTransaction();
        if (transaction != null) {
            Double amtValue = transaction.getAmt();
            double amt = (amtValue != null) ? amtValue : 0.0;
            
            extractedAmt = String.valueOf(amt);
            extractedGender = (transaction.getGender() != null) ? transaction.getGender() : "";
            extractedCategory = (transaction.getCategory() != null) ? transaction.getCategory() : "";
            extractedTransactionTime = (transaction.getTransactionTime() != null) ? transaction.getTransactionTime() : "";
        } else {
            extractedAmt = "0";
            extractedGender = "";
            extractedCategory = "";
            extractedTransactionTime = "";
        }
    }

    /**
     * Navigate to FormActivity without data (user will enter manually)
     */
    private void navigateToFormActivity() {
        try {
            Log.d(TAG, "navigateToFormActivity() - no parameters");
            Intent intent = new Intent(MainActivity.this, FormActivity.class);
            
            // Pass saved extracted data if available
            if (extractedAmt != null) {
                intent.putExtra("amt", extractedAmt);
                intent.putExtra("gender", extractedGender);
                intent.putExtra("category", extractedCategory);
                intent.putExtra("transaction_time", extractedTransactionTime);
            }
            
            startActivity(intent);
        } catch (Exception e) {
            Log.e(TAG, "Error in navigateToFormActivity: " + e.getMessage(), e);
            Toast.makeText(this, "Lỗi khi chuyển màn hình: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    /**
     * Navigate to FormActivity with transaction data (4 fields only)
     */
    private void navigateToFormActivity(ApiResponse apiResponse) {
        try {
            Log.d(TAG, "navigateToFormActivity() called");
            Intent intent = new Intent(MainActivity.this, FormActivity.class);
            
            TransactionData transaction = apiResponse.getTransaction();
            Log.d(TAG, "Transaction data: " + (transaction != null ? "NOT NULL" : "NULL"));
            
            if (transaction != null) {
                // Pass only 4 fields: amt, gender, category, transaction_time
                // Safe conversion for Double to double
                Double amtValue = transaction.getAmt();
                double amt = (amtValue != null) ? amtValue : 0.0;
                
                String gender = (transaction.getGender() != null) ? transaction.getGender() : "";
                String category = (transaction.getCategory() != null) ? transaction.getCategory() : "";
                String transactionTime = (transaction.getTransactionTime() != null) ? transaction.getTransactionTime() : "";
                
                Log.d(TAG, "Parsed values - amt: " + amt + ", gender: " + gender + 
                      ", category: " + category + ", time: " + transactionTime);
                
                intent.putExtra("amt", String.valueOf(amt));  // Convert to String to avoid null issues
                intent.putExtra("gender", gender);
                intent.putExtra("category", category);
                intent.putExtra("transaction_time", transactionTime);
                
                Log.d(TAG, "Intent extras added successfully");
            } else {
                Log.w(TAG, "Transaction data is null, passing empty values");
                intent.putExtra("amt", "0");
                intent.putExtra("gender", "");
                intent.putExtra("category", "");
                intent.putExtra("transaction_time", "");
            }
            
            // Extra info
            String ocrConfidence = apiResponse.getOcrConfidence() != null ? apiResponse.getOcrConfidence() : "0";
            String processingTime = apiResponse.getProcessingTime() != null ? apiResponse.getProcessingTime() : "0";
            
            intent.putExtra("ocr_confidence", ocrConfidence);
            intent.putExtra("processing_time", processingTime);
            
            Log.d(TAG, "Starting FormActivity...");
            startActivity(intent);
            Log.d(TAG, "FormActivity started successfully");
        } catch (Exception e) {
            Log.e(TAG, "CRASH in navigateToFormActivity: " + e.getMessage(), e);
            Toast.makeText(this, "Lỗi khi chuyển màn hình: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }
}
