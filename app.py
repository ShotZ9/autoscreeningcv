import streamlit as st
import pandas as pd
import PyPDF2
import docx
import re

st.set_page_config(page_title="Auto CV Screening", layout="wide")

st.title("📄 Auto Screening CV App")
st.markdown("Unggah file .pdf atau .docx dan pilih jobdesc yang diinginkan untuk menyaring CV kandidat.")

# --- Jobdesc Selector ---
jobdesc_option = st.selectbox("💼 Pilih Posisi yang Dicari", ["Frontend (FE)", "Backend (BE)", "UI/UX", "Machine Learning (ML)"])
jobdesc_keywords_map = {
    "Frontend (FE)": ["javascript", "react", "vue", "next", "frontend"],
    "Backend (BE)": ["golang", "sql", "rest api", "backend", "nodejs"],
    "UI/UX": ["figma", "prototyping", "wireframe", "mockup"],
    "Machine Learning (ML)": ["python", "machine learning", "tensorflow", "sklearn", "model"]
}
keywords = jobdesc_keywords_map[jobdesc_option]
total_keywords = len(keywords)

# --- Upload File ---
uploaded_files = st.file_uploader("📤 Unggah file CV (.pdf atau .docx)", type=["pdf", "docx"], accept_multiple_files=True)

# --- Ekstraksi Teks ---
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text() or ''
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return '\\n'.join([para.text for para in doc.paragraphs])

# --- Simulasi Translasi (ID -> EN) ---
def simulate_translate(text):
    return text.replace("ipk", "gpa").replace("laki-laki", "male").replace("perempuan", "female") \
               .replace("islam", "islam").replace("kristen", "christian").replace("katolik", "catholic") \
               .replace("buddha", "buddhist").replace("hindu", "hindu").replace(",", " ").replace(":", " ")

# --- Ekstraksi Atribut Dasar ---
def extract_attributes(text):
    attributes = {}
    # GPA
    gpa_match = re.search(r"gpa\\s*[:=\\-]?\\s*(\\d\\.\\d+)", text)
    if gpa_match:
        attributes["GPA"] = float(gpa_match.group(1))
    else:
        attributes["GPA"] = None

    # Gender
    if "male" in text:
        attributes["Gender"] = "Male"
    elif "female" in text:
        attributes["Gender"] = "Female"
    else:
        attributes["Gender"] = "Unknown"

    # Religion
    for religion in ["islam", "christian", "catholic", "buddhist", "hindu"]:
        if religion in text:
            attributes["Religion"] = religion.capitalize()
            break
    else:
        attributes["Religion"] = "Unknown"

    # Kota
    city_match = re.search(r"(tinggal di|berdomisili di|alamat di)\\s+([a-zA-Z ]+)", text)
    attributes["City"] = city_match.group(2).strip() if city_match else "Unknown"

    # Usia (jika ada tahun lahir)
    birth_year_match = re.search(r"(lahir tahun|born in)\\s*(\\d{4})", text)
    if birth_year_match:
        birth_year = int(birth_year_match.group(2))
        attributes["Age"] = 2025 - birth_year
    else:
        attributes["Age"] = None

    return attributes

# --- Screening ---
if st.button("🚀 Mulai Screening"):
    if not uploaded_files:
        st.warning("Mohon unggah file terlebih dahulu.")
    else:
        results = []

        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            ext = file_name.split('.')[-1].lower()

            try:
                if ext == 'pdf':
                    text = extract_text_from_pdf(uploaded_file).lower()
                elif ext == 'docx':
                    text = extract_text_from_docx(uploaded_file).lower()
                else:
                    st.warning(f"❌ Format file tidak didukung: {file_name}")
                    continue

                # Simulasi translate ID -> EN
                text_en = simulate_translate(text)

                # Screening keyword binary
                binary_matches = {kw: int(kw in text_en) for kw in keywords}
                score = sum(binary_matches.values())
                percentage_match = (score / total_keywords) * 100 if total_keywords else 0

                # Ekstrak atribut
                attrs = extract_attributes(text_en)

                results.append({
                    "Filename": file_name,
                    **attrs,
                    **binary_matches,
                    "Total_Match (%)": round(percentage_match, 2)
                })
            except Exception as e:
                st.error(f"⚠️ Gagal memproses {file_name}: {e}")

        if results:
            st.session_state["screening_results"] = pd.DataFrame(results)
        else:
            st.warning("Tidak ada hasil yang dapat ditampilkan.")

# --- Tampilkan hasil jika sudah ada di session_state ---
if "screening_results" in st.session_state:
    df = st.session_state["screening_results"]

    st.markdown("### 📊 Opsi Tampilan Hasil")
    limit = st.selectbox("Jumlah hasil yang ditampilkan:", [10, 20, 50, 100], index=1)
    sort_order = st.radio("Urutkan berdasarkan persentase:", ["Descending", "Ascending"], horizontal=True)

    ascending = True if sort_order == "Ascending" else False
    df_sorted = df.sort_values(by="Total_Match (%)", ascending=ascending).reset_index(drop=True)
    df_display = df_sorted.head(limit)

    st.success("✅ Screening selesai!")
    st.dataframe(df_display)

    # Tombol download CSV full
    csv = df_sorted.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Unduh Hasil Screening", data=csv, file_name="hasil_screening.csv", mime="text/csv")
