# ✅ NGROK SETUP HOÀN TẤT!

## 🎉 **TRẠNG THÁI HIỆN TẠI:**

### **Ngrok:**
- ✅ Status: **Online**
- ✅ Account: vonghia9a5@gmail.com (Free Plan)
- ✅ Region: Asia Pacific
- ✅ Public URL: `https://forgettable-prehistorically-leonard.ngrok-free.dev`
- ✅ Forwarding to: `http://localhost:5000`
- ✅ Web Interface: http://127.0.0.1:4040

### **Android App:**
- ✅ BASE_URL đã cập nhật: `https://forgettable-prehistorically-leonard.ngrok-free.dev/`

---

## 🧪 **TEST NGAY TRÊN ĐIỆN THOẠI:**

### **1. Test kết nối:**
Mở Chrome trên điện thoại, truy cập:
```
https://forgettable-prehistorically-leonard.ngrok-free.dev/health
```

**Kết quả mong đợi:**
```json
{"status":"ok","message":"Fraud Detection API is running"}
```

⚠️ **Lần đầu tiên** bạn sẽ thấy cảnh báo ngrok:
```
You are about to visit: forgettable-prehistorically-leonard.ngrok-free.dev
This site is served for free through ngrok.com
```
→ Click **"Visit Site"** để tiếp tục

---

## 📱 **BUILD & RUN ANDROID APP:**

### **Bước 1: Sync Gradle**
Trong Android Studio:
1. Click **File → Sync Project with Gradle Files**
2. Hoặc click biểu tượng 🐘 trên toolbar
3. Đợi sync hoàn tất

### **Bước 2: Rebuild Project**
1. Click **Build → Rebuild Project**
2. Đợi build xong (không có lỗi)

### **Bước 3: Run App**
1. Kết nối điện thoại qua USB (hoặc dùng emulator)
2. Bật **USB Debugging** trên điện thoại
3. Click **Run** ▶️ trong Android Studio
4. Chọn thiết bị
5. Đợi app cài đặt và mở

### **Bước 4: Test Upload**
1. Tap nút **"📷 Select Image"**
2. Chọn ảnh giao dịch ngân hàng
3. Tap nút **"🔍 Analyze Transaction"**
4. Đợi kết quả (khoảng 5-10 giây)
5. Xem thông tin giao dịch được phân tích! 🎉

---

## 🔄 **KHI KHỞI ĐỘNG LẠI:**

### **Mỗi lần làm việc, cần chạy:**

**Terminal 1 - Flask:**
```powershell
python run.py
```

**Terminal 2 - Ngrok:**
```powershell
.\ngrok http 5000
```

⚠️ **LƯU Ý:** Với **Free plan**, ngrok URL sẽ **THAY ĐỔI** mỗi lần khởi động lại!

**Ví dụ:**
- Lần này: `https://forgettable-prehistorically-leonard.ngrok-free.dev`
- Lần sau: `https://another-random-name.ngrok-free.dev` (khác!)

→ Phải cập nhật lại `ApiClient.java` và rebuild app!

---

## 💡 **GIẢI PHÁP URL CỐ ĐỊNH:**

### **Option 1: Giữ ngrok chạy mãi (Free)**
- Không tắt ngrok → URL không đổi
- Nhược điểm: Máy tính phải bật 24/7

### **Option 2: Upgrade ngrok Pro ($8/tháng)**
- URL cố định mãi mãi: `your-app.ngrok.io`
- Không cần cập nhật code mỗi lần
- Link: https://ngrok.com/pricing

### **Option 3: Deploy lên cloud (FREE)**
- Render.com (free tier)
- Railway.app (free tier)
- Fly.io (free tier)
- URL cố định, không cần chạy máy tính

---

## 🌐 **NGROK WEB INTERFACE:**

Bạn có thể xem **real-time requests** tại:
```
http://127.0.0.1:4040
```

Mở trình duyệt trên máy tính để thấy:
- Tất cả requests từ Android app
- Request/Response details
- Timing information
- Debugging logs

**Rất hữu ích để debug!** 🔍

---

## ✅ **CHECKLIST:**

- [x] Ngrok authtoken đã setup
- [x] Ngrok đang chạy
- [x] Flask server đang chạy
- [x] ApiClient.java đã cập nhật URL
- [ ] **Gradle sync** (cần làm)
- [ ] **Rebuild project** (cần làm)
- [ ] **Run app** (cần làm)
- [ ] **Test upload ảnh** (cần làm)

---

## 🆘 **TROUBLESHOOTING:**

### **Lỗi: "Visit Site" warning**
- Bình thường với Free plan
- Click "Visit Site" để tiếp tục
- Chỉ hiện lần đầu mỗi session

### **Lỗi: "Tunnel not found"**
- Ngrok đã tắt hoặc restart
- URL đã thay đổi
- Chạy lại `.\ngrok http 5000` và cập nhật URL mới

### **Lỗi: "ERR_CONNECTION_REFUSED"**
- Flask chưa chạy
- Chạy `python run.py` trước

### **App vẫn timeout:**
- Kiểm tra Flask có đang chạy không
- Kiểm tra ngrok có đang chạy không
- Rebuild app sau khi đổi URL

---

## 🎯 **BƯỚC TIẾP THEO:**

1. ✅ Mở Android Studio
2. ✅ Sync Project with Gradle Files
3. ✅ Rebuild Project
4. ✅ Run app trên điện thoại
5. ✅ Test upload ảnh giao dịch
6. 🎉 Thành công!

---

**Chúc may mắn! 🚀**
