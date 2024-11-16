import streamlit as st
import pandas as pd
import openai
import json
from dotenv import load_dotenv
import os
import pickle
import joblib
import pandas as pd
import numpy as np

load_dotenv()

# Fungsi untuk menganalisis burnout
def burnout_analyzer(burnout_category, top_variable):
    prompt = f"""
    Saya ingin Anda menganalisis tingkat burnout seseorang berdasarkan data berikut:
    
    Kategori Burnout: {burnout_category}
    0: Tidak burnout
    1: Burnout 
    
    Variabel penyebab burnout:
    {json.dumps(top_variable, indent=2)}

    Tugas Anda:
    1. Jelaskan secara ringkas dan lugas mengenai kategori burnout berdasarkan data yang diberikan.
    2. Identifikasi penyebab utama burnout dari variabel.
    3. Berikan rekomendasi yang secara ringkas dan lugas mengenai untuk membantu pemulihan individu ini.

    rangkai ketiga poin tugas di atas menjadi satu narasi yang ringkas dengan bentuk poin poin. highlight hasil klasifikasi burnout, tebalkan variable penyebab dan rekomendasi.
    """
    try:
        # Memanggil API OpenAI
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        # Ambil jawaban dari AI
        return response.choices[0].message.content
    except Exception as e:
        return f"Terjadi kesalahan saat memproses data: {str(e)}"

with open('rf_model.pkl', 'rb') as file:
    model = pickle.load(file)

def make_inference(data):
    predictions = model.predict(data)
    return predictions

# Konfigurasi Streamlit
st.title("Healthflux Burnout Analyzer")
st.write("Unggah file Excel untuk menganalisis tingkat burnout berdasarkan data input.")

# Upload file Excel
uploaded_file = st.file_uploader("Unggah file Excel", type=["xlsx"])

if uploaded_file:
    try:
        # Baca file Excel
        data = pd.read_excel(uploaded_file)
        nama = data.iloc[0, 0]
        data = data.drop(columns=["nama"])
        predictions = make_inference(data)

        # Pastikan kolom yang dibutuhkan ada
        if "Resulting quality of life" in data.columns:
            st.write("**Hasil Analisis Burnout:**")
            for index, row in data.iterrows():
                # Parse data
                burnout_category = predictions
                columns_to_extract = ["Resulting quality of life", "Age", "Duration of working day", "Quantity of patients per day", "Pulse in 60 seconds"]
                top_variable = json.dumps({col: str(data.iloc[0][col]) for col in columns_to_extract})
                
                # Analisis menggunakan OpenAI
                analysis_result = burnout_analyzer(burnout_category, top_variable)
                
                # Tampilkan hasil sebagai teks
                st.markdown(f"{nama}")
                st.markdown(analysis_result)
                st.markdown("---")  # Garis pemisah untuk setiap individu
        else:
            st.error("File Excel harus memiliki kolom 'Resulting quality of life'.")
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {str(e)}")
