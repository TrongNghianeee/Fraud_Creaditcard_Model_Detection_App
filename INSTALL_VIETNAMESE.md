# 🇻🇳 Cài đặt Tiếng Việt cho Tesseract OCR

## ⚠️ Vấn đề hiện tại

Tesseract hiện tại chỉ có ngôn ngữ `eng` (English), chưa có `vie` (Vietnamese).  
Điều này khiến văn bản tiếng Việt bị nhận dạng sai:
- "chuyển tiền" → "chuyen tien"
- "thành công" → "thanh céng"

## 📥 Cách cài đặt tiếng Việt

### Phương pháp 1: Tải file traineddata thủ công (KHUYẾN NGHỊ)

1. **Tải file Vietnamese traineddata:**
   - Truy cập: https://github.com/tesseract-ocr/tessdata_best/blob/main/vie.traineddata
   - Click nút **"Download"** hoặc **"Raw"** để tải file `vie.traineddata`

2. **Copy file vào thư mục tessdata:**
   ```powershell
   # Copy file vừa tải vào:
   C:\Program Files\Tesseract-OCR\tessdata\
   ```
   
   Hoặc dùng lệnh PowerShell:
   ```powershell
   Copy-Item "C:\Users\Admin\Downloads\vie.traineddata" -Destination "C:\Program Files\Tesseract-OCR\tessdata\"
   ```

3. **Kiểm tra cài đặt:**
   ```powershell
   & "C:\Program Files\Tesseract-OCR\tesseract.exe" --list-langs
   ```
   
   Kết quả mong đợi:
   ```
   List of available languages (3):
   eng
   vie
   ```

### Phương pháp 2: Tải bằng PowerShell (Tự động)

Chạy lệnh sau trong PowerShell (Run as Administrator):

```powershell
# Tải file Vietnamese traineddata
$url = "https://github.com/tesseract-ocr/tessdata_best/raw/main/vie.traineddata"
$output = "C:\Program Files\Tesseract-OCR\tessdata\vie.traineddata"

Invoke-WebRequest -Uri $url -OutFile $output

Write-Host "✅ Đã cài đặt tiếng Việt cho Tesseract!" -ForegroundColor Green

# Kiểm tra
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --list-langs
```

### Phương pháp 3: Cài lại Tesseract với Vietnamese

1. Gỡ Tesseract hiện tại (Control Panel → Programs)
2. Tải installer mới: https://github.com/UB-Mannheim/tesseract/wiki
3. Trong quá trình cài đặt:
   - Chọn **"Additional language data"**
   - ✅ Chọn **Vietnamese** (vie)
   - ✅ Chọn **English** (eng)
4. Hoàn tất cài đặt

## 🧪 Test sau khi cài

### 1. Kiểm tra ngôn ngữ:
```powershell
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --list-langs
```

### 2. Test trực tiếp với ảnh:
```powershell
& "C:\Program Files\Tesseract-OCR\tesseract.exe" test_image.jpg output -l vie+eng
```

### 3. Test qua API:
- Mở: http://localhost:5000
- Upload ảnh tiếng Việt
- Chọn ngôn ngữ: **Tiếng Việt + English**
- Nhấn "Trích xuất văn bản"

## 📊 So sánh kết quả

### ❌ TRƯỚC (chỉ có `eng`):
```
Chuyen tien thanh céng 2,500,000 VND
```

### ✅ SAU (có `vie+eng`):
```
Chuyển tiền thành công 2,500,000 VND
```

## 🔗 Tài nguyên

- **Tessdata Best (chất lượng cao)**: https://github.com/tesseract-ocr/tessdata_best
- **Tessdata (nhanh hơn)**: https://github.com/tesseract-ocr/tessdata
- **Tessdata Fast (nhanh nhất)**: https://github.com/tesseract-ocr/tessdata_fast

**Khuyến nghị**: Dùng `tessdata_best` cho độ chính xác cao nhất với tiếng Việt.

## ⚡ Quick Install (Copy & Paste)

```powershell
# Run as Administrator
$url = "https://github.com/tesseract-ocr/tessdata_best/raw/main/vie.traineddata"
$output = "C:\Program Files\Tesseract-OCR\tessdata\vie.traineddata"
Invoke-WebRequest -Uri $url -OutFile $output
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --list-langs
```

Sau khi cài xong, reload lại trang web và thử lại! 🎉
