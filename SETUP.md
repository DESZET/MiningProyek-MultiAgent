# Panduan Setup — Pertama Kali (Setelah Pull/Clone)

> Ikuti langkah-langkah ini secara berurutan. Estimasi waktu: ~10 menit.

---

## Prasyarat

Pastikan sudah terinstall di komputer kamu:

| Tools | Versi minimal | Cek |
|---|---|---|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Git | bebas | `git --version` |

---

## 1. Clone Repo

```bash
git clone https://github.com/DESZET/MiningProyek-MultiAgent.git
cd MiningProyek-MultiAgent
```

---

## 2. Setup Backend (Python / FastAPI)

### 2a. Buat virtual environment

```bash
cd backend
python -m venv .venv
```

### 2b. Aktifkan virtual environment

**Windows (CMD):**
```cmd
.venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Mac / Linux:**
```bash
source .venv/bin/activate
```

### 2c. Install dependencies

```bash
pip install -r requirements.txt
```

### 2d. Buat file `.env`

Copy dari contoh:

```bash
# Windows CMD
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

Lalu buka file `.env` dan isi minimal ini agar backend bisa jalan:

```env
# Wajib diisi jika ingin fitur chat aktif
GITHUB_TOKEN=your_github_pat_here

# Opsional — kalau tidak diisi, fitur gamification & login Google nonaktif
# tapi core quiz tetap berjalan
DATABASE_URL=
GOOGLE_CLIENT_ID=
HF_SPACE_URL=
```

> **GITHUB_TOKEN** — buat di https://github.com/settings/tokens (fine-grained PAT, centang akses "Models")

### 2e. Jalankan backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend berjalan di → **http://localhost:8000**  
Cek health: **http://localhost:8000/health**

---

## 3. Setup Frontend (React / Vite)

Buka terminal **baru** (jangan tutup terminal backend).

### 3a. Masuk ke folder frontend

```bash
cd frontend
```

### 3b. Install dependencies

```bash
npm install
```

### 3c. Buat file `.env.development`

```bash
# Windows CMD
copy .env.example .env.development

# Mac/Linux
cp .env.example .env.development
```

Isi file `.env.development` (biasanya sudah cukup default):

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=
```

### 3d. Jalankan frontend

```bash
npm run dev
```

Frontend berjalan di → **http://localhost:5173**

---

## 4. Verifikasi

Buka browser dan akses:

- Frontend: http://localhost:5173 → halaman web muncul ✅
- Backend API docs: http://localhost:8000/docs → Swagger UI muncul ✅
- Health check: http://localhost:8000/health → `{"status": "ok"}` ✅

---

## Struktur Terminal yang Harus Berjalan

Kamu perlu **2 terminal aktif** sekaligus:

```
Terminal 1 (Backend):
  cd backend
  .venv\Scripts\activate   ← aktifkan venv dulu
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Terminal 2 (Frontend):
  cd frontend
  npm run dev
```

---

## Troubleshooting

**`uvicorn` tidak ditemukan?**
→ Pastikan virtual environment sudah diaktifkan (ada `(.venv)` di awal terminal)

**`npm install` error?**
→ Cek versi Node.js minimal 18: `node --version`

**CORS error di browser?**
→ Pastikan backend berjalan di port 8000 dan `VITE_API_BASE_URL=http://localhost:8000` sudah benar di `.env.development`

**Fitur login Google tidak muncul?**
→ Normal jika `VITE_GOOGLE_CLIENT_ID` kosong — app tetap bisa dipakai sebagai guest

**Fitur chat tidak berfungsi?**
→ Isi `GITHUB_TOKEN` di `backend/.env`
