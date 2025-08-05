## 🔁 **Alur Kerja (Workflow) Sistem Screening CV**

---

### ✅ 1. **Form Input Kandidat (kandidat.py)**

**Tujuan:**
Kandidat mengisi data pribadi dan mengunggah file CV. Semua data dan file disimpan ke server (dalam folder khusus untuk setiap kandidat).

**Alur:**

1. Kandidat membuka `kandidat.py` (form).
2. Mengisi:

   * Nama lengkap
   * Gender
   * Tempat & tanggal lahir
   * Domisili sekarang
   * Universitas & jurusan
   * Email, no. telp, GPA
   * Memilih **Jobdesc (posisi yang dilamar)**
   * Mengunggah CV (`.pdf` atau `.docx`)
3. Saat menekan tombol **"Submit dan Kirim ke Backend"**, maka:

   * Dibuat folder unik di `./kandidat_data/{nama_kandidat_uuid}`.
   * CV disimpan di folder tersebut.
   * Semua data disimpan dalam `data.json`.

📁 **Contoh struktur folder yang dihasilkan:**

```
kandidat_data/
├── yoel_pratomo_a2c9e7f1/
│   ├── yoel_cv.pdf
│   └── data.json
```

---

### ✅ 2. **Panel Admin Screening CV (admin.py)**

**Tujuan:**
Admin melihat semua data kandidat, melakukan pencarian berdasarkan jobdesc, kota, atau universitas, dan menilai **tingkat kecocokan (match)** CV kandidat terhadap jobdesc tertentu berdasarkan kata kunci (keywords).

**Alur:**

1. Admin membuka `admin.py`.
2. Sistem membaca seluruh folder di `./kandidat_data/`.
3. Untuk setiap folder:

   * Memuat `data.json`.
   * Memuat dan membaca isi CV (.pdf / .docx).
   * Mengecek kecocokan kata kunci sesuai jobdesc yang dipilih kandidat.
   * Menghitung **match percentage (%)**.
4. Semua data dirender ke dalam tabel interaktif.
5. Admin dapat:

   * Menyaring hasil berdasarkan **kota**, **universitas**, atau **jobdesc**.
   * Mengurutkan berdasarkan kecocokan (asc/desc).
   * Mengunduh CSV hasil screening.
   * Mengunduh CV masing-masing kandidat.

---

## 🔐 **Keamanan Data dan Arsitektur**

* **Privasi Aman:**
  Kandidat tidak tahu kata kunci jobdesc karena hanya memilih posisi. Kata kunci berada di `admin.py`, **tidak terekspos di frontend**.

* **Struktur Modular & Aman:**

  * `kandidat.py` hanya menyimpan.
  * `admin.py` hanya membaca & memproses.

---

## 🔁 Diagram Ringkas Alur

```plaintext
[ Kandidat Submit Form ]
        |
        ▼
Data + CV disimpan di:
📁 kandidat_data/{nama_uuid}/
      ├── data.json
      └── file_cv.pdf/docx

        |
        ▼

[ Admin Jalankan admin.py ]
        |
        ▼
🔁 Baca semua folder
📖 Muat data.json + CV
🔍 Hitung skor cocok berdasarkan jobdesc
📊 Tampilkan hasil screening
📤 Unduh CV / Hasil CSV
```

---

## 🛠️ Pengembangan Selanjutnya

* 🔐 Tambahkan validasi email/no. telp dengan regex.
* 📩 Notifikasi email otomatis setelah submit (opsional).
* 🔎 Tambahkan preview isi CV langsung di admin (opsional).
* 📦 Tambahkan opsi **arsip/tolak** kandidat agar tidak ditampilkan lagi.

---
* Hosting di Streamlit Cloud / Hugging Face.

Tinggal bilang saja ya, Yoel.
