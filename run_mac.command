#!/bin/bash
clear
cd "$(dirname "$0")"

echo "Dang kich hoat moi truong ao va khoi chay Streamlit..."
source .venv/bin/activate
streamlit run app.py