import streamlit as st
import os
import json
import PyPDF2
import docx
import pandas as pd

st.set_page_config(page_title="Admin Panel - Screening CV", layout="wide")
st.title("📑 Hasil Screening CV Kandidat")

BASE_DIR = "kandidat_data"

# --- Konfigurasi keyword ---
jobdesc_keywords_map = {
    "Frontend (FE)": ["javascript", "react", "vue", "next", "frontend"],
    "Backend (BE)": ["golang", "sql", "rest api", "backend", "nodejs"],
    "UI/UX": ["figma", "prototyping", "wireframe", "mockup", "adobe"],
    "Machine Learning (ML)": ["python", "machine learning", "tensorflow", "sklearn", "model"]
}

# --- Ekstraksi teks dari CV ---
def extract_text(path):
    ext = path.split(".")[-1].lower()
    if ext == "pdf":
        reader = PyPDF2.PdfReader(open(path, "rb"))
        return "\n".join([page.extract_text() or '' for page in reader.pages])
    elif ext == "docx":
        doc = docx.Document(path)
        return "\n".join([para.text for para in doc.paragraphs])
    return ""

# --- Screening semua folder kandidat ---
results = []
if not os.path.isdir(BASE_DIR):
    st.warning("📂 Folder `kandidat_data/` belum tersedia.")
    st.stop()

folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]
if not folders:
    st.warning("🧾 Belum ada data kandidat yang dikirim.")
    st.stop()

for folder in folders:
    folder_path = os.path.join(BASE_DIR, folder)
    json_path = os.path.join(folder_path, "data.json")

    if not os.path.exists(json_path):
        continue

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        cv_path = os.path.join(folder_path, data["cv_filename"])
        if not os.path.exists(cv_path):
            continue

        text = extract_text(cv_path).lower()
        jobdesc = data.get("jobdesc", "-")
        keywords = jobdesc_keywords_map.get(jobdesc, [])
        match_count = sum(1 for kw in keywords if kw.lower() in text)
        percentage = (match_count / len(keywords)) * 100 if keywords else 0

        results.append({
            "Nama": data.get("nama", "-"),
            "Email": data.get("email", "-"),
            "No. Telp": data.get("no_telp", "-"),
            "Domisili": data.get("domisili", "-"),
            "Universitas": data.get("universitas", "-"),
            "Jurusan": data.get("jurusan", "-"),
            "GPA": data.get("gpa", "-"),
            "Jobdesc": jobdesc,
            "Total_Match (%)": round(percentage, 2),
            "CV Path": cv_path,
        })

    except Exception as e:
        st.error(f"Gagal membaca data dari {folder}: {e}")

# --- Tampilkan hasil screening ---
if results:
    df = pd.DataFrame(results)

    st.success("✅ Screening selesai. Berikut data dari semua kandidat:")

    with st.expander("🔎 Filter"):
        col1, col2, col3 = st.columns(3)

        # Filter Domisili (jika ada)
        unique_city = sorted(df["Domisili"].dropna().unique())
        selected_city = col1.selectbox("Domisili", ["Semua"] + unique_city) if unique_city else "Semua"

        # Filter Universitas
        unique_univ = sorted(df["Universitas"].dropna().unique())
        selected_univ = col2.selectbox("Universitas", ["Semua"] + unique_univ) if unique_univ else "Semua"

        # Filter Jobdesc
        unique_jobs = sorted(df["Jobdesc"].dropna().unique())
        selected_job = col3.selectbox("Jobdesc", ["Semua"] + unique_jobs) if unique_jobs else "Semua"

        # Filter Match % minimal
        match_threshold = st.slider("Minimum Total Match (%)", min_value=0, max_value=100, value=0, step=5)

    # --- Sorting ---
    sort_order = st.radio("Urutkan berdasarkan Match (%)", ["Descending", "Ascending"], horizontal=True)
    ascending = True if sort_order == "Ascending" else False

    # --- Terapkan filter
    filtered_df = df.copy()

    if selected_city != "Semua":
        filtered_df = filtered_df[filtered_df["Domisili"] == selected_city]
    if selected_univ != "Semua":
        filtered_df = filtered_df[filtered_df["Universitas"] == selected_univ]
    if selected_job != "Semua":
        filtered_df = filtered_df[filtered_df["Jobdesc"] == selected_job]

    filtered_df = filtered_df[filtered_df["Total_Match (%)"] >= match_threshold]
    filtered_df = filtered_df.sort_values(by="Total_Match (%)", ascending=ascending).reset_index(drop=True)

    # --- Tampilkan tabel + tombol unduh
    st.dataframe(filtered_df.drop(columns=["CV Path"]), use_container_width=True)

    csv = filtered_df.drop(columns=["CV Path"]).to_csv(index=False).encode("utf-8")
    st.download_button("📥 Unduh Hasil Screening", data=csv, file_name="hasil_screening.csv", mime="text/csv")

    st.markdown("### 📂 Akses CV Per Kandidat")
    for _, row in filtered_df.iterrows():
        with open(row["CV Path"], "rb") as f:
            st.download_button(
                label=f"📄 Unduh CV - {row['Nama']}",
                data=f.read(),
                file_name=os.path.basename(row["CV Path"]),
                mime="application/pdf" if row["CV Path"].endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
else:
    st.warning("📂 Tidak ada kandidat valid yang bisa ditampilkan.")
