import { isNewerVersion } from "../lib/version";

describe("isNewerVersion", () => {
  it("returns true when the latest version is newer than the current version", () => {
    expect(isNewerVersion("2.1.0", "2.2.0")).toBe(true);
  });

  it("returns false when the latest version equals the current version", () => {
    expect(isNewerVersion("2.2.0", "2.2.0")).toBe(false);
  });

  it("returns false when the latest version is older than the current version", () => {
    expect(isNewerVersion("2.2.0", "2.1.0")).toBe(false);
  });

  it("treats versions with different segment counts as equal when numerically equal", () => {
    expect(isNewerVersion("2.2", "2.2.0")).toBe(false);
    expect(isNewerVersion("2.2.0", "2.2")).toBe(false);
  });

  it("compares multi-digit segments numerically, not lexically", () => {
    expect(isNewerVersion("2.9.0", "2.10.0")).toBe(true);
  });
});
