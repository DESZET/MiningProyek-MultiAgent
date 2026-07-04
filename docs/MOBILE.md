# Mobile Strategy — Asahlagi (Capacitor, Android-first)

**Status**: Planning. Belum dieksekusi.
**Owner**: Ravi (Frontend, track mobile)
**Created**: 2026-05-25
**Last updated**: 2026-05-25

Acuan: `GAMIFICATION.md`, `ROADMAP.md`, `BRAND.md`.

---

## 1. Ringkasan keputusan

| Aspek | Keputusan |
|---|---|
| Pendekatan | **Capacitor** (bungkus web app React yang sudah ada) |
| Platform | **Android saja** (iOS dibatalkan: tim tidak punya Mac) |
| Push notification | **Ditunda ke roadmap** (nilai jual mobile terbesar untuk gamifikasi) |
| Alasan | Frontend sudah React+Vite, Capacitor reuse seluruh codebase tanpa rewrite |

---

## 2. Kenapa Capacitor (vs alternatif)

| Opsi | Effort | Catatan |
|---|---|---|
| **Capacitor** (dipilih) | Rendah | Bungkus React web yang ada jadi APK/IPA + akses API native. Codebase sama. |
| React Native | Tinggi | Harus rewrite UI dari nol. Tidak masuk akal, UI sudah jadi di React-web. |
| PWA | Sangat rendah | Installable web tanpa app store, tapi push iOS terbatas. Opsi kalau tidak butuh Play Store. |

Karena UI React-web sudah matang, Capacitor = jalur paling efisien menuju native + Play Store + (nanti) push notification.

---

## 3. Prasyarat (HARUS beres dulu)

1. **Backend deploy ke URL publik HTTPS.** App mobile tidak bisa pakai `localhost:8000`. Item deploy di ROADMAP berubah dari opsional jadi **prasyarat mobile**.
   - **Keputusan: Hugging Face Spaces (Docker)** — tanpa kartu kredit. HTTPS otomatis (`*.hf.space`) memenuhi syarat Android. Config di `huggingface/backend/`; langkah lengkap di `DEPLOY.md`.
   - Catatan: free Space sleep ~48 jam idle (wake ~30-60s). Render tetap jadi alternatif (butuh kartu) lewat `render.yaml`.
2. **`VITE_API_BASE_URL`** di build mobile diarahkan ke backend HTTPS publik (bukan localhost).
3. **CORS**: backend harus mengizinkan origin Capacitor. Android default pakai `https://localhost` (androidScheme https). Tambahkan ke `CORS_ALLOWED_ORIGINS`.
4. **HTTPS wajib**: Android memblokir cleartext (HTTP) traffic secara default. Backend produksi harus HTTPS.

---

## 4. Langkah setup (Android)

```bash
cd frontend
npm install @capacitor/core @capacitor/cli
npx cap init "Asahlagi" "com.asahlagi.app" --web-dir=dist
npm install @capacitor/android
npx cap add android

# tiap kali update web:
npm run build          # output ke dist/
npx cap sync           # salin web build + plugin ke proyek android
npx cap open android   # buka di Android Studio untuk build APK
```

`capacitor.config.ts`:
- `webDir: 'dist'`
- `server.androidScheme: 'https'` (default; konsisten dengan CORS)
- untuk produksi: API URL di-bake via `VITE_API_BASE_URL` saat `npm run build`

**APK untuk demo**: build debug APK di Android Studio, sideload ke HP (tanpa signing/Play Store). Cukup untuk demo capstone.

---

## 5. Pertimbangan khusus mobile

| Hal | Status MVP | Catatan |
|---|---|---|
| Identitas (device ID) | localStorage jalan di WebView | Enhancement: pakai `@capacitor/preferences` (storage native) biar lebih stabil |
| Input PDF | `<input type=file>` buka native picker di Android WebView | Tidak perlu ubah untuk MVP |
| Cleartext traffic | OK kalau backend HTTPS | Android blok HTTP non-secure |
| Offline | Quiz gen butuh jaringan (HF Space) | Online-required untuk MVP |
| App icon / splash | Pakai logo Asahlagi (`assets/logo-icon.svg`) | Generate via `@capacitor/assets` |

---

## 6. Roadmap mobile (ditunda)

Diurutkan dari nilai tertinggi:

1. **Push notification** (Capacitor Push + Firebase Cloud Messaging)
   - Reminder streak ("jaga streak-mu hari ini"), daily goal, level-up nudge
   - **Nyambung ke Fase 4 (Desta) nudge logic** — logika nudge jadi sumber konten push
   - Nilai jual mobile terbesar untuk gamifikasi (pola Duolingo)
2. **iOS support** — DIBATALKAN untuk sekarang (tim tidak punya Mac, dan butuh Apple Developer $99/tahun). Bisa ditinjau ulang nanti jika ada akses Mac.
3. **Native storage** (`@capacitor/preferences`) untuk device ID + cache
4. **Native file picker** (`@capacitor/filesystem`) untuk PDF, UX lebih baik
5. **Publish Play Store** (Google Play Console, $25 sekali bayar) — perlu release signing
6. **Offline mode** — rule-based generator + cache untuk kuis tanpa jaringan

---

## 7. Ownership & sequencing

- **Track**: Ravi (frontend → native wrap)
- **Urutan**:
  1. Web MVP + gamifikasi solid (jangan fork effort)
  2. Deploy backend HTTPS (prasyarat)
  3. Wrap Capacitor Android (additive, codebase sama)
  4. Enhancement native (storage, file picker)
  5. Push notification (roadmap, nyambung Desta Fase 4)
  6. iOS + Play Store (roadmap)

---

## 8. Catatan capstone

Mobile via Capacitor = ekspansi scope dari proposal awal (yang fokus web). **Angkat ke advisor (Rosyiidah)** bareng topik gamifikasi. Untuk demo capstone, web app tetap deliverable utama; APK Android jadi nilai tambah, bukan pengganti.

---

## 9. Decision log

| Tanggal | Keputusan | Reason |
|---|---|---|
| 2026-05-25 | Android-first, Capacitor, push notification ditunda | Android cukup untuk demo; push butuh setup FCM terpisah |
| 2026-05-25 | iOS dibatalkan | Tim tidak punya Mac (Xcode wajib Mac) + Apple Developer $99/tahun |
| 2026-05-25 | Hosting backend: Render (free tier) | Sempat dipilih, lalu dibatalkan karena tetap minta kartu |
| 2026-05-25 | Hosting backend: HF Spaces (Docker) | Final. Tanpa kartu, HTTPS otomatis, tim familiar. Config di `huggingface/backend/`. Render disimpan sebagai alternatif (`render.yaml`) |
