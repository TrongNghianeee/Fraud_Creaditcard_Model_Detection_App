package com.example.mobile_app;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;

import java.util.ArrayList;
import java.util.List;

public class HistoryRepository {
    private final HistoryDbHelper dbHelper;

    public HistoryRepository(Context context) {
        this.dbHelper = new HistoryDbHelper(context.getApplicationContext());
    }

    public void insert(HistoryItem item) {
        SQLiteDatabase db = dbHelper.getWritableDatabase();
        ContentValues values = new ContentValues();
        values.put(HistoryDbHelper.COL_CHECKED_AT, item.checkedAt);
        values.put(HistoryDbHelper.COL_AMT, item.amt);
        values.put(HistoryDbHelper.COL_IS_FRAUD, item.isFraud ? 1 : 0);
        values.put(HistoryDbHelper.COL_FRAUD_PROB, item.fraudProbability);
        values.put(HistoryDbHelper.COL_CATEGORY, item.category);
        values.put(HistoryDbHelper.COL_GENDER, item.gender);
        values.put(HistoryDbHelper.COL_TX_TIME, item.transactionTime);
        values.put(HistoryDbHelper.COL_TX_DAY, item.transactionDay);
        values.put(HistoryDbHelper.COL_CITY, item.city);
        values.put(HistoryDbHelper.COL_AGE, item.age);
        values.put(HistoryDbHelper.COL_RISK_LEVEL, item.riskLevel);
        db.insert(HistoryDbHelper.TABLE, null, values);
        db.close();
    }

    public List<HistoryItem> getAllDesc() {
        SQLiteDatabase db = dbHelper.getReadableDatabase();
        List<HistoryItem> list = new ArrayList<>();
        Cursor cursor = db.query(HistoryDbHelper.TABLE, null, null, null, null, null,
                HistoryDbHelper.COL_CHECKED_AT + " DESC");
        if (cursor != null) {
            while (cursor.moveToNext()) {
                HistoryItem item = new HistoryItem();
                item.id = cursor.getLong(cursor.getColumnIndexOrThrow(HistoryDbHelper.COL_ID));
                item.checkedAt = cursor.getLong(cursor.getColumnIndexOrThrow(HistoryDbHelper.COL_CHECKED_AT));
                item.amt = cursor.getDouble(cursor.getColumnIndexOrThrow(HistoryDbHelper.COL_AMT));
                item.isFraud = cursor.getInt(cursor.getColumnIndexOrThrow(HistoryDbHelper.COL_IS_FRAUD)) == 1;
                item.fraudProbability = cursor.getDouble(cursor.getColumnIndexOrThrow(HistoryDbHelper.COL_FRAUD_PROB));
                item.category = cursor.getString(cursor.getColumnIndexOrThrow(HistoryDbHelper.COL_CATEGORY));
                item.gender = cursor.getString(cursor.getColumnIndexOrThrow(HistoryDbHelper.COL_GENDER));
                item.transactionTime = cursor.getString(cursor.getColumnIndexOrThrow(HistoryDbHelper.COL_TX_TIME));
                if (!cursor.isNull(cursor.getColumnIndexOrThrow(HistoryDbHelper.COL_TX_DAY))) {
                    item.transactionDay = cursor.getInt(cursor.getColumnIndexOrThrow(HistoryDbHelper.COL_TX_DAY));
                }
                item.city = cursor.getString(cursor.getColumnIndexOrThrow(HistoryDbHelper.COL_CITY));
                if (!cursor.isNull(cursor.getColumnIndexOrThrow(HistoryDbHelper.COL_AGE))) {
                    item.age = cursor.getInt(cursor.getColumnIndexOrThrow(HistoryDbHelper.COL_AGE));
                }
                item.riskLevel = cursor.getString(cursor.getColumnIndexOrThrow(HistoryDbHelper.COL_RISK_LEVEL));
                list.add(item);
            }
            cursor.close();
        }
        db.close();
        return list;
    }
}
