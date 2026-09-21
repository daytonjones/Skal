import { render, screen, waitFor } from "@testing-library/react-native";
import { AuthProvider } from "../lib/authContext";
import Index from "../app/index";
import * as secureStorage from "../lib/secureStorage";

jest.mock("../lib/secureStorage");
jest.mock("expo-router", () => ({
  router: { replace: jest.fn() },
}));

const mockedStorage = secureStorage as jest.Mocked<typeof secureStorage>;

describe("Index screen", () => {
  beforeEach(() => jest.resetAllMocks());

  it("renders without crashing", async () => {
    mockedStorage.getServerUrl.mockResolvedValue("https://skal.example.com");
    mockedStorage.getTokens.mockResolvedValue({ access: "a", refresh: "r" });
    render(
      <AuthProvider>
        <Index />
      </AuthProvider>
    );
    await waitFor(() => {
      expect(mockedStorage.getServerUrl).toHaveBeenCalled();
    });
  });
});
