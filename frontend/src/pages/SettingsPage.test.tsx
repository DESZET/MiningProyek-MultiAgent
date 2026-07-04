import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

vi.mock("@/context/AuthContext", () => ({ useAuth: vi.fn() }));

import { SettingsPage } from "@/pages/SettingsPage";
import { useAuth } from "@/context/AuthContext";

// Stub reload so the logout handler doesn't trip jsdom navigation.
Object.defineProperty(window, "location", {
  configurable: true,
  value: { ...window.location, reload: vi.fn() },
});

beforeEach(() => vi.clearAllMocks());

describe("SettingsPage", () => {
  it("shows only the appearance card when login is not configured", () => {
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      isConfigured: false,
      login: vi.fn(),
      logout: vi.fn(),
    });
    render(<SettingsPage />);
    expect(screen.getByRole("heading", { name: "Tampilan" })).toBeInTheDocument();
    expect(screen.queryByText(/^Akun$/)).not.toBeInTheDocument();
  });

  it("shows account info and logs out when a user is signed in", async () => {
    const logout = vi.fn();
    vi.mocked(useAuth).mockReturnValue({
      user: { id: "u1", name: "Ravi", email: "ravi@x.test", avatar_url: null, device_id: "d1" },
      isConfigured: true,
      login: vi.fn(),
      logout,
    });
    render(<SettingsPage />);
    expect(screen.getByText("ravi@x.test")).toBeInTheDocument();
    expect(screen.getByText("Ravi")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /keluar dari akun/i }));
    expect(logout).toHaveBeenCalledOnce();
  });
});
