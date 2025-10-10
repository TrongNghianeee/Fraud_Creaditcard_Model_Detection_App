@echo off
echo ================================================
echo  Cai dat Tieng Viet cho Tesseract OCR
echo ================================================
echo.

echo Dang copy file vie.traineddata...
copy /Y "%USERPROFILE%\Downloads\vie.traineddata" "C:\Program Files\Tesseract-OCR\tessdata\vie.traineddata"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Cai dat thanh cong!
    echo.
    echo Kiem tra cac ngon ngu da cai:
    "C:\Program Files\Tesseract-OCR\tesseract.exe" --list-langs
) else (
    echo.
    echo ❌ Loi! Can chay file nay voi quyen Administrator
    echo Chuot phai vao file -> Run as administrator
)

echo.
pause
