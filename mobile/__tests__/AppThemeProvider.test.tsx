import { render } from "@testing-library/react-native";
import { useTheme } from "react-native-paper";
import { Text } from "react-native";
import AppThemeProvider from "../components/AppThemeProvider";
import { lightTheme, darkTheme } from "../lib/theme";

const mockAuth = jest.fn();
const mockMe = jest.fn();
jest.mock("../lib/authContext", () => ({ useAuthState: () => mockAuth() }));
jest.mock("../hooks/useMe", () => ({ useMe: (o: unknown) => mockMe(o) }));

function Probe() {
  const t = useTheme();
  return <Text testID="bg">{t.colors.background}</Text>;
}

describe("AppThemeProvider", () => {
  it("defaults to dark and disables useMe when unauthenticated", () => {
    mockAuth.mockReturnValue({ status: "unauthenticated" });
    mockMe.mockReturnValue({ data: undefined });
    const { getByTestId } = render(<AppThemeProvider><Probe /></AppThemeProvider>);
    expect(getByTestId("bg").props.children).toBe(darkTheme.colors.background);
    expect(mockMe).toHaveBeenCalledWith({ enabled: false });
  });

  it("uses the saved light theme when authenticated", () => {
    mockAuth.mockReturnValue({ status: "authenticated" });
    mockMe.mockReturnValue({ data: { theme: "light" } });
    const { getByTestId } = render(<AppThemeProvider><Probe /></AppThemeProvider>);
    expect(getByTestId("bg").props.children).toBe(lightTheme.colors.background);
    expect(mockMe).toHaveBeenCalledWith({ enabled: true });
  });
});
