import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

vi.mock("@/services/api", () => ({ loginWithGoogle: vi.fn() }));
vi.mock("@/lib/deviceId", () => ({ resetDeviceId: vi.fn() }));

import { AuthProvider, useAuth } from "@/context/AuthContext";
import { loginWithGoogle } from "@/services/api";
import { resetDeviceId } from "@/lib/deviceId";

function Consumer() {
  const { user, login, logout } = useAuth();
  return (
    <div>
      <span data-testid="user">{user ? user.name : "guest"}</span>
      <button onClick={() => login("cred")}>login</button>
      <button onClick={logout}>logout</button>
    </div>
  );
}

function renderAuth() {
  return render(
    <AuthProvider>
      <Consumer />
    </AuthProvider>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});

describe("AuthContext", () => {
  it("starts as a guest", () => {
    renderAuth();
    expect(screen.getByTestId("user")).toHaveTextContent("guest");
  });

  it("stores the user and persists to localStorage on login", async () => {
    vi.mocked(loginWithGoogle).mockResolvedValue({
      id: "u1",
      name: "Ravi",
      email: "ravi@x.test",
      avatar_url: null,
      device_id: "d1",
    });
    renderAuth();
    await userEvent.click(screen.getByText("login"));
    await waitFor(() => expect(screen.getByTestId("user")).toHaveTextContent("Ravi"));
    expect(localStorage.getItem("asahlagi-auth")).toContain("Ravi");
  });

  it("clears the user, wipes storage and resets the device id on logout", async () => {
    vi.mocked(loginWithGoogle).mockResolvedValue({
      id: "u1",
      name: "Ravi",
      email: null,
      avatar_url: null,
      device_id: "d1",
    });
    renderAuth();
    await userEvent.click(screen.getByText("login"));
    await waitFor(() => expect(screen.getByTestId("user")).toHaveTextContent("Ravi"));

    await userEvent.click(screen.getByText("logout"));
    expect(screen.getByTestId("user")).toHaveTextContent("guest");
    expect(localStorage.getItem("asahlagi-auth")).toBeNull();
    expect(resetDeviceId).toHaveBeenCalledOnce();
  });

  it("hydrates an existing user from localStorage", () => {
    localStorage.setItem(
      "asahlagi-auth",
      JSON.stringify({ id: "u9", name: "Sudah", email: null, avatar_url: null, device_id: "d9" }),
    );
    renderAuth();
    expect(screen.getByTestId("user")).toHaveTextContent("Sudah");
  });
});
