import { useState } from "react";
import { ScrollView, StyleSheet, View } from "react-native";
import { Button, Menu, Text } from "react-native-paper";
import type { Yeast } from "../api/types";

interface YeastPickerProps {
  label: string;
  yeasts: Yeast[] | undefined;
  isLoading: boolean;
  isError: boolean;
  value: string;
  onChange: (name: string) => void;
}

// A Menu-based picker for yeast strains. There's no native <select> in RN and
// the yeast list can run 40+ entries long, so a plain always-visible list
// (e.g. SegmentedButtons) is impractical here; a button-anchored Menu with a
// scrollable item list is the lowest-effort, reasonably usable option built
// entirely from components already in this app's dependency tree.
export function YeastPicker({ label, yeasts, isLoading, isError, value, onChange }: YeastPickerProps) {
  const [visible, setVisible] = useState(false);

  const buttonLabel = isLoading
    ? "Loading yeasts…"
    : isError
      ? "Couldn't load yeasts"
      : value || "Select a yeast";

  return (
    <View style={styles.container}>
      <Text variant="labelLarge" style={styles.label}>{label}</Text>
      <Menu
        visible={visible}
        onDismiss={() => setVisible(false)}
        anchor={
          <Button
            mode="outlined"
            onPress={() => setVisible(true)}
            disabled={isLoading || isError || !yeasts?.length}
            style={styles.button}
          >
            {buttonLabel}
          </Button>
        }
      >
        <ScrollView style={styles.menuScroll}>
          {(yeasts ?? []).map((y) => (
            <Menu.Item
              key={y.name}
              title={y.name}
              onPress={() => {
                onChange(y.name);
                setVisible(false);
              }}
            />
          ))}
        </ScrollView>
      </Menu>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { marginBottom: 12 },
  label: { marginBottom: 4 },
  button: { alignSelf: "flex-start" },
  menuScroll: { maxHeight: 320 },
});
