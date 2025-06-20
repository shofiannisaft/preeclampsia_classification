import streamlit as st
import joblib
import numpy as np

# Load model
preeclampsi_model = joblib.load(open('stacking_tuned_LGBM_v2.sav', 'rb'))

st.set_page_config(page_title="Prediksi Preeklampsia", layout="centered")
st.title("🩺 Deteksi Risiko Preeklampsia pada Ibu Hamil")

# Reset flag
reset_form = st.button("🔄 Reset Formulir ke Nilai Normal")

# Default values
defaults = {
    "age": 28,
    "weight": 60.0,
    "height_cm": 160.0,
    "Sistol": 110,
    "Diastol": 75,
    "HR": 85,
    "RR": 19,
    "SpO2": 98,
    "Temp": 36.6,
    "Hb": 12.0,
    "Tromb": 250.0,
    "ProtUrin_input": '0',
    "Glucose": 90.0,
    "Gravida": 2,
    "Paritas": 1,
    "Abortus": 0,
    "riw_HT": "Tidak",
    "DM": "Tidak",
    "UK": 26
}

# Set function untuk ambil input dengan reset support
def input_or_default(label, key, type_func, **kwargs):
    val = defaults[key] if reset_form else kwargs.get("value", defaults[key])
    return type_func(label, key=key, **kwargs, value=val)

st.markdown("### 📌 1. Data Demografi")
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        age = input_or_default("Usia Ibu (tahun)", "age", st.number_input, min_value=10, max_value=60, step=1)
    with col2:
        weight = input_or_default("Berat Badan (kg)", "weight", st.number_input, min_value=30.0, max_value=200.0)
        height_cm = input_or_default("Tinggi Badan (cm)", "height_cm", st.number_input, min_value=100.0, max_value=220.0)
    height_m = height_cm / 100
    IMT = round(weight / (height_m ** 2), 2) if height_m > 0 else 0
    st.markdown(f"**IMT: {IMT} kg/m²**")

st.divider()
st.markdown("### 💓 2. Pemeriksaan Vital")
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        Sistol = input_or_default("Tekanan Sistolik (mmHg)", "Sistol", st.number_input, min_value=60, max_value=250)
        HR = input_or_default("Detak Jantung (/menit)", "HR", st.number_input, min_value=40, max_value=200)
        SpO2 = input_or_default("Saturasi Oksigen (%)", "SpO2", st.number_input, min_value=60, max_value=100)
    with col2:
        Diastol = input_or_default("Tekanan Diastolik (mmHg)", "Diastol", st.number_input, min_value=40, max_value=150)
        RR = input_or_default("Laju Pernapasan (/menit)", "RR", st.number_input, min_value=10, max_value=60)
        Temp = input_or_default("Suhu Tubuh (°C)", "Temp", st.number_input, min_value=30.0, max_value=45.0, step=0.1, format="%.1f")

st.divider()
st.markdown("### 🧪 3. Pemeriksaan Laboratorium")
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        Hb = input_or_default("Hemoglobin (g/dL)", "Hb", st.number_input, min_value=4.0, max_value=20.0, step=0.1, format="%.1f")
        ProtUrin_input = st.selectbox("Protein Urin", ['0', '+1', '+2', '+3', '+4'], index=['0', '+1', '+2', '+3', '+4'].index(defaults["ProtUrin_input"]) if reset_form else 0)
    with col2:
        Glucose = input_or_default("Gula Darah (mg/dL)", "Glucose", st.number_input, min_value=50.0, max_value=500.0, step=0.1, format="%.1f")
        Tromb = input_or_default("Trombosit (x10⁹/L)", "Tromb", st.number_input, min_value=50.0, max_value=1000.0, step=0.1, format="%.1f")

proturin_map = {'0': 0, '+1': 1, '+2': 2, '+3': 3, '+4': 4}
ProtUrin = proturin_map[ProtUrin_input]

st.divider()
st.markdown("### 👶 4. Riwayat Kehamilan & Penyakit")
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        Gravida = input_or_default("Jumlah Kehamilan", "Gravida", st.number_input, min_value=1, max_value=20)
        Paritas = input_or_default("Jumlah Persalinan", "Paritas", st.number_input, min_value=0, max_value=15)
        Abortus = input_or_default("Jumlah Keguguran", "Abortus", st.number_input, min_value=0, max_value=10)
    with col2:
        riw_HT = st.selectbox("Riwayat Hipertensi", ["Tidak", "Ya"], index=0 if reset_form else 0)
        riw_HT = 1 if riw_HT == "Ya" else 0
        DM = st.selectbox("Riwayat Diabetes", ["Tidak", "Ya"], index=0 if reset_form else 0)
        DM = 1 if DM == "Ya" else 0
        UK = st.selectbox("Usia Kehamilan (minggu)", list(range(10, 42)), index=defaults["UK"] - 10 if reset_form else 16)

# Tombol Prediksi
if st.button("🔍 Prediksi Preeklampsia"):
    input_data = np.array([[
    age, IMT, Sistol, Diastol, HR, RR, SpO2, Temp,
    Gravida, Paritas, Abortus, Glucose, Hb, Tromb,
    ProtUrin, riw_HT, UK, 1, DM  # ← jml_janin = 1 (jika belum ada input)
]])

    prediction = preeclampsi_model.predict(input_data)
    label = prediction[0]
    # Mapping label model ke label diagnosis yang lebih deskriptif
    label_mapping = {
        "normal": "Normal",
        "mild": "Preeklampsia Ringan",
        "severe": "Preeklampsia Berat"
    }
    kategori = label_mapping.get(label.lower(), "Kategori tidak dikenali")
    #st.write("Prediksi mentah dari model:", label)
    #kategori = label  # langsung pakai string dari model

    #if label == 0:
    #    kategori = label
    #elif label == 1:
    #    kategori = "Preeklampsia Ringan"
    #elif label == 2:
    #    kategori = "Preeklampsia Berat"
    #else:
    #    kategori = "Kategori tidak dikenali"
    st.success(f"🧾 Diagnosis: **{kategori}**")

    # Rekomendasi POGI
    def rekomendasi_pogi(kategori):
        kategori = kategori.lower()
        #kategori = label  # langsung pakai string dari model

        if kategori == "preeklampsia berat":
            return """
            - Rawat inap segera
            - Pemberian MgSO₄ untuk pencegahan kejang
            - Antihipertensi aktif (labetalol, nifedipin)
            - Evaluasi terminasi kehamilan
            - USG pertumbuhan janin
            - Rujukan ke RS tipe A
            """
        elif kategori == "preeklampsia ringan":
            return """
            - Observasi tekanan darah dan protein urin secara berkala
            - Suplementasi kalsium 1 g/hari
            - Aspirin dosis rendah (<16 minggu kehamilan jika perlu)
            - Evaluasi gejala subjektif (nyeri kepala, visus)
            """
        elif kategori == "normal":
            return """
            - ANC rutin sesuai trimester
            - Edukasi ibu mengenai tanda bahaya preeklampsia
            - Monitor tekanan darah dan urin tiap kunjungan
            """
        else:
            return "Kategori tidak dikenali."

    st.subheader("📋 Rekomendasi Penanganan Menurut POGI:")
    st.markdown(rekomendasi_pogi(kategori))
