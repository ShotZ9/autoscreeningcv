import streamlit as st
import pandas as pd
import PyPDF2
import docx
import re
from datetime import datetime
from dateutil import parser as dateparser

st.set_page_config(page_title="Auto CV Screening", layout="wide")

st.title("📄 Auto CV Screening App")
st.markdown("Unggah file .pdf atau .docx dan pilih jobdesc untuk menyaring CV kandidat. Ekstraksi otomatis: GPA, tanggal lahir, gender, agama, dan kota.")

TODAY = datetime.today()

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

# --- Input Kota untuk filter tampilan hasil ---
input_city = st.text_input("🔍 Filter hasil berdasarkan asal kota (opsional):").strip()

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

def simulate_translate(text):
    return text.replace("ipk", "gpa").replace("laki-laki", "male").replace("perempuan", "female") \
               .replace("islam", "islam").replace("kristen", "christian").replace("katolik", "catholic") \
               .replace("buddha", "buddhist").replace("hindu", "hindu")

def guess_gender_from_name(name):
    name = name.lower()
    female_hint = ["ayu", "nia", "sari", "dwi", "wati"]
    male_hint = ["yoel", "agus", "budi", "adi", "joko", "tono"]
    for w in female_hint:
        if w in name:
            return "Female"
    for m in male_hint:
        if m in name:
            return "Male"
    return "Unknown"

def extract_attributes(text, raw_text):
    attributes = {}

    # --- GPA ---
    gpa_match = re.search(r"gpa\s*[:=]?\s*([0-4][\.,]?\d{1,2})", text)
    gpa_raw = gpa_match.group(1).replace(",", ".") if gpa_match else None
    attributes["GPA"] = float(gpa_raw) if gpa_raw else None

    if "male" in text:
        attributes["Gender"] = "Male"
    elif "female" in text:
        attributes["Gender"] = "Female"
    else:
        name_match = re.search(r"^([A-Z][a-z]+(?:\\s[A-Z][a-z]+)*)", raw_text)
        name = name_match.group(1) if name_match else "Unknown"
        attributes["Gender"] = guess_gender_from_name(name)

    for religion in ["islam", "christian", "catholic", "buddhist", "hindu"]:
        if religion in text:
            attributes["Religion"] = religion.capitalize()
            break
    else:
        attributes["Religion"] = "Unknown"

    city_match = re.search(r"(malang|jakarta|surabaya|bandung|yogyakarta|semarang|denpasar|makassar|medan|solo|bali)", text)
    attributes["City"] = city_match.group(1).title() if city_match else "Unknown"

    search_area = raw_text.lower().split("about me")[0] if "about me" in raw_text.lower() else raw_text[:500]
    date_match = re.search(r"(born|lahir)[^\\d]*(\\d{1,2}[^\\d\\w]?\\s?[a-zA-Z]+[^\\d\\w]?\\s?\\d{4})", search_area)
    if date_match:
        try:
            bdate = dateparser.parse(date_match.group(2), languages=["id", "en"])
            age = TODAY.year - bdate.year - ((TODAY.month, TODAY.day) < (bdate.month, bdate.day))
            attributes["Birth"] = f"{bdate.strftime('%-d %B %Y')} ({age} Tahun)"
        except:
            attributes["Birth"] = "Format tanggal tidak dikenali"
    else:
        attributes["Birth"] = "Tidak ditemukan"

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
                    raw_text = extract_text_from_pdf(uploaded_file)
                elif ext == 'docx':
                    raw_text = extract_text_from_docx(uploaded_file)
                else:
                    st.warning(f"❌ Format file tidak didukung: {file_name}")
                    continue

                text = simulate_translate(raw_text.lower())
                binary_matches = {kw: int(kw in text) for kw in keywords}
                score = sum(binary_matches.values())
                percentage_match = (score / total_keywords) * 100 if total_keywords else 0
                attrs = extract_attributes(text, raw_text)

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

# --- Display ---
if "screening_results" in st.session_state:
    df = st.session_state["screening_results"]
    st.markdown("### 📊 Opsi Tampilan Hasil")
    limit = st.selectbox("Jumlah hasil yang ditampilkan:", [10, 20, 50, 100], index=1)
    sort_order = st.radio("Urutkan berdasarkan persentase:", ["Descending", "Ascending"], horizontal=True)
    ascending = True if sort_order == "Ascending" else False
    df_sorted = df.sort_values(by="Total_Match (%)", ascending=ascending).reset_index(drop=True)

    # Filter by input city
    if input_city:
        df_sorted = df_sorted[df_sorted["City"].str.lower() == input_city.lower()]

    df_display = df_sorted.head(limit)

    st.success("✅ Screening selesai!")
    st.dataframe(df_display)

    csv = df_sorted.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Unduh Hasil Screening", data=csv, file_name="hasil_screening.csv", mime="text/csv")
