package com.example.mobile_app;

import android.os.Bundle;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

public class SettingsActivity extends AppCompatActivity {

    private Spinner spGender;
    private Spinner spCity;
    private EditText etAge;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);

        spGender = findViewById(R.id.spDefaultGender);
        spCity = findViewById(R.id.spDefaultCity);
        etAge = findViewById(R.id.etDefaultAge);

        loadSavedValues();

        findViewById(R.id.btnSaveSettings).setOnClickListener(v -> saveSettings());
        findViewById(R.id.btnBackSettings).setOnClickListener(v -> finish());
    }

    private void loadSavedValues() {
        // Gender
        String savedGender = SettingsManager.getDefaultGender(this);
        if (savedGender != null) {
            String[] genderOptions = getResources().getStringArray(R.array.gender_options);
            for (int i = 0; i < genderOptions.length; i++) {
                if (genderOptions[i].equalsIgnoreCase(savedGender)) {
                    spGender.setSelection(i);
                    break;
                }
            }
        }
        // City
        String savedCity = SettingsManager.getDefaultCity(this);
        if (savedCity != null) {
            String[] cityOptions = getResources().getStringArray(R.array.city_options);
            for (int i = 0; i < cityOptions.length; i++) {
                if (cityOptions[i].equalsIgnoreCase(savedCity)) {
                    spCity.setSelection(i);
                    break;
                }
            }
        }
        // Age
        Integer savedAge = SettingsManager.getDefaultAge(this);
        if (savedAge != null) {
            etAge.setText(String.valueOf(savedAge));
        }
    }

    private void saveSettings() {
        String gender = spGender.getSelectedItem().toString();
        String city = spCity.getSelectedItem().toString();
        int age = 18;
        try {
            age = Integer.parseInt(etAge.getText().toString().trim());
        } catch (Exception ignored) {
        }

        if (age < 18 || age > 100) {
            Toast.makeText(this, "Tuổi phải trong khoảng 18-100", Toast.LENGTH_SHORT).show();
            return;
        }

        SettingsManager.saveDefaults(this, gender, city, age);
        Toast.makeText(this, "Đã lưu cài đặt mặc định", Toast.LENGTH_SHORT).show();
        finish();
    }
}
