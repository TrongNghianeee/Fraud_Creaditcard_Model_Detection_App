# ✅ KIỂM TRA CẤU HÌNH MOBILE_APP_1

## 📱 Android App Configuration

### 1️⃣ **API Configuration** ✅
**File:** `app/src/main/java/com/example/mobile_app/ApiClient.java`

```java
private static final String BASE_URL = "http://192.168.1.32:5000/";
```

- ✅ **Emulator**: Dùng `http://10.0.2.2:5000/`
- ✅ **Physical Device**: Dùng `http://192.168.1.32:5000/` (đang dùng)

**Timeout Settings:**
- Connect: 60 seconds ✅
- Read: 60 seconds ✅
- Write: 60 seconds ✅

---

### 2️⃣ **API Endpoint** ✅
**File:** `app/src/main/java/com/example/mobile_app/ApiService.java`

```java
@POST("api/preprocess/extract-and-parse")
Call<ApiResponse> extractAndParse(
    @Part MultipartBody.Part file,
    @Part("language") RequestBody language
);
```

✅ Endpoint đúng: `/api/preprocess/extract-and-parse`

---

### 3️⃣ **AndroidManifest.xml** ✅ (VỪA SỬA)
**File:** `app/src/main/AndroidManifest.xml`

```xml
<!-- Permissions -->
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />

<application
    android:usesCleartextTraffic="true"
    ...>
```

**Đã thêm:**
- ✅ `INTERNET` permission
- ✅ `READ_EXTERNAL_STORAGE` permission (Android 12-)
- ✅ `READ_MEDIA_IMAGES` permission (Android 13+)
- ✅ `android:usesCleartextTraffic="true"` - **QUAN TRỌNG** để dùng HTTP thay vì HTTPS
- ✅ Khai báo `FormActivity`

---

### 4️⃣ **Dependencies** ✅
**File:** `app/build.gradle`

```gradle
// Retrofit for API calls
implementation 'com.squareup.retrofit2:retrofit:2.9.0'
implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
implementation 'com.squareup.okhttp3:okhttp:4.11.0'
implementation 'com.squareup.okhttp3:logging-interceptor:4.11.0'

// Gson for JSON parsing
implementation 'com.google.code.gson:gson:2.10.1'

// Material Design
implementation 'com.google.android.material:material:1.11.0'
```

✅ Tất cả dependencies đầy đủ

---

### 5️⃣ **Package Structure** ✅
```
com.example.mobile_app/
├── MainActivity.java       ✅
├── FormActivity.java       ✅
├── ApiClient.java          ✅
├── ApiService.java         ✅
├── ApiResponse.java        ✅
└── TransactionData.java    ✅
```

---

## 🔧 CHECKLIST TRƯỚC KHI CHẠY

### Phía Server (Flask):
- [x] Flask đang chạy trên `http://192.168.1.32:5000`
- [x] Port 5000 đã mở trong Windows Firewall
- [x] Server có thể truy cập từ: `http://192.168.1.32:5000/health`

### Phía Android:
- [x] `BASE_URL` = `http://192.168.1.32:5000/`
- [x] `android:usesCleartextTraffic="true"` đã thêm ✅ **VỪA SỬA**
- [x] Permissions đã khai báo đầy đủ ✅ **VỪA SỬA**
- [x] Dependencies đã đầy đủ
- [ ] **Gradle sync thành công** (cần làm)
- [ ] **Build thành công** (cần làm)

### Mạng:
- [ ] Điện thoại và máy tính **CÙNG WiFi**
- [ ] IP điện thoại có dạng `192.168.1.xxx`

---

## 🚀 BƯỚC TIẾP THEO

### 1. Sync Gradle (BẮT BUỘC)
Trong Android Studio:
1. Click **File → Sync Project with Gradle Files**
2. Hoặc click biểu tượng 🐘 trên toolbar
3. Đợi sync hoàn tất

### 2. Build Project
1. Click **Build → Rebuild Project**
2. Đợi build xong không lỗi

### 3. Kiểm tra mạng
**Trên điện thoại:**
- Vào **Settings → WiFi**
- Kiểm tra tên WiFi giống máy tính
- Xem IP có dạng `192.168.1.xxx` không

### 4. Test kết nối
**Trên trình duyệt điện thoại:**
```
http://192.168.1.32:5000/health
```

**Kết quả mong đợi:**
```json
{"status":"ok","message":"Fraud Detection API is running"}
```

- ✅ Thấy JSON → OK, tiếp tục bước 5
- ❌ Timeout/Error → **KHÔNG cùng WiFi** hoặc **dùng ngrok**

### 5. Run app trên điện thoại
1. Kết nối điện thoại qua USB
2. Bật USB Debugging
3. Click **Run** ▶️ trong Android Studio

---

## ❗ NẾU VẪN TIMEOUT

### Giải pháp 1: Kiểm tra AP Isolation
Router có thể chặn kết nối giữa các thiết bị WiFi.

**Test:** Ping từ điện thoại sang máy tính
- Cài app **Network Tools** trên điện thoại
- Ping: `192.168.1.32`
- Nếu **Request timeout** → Router có AP Isolation

**Giải pháp:**
- Vào router settings, tắt **AP Isolation / Client Isolation**
- Hoặc dùng **ngrok** (xem `NGROK_SETUP_VI.md`)

---

### Giải pháp 2: Dùng ngrok (100% hoạt động)
Nếu không thể fix mạng, dùng ngrok:

```powershell
# Terminal 1
python run.py

# Terminal 2
.\ngrok.exe http 5000
```

Copy URL từ ngrok (ví dụ: `https://abc123.ngrok-free.app`)

Sửa `ApiClient.java`:
```java
private static final String BASE_URL = "https://abc123.ngrok-free.app/";
```

Rebuild app và chạy!

---

## 📊 TRẠNG THÁI HIỆN TẠI

| Component | Status | Note |
|-----------|--------|------|
| Flask Server | ✅ Running | `http://192.168.1.32:5000` |
| Firewall | ✅ Open | Port 5000 |
| BASE_URL | ✅ Configured | `http://192.168.1.32:5000/` |
| Permissions | ✅ **FIXED** | Đã thêm INTERNET, READ_EXTERNAL_STORAGE, READ_MEDIA_IMAGES |
| Cleartext Traffic | ✅ **FIXED** | Đã thêm `usesCleartextTraffic="true"` |
| Dependencies | ✅ Complete | Retrofit, Gson, OkHttp |
| FormActivity | ✅ **FIXED** | Đã khai báo trong manifest |
| Gradle Sync | ⏳ Pending | **CẦN CHẠY** |
| Build | ⏳ Pending | **CẦN CHẠY** |

---

## 🎯 HÀNH ĐỘNG TIẾP THEO

**BẮT BUỘC:**
1. ✅ Mở Android Studio
2. ✅ Sync Project with Gradle Files (🐘)
3. ✅ Rebuild Project
4. ✅ Test trên trình duyệt điện thoại: `http://192.168.1.32:5000/health`
5. ✅ Run app

**NẾU TIMEOUT:**
- Dùng ngrok (xem `NGROK_SETUP_VI.md`)
