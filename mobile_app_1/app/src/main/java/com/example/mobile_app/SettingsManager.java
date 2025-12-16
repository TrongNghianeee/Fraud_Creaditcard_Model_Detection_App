package com.example.mobile_app;

import android.content.Context;
import android.content.SharedPreferences;

public class SettingsManager {
    private static final String PREF_NAME = "fraud_settings";
    private static final String KEY_GENDER = "default_gender";
    private static final String KEY_CITY = "default_city";
    private static final String KEY_AGE = "default_age";

    private static SharedPreferences prefs(Context context) {
        return context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
    }

    public static void saveDefaults(Context context, String gender, String city, int age) {
        prefs(context).edit()
                .putString(KEY_GENDER, gender)
                .putString(KEY_CITY, city)
                .putInt(KEY_AGE, age)
                .apply();
    }

    public static String getDefaultGender(Context context) {
        return prefs(context).getString(KEY_GENDER, null);
    }

    public static String getDefaultCity(Context context) {
        return prefs(context).getString(KEY_CITY, null);
    }

    public static Integer getDefaultAge(Context context) {
        if (!prefs(context).contains(KEY_AGE)) return null;
        return prefs(context).getInt(KEY_AGE, 18);
    }
}
