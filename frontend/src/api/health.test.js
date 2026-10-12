import { afterEach, describe, expect, it, vi } from "vitest";
import { checkBackendHealth } from "./health";

const { mockGet } = vi.hoisted(() => ({
  mockGet: vi.fn(),
}));

vi.mock("axios", () => ({
  default: {
    create: vi.fn(() => ({
      get: mockGet,
    })),
  },
}));

describe("checkBackendHealth", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("returns online when the health endpoint succeeds", async () => {
    mockGet.mockResolvedValue({
      data: { status: "ok" },
    });

    const result = await checkBackendHealth();

    expect(result.online).toBe(true);
    expect(result.status).toBe("ok");
  });

  it("returns unavailable when the endpoint fails", async () => {
    mockGet.mockRejectedValue(new Error("Connection refused"));

    const result = await checkBackendHealth();

    expect(result.online).toBe(false);
    expect(result.status).toBe("unavailable");
  });
});