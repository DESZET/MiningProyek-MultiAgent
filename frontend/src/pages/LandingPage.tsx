import React, { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { 
  FileText, 
  Link as LinkIcon, 
  Brain, 
  LineChart, 
  Zap, 
  Trophy,
  ArrowRight
} from "lucide-react";
import { ScoreChart } from "@/components/ScoreChart";
import { HeroMascot } from "@/components/HeroMascot";
import { UnderstandingBadge } from "@/components/UnderstandingBadge";

/**
 * Utility component for scroll-reveal animations respecting prefers-reduced-motion.
 */
function ScrollReveal({ 
  children, 
  delay = 0,
  className = ""
}: { 
  children: React.ReactNode, 
  delay?: number,
  className?: string
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [inView, setInView] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      const entry = entries[0];
      if (entry && entry.isIntersecting) {
        setInView(true);
        observer.unobserve(entry.target);
      }
    }, { threshold: 0.1 });

    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  return (
    <div 
      ref={ref} 
      className={`transition-all duration-700 ease-out motion-reduce:transition-none motion-reduce:opacity-100 motion-reduce:translate-y-0 ${
        inView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
      } ${className}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  );
}

export function LandingPage() {
  const [heroMounted, setHeroMounted] = useState(false);
  
  useEffect(() => {
    // Trigger entrance animation on mount
    setHeroMounted(true);
  }, []);

  return (
    <div className="flex flex-col gap-24 pt-8 pb-12 overflow-x-hidden">
      {/* Hero Section */}
      <section className="grid md:grid-cols-2 gap-12 items-center">
        <div className="space-y-6">
          <h1 
            className={`text-5xl lg:text-6xl font-medium leading-[1.05] tracking-tight text-text-primary transition-all duration-700 ease-out motion-reduce:transition-none motion-reduce:opacity-100 motion-reduce:translate-y-0 ${heroMounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
          >
            Asah lagi sampai paham.
          </h1>
          <p 
            className={`text-lg text-text-secondary max-w-lg transition-all duration-700 ease-out delay-150 motion-reduce:transition-none motion-reduce:opacity-100 motion-reduce:translate-y-0 ${heroMounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
          >
            Sistem deteksi tingkat pemahaman yang mengubah materi belajarmu menjadi kuis interaktif, menganalisis hasilnya, dan memberikan rekomendasi personal.
          </p>
          <div 
            className={`pt-4 transition-all duration-700 ease-out delay-300 motion-reduce:transition-none motion-reduce:opacity-100 motion-reduce:translate-y-0 ${heroMounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
          >
            <Link
              to="/app"
              className="group inline-flex items-center gap-2 rounded-pill border border-status-tinggi bg-status-tinggi px-8 py-3 text-base font-medium text-[var(--status-tinggi-text)] shadow-level-1 outline-none transition-all hover:opacity-90 hover:scale-[1.02] active:scale-95 focus-visible:[box-shadow:var(--focus-ring)]"
            >
              Coba sekarang
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Link>
          </div>
        </div>
        
        <div 
          className={`flex justify-center transition-all duration-1000 ease-out delay-200 motion-reduce:transition-none motion-reduce:opacity-100 motion-reduce:translate-x-0 ${heroMounted ? "opacity-100 translate-x-0" : "opacity-0 translate-x-8"}`}
        >
          <HeroMascot />
        </div>
      </section>

      {/* Product Preview Section (Supabase style) */}
      <section className="grid lg:grid-cols-2 gap-16 items-center">
        <ScrollReveal className="order-2 lg:order-1">
          <div className="relative rounded-2xl border border-border-standard bg-bg-alt p-6 shadow-level-2 transform rotate-1 hover:rotate-0 transition-transform duration-500">
            {/* Fake App Mockup */}
            <div className="flex items-center justify-between border-b border-border-standard pb-4 mb-6">
              <div>
                <div className="text-sm font-medium text-text-secondary mb-1">SKOR AKHIR</div>
                <div className="text-4xl font-bold text-text-primary">85%</div>
              </div>
              <UnderstandingBadge level="high" className="scale-110 origin-right" />
            </div>
            
            <div className="space-y-4">
              <ScoreChart data={{ correct: 4, wrong: 1, unanswered: 0 }} />
              
              <div className="rounded-xl border border-border-standard bg-bg-page p-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className="h-8 w-8 rounded-full bg-status-tinggi flex items-center justify-center">
                    <Zap className="h-4 w-4 text-white" />
                  </div>
                  <div className="font-medium text-text-primary">Insight</div>
                </div>
                <p className="text-sm text-text-secondary leading-relaxed">
                  Kamu menjawab sebagian besar soal dengan benar dan waktu pengerjaan yang cepat. Pemahamanmu pada topik ini sudah sangat baik.
                </p>
              </div>
            </div>
          </div>
        </ScrollReveal>
        
        <div className="order-1 lg:order-2 space-y-6">
          <ScrollReveal>
            <h2 className="text-3xl font-medium text-text-primary">Analisis Pemahaman Mendalam</h2>
          </ScrollReveal>
          <ScrollReveal delay={150}>
            <p className="text-lg text-text-secondary">
              Kami tidak hanya menghitung berapa jawaban yang benar. Sistem kami menganalisis pola jawaban dan waktu pengerjaan untuk mendeteksi tingkat pemahamanmu yang sebenarnya.
            </p>
          </ScrollReveal>
          <ScrollReveal delay={300}>
            <ul className="space-y-4 mt-6">
              {[
                "Deteksi level pemahaman: Tinggi, Sedang, atau Rendah.",
                "Distribusi jawaban benar, salah, dan tidak terjawab.",
                "Insight personal berdasarkan performa.",
                "Rekomendasi langkah belajar selanjutnya."
              ].map((item, i) => (
                <li key={i} className="flex items-start gap-3">
                  <div className="mt-1 h-1.5 w-1.5 rounded-full bg-brand-button flex-shrink-0" />
                  <span className="text-text-secondary">{item}</span>
                </li>
              ))}
            </ul>
          </ScrollReveal>
        </div>
      </section>

      {/* How it works */}
      <section className="space-y-12">
        <ScrollReveal>
          <h2 className="text-3xl font-medium text-center text-text-primary">Cara Kerja</h2>
        </ScrollReveal>
        <div className="grid md:grid-cols-3 gap-6">
          <ScrollReveal delay={100}>
            <StepCard 
              number="1"
              title="Pilih Materi"
              description="Masukkan teks, paste URL artikel, atau upload file PDF yang ingin kamu pelajari."
            />
          </ScrollReveal>
          <ScrollReveal delay={200}>
            <StepCard 
              number="2"
              title="Kerjakan Kuis"
              description="Jawab pertanyaan satu-per-satu yang dibuat otomatis berdasarkan materimu."
            />
          </ScrollReveal>
          <ScrollReveal delay={300}>
            <StepCard 
              number="3"
              title="Lihat Analisis"
              description="Dapatkan insight tentang tingkat pemahamanmu dan rekomendasi langkah selanjutnya."
            />
          </ScrollReveal>
        </div>
      </section>

      {/* Features Grid */}
      <section className="space-y-12">
        <ScrollReveal>
          <h2 className="text-3xl font-medium text-center text-text-primary">Fitur Unggulan</h2>
        </ScrollReveal>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            { icon: <FileText className="h-6 w-6 text-status-tinggi" />, title: "Input Multi-source", desc: "Mendukung materi dari teks langsung, link web, maupun dokumen PDF." },
            { icon: <Brain className="h-6 w-6 text-status-tinggi" />, title: "Kuis Terfokus", desc: "Satu pertanyaan setiap waktu agar kamu bisa fokus penuh tanpa terdistraksi." },
            { icon: <LineChart className="h-6 w-6 text-status-tinggi" />, title: "Analisis Pemahaman", desc: "Tidak hanya skor, tapi deteksi seberapa jauh tingkat pemahamanmu." },
            { icon: <Zap className="h-6 w-6 text-status-tinggi" />, title: "Insight & Rekomendasi", desc: "Umpan balik personal berdasarkan pola jawaban dan kecepatan menjawabmu." },
            { icon: <Trophy className="h-6 w-6 text-status-tinggi" />, title: "Gamifikasi Seru", desc: "Kumpulkan XP, pertahankan streak harian, dan raih badge pencapaian." },
            { icon: <LinkIcon className="h-6 w-6 text-status-tinggi" />, title: "Mastery Per-topik", desc: "Lacak perkembangan pemahamanmu untuk berbagai topik berbeda dari waktu ke waktu." }
          ].map((feat, i) => (
            <ScrollReveal key={i} delay={i * 100}>
              <FeatureCard icon={feat.icon} title={feat.title} description={feat.desc} />
            </ScrollReveal>
          ))}
        </div>
      </section>

      {/* Bottom CTA & Footer */}
      <footer className="mt-12 space-y-16">
        <ScrollReveal>
          <div className="rounded-3xl bg-bg-alt border border-border-standard p-10 text-center space-y-6 shadow-level-1">
            <h2 className="text-3xl font-medium text-text-primary">Siap untuk menguji pemahamanmu?</h2>
            <p className="text-text-secondary max-w-xl mx-auto">
              Tidak ada cara yang lebih baik untuk belajar selain dengan menguji diri sendiri. Mulai asah kemampuanmu sekarang.
            </p>
            <div className="pt-2">
              <Link
                to="/app"
                className="group inline-flex items-center gap-2 rounded-pill border border-status-tinggi bg-status-tinggi px-8 py-3 text-base font-medium text-[var(--status-tinggi-text)] shadow-level-1 outline-none transition-all hover:opacity-90 hover:scale-[1.02] active:scale-95 focus-visible:[box-shadow:var(--focus-ring)]"
              >
                Mulai Belajar
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Link>
            </div>
          </div>
        </ScrollReveal>

        <div className="border-t border-border-standard pt-8 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-text-muted pb-4">
          <div>
            &copy; {new Date().getFullYear()} Asahlagi. Dibuat oleh Tim TP-G005.
          </div>
          <a 
            href="https://github.com/ravi-arnan/TempaCapstoneProject" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-2 hover:text-text-primary transition-colors"
          >
            <span>GitHub Repository</span>
          </a>
        </div>
      </footer>
    </div>
  );
}

function StepCard({ number, title, description }: { number: string, title: string, description: string }) {
  return (
    <div className="flex flex-col items-center text-center space-y-3 p-6 rounded-2xl border border-border-standard bg-bg-page shadow-level-1 transition-all duration-300 hover:-translate-y-1 hover:shadow-level-2 hover:border-status-tinggi">
      <div className="flex items-center justify-center h-12 w-12 rounded-full bg-status-tinggi text-[var(--status-tinggi-text)] font-bold text-xl mb-2">
        {number}
      </div>
      <h3 className="text-xl font-medium text-text-primary">{title}</h3>
      <p className="text-text-secondary leading-relaxed">{description}</p>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="p-6 rounded-2xl border border-border-standard bg-bg-page shadow-level-1 text-left space-y-3 transition-all duration-300 hover:-translate-y-1 hover:shadow-level-2 hover:border-status-tinggi group">
      <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-bg-alt group-hover:bg-status-tinggi/10 transition-colors">
        {icon}
      </div>
      <h3 className="text-lg font-medium text-text-primary">{title}</h3>
      <p className="text-text-secondary text-sm leading-relaxed">{description}</p>
    </div>
  );
}
