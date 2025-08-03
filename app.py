import streamlit as st
import pandas as pd
import PyPDF2
import docx
import io

st.set_page_config(page_title="Auto CV Screening", layout="wide")

st.title("📄 Auto Screening CV App")
st.markdown("Unggah file .pdf atau .docx dan masukkan kata kunci untuk menyaring CV kandidat.")

# --- Input Kata Kunci Skrining ---
keywords_input = st.text_input("🔍 Masukkan kata kunci skrining (pisahkan dengan koma):", "Python, machine learning, SQL")
keywords = [kw.strip().lower() for kw in keywords_input.split(",") if kw.strip()]
total_keywords = len(keywords)

# --- Upload File ---
uploaded_files = st.file_uploader("📤 Unggah file CV (.pdf atau .docx)", type=["pdf", "docx"], accept_multiple_files=True)

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text() or ''
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return '\n'.join([para.text for para in doc.paragraphs])

# --- Proses Screening ---
if st.button("🚀 Mulai Screening"):
    if not uploaded_files or not keywords:
        st.warning("Mohon unggah file dan masukkan kata kunci terlebih dahulu.")
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

                binary_matches = {kw: int(kw in text) for kw in keywords}
                score = sum(binary_matches.values())
                percentage_match = (score / total_keywords) * 100 if total_keywords else 0

                results.append({
                    "Filename": file_name,
                    **binary_matches,
                    "Total_Match (%)": round(percentage_match, 2)
                })
            except Exception as e:
                st.error(f"⚠️ Gagal memproses {file_name}: {e}")

        if results:
            df = pd.DataFrame(results)

            # --- Filter Tampilan ---
            st.markdown("### 📊 Opsi Tampilan Hasil")
            limit = st.selectbox("Jumlah hasil yang ditampilkan:", [10, 20, 50, 100], index=1)
            sort_order = st.radio("Urutkan berdasarkan persentase:", ["Descending", "Ascending"], horizontal=True)

            ascending = True if sort_order == "Ascending" else False
            df = df.sort_values(by="Total_Match (%)", ascending=ascending).reset_index(drop=True)
            df_display = df.head(limit)

            st.success("✅ Screening selesai!")
            st.dataframe(df_display)

            # Tombol download CSV full
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Unduh Seluruh Hasil CSV", data=csv, file_name="hasil_screening.csv", mime="text/csv")
        else:
            st.warning("Tidak ada hasil yang dapat ditampilkan.")
