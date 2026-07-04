import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

vi.mock("@/hooks/useProfileData", () => ({ useProfileData: vi.fn() }));
vi.mock("@/context/AuthContext", () => ({ useAuth: vi.fn() }));

import { ProfilePage } from "@/pages/ProfilePage";
import { useProfileData } from "@/hooks/useProfileData";
import { useAuth } from "@/context/AuthContext";

function renderProfile() {
  return render(
    <MemoryRouter>
      <ProfilePage />
    </MemoryRouter>,
  );
}

const loggedInAuth = {
  user: { id: "u1", name: "Ravi", email: "ravi@x.test", avatar_url: null, device_id: "d1" },
  isConfigured: true,
  login: vi.fn(),
  logout: vi.fn(),
};

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(useAuth).mockReturnValue(loggedInAuth);
});

describe("ProfilePage", () => {
  it("shows a loading state", () => {
    vi.mocked(useProfileData).mockReturnValue({ status: "loading" });
    renderProfile();
    expect(screen.getByText(/memuat profilmu/i)).toBeInTheDocument();
  });

  it("shows an unavailable state", () => {
    vi.mocked(useProfileData).mockReturnValue({ status: "unavailable" });
    renderProfile();
    expect(screen.getByText(/profil belum aktif/i)).toBeInTheDocument();
  });

  it("renders identity, gamification summary, badges and recent history when ready", () => {
    vi.mocked(useProfileData).mockReturnValue({
      status: "ready",
      stats: {
        total_xp: 250,
        level: 3,
        xp_into_level: 50,
        xp_for_next_level: 100,
        current_streak: 2,
        longest_streak: 5,
      },
      achievements: [
        { code: "first_quiz", label: "Langkah Pertama", description: "d", icon: "Sparkles", unlocked_at: "2026-06-07T00:00:00Z" },
      ],
      summary: { total_quizzes: 7, average_score: 80, total_xp: 250, best_score: 100, worst_score: 60 },
      recent: [
        { quiz_id: "q1", score: 80, understanding_level: "high", xp_earned: 10, completed_at: "2026-06-07T00:00:00Z", topic: "Fotosintesis" },
      ],
    });
    renderProfile();
    expect(screen.getByText("Ravi")).toBeInTheDocument();
    expect(screen.getByText("ravi@x.test")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument(); // level tile
    expect(screen.getByText("7")).toBeInTheDocument(); // total quizzes tile
    expect(screen.getByText("Langkah Pertama")).toBeInTheDocument(); // badge
    expect(screen.getByText("Fotosintesis")).toBeInTheDocument(); // recent row
    expect(screen.getByText(/lihat semua riwayat/i)).toBeInTheDocument();
  });
});
