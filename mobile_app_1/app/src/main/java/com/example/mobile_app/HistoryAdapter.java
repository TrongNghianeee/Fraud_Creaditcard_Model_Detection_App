package com.example.mobile_app;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.core.content.ContextCompat;

import java.text.NumberFormat;
import java.text.SimpleDateFormat;
import java.util.List;
import java.util.Locale;

public class HistoryAdapter extends BaseAdapter {
    private final List<HistoryItem> items;
    private final LayoutInflater inflater;
    private final NumberFormat currencyFormat = NumberFormat.getInstance(new Locale("vi", "VN"));
    private final SimpleDateFormat dateTimeFormat = new SimpleDateFormat("dd/MM/yyyy HH:mm:ss", Locale.getDefault());
    private final Context context;

    public HistoryAdapter(Context context, List<HistoryItem> items) {
        this.context = context;
        this.items = items;
        this.inflater = LayoutInflater.from(context);
    }

    @Override
    public int getCount() {
        return items.size();
    }

    @Override
    public Object getItem(int position) {
        return items.get(position);
    }

    @Override
    public long getItemId(int position) {
        return items.get(position).id;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        ViewHolder holder;
        if (convertView == null) {
            convertView = inflater.inflate(R.layout.item_history, parent, false);
            holder = new ViewHolder();
            holder.txtAmount = convertView.findViewById(R.id.txtAmount);
            holder.txtDate = convertView.findViewById(R.id.txtDate);
            holder.txtShield = convertView.findViewById(R.id.txtShield);
            holder.iconShield = convertView.findViewById(R.id.iconShield);
            convertView.setTag(holder);
        } else {
            holder = (ViewHolder) convertView.getTag();
        }

        HistoryItem item = items.get(position);
        holder.txtAmount.setText(currencyFormat.format(item.amt) + " VND");
        holder.txtDate.setText(dateTimeFormat.format(item.checkedAt));

        int percent = (int) Math.round(item.fraudProbability * 100);
        holder.txtShield.setText(percent + "%");

        int color = ContextCompat.getColor(context, item.isFraud ? R.color.error : R.color.success);
        convertView.setBackgroundColor(color);
        holder.iconShield.setColorFilter(ContextCompat.getColor(context, android.R.color.white));
        holder.txtShield.setTextColor(ContextCompat.getColor(context, android.R.color.white));
        holder.txtAmount.setTextColor(ContextCompat.getColor(context, android.R.color.white));
        holder.txtDate.setTextColor(ContextCompat.getColor(context, android.R.color.white));

        return convertView;
    }

    static class ViewHolder {
        TextView txtAmount;
        TextView txtDate;
        TextView txtShield;
        ImageView iconShield;
    }
}
