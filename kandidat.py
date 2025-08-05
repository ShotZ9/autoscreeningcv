import streamlit as st
from datetime import datetime

# --- Form Input Manual ---
st.subheader("🧾 Formulir Data Kandidat")
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

    
    # --- Pilih Jobdesc Setelah Upload CV ---
    jobdesc_option = st.selectbox("💼 Pilih Posisi yang Dituju", [
        "Frontend (FE)", "Backend (BE)", "UI/UX", "Machine Learning (ML)"
    ])
    jobdesc_keywords_map = {
        "Frontend (FE)": ["javascript", "react", "vue", "next", "frontend"],
        "Backend (BE)": ["golang", "sql", "rest api", "backend", "nodejs"],
        "UI/UX": ["figma", "prototyping", "wireframe", "mockup"],
        "Machine Learning (ML)": ["python", "machine learning", "tensorflow", "sklearn", "model"]
    }
    keywords = jobdesc_keywords_map[jobdesc_option]

    uploaded_cv = st.file_uploader("📤 Unggah CV (.pdf atau .docx)", type=["pdf", "docx"])
    submitted = st.form_submit_button("🚀 Submit dan Kirim ke Backend")

# --- Simpan dan kirim ke server backend (simulasi upload saja) ---
if submitted:
    if not all([name, gender, birth_place, birth_date, current_city, university, major, email, phone, gpa, uploaded_cv]):
        st.warning("⚠️ Harap isi seluruh form dan unggah CV.")
    else:
        # Simpan file ke folder server backend (simulasi)
        file_path = f"./uploads/{uploaded_cv.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_cv.getbuffer())

        # Simulasi kirim data ke backend (bisa pakai requests.post jika ada API)
        st.success("✅ Data berhasil disimpan dan CV telah dikirim ke server backend.")

        # Tampilkan resume singkat
        st.markdown("### 📋 Ringkasan Data yang Dikirim")
        st.json({
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
            "keywords": keywords,
            "cv_filename": uploaded_cv.name
        })

# --- Disclaimer ---
st.markdown("---")
st.info("🛡️ **Disclaimer:** Seluruh data dan file yang Anda unggah akan diproses dan disimpan secara internal di server backend untuk keperluan screening dan evaluasi kandidat.")
