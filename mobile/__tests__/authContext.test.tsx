import { render, screen, waitFor } from "@testing-library/react-native";
import { Text } from "react-native";
import { AuthProvider, useAuthState } from "../lib/authContext";
import * as secureStorage from "../lib/secureStorage";

jest.mock("../lib/secureStorage");
const mockedStorage = secureStorage as jest.Mocked<typeof secureStorage>;

function StatusProbe() {
  const { status } = useAuthState();
  return <Text>{status}</Text>;
}

describe("AuthProvider", () => {
  beforeEach(() => jest.resetAllMocks());

  it("reports no-server when no server url is configured", async () => {
    mockedStorage.getServerUrl.mockResolvedValue(null);
    render(
      <AuthProvider>
        <StatusProbe />
      </AuthProvider>
    );
    await waitFor(() => expect(screen.getByText("no-server")).toBeTruthy());
  });

  it("reports unauthenticated when a server is set but no tokens exist", async () => {
    mockedStorage.getServerUrl.mockResolvedValue("https://skal.example.com");
    mockedStorage.getTokens.mockResolvedValue(null);
    render(
      <AuthProvider>
        <StatusProbe />
      </AuthProvider>
    );
    await waitFor(() => expect(screen.getByText("unauthenticated")).toBeTruthy());
  });

  it("reports authenticated when tokens exist", async () => {
    mockedStorage.getServerUrl.mockResolvedValue("https://skal.example.com");
    mockedStorage.getTokens.mockResolvedValue({ access: "a", refresh: "r" });
    render(
      <AuthProvider>
        <StatusProbe />
      </AuthProvider>
    );
    await waitFor(() => expect(screen.getByText("authenticated")).toBeTruthy());
  });
});
