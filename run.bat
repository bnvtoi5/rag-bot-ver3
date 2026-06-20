@echo off
title TRO LY AO RAG
cls

:: Ep Windows dung dung thu muc chua file .bat này
cd /d "%~dp0"

echo Dang kich hoat moi truong ao va khoi chay Streamlit...
echo ------------------------------------------------------------

:: Kich hoat moi truong ao
call .venv\Scripts\activate

:: Chay ung dung Streamlit
streamlit run app.py

:: CHẶN MÀN HÌNH LẠI ĐỂ ĐỌC LỖI NẾU APP BỊ CRASH
echo ------------------------------------------------------------
echo [THONG BAO] App da bi dung lai hoac gap loi vao luc khoi chay.
echo Vui long doc dong chu mau do phia tren de biet loi gi nhe!
echo ------------------------------------------------------------
pause