# Fraud Detection (Flask API + Android App)

Dự án gồm:
- **Flask API** (localhost:5000) để OCR + AI parse thông tin giao dịch và dự đoán gian lận.
- **Android app** (thư mục `mobile_app_1/`) để chọn ảnh giao dịch, tự động điền form, dự đoán và lưu **Lịch sử**.

## ✅ Chức năng hiện tại

### Backend (Flask)
- `POST /api/preprocess/extract-and-parse`: Upload ảnh → OCR (Tesseract) → AI parse ra **7 trường**:
  - `amt`, `gender`, `category`, `transaction_time`, `transaction_day`, `city`, `age`
- `POST /api/model/predict-fraud`: Nhận dữ liệu giao dịch (7 trường + city_pop) → trả về `prediction` + `input` đã convert.
- `GET /health`: Health check.
- `GET /`: Trang test UI (static) để thử OCR/parse trên trình duyệt.

### Android app
- Home có 4 card chức năng (Phân tích ảnh / Mô phỏng / Cài đặt / Lịch sử) với UI cải thiện.
- Chọn ảnh → gọi API OCR+AI → đổ dữ liệu vào form.
- Bấm dự đoán → gọi API `predict-fraud`.
- **Lịch sử**: lưu local (SQLite) mỗi lần dự đoán, hiển thị đỏ/xanh + % và xem chi tiết; có nút quay về Home.

## 🏗️ Cấu trúc project

```
Fraud_creaditCart_detection_app/
├── app/
│   ├── __init__.py                 # Application Factory + / + /health
│   ├── config.py
│   └── blueprints/
│       ├── model/
│       │   ├── __init__.py
│       │   └── routes.py           # /api/model/predict-fraud
│       ├── preprocess/
│       │   ├── __init__.py
│       │   ├── routes.py           # /api/preprocess/extract-and-parse
│       │   └── services.py         # OCRService
│       └── openai/
│           ├── __init__.py         # Blueprint (hiện chưa có routes)
│           └── services.py         # OpenAIService.parse_transaction_text
├── static/
│   └── index.html                  # Trang test khi mở http://localhost:5000/
├── models/                         # ML models (pkl)
├── mobile_app_1/                   # Android project (Android Studio)
├── .env.example
├── requirements_core.txt
└── run.py                          # Chạy server
```

## 🚀 Cài đặt & chạy Backend (Flask API)

### 1) Yêu cầu
- Python 3.9 (khuyến nghị)
- **Tesseract OCR** (bắt buộc vì dùng `pytesseract`)
  - Windows: cài “Tesseract-OCR” và đảm bảo `tesseract.exe` có trong `PATH`.

### 2) Tạo môi trường ảo + cài dependencies

Windows PowerShell:

```powershell
cd C:\Users\Admin\Code\Fraud_creaditCart_detection_app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements_core.txt
```

### 3) Cấu hình `.env`

```powershell
copy .env.example .env
```

Sửa `.env` (ít nhất cần `OPENAI_API_KEY` nếu muốn AI parse):

```dotenv
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=anthropic/claude-3.5-sonnet

HOST=0.0.0.0
PORT=5000
```

### 4) Chạy server

```powershell
python run.py
```

Mở:
- Test page: `http://localhost:5000/`
- Health: `http://localhost:5000/health`

## 📋 API Endpoints (hiện có)

### Health
- `GET /health`

### OCR + AI parse
- `POST /api/preprocess/extract-and-parse`
  - `multipart/form-data`:
    - `file`: ảnh giao dịch
    - `language`: (optional) ví dụ `vie+eng`
  - Response (khi OCR ok, AI parse ok):
    - `success: true`, `ai_parsing_success: true`, `transaction: { amt, gender, category, transaction_time, transaction_day, city, age }`
  - Nếu AI parse fail nhưng OCR ok:
    - `success: true`, `ai_parsing_success: false`, có `ocr_text` để debug

### Predict fraud
- `POST /api/model/predict-fraud`
  - JSON body:
    - `amt` (VND), `gender` (Nam/Nữ), `category` (VN), `transaction_hour` (0-23), `transaction_day` (0-6), `age` (18-100), `city`, `city_pop` (optional)

## 🧪 Test nhanh bằng localhost:5000

### 1) Health

```powershell
Invoke-RestMethod http://localhost:5000/health
```

### 2) Predict fraud

```powershell
$body = @{
  amt = 500000
  gender = "Nam"
  category = "xăng dầu"
  transaction_hour = 13
  transaction_day = 1
  age = 28
  city = "ha noi"
  city_pop = 8054000
} | ConvertTo-Json

Invoke-RestMethod -Method Post "http://localhost:5000/api/model/predict-fraud" -ContentType "application/json" -Body $body
```

### 3) OCR + AI parse (upload ảnh)

Gợi ý nhanh nhất: mở `http://localhost:5000/` và upload ảnh trên web test page.

## 📱 Cài & chạy Android app (Android Studio)

### 1) Mở project
- Mở **Android Studio** → **Open** → chọn thư mục: `mobile_app_1/`
- Chờ **Gradle Sync** hoàn tất

### 2) Cấu hình API base URL

Android app gọi API qua Retrofit ở `mobile_app_1/app/src/main/java/com/example/mobile_app/ApiClient.java`.

Bạn có 3 lựa chọn:

1) **Dùng ngrok (khuyến nghị khi chạy trên điện thoại thật)**
   - Chạy backend ở port 5000
   - Chạy: `ngrok http 5000`
   - Copy URL ngrok và dán vào `BASE_URL` (phải có dấu `/` cuối).

2) **Android Emulator + localhost**
   - Set `BASE_URL = "http://10.0.2.2:5000/"` (10.0.2.2 là localhost của máy host trên emulator)

3) **Điện thoại thật cùng Wi‑Fi với máy chạy backend**
   - Set `BASE_URL = "http://<IP_MAY_TINH>:5000/"` (ví dụ `http://192.168.1.10:5000/`)

### 3) Run
- Cắm điện thoại hoặc mở emulator
- Bấm **Run ▶**

## 🔒 Ghi chú bảo mật
- Không commit `.env` lên GitHub (file chứa API key).

