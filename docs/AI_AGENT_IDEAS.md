# AI Agent Ideas — Asahlagi

Dokumen ini berisi catatan arsitektur AI yang sudah ada, keterbatasannya,
dan ide pengembangan multi-agent untuk masa depan.

---

## Arsitektur AI Saat Ini (Single-Agent + ML Pipeline)

```
User
 ├── /chat atau /chat/ask ──→ GPT-4o-mini (GitHub Models)
 │                              ↑ context: chat history + quiz history DB
 └── /quiz/generate ──────────→ IndoT5 (HF Space / local CPU / rule-based)
      └── /quiz/submit ────────→ Pipeline linear:
                                  evaluator
                                    → Random Forest classifier
                                      → insight engine (rule-based)
                                        → recommendation engine (rule-based)
```

### Komponen AI yang Ada

| Komponen | File | Tipe | Fungsi |
|---|---|---|---|
| Asahi chatbot | `backend/app/services/asahi_chat.py` | LLM (GPT-4o-mini) | Ngobrol & feedback hasil kuis |
| Quiz Generator | `backend/ml/generator/inference.py` | IndoT5 Transformer | Generate soal dari teks materi |
| Understanding Classifier | `backend/ml/classifier/inference.py` | Random Forest (sklearn) | Klasifikasi tingkat pemahaman: high/medium/low |
| Insight Engine | `backend/app/services/insight_engine.py` | Rule-based template | Teks insight dari hasil kuis |
| Recommendation Engine | `backend/app/services/recommendation_engine.py` | Rule-based template | Rekomendasi belajar berikutnya |
| Material Quality | `backend/app/services/material_quality.py` | Rule-based | Validasi materi sebelum diproses |
| Submit Coordinator | `backend/app/services/submit_coordinator.py` | Orchestrator | Pipeline linear submit kuis |

### Keterbatasan Arsitektur Sekarang

- Setiap komponen berjalan **terpisah** dan tidak saling berkomunikasi
- Asahi (LLM) tidak bisa memicu aksi lain seperti generate soal baru atau cek riwayat secara aktif
- Insight & rekomendasi masih **template statis**, bukan dihasilkan LLM
- Tidak ada **feedback loop** — hasil kuis tidak dipakai untuk memperbaiki soal berikutnya
- Quiz Generator (IndoT5) dan Asahi (GPT) adalah dua sistem terpisah yang tidak terhubung

---

## Ide Pengembangan: Multi-Agent Architecture

### Konsep Dasar

Multi-agent = beberapa AI "agen" dengan peran berbeda yang bisa saling berkomunikasi
dan mendelegasikan tugas ke satu sama lain melalui sebuah orchestrator.

### Rancangan Sistem Multi-Agent

```
User
  ↓
[Agent Orchestrator]  ← koordinasi semua agen
  ├── [Agent Extractor]       → ekstrak & bersihkan teks dari PDF/URL/input
  ├── [Agent Quiz Maker]      → generate & validasi soal (IndoT5 + LLM polish)
  ├── [Agent Evaluator]       → nilai jawaban + klasifikasi pemahaman
  ├── [Agent Insight]         → generate insight personal pakai LLM (bukan template)
  └── [Agent Asahi]           → chatbot dengan akses ke tools
        ├── tool: get_quiz_history(user_id)
        ├── tool: generate_new_quiz(topic)
        ├── tool: get_weak_topics(user_id)
        └── tool: search_study_tips(topic)
```

### Ide Spesifik Per Agen

#### 1. Agent Extractor (baru)
- Input: URL, PDF file, atau teks mentah
- Tugas: ekstrak teks, deteksi bahasa, bersihkan noise, nilai kualitas materi
- Output: teks bersih + metadata (bahasa, topik perkiraan, jumlah kalimat)
- Improvement dari sekarang: tambah LLM untuk summarize materi panjang sebelum dikirim ke quiz maker

#### 2. Agent Quiz Maker (upgrade dari yang ada)
- Input: teks bersih dari Agent Extractor
- Tugas: generate soal lalu polish/validasi pakai LLM
- Tahap 1: IndoT5 generate soal kasar (seperti sekarang)
- Tahap 2: LLM (GPT-4o-mini) polish soal: perbaiki grammar, pastikan distractor masuk akal
- Tahap 3: LLM validasi: apakah soal benar-benar terjawab dari materi?
- Output: soal yang sudah divalidasi

#### 3. Agent Evaluator (upgrade dari yang ada)
- Input: soal + jawaban user
- Tugas: nilai jawaban + klasifikasi pemahaman + identifikasi topik lemah
- Pakai Random Forest yang sudah ada untuk klasifikasi
- Tambah analisis topik lemah yang lebih granular (per subtopik, bukan keseluruhan)
- Output: EvaluationResult yang lebih kaya

#### 4. Agent Insight (upgrade dari yang ada)
- Input: EvaluationResult dari Agent Evaluator
- Tugas: generate insight & rekomendasi yang personal pakai LLM
- Berbeda dari sekarang: bukan template statis, tapi prompt ke LLM dengan data hasil
- Contoh output: "Kamu kuat di bagian definisi, tapi keliru di 3 soal aplikasi rumus. Coba fokus latihan soal hitungan minggu ini."
- Output: insight + rekomendasi dalam bahasa natural

#### 5. Agent Asahi (upgrade dari yang ada)
- Input: pesan user
- Upgrade utama: Asahi punya **tools** yang bisa dipanggil sendiri
- Tool `get_quiz_history`: ambil riwayat kuis user dari DB
- Tool `generate_new_quiz`: trigger quiz baru dari topik tertentu
- Tool `get_weak_topics`: ambil topik lemah user dari history
- Tool `search_study_tips`: cari tips belajar dari knowledge base internal
- Dengan tools, Asahi bisa jawab "Buatkan aku soal tentang fotosintesis lagi" secara langsung

---

## Ide Fitur Baru yang Butuh Multi-Agent

### Adaptive Quiz
Soal berikutnya disesuaikan otomatis berdasarkan performa sebelumnya.
Butuh Agent Evaluator yang bisa komunikasi ke Agent Quiz Maker.

### Study Path Generator
Generate jalur belajar personal: "Kamu perlu kuasai A dulu sebelum B."
Butuh Agent Insight yang bisa baca history + generate urutan topik.

### Auto-Retry Question
Kalau salah di soal tertentu, sistem otomatis generate soal baru
dengan topik yang sama tapi dari sudut berbeda.
Butuh feedback loop antara Agent Evaluator → Agent Quiz Maker.

### Real-time Feedback Saat Kuis
Asahi bisa komentar di tengah kuis (bukan hanya di akhir).
Butuh Agent Asahi yang bisa dipanggil per-soal, bukan hanya setelah submit.

---

## Framework yang Bisa Dipakai

| Framework | Kelebihan | Cocok untuk |
|---|---|---|
| **LangChain Agents** | Populer, dokumentasi lengkap, banyak tools built-in | Agent Asahi dengan tools |
| **AutoGen (Microsoft)** | Multi-agent conversation, bisa agent vs agent | Orchestrator + multiple agents |
| **CrewAI** | Role-based agents, mudah disetup | Pipeline Quiz Maker → Evaluator → Insight |
| **LangGraph** | State machine untuk agent flow, lebih kontrol | Complex orchestration dengan kondisi |

Rekomendasi untuk proyek ini: **LangChain + LangGraph** karena sudah familier
dengan OpenAI-compatible API (GitHub Models yang sudah dipakai) dan bisa
diintegrasikan bertahap tanpa harus rewrite semua.

---

## Roadmap Migrasi (Bertahap)

### Fase 1 — Quick Win (tanpa rewrite besar)
- Upgrade Agent Insight: ganti template statis dengan LLM prompt
- Tambah tools ke Asahi: `get_quiz_history` dan `get_weak_topics`
- Estimasi: 1-2 minggu

### Fase 2 — Agent Quiz Maker
- Tambah LLM polish step setelah IndoT5 generate soal
- Validasi soal dengan LLM sebelum dikirim ke user
- Estimasi: 2-3 minggu

### Fase 3 — Full Multi-Agent
- Implementasi orchestrator (LangGraph)
- Pisahkan semua komponen jadi agent mandiri
- Tambah feedback loop antar agent
- Estimasi: 1-2 bulan

---

## Catatan untuk AI Agent yang Baca Dokumen Ini

Proyek ini adalah **aplikasi kuis pembelajaran** berbahasa Indonesia.
Stack: FastAPI (backend), React + Vite (frontend), Python 3.13.

File-file kunci yang relevan:
- `backend/app/services/asahi_chat.py` — chatbot LLM utama
- `backend/app/services/submit_coordinator.py` — pipeline orchestrator saat ini
- `backend/ml/generator/inference.py` — quiz generation ML
- `backend/ml/classifier/inference.py` — understanding classification ML
- `docs/ARCHITECTURE.md` — arsitektur lengkap proyek
- `docs/API.md` — dokumentasi semua endpoint
- `docs/ML.md` — detail semua model ML

Saat menambah fitur AI baru:
1. Ikuti pola thin-wrapper: logic di `services/`, route di `routes/`
2. Selalu sediakan fallback rule-based kalau model tidak tersedia
3. Jangan taruh API key/token di code — pakai environment variable dari `.env`
4. Test dengan materi bahasa Indonesia (bukan Inggris)
