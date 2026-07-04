# PRD — Sistem Deteksi Tingkat Pemahaman Mahasiswa Berdasarkan Hasil Kuis Berbasis Data

## 1. Ringkasan Produk

Produk ini adalah aplikasi pembelajaran yang membantu mahasiswa mengukur tingkat pemahaman mereka setelah mempelajari materi digital seperti modul, ringkasan, atau artikel. Sistem menerima materi berbentuk teks, menghasilkan kuis secara otomatis, mencatat hasil pengerjaan pengguna, lalu menampilkan tingkat pemahaman, insight singkat, dan rekomendasi belajar lanjutan. [file:42]

Proyek ini berada dalam tema **Digital Education & Skill Development** dan dikembangkan sebagai capstone project oleh tim **TP-G005** dengan empat anggota aktif dari learning path AI. [file:42]

## 2. Latar Belakang Masalah

Dalam proses pembelajaran mandiri, mahasiswa sering membaca materi tanpa mengetahui apakah mereka benar-benar memahami isi pembelajaran tersebut. Di sisi lain, pembuatan kuis sebagai alat evaluasi masih banyak dilakukan secara manual dan tidak selalu tersedia setelah materi dipelajari. [file:42]

Akibatnya, ada gap antara proses belajar dan proses evaluasi. Pengguna dapat mengonsumsi materi, tetapi tidak memperoleh umpan balik yang cukup untuk mengetahui tingkat penguasaan, kelemahan, atau langkah belajar berikutnya. [file:42]

## 3. Problem Statement

Bagaimana membangun sistem sederhana yang dapat mengubah materi pembelajaran menjadi kuis secara otomatis, menganalisis hasil pengerjaan kuis, lalu mendeteksi tingkat pemahaman pengguna beserta insight dan rekomendasi belajar dalam satu alur yang terintegrasi. [file:42]

## 4. Research Questions

1. Bagaimana sistem dapat mengubah materi pembelajaran menjadi kuis secara otomatis. [file:42]
2. Bagaimana mendeteksi tingkat pemahaman mahasiswa berdasarkan hasil kuis. [file:42]
3. Bagaimana memberikan insight dan rekomendasi belajar berdasarkan hasil analisis data. [file:42]

## 5. Tujuan Produk

### Goals

- Membantu mahasiswa mengevaluasi pemahaman setelah membaca materi.
- Mengurangi kebutuhan pembuatan kuis manual.
- Menyediakan hasil evaluasi yang lebih informatif daripada skor saja.
- Mengintegrasikan proses input materi, pembuatan kuis, pengerjaan kuis, analisis, dan rekomendasi dalam satu aplikasi. [file:42]

### Non-goals

- Tidak mendukung input materi kompleks seperti PDF, video, atau audio pada MVP. [file:42]
- Tidak membangun sistem login, autentikasi, atau manajemen akun yang kompleks pada MVP. [file:42]
- Tidak membangun learning management system penuh seperti manajemen kelas, forum, atau penugasan multi-user.
- Tidak melatih model bahasa besar dari nol (gunakan pretrained model + fine-tuning ringan).
- Tidak menggunakan GPU di runtime production (inference di CPU; training pakai Colab).

## 6. Target Pengguna

### Primary User
- Mahasiswa yang belajar secara mandiri menggunakan materi digital berbentuk teks. [file:42]

### Secondary User
- Pengguna umum atau pelajar lain yang ingin menguji pemahaman dari materi bacaan singkat.

## 7. Nilai Utama Produk

Produk ini tidak hanya memberikan nilai akhir, tetapi juga:
- Menghasilkan kuis dari materi yang dimasukkan pengguna.
- Menunjukkan performa pengerjaan seperti skor dan waktu.
- Mengklasifikasikan tingkat pemahaman menjadi kategori sederhana.
- Memberikan insight yang menjelaskan kemungkinan alasan hasil tersebut.
- Memberikan rekomendasi belajar yang dapat ditindaklanjuti. [file:42]

## 8. Asumsi Produk

- Input materi diberikan dalam bentuk teks atau hasil copy-paste.
- **Quiz generator menggunakan pendekatan Deep Learning** dengan pretrained model Indonesian T5 (`Wikidepia/IndoT5-base`), di-fine-tune pada dataset TyDiQA-id via Google Colab.
- **Analisis tingkat pemahaman menggunakan ML konvensional** (scikit-learn Random Forest), dilatih pada dataset sintetis yang di-generate secara programatis.
- **Insight & rekomendasi tetap berbasis template** dengan sub-conditions — bukan dari model NLG yang sulit dikontrol kualitasnya untuk MVP.
- Backend dibangun dengan Python untuk logika quiz, analisis, dan ML/DL inference; frontend dibangun dengan React + TypeScript sesuai proposal. [file:42]
- Inference DL di CPU — wait time saat generate kuis ~15-40 detik (sekali per session); seluruh interaction lain instant.

## 9. User Flow

### Flow utama
1. Pengguna membuka aplikasi.
2. Pengguna menempelkan materi pembelajaran dalam bentuk teks.
3. Sistem memproses teks dan menghasilkan kuis.
4. Pengguna mengerjakan kuis dalam antarmuka web.
5. Sistem menghitung hasil seperti jumlah benar, jumlah salah, skor, dan waktu pengerjaan.
6. Sistem menganalisis hasil dengan aturan sederhana.
7. Sistem menampilkan tingkat pemahaman, insight, rekomendasi, dan grafik sederhana. [file:42]

## 10. Fitur Inti MVP

### 10.1 Input Materi
Pengguna dapat memasukkan materi pembelajaran dalam bentuk teks melalui text area.

**Acceptance criteria**
- Pengguna dapat paste teks minimal 1 paragraf.
- Sistem menolak input kosong.
- Sistem menampilkan pesan validasi jika teks terlalu pendek.

### 10.2 Quiz Generator (Deep Learning)
Sistem menghasilkan kuis otomatis dari materi yang dimasukkan menggunakan **fine-tuned IndoT5 model**.

**Scope MVP**
- Format soal pilihan ganda (4 opsi per soal, 1 jawaban benar).
- Jumlah soal default 5 (bisa di-tweak).
- **Implementasi**: pretrained `Wikidepia/IndoT5-base` di-fine-tune pada TyDiQA-id (Indonesian QA dataset) via Google Colab.
- Hosting model: Hugging Face Hub (public, gratis).
- Inference di runtime: CPU, expected 15-40s per quiz.

**Acceptance criteria**
- Setelah materi dikirim, sistem menampilkan daftar soal.
- Setiap soal memiliki pertanyaan, 4 opsi jawaban, dan satu jawaban benar.
- Soal tetap relevan dengan isi materi input.
- Loading state di frontend visible selama proses generate (tidak terkesan freeze).
- Fallback ke rule-based generator kalau DL inference gagal.

### 10.3 Halaman Pengerjaan Kuis
Pengguna menjawab kuis pada halaman interaktif.

**Acceptance criteria**
- Pengguna bisa memilih jawaban satu per soal.
- Pengguna bisa submit jawaban setelah semua atau sebagian soal dijawab.
- Sistem merekam total jawaban benar, salah, dan waktu pengerjaan.

### 10.4 Hasil Kuis
Sistem menampilkan hasil dasar pengerjaan kuis.

**Acceptance criteria**
- Sistem menampilkan skor akhir.
- Sistem menampilkan jumlah benar dan salah.
- Sistem menampilkan durasi pengerjaan.
- Sistem menampilkan ringkasan performa.

### 10.5 Deteksi Tingkat Pemahaman (Conventional ML)
Sistem mengklasifikasikan tingkat pemahaman pengguna menggunakan **scikit-learn Random Forest classifier**.

**Kategori**
- Tinggi (`high`)
- Sedang (`medium`)
- Rendah (`low`)

**Input fitur** (dari `EvaluationResult`)
- `score_percentage`
- `time_taken_seconds`
- `correct_count`
- `wrong_count`
- `unanswered_count`
- (opsional turunan) avg time per question, time variance

**Training data**: dataset sintetis (~10,000 sample) yang di-generate dengan rule-based labeling + noise injection. Generator-nya di `backend/ml/classifier/data_generation.py`.

**Algoritma**: Random Forest Classifier (sklearn). Alasan dipilih:
- Tabular features dengan dataset sedang → sklearn ideal (DL overkill)
- Interpretable — bisa expose feature importance ke dosen sebagai insight tambahan
- Robust terhadap outlier
- Training cepat (<1 menit di CPU lokal)

**Acceptance criteria**
- Setiap hasil kuis memiliki satu kategori tingkat pemahaman.
- Model accuracy ≥ 85% di test set sintetis.
- Logika dan training reproducible — `python -m ml.classifier.train` dari `backend/`.
- Hasil klasifikasi muncul langsung di halaman hasil.
- Fallback ke rule-based kalau model loading gagal.

### 10.6 Insight Otomatis
Sistem menjelaskan kenapa pengguna mendapat kategori tertentu.

**Contoh pendekatan**
- Skor tinggi dan waktu stabil → pemahaman baik.
- Skor sedang dengan waktu lama → kemungkinan memahami sebagian, tetapi masih ragu.
- Skor rendah dengan banyak salah → materi belum dipahami secara cukup.

**Acceptance criteria**
- Insight ditampilkan dalam bahasa yang mudah dipahami.
- Insight selaras dengan data hasil kuis.
- Insight tidak hanya mengulang skor mentah.

### 10.7 Rekomendasi Belajar
Sistem memberikan saran langkah selanjutnya.

**Contoh rekomendasi**
- Ulangi membaca bagian inti materi.
- Fokus ke konsep yang paling banyak salah.
- Kerjakan kuis ulang setelah review singkat.
- Gunakan ringkasan poin penting sebelum mengulang tes.

**Acceptance criteria**
- Setiap kategori pemahaman memiliki rekomendasi yang sesuai.
- Rekomendasi bersifat praktis dan dapat dilakukan pengguna.

### 10.8 Grafik Sederhana
Sistem menampilkan visualisasi sederhana dari hasil pengerjaan.

**Contoh**
- Bar chart benar vs salah
- Donut/pie chart persentase hasil
- Indikator kategori pemahaman

**Acceptance criteria**
- Grafik tampil di halaman hasil.
- Data grafik konsisten dengan hasil analisis.

## 11. Kebutuhan Fungsional

- Sistem harus menerima input materi dalam bentuk teks. [file:42]
- Sistem harus dapat mengubah materi menjadi kuis menggunakan **model Deep Learning** (IndoT5 fine-tuned).
- Sistem harus menyediakan halaman pengerjaan kuis.
- Sistem harus menghitung skor, benar, salah, dan waktu pengerjaan. [file:42]
- Sistem harus menentukan tingkat pemahaman menggunakan **model Machine Learning konvensional** (Random Forest classifier).
- Sistem harus menampilkan insight otomatis berbasis template + sub-conditions. [file:42]
- Sistem harus menampilkan rekomendasi belajar berbasis template + sub-conditions. [file:42]
- Sistem harus menampilkan grafik sederhana. [file:42]
- Sistem harus mempertahankan fallback rule-based untuk DL/ML components agar tidak ada hard failure di demo.

## 12. Kebutuhan Non-Fungsional

### Usability
- Antarmuka sederhana dan mudah dipahami oleh pengguna pertama.
- Alur utama dapat diselesaikan tanpa panduan panjang.

### Performance
- Waktu generate kuis untuk input teks normal sebaiknya tidak lebih dari beberapa detik pada lingkungan demo.
- Hasil analisis ditampilkan segera setelah submit.

### Reliability
- Validasi input harus mencegah error umum seperti teks kosong.
- Sistem harus tetap berjalan untuk materi pendek hingga sedang.

### Maintainability
- Arsitektur modular antara generator kuis, evaluator hasil, engine insight, dan frontend.
- Rule klasifikasi dapat diubah tanpa membongkar seluruh sistem.

## 13. Batasan Sistem

- Input hanya berupa teks, bukan PDF, DOCX, video, atau link. [file:42]
- Quiz generation masih sederhana dan tidak mengejar kualitas setara platform komersial berbasis LLM. [file:42]
- Analisis memakai metode sederhana tanpa model AI kompleks sebagai inti sistem. [file:42]
- Tidak ada sistem login dan database kompleks pada versi awal. [file:42]

## 14. Arsitektur Teknis

### Frontend
- React
- TypeScript [file:42]
- Tailwind CSS + shadcn-style design system (lihat DESIGN.md)

### Backend (web app layer)
- Python (FastAPI) untuk HTTP layer + orchestration. [file:42]
- Pydantic untuk schema validation.

### ML/DL Layer
- **PyTorch + Hugging Face Transformers** — Quiz Generator (Audry's DL).
- **scikit-learn** — Understanding Classifier (Desta's ML konvensional).
- **Pandas** — data processing untuk Ariq's evaluator + Desta's training data analysis.

### Training Infrastructure
- **Google Colab** (free tier dengan GPU T4) untuk fine-tuning IndoT5.
- Lokal CPU untuk training sklearn Random Forest.

### Model Distribution
- **Hugging Face Hub** — fine-tuned IndoT5 di-push ke account Audry, di-load di backend startup.
- **Git** — sklearn `.pkl` artifact di-commit langsung (kecil, < 5MB).

### Tools
- GitHub untuk version control. [file:42]
- VS Code sebagai development environment. [file:42]
- Hugging Face Hub untuk distribusi model.

### Arsitektur logis
- Frontend menerima input materi dan menampilkan hasil.
- Backend `app/` menerima request, memvalidasi, memanggil layer `ml/` untuk inference (DL untuk QG, ML konv untuk klasifikasi), menjalankan business logic (scoring, insight, recommendation), lalu mengembalikan hasil.
- ML layer (`backend/ml/`) menjalankan model loading + inference. Model artifacts di-load sekali saat app startup.
- Komponen analisis terdiri dari evaluator (rule-based), classifier (ML), insight engine (template), recommendation engine (template).

## 15. Logika Analisis

### Variabel input (dari `EvaluationResult`)
- `score_percentage`
- `time_taken_seconds`
- `correct_count`
- `wrong_count`
- `unanswered_count`

### Klasifikasi tingkat pemahaman (ML — Random Forest)
Diserahkan ke model sklearn yang dilatih pada dataset sintetis. Aturan **deterministik** berikut digunakan sebagai **ground truth saat generate training data** (bukan sebagai aturan runtime — model yang menentukan):

- **Tinggi** (training label): `score_percentage >= 80` AND `time_taken <= total_questions * 90s`
- **Sedang** (training label): `50 <= score_percentage < 80` OR (skor tinggi tetapi waktu lebih dari 1.5x baseline)
- **Rendah** (training label): `score_percentage < 50` OR (banyak unanswered)

Setelah training, model akan generalize berdasarkan pattern di data sintetis (bukan strict rule). Lihat `backend/ml/classifier/data_generation.py` untuk detail logika synthetic generation.

### Insight (template + sub-conditions, di `insight_engine.py`)
Base templates per level (lihat BRAND.md §7.6) + sub-conditions:
- Tinggi + waktu efisien → "kamu paham dan cepat menyerap materi"
- Tinggi + waktu lambat → "kamu paham tapi mungkin masih ragu-ragu"
- Sedang + many unanswered → "kamu skip beberapa soal — coba lebih confident"
- Rendah + all answered → "kamu coba semua tapi banyak salah — konsep dasar perlu di-review"
- dst (Desta extend untuk minimal 6-8 variasi)

### Rekomendasi (template + sub-conditions, di `recommendation_engine.py`)
Sama dengan insight tapi fokus pada **next action**. Brand mechanic: medium/low recommendations ditutup dengan "...lalu asah lagi." (callback brand name).

## 16. Metrik Keberhasilan MVP

### Product metrics
- Pengguna berhasil membuat kuis dari materi teks.
- Pengguna berhasil menyelesaikan kuis tanpa error.
- Sistem menampilkan hasil, kategori, insight, dan rekomendasi secara lengkap.

### Quality metrics
- Relevansi soal terhadap materi dinilai layak oleh tim penguji internal.
- Hasil klasifikasi konsisten terhadap rule yang sudah didefinisikan.
- Tidak ada blocker bug pada flow utama demo.

## 17. Skenario Demo

### Skenario 1
- Pengguna memasukkan materi singkat.
- Sistem menghasilkan 5 soal pilihan ganda.
- Pengguna mengerjakan kuis.
- Sistem menampilkan skor 80, kategori tinggi, insight, dan rekomendasi.

### Skenario 2
- Pengguna memasukkan materi lain.
- Pengguna mengerjakan kuis dengan banyak jawaban salah.
- Sistem menampilkan kategori rendah dan rekomendasi review.

## 18. Timeline Pengembangan

### Minggu 1
- Finalisasi ide dan desain sistem.
- Finalisasi requirement produk.
- Setup environment React dan backend Python. [file:42]

### Minggu 2
- Implementasi input materi.
- Implementasi quiz generator sederhana. [file:42]

### Minggu 3
- Implementasi halaman pengerjaan kuis.
- Implementasi penyimpanan dan pengolahan hasil kuis. [file:42]

### Minggu 4
- Implementasi analisis hasil.
- Implementasi fitur insight dan rekomendasi. [file:42]

### Minggu 5
- Integrasi frontend dan backend.
- Testing, debugging, dan finalisasi presentasi. [file:42]

## 19. Pembagian Tugas Tim

| Anggota | Peran | Tanggung Jawab |
|---|---|---|
| Audry Nabila Anastasya | Backend — Quiz Generator | Mengembangkan fitur perubahan materi menjadi kuis [file:42] |
| Ariq Marwan Permana | Backend — Data & Analisis | Mengolah hasil kuis dan menghitung performa pengguna [file:42] |
| Desta Anandhika Rajendra Maheswara | Backend — Logic & Insight | Membuat aturan deteksi pemahaman, insight, dan rekomendasi [file:42] |
| Ravi Arnan Irianto | Frontend — React & TypeScript | Mengembangkan UI dan integrasi frontend-backend [file:42] |

## 20. Risiko dan Mitigasi

### Kompleksitas sistem terlalu tinggi
Sistem yang terlalu luas dapat menghambat progres dan menurunkan kualitas. Mitigasinya adalah menjaga scope tetap kecil, modular, dan fokus pada fitur inti. [file:42]

### Keterbatasan waktu
Waktu 4–5 minggu dapat menyebabkan fitur tidak selesai jika scope melebar. Mitigasinya adalah milestone mingguan, prioritas MVP, dan evaluasi progres rutin. [file:42]

### Kekurangan data atau contoh materi
Kurangnya bahan uji dapat memengaruhi kualitas quiz generation dan analisis. Mitigasinya adalah memakai data dummy, materi sintetis, dan hasil kuis pengguna sebagai bahan evaluasi awal. [file:42]

### Koordinasi tim kurang efektif
Miskomunikasi dapat memperlambat integrasi. Mitigasinya adalah pembagian peran jelas, meeting mingguan, dan tracking progres bersama. [file:42]

## 21. MVP Acceptance Checklist

- [ ] Pengguna dapat memasukkan materi teks.
- [ ] Sistem dapat menghasilkan kuis otomatis.
- [ ] Pengguna dapat mengerjakan kuis sampai submit.
- [ ] Sistem menghitung skor dan waktu.
- [ ] Sistem menampilkan kategori pemahaman.
- [ ] Sistem menampilkan insight otomatis.
- [ ] Sistem menampilkan rekomendasi belajar.
- [ ] Sistem menampilkan grafik sederhana.
- [ ] Frontend dan backend terintegrasi dengan baik.
- [ ] Flow demo berjalan tanpa error kritis.

## 22. Future Enhancements

- Dukungan file PDF atau dokumen.
- Analisis berbasis topik atau per submateri (TF-IDF clustering — bisa dieksplor Ariq sebagai bonus).
- Riwayat pengerjaan kuis.
- Dashboard perkembangan pengguna.
- Login dan penyimpanan data persisten.
- LLM-based question generation (e.g., Llama / GPT API) — saat ini pakai T5 fine-tuned untuk MVP.
- GPU inference untuk turun-kan latency (saat ini CPU only).
- Real user data collection untuk re-training Random Forest dengan distribusi data nyata (bukan sintetis).
