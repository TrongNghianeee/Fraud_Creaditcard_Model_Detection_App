package com.example.mobile_app;

import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

public class HistoryDbHelper extends SQLiteOpenHelper {
    public static final String DB_NAME = "fraud_history.db";
    private static final int DB_VERSION = 1;

    public static final String TABLE = "history";
    public static final String COL_ID = "id";
    public static final String COL_CHECKED_AT = "checked_at"; // epoch millis
    public static final String COL_AMT = "amt";
    public static final String COL_IS_FRAUD = "is_fraud";
    public static final String COL_FRAUD_PROB = "fraud_probability";
    public static final String COL_CATEGORY = "category";
    public static final String COL_GENDER = "gender";
    public static final String COL_TX_TIME = "transaction_time";
    public static final String COL_TX_DAY = "transaction_day";
    public static final String COL_CITY = "city";
    public static final String COL_AGE = "age";
    public static final String COL_RISK_LEVEL = "risk_level";

    public HistoryDbHelper(Context context) {
        super(context, DB_NAME, null, DB_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        String sql = "CREATE TABLE " + TABLE + " (" +
                COL_ID + " INTEGER PRIMARY KEY AUTOINCREMENT, " +
                COL_CHECKED_AT + " INTEGER NOT NULL, " +
                COL_AMT + " REAL NOT NULL, " +
                COL_IS_FRAUD + " INTEGER NOT NULL, " +
                COL_FRAUD_PROB + " REAL, " +
                COL_CATEGORY + " TEXT, " +
                COL_GENDER + " TEXT, " +
                COL_TX_TIME + " TEXT, " +
                COL_TX_DAY + " INTEGER, " +
                COL_CITY + " TEXT, " +
                COL_AGE + " INTEGER, " +
                COL_RISK_LEVEL + " TEXT" +
                ");";
        db.execSQL(sql);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS " + TABLE);
        onCreate(db);
    }
}
