# Fraud Detection API

API phát hiện gian lận thẻ tín dụng sử dụng Flask với kiến trúc Blueprints và Application Factory Pattern.

## 🏗️ Cấu trúc Project

```
Fraud_creaditCart_detection_app/
│
├── app/
│   ├── __init__.py                 # Application Factory
│   ├── config.py                   # Configuration settings
│   │
│   └── blueprints/                 # Blueprints package
│       ├── __init__.py
│       │
│       ├── model/                  # Model Blueprint
│       │   ├── __init__.py
│       │   ├── routes.py           # Model API endpoints
│       │   └── services.py         # Model business logic
│       │
│       ├── openai/                 # OpenAI Blueprint
│       │   ├── __init__.py
│       │   ├── routes.py           # OpenAI API endpoints
│       │   └── services.py         # OpenAI integration logic
│       │
│       └── preprocess/             # Preprocess Blueprint
│           ├── __init__.py
│           ├── routes.py           # Preprocessing endpoints
│           └── services.py         # Preprocessing logic
│
├── models/                         # ML models (not committed to git)
│   ├── fraud_detection_model.pkl
│   └── scaler.pkl
│
├── .env                            # Environment variables (NOT in git)
├── .env.example                    # Example environment file
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
├── run.py                          # Application entry point
└── README.md                       # This file
```

## 🚀 Cài đặt

### 1. Clone repository

```bash
cd Fraud_creaditCart_detection_app
```

### 2. Tạo virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình environment variables

Sao chép file `.env.example` thành `.env` và cập nhật các giá trị:

```bash
copy .env.example .env
```

Chỉnh sửa file `.env`:

```env
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo
MODEL_PATH=models/fraud_detection_model.pkl
SCALER_PATH=models/scaler.pkl
```

⚠️ **QUAN TRỌNG**: File `.env` chứa các API keys và không được đẩy lên GitHub.

### 5. Chạy application

```bash
python run.py
```

Server sẽ chạy tại: `http://localhost:5000`

## 📋 API Endpoints

### Health Check
- `GET /health` - Kiểm tra trạng thái server

### Model APIs (`/api/model`)
- `POST /api/model/predict` - Dự đoán gian lận cho 1 giao dịch
- `POST /api/model/batch-predict` - Dự đoán hàng loạt
- `GET /api/model/model-info` - Thông tin về model
- `POST /api/model/reload` - Tải lại model

### OpenAI APIs (`/api/openai`)
- `POST /api/openai/analyze-transaction` - Phân tích giao dịch bằng AI
- `POST /api/openai/explain-prediction` - Giải thích kết quả dự đoán
- `POST /api/openai/chat` - Chat về phát hiện gian lận
- `POST /api/openai/generate-report` - Tạo báo cáo phân tích

### Preprocess APIs (`/api/preprocess`)
- `POST /api/preprocess/transaction-to-text` - Chuyển giao dịch thành text
- `POST /api/preprocess/normalize-input` - Chuẩn hóa input
- `POST /api/preprocess/extract-features` - Trích xuất features
- `POST /api/preprocess/validate-input` - Validate dữ liệu đầu vào
- `POST /api/preprocess/batch-preprocess` - Xử lý hàng loạt

## 📝 Ví dụ sử dụng

### Dự đoán gian lận

```bash
curl -X POST http://localhost:5000/api/model/predict \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_data": {
      "amount": 1500.00,
      "merchant_id": "M123",
      "customer_id": "C456"
    }
  }'
```

### Phân tích bằng AI

```bash
curl -X POST http://localhost:5000/api/openai/analyze-transaction \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_text": "Large purchase at unusual location",
    "transaction_data": {"amount": 5000}
  }'
```

## 🔒 Bảo mật

- File `.env` chứa API keys và **KHÔNG BAO GIỜ** được commit lên Git
- Đã được thêm vào `.gitignore`
- Sử dụng `.env.example` để hướng dẫn cấu hình
- Thay đổi `SECRET_KEY` trong production

## 🧪 Testing

```bash
pytest
```

## 📦 Dependencies chính

- **Flask**: Web framework
- **Flask-CORS**: Cross-Origin Resource Sharing
- **OpenAI**: AI integration
- **NumPy, Pandas**: Data processing
- **scikit-learn**: Machine learning
- **python-dotenv**: Environment variables

## 🛠️ Development

### Code formatting

```bash
black .
```

### Linting

```bash
flake8
```

## 📄 License

MIT License

## 👥 Contributors

Your Name - Fraud Detection Team
