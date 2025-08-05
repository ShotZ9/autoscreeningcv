import streamlit as st
from datetime import datetime
import os
import json
import uuid

# --- Form Input Manual ---
st.set_page_config(page_title="Formulir Kandidat", layout="centered")
st.title("🧾 Formulir Data Kandidat")

with st.form("form_data"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Nama Lengkap")
        gender = st.selectbox("Gender", ["Laki-laki", "Perempuan"])
        birth_place = st.text_input("Tempat Lahir")
        birth_date = st.date_input(
            "Tanggal Lahir",
            format="DD-MM-YYYY",
            min_value=datetime(1970, 1, 1),
            max_value=datetime(2010, 12, 31)
        )
        current_city = st.text_input("Domisili Sekarang")

    with col2:
        university = st.text_input("Lulusan Dari Universitas")
        major = st.text_input("Jurusan")
        email = st.text_input("Email")
        phone = st.text_input("No. Telepon")
        gpa = st.text_input("GPA")

    # --- Pilih Jobdesc ---
    jobdesc_option = st.selectbox("💼 Pilih Posisi yang Dituju", [
        "Frontend (FE)", "Backend (BE)", "UI/UX", "Machine Learning (ML)"
    ])

    uploaded_cv = st.file_uploader("📤 Unggah CV (.pdf atau .docx)", type=["pdf", "docx"])
    submitted = st.form_submit_button("🚀 Submit dan Kirim ke Backend")

# --- Simpan dan kirim ke server backend ---
if submitted:
    if not all([name, gender, birth_place, birth_date, current_city, university, major, email, phone, gpa, uploaded_cv]):
        st.warning("⚠️ Harap isi seluruh form dan unggah CV.")
    else:
        # Generate folder unik untuk kandidat
        folder_id = f"{name.strip().lower().replace(' ', '_')}_{str(uuid.uuid4())[:8]}"
        save_dir = os.path.join("kandidat_data", folder_id)
        os.makedirs(save_dir, exist_ok=True)

        # Simpan CV
        cv_path = os.path.join(save_dir, uploaded_cv.name)
        with open(cv_path, "wb") as f:
            f.write(uploaded_cv.getbuffer())

        # Simpan data ke JSON
        data = {
            "nama": name,
            "gender": gender,
            "tempat_lahir": birth_place,
            "tanggal_lahir": birth_date.strftime("%d-%m-%Y"),
            "domisili": current_city,
            "universitas": university,
            "jurusan": major,
            "email": email,
            "no_telp": phone,
            "gpa": gpa,
            "jobdesc": jobdesc_option,
            "cv_filename": uploaded_cv.name
        }

        json_path = os.path.join(save_dir, "data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        st.success("✅ Data berhasil disimpan dan CV telah dikirim ke backend.")

        # Tampilkan ringkasan
        st.markdown("### 📋 Ringkasan Data yang Dikirim")
        st.json(data)

# --- Disclaimer ---
st.markdown("---")
st.info("🛡️ **Disclaimer:** Seluruh data dan file yang Anda unggah akan diproses dan disimpan secara internal di server backend untuk keperluan screening dan evaluasi kandidat.")
