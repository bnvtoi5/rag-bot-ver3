#!/bin/bash
clear
cd "$(dirname "$0")"

echo "============================================================"
echo "   BUOC 1: KHOI TAO MOI TRUONG VA CAI DAT (1 LAN DUY NHAT)"
echo "============================================================"
echo ""

# 1. Kiem tra Python
if ! command -v python3 &> /dev/null
then
    echo "[LOI] Khong tim thay Python tren may tinh! Vui long cai dat Python 3.10+."
    exit 1
fi

# 2. Khoi tao moi truong ao
echo "[*] Dang khoi tao moi truong ao Python (.venv)..."
python3 -m venv .venv
echo "[OK] Da khoi tao xong .venv"
echo ""

# 3. Kich hoat venv
source .venv/bin/activate

# 4. Nhap cac API Key va thiet lap moi truong Qdrant Cloud
if [ ! -f .env ]; then
    echo "------------------------------------------------------------"
    echo "[CAU HINH] Thiet lap tai khoan cho lan dau su dung:"
    
    # Nhập mã GROQ
    printf "👉 Vui long nhap hoac dan GROQ_API_KEY cua ban: "
    read api_key
    
    # Nhập mã Hugging Face
    printf "👉 Vui long nhap hoac dan HF_TOKEN (Hugging Face Token) cua ban: "
    read hf_token

    # Nhập cấu hình Qdrant Cloud
    printf "👉 Vui long nhap Cluster URL cua Qdrant Cloud: "
    read qdrant_url
    
    printf "👉 Vui long nhap API Key cua Qdrant Cloud: "
    read qdrant_key
    
    # Ghi cau hinh sach se va bao mat vao file .env
    echo "GROQ_API_KEY=$api_key" > .env
    echo "HF_TOKEN=$hf_token" >> .env
    echo "QDRANT_URL=$qdrant_url" >> .env
    echo "QDRANT_API_KEY=$qdrant_key" >> .env
    
    echo ""
    echo "[OK] Da luu cau hinh he thong hoan chinh vao file .env!"
    echo "------------------------------------------------------------"
    echo ""
fi

# 5. Cai dat thu vien
echo "[*] Dang tien hanh cai dat cac thu vien (Vui long cho)..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt --no-cache-dir -v

echo ""
echo "============================================================"
echo "[THANH CONG] Da thiet lap xong! Ban co the tat cua so nay."
echo "Hay nhap dup file 'run_mac.command' de su dung."
echo "============================================================"
echo ""
