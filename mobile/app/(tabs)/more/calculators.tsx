import { useState, useMemo } from "react";
import { ScrollView, StyleSheet } from "react-native";
import { TextInput, Text, SegmentedButtons } from "react-native-paper";
import { abvStandard, abvAlternate, caloriesPerGlass } from "../../../lib/calculators";

export default function CalculatorsScreen() {
  const [og, setOg] = useState("1.090");
  const [fg, setFg] = useState("1.000");
  const [formula, setFormula] = useState<"standard" | "alternate">("standard");

  const { abv, calories } = useMemo(() => {
    const ogNum = parseFloat(og);
    const fgNum = parseFloat(fg);
    if (Number.isNaN(ogNum) || Number.isNaN(fgNum)) return { abv: null, calories: null };
    const abvValue = formula === "standard" ? abvStandard(ogNum, fgNum) : abvAlternate(ogNum, fgNum);
    return { abv: abvValue, calories: caloriesPerGlass(abvValue, 5) };
  }, [og, fg, formula]);

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text variant="titleMedium" style={styles.title}>ABV &amp; Calories</Text>
      <TextInput mode="outlined" label="Original Gravity" value={og} onChangeText={setOg} keyboardType="decimal-pad" style={styles.input} />
      <TextInput mode="outlined" label="Final Gravity" value={fg} onChangeText={setFg} keyboardType="decimal-pad" style={styles.input} />
      <SegmentedButtons
        value={formula}
        onValueChange={(v) => setFormula(v as "standard" | "alternate")}
        buttons={[
          { value: "standard", label: "Standard" },
          { value: "alternate", label: "Alternate" },
        ]}
        style={styles.segmented}
      />
      <Text variant="bodyLarge">ABV: {abv != null ? `${abv.toFixed(2)}%` : "--"}</Text>
      <Text variant="bodyLarge">Calories (5oz glass): {calories != null ? calories.toFixed(0) : "--"}</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  title: { marginBottom: 16 },
  input: { marginBottom: 12 },
  segmented: { marginBottom: 16 },
});
