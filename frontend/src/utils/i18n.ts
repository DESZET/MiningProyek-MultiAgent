/**
 * Indonesian-default copy library — mirrors BRAND.md §7.
 * Source of truth: /BRAND.md
 *
 * Components MUST NOT inline copy strings. Always import from here.
 */

import type { UnderstandingLevel } from "@/types/result";

// ============================================================================
// Page titles & headers (BRAND.md §7.1)
// ============================================================================

export const PAGE_TITLES = {
  home: "Asahlagi. Asah lagi sampai paham.",
  quiz: "Kuis sedang berlangsung",
  result: "Hasil. Asahlagi",
} as const;

export const HOMEPAGE = {
  hero: "Asah lagi sampai paham.",
  subtitle:
    "Tempel materi belajarmu, kerjakan kuis otomatis, dan ukur tingkat pemahamanmu.",
} as const;

// ============================================================================
// Share result (ROADMAP §4.2)
// ============================================================================

export const RESULT_SHARE = {
  button: "Bagikan hasil",
  copied: "Tertaut tersalin!",
  shareTitle: "Hasil kuis Asahlagi",
  shareText: (pct: number) =>
    `Aku dapat ${pct}% di kuis Asahlagi. Coba ukur pemahamanmu juga!`,
  sharedBanner:
    "Ini hasil kuis yang dibagikan seseorang. Buat kuismu sendiri untuk mengukur pemahamanmu.",
  ctaCreate: "Buat kuismu sendiri",
} as const;

// ============================================================================
// Onboarding tour (ROADMAP §4.6) — voice per BRAND.md: "kamu", calm, no patronising
// ============================================================================

export const ONBOARDING = {
  replayLabel: "Lihat panduan singkat",
  next: "Lanjut",
  prev: "Kembali",
  done: "Selesai",
  steps: {
    welcome: {
      title: "Halo, selamat datang di Asahlagi 👋",
      body: "Tempel materi belajarmu, kerjakan kuis otomatis, lalu lihat seberapa paham kamu. Kuajak keliling sebentar, ya.",
    },
    source: {
      title: "Pilih sumber materi",
      body: "Kamu bisa mulai dari teks, tautan artikel, atau berkas PDF. Pilih yang paling pas.",
    },
    settings: {
      title: "Atur kuismu",
      body: "Tentukan jumlah soal dan tingkat kesulitan kalau mau. Boleh juga dibiarkan default.",
    },
    input: {
      title: "Tempel materimu di sini",
      body: "Masukkan materi (minimal 100 karakter), lalu tekan Mulai Mengasah untuk membuat kuis.",
    },
    daily: {
      title: "Atau coba Tantangan Harian",
      body: "Kuis pilihan tiap hari dengan bonus XP. Cara cepat menjaga streak belajarmu.",
    },
    finish: {
      title: "Setelah kuis",
      body: "Kamu akan lihat skor, tingkat pemahaman, insight, dan rekomendasi langkah berikutnya. Selamat mengasah!",
    },
  },
} as const;

// ============================================================================
// §4.8 Batch 2 — Leaderboard + Weekly goal
// ============================================================================

export const LEADERBOARD = {
  eyebrow: "Komunitas",
  title: "Papan Peringkat",
  subtitle: "Peringkat berdasarkan total XP",
  you: "Kamu",
  yourRankTemplate: (rank: number) => `Peringkatmu: #${rank}`,
  levelTemplate: (level: number) => `Lv ${level}`,
  empty: "Belum ada yang masuk papan peringkat. Jadilah yang pertama!",
} as const;

export const WEEKLY_GOAL = {
  title: "Target Mingguan",
  progressTemplate: (done: number, target: number) =>
    `${done} dari ${target} kuis minggu ini`,
  remainingTemplate: (n: number) =>
    n === 1 ? "1 kuis lagi menuju target" : `${n} kuis lagi menuju target`,
  met: "Target minggu ini tercapai! 🎉",
} as const;

// ============================================================================
// §4.8 Batch 2-B — Preferences + Material bookmarks
// ============================================================================

export const LEARNING_PREFS = {
  title: "Preferensi Belajar",
  subtitle: "Jadi default saat membuat kuis baru",
  countLabel: "Jumlah soal default",
  difficultyLabel: "Tingkat kesulitan default",
  shuffleLabel: "Acak urutan opsi",
  weeklyGoalLabel: "Target kuis per minggu",
  saved: "Tersimpan",
  unavailable: "Preferensi belum aktif (butuh database).",
} as const;

export const BOOKMARKS = {
  save: "Simpan materi",
  saved: "Materi tersimpan",
  title: "Materi Tersimpan",
  empty: "Belum ada materi tersimpan. Simpan materi untuk diasah lagi nanti.",
  practice: "Asah",
  delete: "Hapus",
  deleteConfirm: "Hapus materi tersimpan ini?",
} as const;

// ============================================================================
// Quiz settings — pre-generate (ROADMAP §4.3)
// ============================================================================

export const QUIZ_SETTINGS = {
  toggle: "Atur kuis",
  toggleHint: "Jumlah soal, tingkat kesulitan, acak opsi",
  countLabel: "Jumlah soal",
  difficultyLabel: "Tingkat kesulitan",
  shuffleLabel: "Acak urutan opsi",
  difficulty: {
    easy: "Mudah",
    medium: "Sedang",
    hard: "Sulit",
  },
} as const;

// ============================================================================
// Button labels (BRAND.md §7.2)
// ============================================================================

export const BUTTON_LABELS = {
  homePrimary: "Mulai Mengasah",
  homePrimaryReturn: "Asah Lagi",
  homeLoading: "Sedang menyiapkan kuis...",
  submitQuiz: "Selesai & Lihat Hasil",
  skipQuestion: "Lewati",
  prevQuestion: "Sebelumnya",
  nextQuestion: "Lanjut",
  jumpToUnanswered: "Lihat soal yang belum",
  resultRetry: "Asah Lagi",
  resultRetryLoading: "Menyusun pertanyaan baru...",
  resetAll: "Mulai Ulang",
  backToHome: "Kembali ke Beranda",
} as const;

// ============================================================================
// Empty states (BRAND.md §7.3)
// ============================================================================

export const EMPTY_STATES = {
  materialPlaceholder: "Tempel materi belajarmu di sini...",
  materialHelp:
    "Minimal 100 karakter. Bisa berupa ringkasan, artikel, atau bab buku.",
  urlPlaceholder: "https://contoh.com/artikel-pelajaran",
  urlHelp:
    "Tempel link artikel pelajaran. Sistem akan mengambil isi artikelnya secara otomatis.",
  pdfHelp:
    "Upload file PDF (maksimal 10 MB). Sistem akan ekstrak teks dari PDF. Pastikan PDF berisi teks, bukan scan atau gambar.",
  pdfDropzone: "Klik atau seret file PDF ke sini",
  pdfDropActive: "Lepaskan PDF di sini",
  pdfChangeFile: "klik untuk ganti file",
  pdfMustBePdf: "File harus berformat .pdf",
  pdfTooLarge: "File terlalu besar. Maksimal 10 MB.",
  pleaseWait: "Mohon tunggu",
  quizLoading: "Sedang menyusun pertanyaan...",
  submitProcessing: "Menganalisis hasil...",
} as const;

// ============================================================================
// Quiz page strings
// ============================================================================

export const QUIZ_PAGE = {
  title: "Kuis sedang berlangsung",
  allAnswered: "Semua soal sudah terjawab",
  remainingTemplate: (n: number) => `Sisa ${n} soal`,
  answeredProgressTemplate: (answered: number, total: number) =>
    `${answered} / ${total} terjawab`,
  questionLabelTemplate: (index: number, total: number) =>
    `Soal ${index + 1} / ${total}`,
  minCharsTemplate: (current: number) => `${current} / 100 karakter (minimal)`,
  progressRestored: "Progres dari sesi sebelumnya dipulihkan.",
  shortcutHint: "Tekan ? untuk shortcut keyboard",
} as const;

// ============================================================================
// Keyboard shortcut help overlay
// ============================================================================

export const SHORTCUT_HELP = {
  title: "Shortcut Keyboard",
  closeHint: "Tekan Esc atau klik di luar untuk tutup",
  shortcuts: [
    { keys: ["1", "2", "3", "4"], action: "Pilih opsi A, B, C, atau D" },
    { keys: ["Enter"], action: "Lanjut ke soal berikutnya" },
    { keys: ["J", "↓"], action: "Soal berikutnya" },
    { keys: ["K", "↑"], action: "Soal sebelumnya" },
    { keys: ["?"], action: "Buka / tutup bantuan shortcut" },
    { keys: ["Esc"], action: "Tutup overlay" },
  ],
} as const;

// ============================================================================
// Card labels (result page sections)
// ============================================================================

export const CARD_LABELS = {
  insight: "Insight",
  recommendation: "Rekomendasi",
  chartDistribution: "Distribusi Jawaban",
  reviewSection: "Tinjau Jawaban",
} as const;

// ============================================================================
// Per-question review badges & helper strings
// ============================================================================

export const REVIEW_LABELS = {
  correct: "BENAR",
  wrong: "SALAH",
  unanswered: "TIDAK DIJAWAB",
  yourAnswer: "Pilihanmu",
  correctAnswer: "Jawaban benar",
  noAnswer: "Tidak dijawab",
} as const;

// ============================================================================
// Theme toggle labels
// ============================================================================

export const THEME_LABELS = {
  light: "Light",
  dark: "Dark",
  switchToLight: "Ganti ke mode terang",
  switchToDark: "Ganti ke mode gelap",
} as const;

// ============================================================================
// Gamification (XP, streak, level, badges)
// ============================================================================

export const GAMIFICATION = {
  levelShort: "Lv",
  xpEarnedTemplate: (n: number) => `+${n} XP`,
  levelUpTemplate: (level: number) => `Naik ke level ${level}!`,
  streakTemplate: (n: number) => `Streak ${n} hari`,
  newBadgeTitle: "Badge baru terbuka",
} as const;

// ============================================================================
// Daily Challenge (ROADMAP §4.8i) — surfaced on Home & Profil
// ============================================================================

export const DAILY_CHALLENGE = {
  eyebrow: "Tantangan Harian",
  title: "Tantangan hari ini",
  body: "Satu kuis pilihan tiap hari dengan topik kejutan. Selesaikan untuk bonus XP dan jaga streak-mu.",
  bonusBadge: "+50 XP bonus",
  start: "Mulai Tantangan",
  starting: "Menyiapkan tantangan...",
} as const;

// ============================================================================
// Streak (ROADMAP §4.8i) — streak calendar / strip
// ============================================================================

export const STREAK = {
  title: "Streak Belajar",
  currentLabel: "Streak saat ini",
  longestLabel: "Terpanjang",
  dayUnit: "hari",
  emptyHint: "Kerjakan kuis hari ini untuk memulai streak.",
} as const;

// ============================================================================
// Navigation labels
// ============================================================================

export const NAV_LABELS = {
  progress: "Progresku",
  profile: "Profilku",
} as const;

// ============================================================================
// Auth — Google login (post-MVP, ROADMAP §4.7)
// ============================================================================

export const AUTH_LABELS = {
  accountMenu: "Menu akun",
  guestName: "Pengguna",
  logout: "Keluar",
  loginError: "Login gagal. Coba lagi sebentar.",
  menuProfile: "Profilku",
  menuProgress: "Progresku",
  menuHistory: "Riwayat Kuis",
  menuLeaderboard: "Papan Peringkat",
  menuSettings: "Pengaturan",
} as const;

// ============================================================================
// Progress page (score trend + per-topic mastery) — Gamification Fase 3
// ============================================================================

export const PROGRESS_PAGE = {
  title: "Progresku",
  subtitle: "Lihat perkembangan skormu dan topik yang masih perlu diasah.",
  summaryQuizzes: "TOTAL KUIS",
  summaryAvg: "RATA-RATA SKOR",
  summaryXp: "TOTAL XP",
  trendTitle: "Tren Skor",
  trendCaption: "Rata-rata skor per hari",
  trendEmpty: "Belum ada cukup data tren. Kerjakan beberapa kuis dulu, ya.",
  masteryTitle: "Pemahaman per Topik",
  masteryCaption: "Diurutkan dari yang paling perlu diasah",
  masteryEmpty:
    "Belum ada topik terlacak. Topik muncul otomatis setelah kamu mengerjakan kuis.",
  masteryWeakestHint: "Paling perlu diasah",
  attemptsTemplate: (n: number) => (n === 1 ? "1 kuis" : `${n} kuis`),
  emptyTitle: "Belum ada progres",
  emptyBody:
    "Kerjakan kuis pertamamu untuk mulai melacak pemahaman dan tren skormu.",
  emptyCta: "Mulai Mengasah",
  loading: "Memuat progresmu...",
  unavailableTitle: "Fitur progres belum aktif",
  unavailableBody:
    "Pelacakan progres sedang tidak tersedia. Fitur kuis tetap bisa kamu pakai seperti biasa.",
} as const;

// ============================================================================
// Profile hub (ROADMAP §4.8a) — identity + gamification summary + badges
// ============================================================================

export const PROFILE_PAGE = {
  eyebrow: "Profilku",
  title: "Profilku",
  subtitle: "Ringkasan perjalanan belajarmu di Asahlagi.",
  guestName: "Tamu",
  guestNote:
    "Kamu memakai mode tamu. Progresmu tersimpan di perangkat ini. Masuk dengan Google agar progres aman dan tersinkron.",
  summaryLevel: "LEVEL",
  summaryXp: "TOTAL XP",
  summaryQuizzes: "TOTAL KUIS",
  badgesTitle: "Pencapaian",
  badgesCaption: "Badge yang sudah kamu buka",
  badgesEmpty: "Belum ada badge. Kerjakan kuis untuk membuka yang pertama.",
  recentTitle: "Kuis Terakhir",
  recentEmpty: "Belum ada riwayat. Yuk kerjakan kuis pertamamu.",
  recentSeeAll: "Lihat semua riwayat",
  linkProgress: "Lihat tren & pemahaman per topik",
  linkSettings: "Pengaturan",
  loading: "Memuat profilmu...",
  unavailableTitle: "Profil belum aktif",
  unavailableBody:
    "Fitur profil sedang tidak tersedia. Fitur kuis tetap bisa kamu pakai seperti biasa.",
} as const;

// ============================================================================
// History page (ROADMAP §4.8c) — DB-backed quiz history
// ============================================================================

export const HISTORY_PAGE = {
  eyebrow: "Riwayat",
  title: "Riwayat Kuis",
  subtitle: "Semua kuis yang sudah kamu kerjakan, terbaru di atas.",
  summaryQuizzes: "TOTAL KUIS",
  summaryAvg: "RATA-RATA",
  summaryBest: "SKOR TERBAIK",
  summaryXp: "TOTAL XP",
  scoreUnit: "skor",
  xpTemplate: (n: number) => `+${n} XP`,
  noTopic: "Tanpa topik",
  loading: "Memuat riwayatmu...",
  emptyTitle: "Belum ada riwayat",
  emptyBody:
    "Setiap kuis yang kamu selesaikan akan muncul di sini. Mulai kuis pertamamu, yuk.",
  emptyCta: "Mulai Mengasah",
  unavailableTitle: "Riwayat belum aktif",
  unavailableBody:
    "Pelacakan riwayat sedang tidak tersedia. Fitur kuis tetap bisa kamu pakai seperti biasa.",
} as const;

// ============================================================================
// Settings page (ROADMAP §4.8b) — theme, account, logout
// ============================================================================

export const SETTINGS_PAGE = {
  eyebrow: "Pengaturan",
  title: "Pengaturan",
  subtitle: "Atur tampilan dan akunmu.",
  appearanceTitle: "Tampilan",
  appearanceCaption: "Pilih tema terang atau gelap.",
  accountTitle: "Akun",
  accountCaption: "Informasi akun yang sedang masuk.",
  accountEmailLabel: "Email",
  accountNameLabel: "Nama",
  guestTitle: "Mode tamu",
  guestBody:
    "Kamu belum masuk. Progres tersimpan di perangkat ini. Masuk dengan Google untuk mengamankan progresmu.",
  logout: "Keluar dari akun",
} as const;

// ============================================================================
// Source type labels (for HomePage tabs)
// ============================================================================

export const SOURCE_TYPE_LABELS = {
  text: "Teks",
  url: "Tautan Web",
  pdf: "File PDF",
} as const;

// ============================================================================
// Loading progress messages — rotated during DL inference (~9s wait)
// ============================================================================

export const LOADING_PROGRESS_MESSAGES = [
  "Membaca materimu...",
  "Menyusun pertanyaan...",
  "Memeriksa kualitas pertanyaan...",
  "Hampir selesai...",
] as const;

// ============================================================================
// Sample materials (one-click "try a demo" on the homepage)
// ============================================================================

export const SAMPLE_MATERIALS = {
  fotosintesis: {
    label: "Coba contoh: Fotosintesis",
    text:
      "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau " +
      "dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di " +
      "kloroplas dan menghasilkan oksigen sebagai produk samping. Reaksi " +
      "terang berlangsung di tilakoid, sedangkan reaksi gelap berlangsung " +
      "di stroma. Klorofil berperan menyerap cahaya pada panjang gelombang " +
      "biru dan merah, sementara karotenoid membantu menangkap cahaya hijau.",
  },
} as const;

// ============================================================================
// Error messages (BRAND.md §7.4 + API.md §6)
// ============================================================================

export const ERROR_MESSAGES: Record<string, string> = {
  MATERIAL_EMPTY: "Materi belum ada. Tempel teks materimu dulu, ya.",
  MATERIAL_TOO_SHORT:
    "Materinya terlalu pendek. Tambahkan minimal 100 karakter agar sistem bisa membuat kuis.",
  MATERIAL_TOO_LONG:
    "Materinya terlalu panjang. Maksimal 20.000 karakter, coba ringkas dulu bagian intinya.",
  QUIZ_GENERATION_FAILED:
    "Gagal membuat kuis. Coba materi lain atau ulangi sebentar lagi.",
  PDF_INVALID:
    "File PDF tidak bisa diproses. Pastikan file PDF valid dan tidak rusak.",
  PDF_EMPTY:
    "PDF tidak punya teks yang bisa diekstrak. Mungkin PDF berupa scan atau gambar. Coba ketik ulang materinya.",
  PDF_TOO_SHORT:
    "Teks PDF terlalu pendek. Coba PDF dengan konten lebih banyak.",
  PDF_TOO_LONG:
    "PDF terlalu panjang. Sistem ambil 20.000 karakter pertama saja.",
  URL_INVALID: "URL tidak valid. Pastikan dimulai dengan http:// atau https://",
  URL_FETCH_FAILED:
    "Gagal mengambil halaman dari URL. Pastikan URL bisa diakses publik.",
  URL_EMPTY_CONTENT:
    "Halaman tidak punya artikel yang bisa diambil. Mungkin butuh login atau isinya kebanyakan gambar.",
  URL_TOO_SHORT:
    "Artikel di URL terlalu pendek. Coba artikel yang lebih panjang.",
  URL_TOO_LONG:
    "Artikel terlalu panjang. Sistem ambil 20.000 karakter pertama saja.",
  QUIZ_NOT_FOUND:
    "Kuis tidak ditemukan atau sudah kedaluwarsa. Mulai ulang dari halaman utama.",
  ANSWERS_LENGTH_MISMATCH:
    "Ada ketidaksesuaian jumlah jawaban. Coba mulai kuis dari awal.",
  INVALID_OPTION_INDEX: "Pilihan jawaban tidak valid. Coba pilih ulang.",
  INVALID_QUESTION_ID: "Soal tidak ditemukan dalam kuis. Coba mulai ulang.",
  INVALID_TIME: "Waktu pengerjaan tidak valid. Coba mulai ulang.",
  EVALUATION_FAILED:
    "Gagal menganalisis hasil kuis. Coba kirim ulang sebentar lagi.",
  INTERNAL_ERROR: "Ada hambatan dari sisi kami. Coba lagi sebentar.",
};

// Codes where the backend's `detail` is more context-aware than our canned
// copy (e.g. QUIZ_GENERATION_FAILED has several distinct failure modes, each
// with its own actionable detail). For these, prefer the backend message.
const PREFER_BACKEND_DETAIL = new Set([
  "QUIZ_GENERATION_FAILED",
  "PDF_INVALID",
  "URL_FETCH_FAILED",
  "URL_EMPTY_CONTENT",
  "MATERIAL_LOW_QUALITY", // show the specific "unsuitable material" hint
]);

export function getErrorMessage(code: string | undefined, fallback?: string) {
  if (code && PREFER_BACKEND_DETAIL.has(code) && fallback) return fallback;
  if (code && ERROR_MESSAGES[code]) return ERROR_MESSAGES[code];
  return fallback ?? ERROR_MESSAGES.INTERNAL_ERROR!;
}

// ============================================================================
// Result page dynamic headers (BRAND.md §7.5)
// ============================================================================

export const RESULT_HEADERS: Record<
  UnderstandingLevel,
  { headline: string; subhead: string }
> = {
  high: {
    headline: "Pemahamanmu mantap.",
    subhead: "Konsep utama materi sudah kamu kuasai.",
  },
  medium: {
    headline: "Pemahamanmu sudah baik, masih bisa lebih tajam.",
    subhead: "Beberapa konsep masih perlu diteguhkan.",
  },
  low: {
    headline: "Yuk asah lagi.",
    subhead: "Materi ini perlu dibaca ulang dengan fokus.",
  },
};

// ============================================================================
// Status badge labels (BRAND.md §7.9)
// ============================================================================

export const UNDERSTANDING_LEVEL_LABEL: Record<UnderstandingLevel, string> = {
  high: "TINGGI",
  medium: "SEDANG",
  low: "RENDAH",
};

// ============================================================================
// Stat labels (BRAND.md §7.8)
// ============================================================================

export const STAT_LABELS = {
  score: "SKOR",
  time: "WAKTU",
  correct: "BENAR",
  wrong: "SALAH",
  unanswered: "TIDAK DIJAWAB",
} as const;

// ============================================================================
// Helpers
// ============================================================================

export function formatSeconds(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

/** Format an ISO timestamp as a short Indonesian date, e.g. "7 Jun 2026". */
export function formatDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return new Intl.DateTimeFormat("id-ID", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(d);
}

/** Coerce a stored understanding-level string to the typed union, or null. */
export function toUnderstandingLevel(
  value: string,
): UnderstandingLevel | null {
  const v = value.trim().toLowerCase();
  return v === "high" || v === "medium" || v === "low" ? v : null;
}
