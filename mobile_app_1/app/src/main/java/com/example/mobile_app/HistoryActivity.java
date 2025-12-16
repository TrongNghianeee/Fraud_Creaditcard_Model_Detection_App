package com.example.mobile_app;

import android.content.Intent;
import android.os.Bundle;
import android.widget.AdapterView;
import android.widget.ImageButton;
import android.widget.ListView;
import android.widget.TextView;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import java.util.List;

public class HistoryActivity extends AppCompatActivity {
    private ListView listView;
    private TextView emptyView;
    private HistoryRepository repository;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_history);

        listView = findViewById(R.id.historyList);
        emptyView = findViewById(R.id.emptyView);
        repository = new HistoryRepository(this);

        ImageButton btnBackHome = findViewById(R.id.btnBackHome);
        btnBackHome.setOnClickListener(v -> {
            Intent intent = new Intent(this, MainActivity.class);
            intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);
            startActivity(intent);
            finish();
        });

        loadData();
    }

    private void loadData() {
        List<HistoryItem> items = repository.getAllDesc();
        if (items.isEmpty()) {
            listView.setEmptyView(emptyView);
        }
        HistoryAdapter adapter = new HistoryAdapter(this, items);
        listView.setAdapter(adapter);

        listView.setOnItemClickListener((AdapterView<?> parent, android.view.View view, int position, long id) -> {
            HistoryItem item = items.get(position);
            showDetail(item);
        });
    }

    private void showDetail(HistoryItem item) {
        StringBuilder sb = new StringBuilder();
        sb.append("Số tiền: ").append(item.amt).append(" VND\n");
        sb.append("Fraud: ").append(item.isFraud ? "Có" : "Không").append(" (" + Math.round(item.fraudProbability * 100) + "%)\n");
        sb.append("Thời gian giao dịch: ").append(item.transactionTime != null ? item.transactionTime : "-").append("\n");
        sb.append("Ngày trong tuần: ").append(item.transactionDay != null ? item.transactionDay : "-").append("\n");
        sb.append("Giới tính: ").append(item.gender != null ? item.gender : "-").append("\n");
        sb.append("Loại: ").append(item.category != null ? item.category : "-").append("\n");
        sb.append("Tỉnh/TP: ").append(item.city != null ? item.city : "-").append("\n");
        sb.append("Tuổi: ").append(item.age != null ? item.age : "-").append("\n");
        sb.append("Risk level: ").append(item.riskLevel != null ? item.riskLevel : "-");

        new AlertDialog.Builder(this)
                .setTitle("Chi tiết giao dịch")
                .setMessage(sb.toString())
                .setPositiveButton("Đóng", null)
                .show();
    }
}
