import { useMemo, useState } from "react";
import { ScrollView, StyleSheet, View } from "react-native";
import { Card, DataTable, SegmentedButtons, Text, TextInput, useTheme } from "react-native-paper";
import { Stack } from "expo-router";
import { useYeast } from "../../../hooks/useYeast";
import { YeastPicker } from "../../../components/YeastPicker";
import {
  abvStandard,
  abvAlternate,
  caloriesPerGlass,
  attenuation,
  brixToSG,
  batchBuilder,
  tosnaSchedule,
  SWEETNESS_LEVELS,
  type NutrientType,
} from "../../../lib/calculators";

type GlassSize = "5" | "8" | "12";

function parseNum(v: string): number | null {
  const n = parseFloat(v);
  return Number.isFinite(n) ? n : null;
}

function SweetnessTable({ abv }: { abv: number | null }) {
  const theme = useTheme();
  return (
    <DataTable>
      <DataTable.Header>
        <DataTable.Title>Style</DataTable.Title>
        <DataTable.Title>SG Range</DataTable.Title>
        <DataTable.Title>ABV Range</DataTable.Title>
      </DataTable.Header>
      {SWEETNESS_LEVELS.map((level) => {
        const highlight = abv != null && abv >= level.abvMin && abv <= level.abvMax;
        return (
          <DataTable.Row
            key={level.label}
            style={highlight ? { backgroundColor: theme.colors.primaryContainer } : undefined}
          >
            <DataTable.Cell>{level.label}</DataTable.Cell>
            <DataTable.Cell>{level.sgRange}</DataTable.Cell>
            <DataTable.Cell>
              {level.abvMin.toFixed(1)}–{level.abvMax.toFixed(1)}%
            </DataTable.Cell>
          </DataTable.Row>
        );
      })}
    </DataTable>
  );
}

const GLASS_SIZE_OPTIONS = [
  { value: "5", label: "5 oz" },
  { value: "8", label: "8 oz" },
  { value: "12", label: "12 oz" },
];

export default function CalculatorsScreen() {
  const { data: yeasts, isLoading: yeastLoading, isError: yeastError } = useYeast();

  // --- Section 1: SG calculator (shared OG/FG feed the TOSNA section too) ---
  const [og, setOg] = useState("1.090");
  const [fg, setFg] = useState("1.000");
  const [formula, setFormula] = useState<"standard" | "alternate">("standard");
  const [glassSizeSG, setGlassSizeSG] = useState<GlassSize>("5");

  const sgResult = useMemo(() => {
    const ogNum = parseNum(og);
    const fgNum = parseNum(fg);
    if (ogNum == null || fgNum == null) return null;
    const abv = formula === "standard" ? abvStandard(ogNum, fgNum) : abvAlternate(ogNum, fgNum);
    return {
      abv,
      attenuation: attenuation(ogNum, fgNum),
      calories: caloriesPerGlass(abv, parseFloat(glassSizeSG)),
    };
  }, [og, fg, formula, glassSizeSG]);

  // --- Section 2: Brix calculator (independent glass size, own inputs) ---
  const [ogBrix, setOgBrix] = useState("20.0");
  const [fgBrix, setFgBrix] = useState("0.0");
  const [glassSizeBx, setGlassSizeBx] = useState<GlassSize>("5");

  const brixResult = useMemo(() => {
    const obx = parseNum(ogBrix);
    const fbx = parseNum(fgBrix);
    if (obx == null || fbx == null) return null;
    const ogSG = brixToSG(obx);
    const fgSG = brixToSG(fbx);
    // Web's Brix path: convert Brix -> SG, then apply the standard formula
    // (ogSG - fgSG) * 131.25 — never the alternate formula.
    const abv = abvStandard(ogSG, fgSG);
    return {
      abv,
      attenuation: attenuation(ogSG, fgSG),
      calories: caloriesPerGlass(abv, parseFloat(glassSizeBx)),
    };
  }, [ogBrix, fgBrix, glassSizeBx]);

  // --- Section 3: TOSNA 3.0 schedule (reuses section 1's OG/FG, like the web) ---
  const [batchSize, setBatchSize] = useState("5");
  const [nutrient, setNutrient] = useState<NutrientType>("FO");
  const [yeastName, setYeastName] = useState("");

  const tosnaResult = useMemo(() => {
    const ogNum = parseNum(og);
    const fgNum = parseNum(fg);
    const batchNum = parseNum(batchSize);
    if (ogNum == null || fgNum == null || batchNum == null || !yeastName) return null;
    return tosnaSchedule(ogNum, fgNum, batchNum, yeastName, nutrient);
  }, [og, fg, batchSize, yeastName, nutrient]);

  // --- Section 4: Batch Builder ---
  const [builderBatchSize, setBuilderBatchSize] = useState("5");
  const [desiredAbv, setDesiredAbv] = useState("12");
  const [builderYeastName, setBuilderYeastName] = useState("");
  const [builderNutrient, setBuilderNutrient] = useState<NutrientType>("FO");

  const builderResult = useMemo(() => {
    const batchNum = parseNum(builderBatchSize);
    const abvNum = parseNum(desiredAbv);
    if (batchNum == null || abvNum == null || !builderYeastName) return null;
    const fgNum = parseNum(fg);
    return batchBuilder(batchNum, abvNum, builderYeastName, builderNutrient, fgNum ?? undefined);
  }, [builderBatchSize, desiredAbv, builderYeastName, builderNutrient, fg]);

  return (
    <>
      <Stack.Screen options={{ title: "Calculators" }} />
      <ScrollView contentContainerStyle={styles.container}>
        <Card style={styles.card}>
          <Card.Title title="ABV & Calories — Specific Gravity" />
          <Card.Content>
            <TextInput
              mode="outlined"
              label="Original Gravity (SG)"
              value={og}
              onChangeText={setOg}
              keyboardType="decimal-pad"
              style={styles.input}
            />
            <TextInput
              mode="outlined"
              label="Final Gravity (SG)"
              value={fg}
              onChangeText={setFg}
              keyboardType="decimal-pad"
              style={styles.input}
            />
            <SegmentedButtons
              value={formula}
              onValueChange={(v) => setFormula(v as "standard" | "alternate")}
              buttons={[
                { value: "standard", label: "Standard" },
                { value: "alternate", label: "Alternate" },
              ]}
              style={styles.segmented}
            />
            <Text variant="bodyLarge">ABV: {sgResult ? `${sgResult.abv.toFixed(2)}%` : "--"}</Text>
            <Text variant="bodyLarge">
              Attenuation: {sgResult ? `${sgResult.attenuation.toFixed(2)}%` : "--"}
            </Text>
            <Text variant="labelLarge" style={styles.subLabel}>Glass size</Text>
            <SegmentedButtons
              value={glassSizeSG}
              onValueChange={(v) => setGlassSizeSG(v as GlassSize)}
              buttons={GLASS_SIZE_OPTIONS}
              style={styles.segmented}
            />
            <Text variant="bodyLarge">
              Calories: {sgResult ? sgResult.calories.toFixed(2) : "--"}
            </Text>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Title title="Sweetness Levels" />
          <Card.Content>
            <SweetnessTable abv={sgResult?.abv ?? null} />
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Title title="ABV & Calories — Brix" />
          <Card.Content>
            <TextInput
              mode="outlined"
              label="Original Gravity (°Bx)"
              value={ogBrix}
              onChangeText={setOgBrix}
              keyboardType="decimal-pad"
              style={styles.input}
            />
            <TextInput
              mode="outlined"
              label="Final Gravity (°Bx)"
              value={fgBrix}
              onChangeText={setFgBrix}
              keyboardType="decimal-pad"
              style={styles.input}
            />
            <Text variant="bodyLarge">ABV: {brixResult ? `${brixResult.abv.toFixed(2)}%` : "--"}</Text>
            <Text variant="bodyLarge">
              Attenuation: {brixResult ? `${brixResult.attenuation.toFixed(2)}%` : "--"}
            </Text>
            <Text variant="labelLarge" style={styles.subLabel}>Glass size</Text>
            <SegmentedButtons
              value={glassSizeBx}
              onValueChange={(v) => setGlassSizeBx(v as GlassSize)}
              buttons={GLASS_SIZE_OPTIONS}
              style={styles.segmented}
            />
            <Text variant="bodyLarge">
              Calories: {brixResult ? brixResult.calories.toFixed(2) : "--"}
            </Text>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Title title="TOSNA 3.0 Nutrient Schedule" />
          <Card.Content>
            <Text variant="bodySmall" style={styles.helperText}>
              Uses the OG/FG from the SG calculator above. 4 equal additions at 24h, 48h, 72h, and
              1/3 sugar break.
            </Text>
            <TextInput
              mode="outlined"
              label="Batch size (gal)"
              value={batchSize}
              onChangeText={setBatchSize}
              keyboardType="decimal-pad"
              style={styles.input}
            />
            <Text variant="labelLarge" style={styles.subLabel}>Nutrient</Text>
            <SegmentedButtons
              value={nutrient}
              onValueChange={(v) => setNutrient(v as NutrientType)}
              buttons={[
                { value: "FO", label: "Fermaid O" },
                { value: "FK", label: "Fermaid K" },
              ]}
              style={styles.segmented}
            />
            <YeastPicker
              label="Yeast strain"
              yeasts={yeasts}
              isLoading={yeastLoading}
              isError={yeastError}
              value={yeastName}
              onChange={setYeastName}
            />
            {tosnaResult ? (
              <View>
                <Text variant="bodyLarge">N-factor: {tosnaResult.nFactor.toFixed(2)}</Text>
                <Text variant="bodyLarge">Pitch rate: {tosnaResult.pitchRateRange}</Text>
                <Text variant="bodyLarge">Yeast needed: {tosnaResult.yeastNeededRange}</Text>
                <Text variant="bodyLarge">
                  Total nutrient: {tosnaResult.totalNutrientG.toFixed(2)} g ({nutrient})
                </Text>
                <DataTable style={styles.subTable}>
                  <DataTable.Header>
                    <DataTable.Title>Stage</DataTable.Title>
                    <DataTable.Title numeric>Grams</DataTable.Title>
                  </DataTable.Header>
                  {tosnaResult.additions.map((addition) => (
                    <DataTable.Row key={addition.label}>
                      <DataTable.Cell>{addition.label}</DataTable.Cell>
                      <DataTable.Cell numeric>{addition.grams.toFixed(2)}</DataTable.Cell>
                    </DataTable.Row>
                  ))}
                </DataTable>
              </View>
            ) : (
              <Text variant="bodyMedium" style={styles.helperText}>
                Enter OG/FG above, a batch size, and pick a yeast to see the schedule.
              </Text>
            )}
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Title title="Batch Builder" />
          <Card.Content>
            <Text variant="bodySmall" style={styles.helperText}>
              Estimate honey needed and a nutrient schedule for a target ABV.
            </Text>
            <TextInput
              mode="outlined"
              label="Batch size (gal)"
              value={builderBatchSize}
              onChangeText={setBuilderBatchSize}
              keyboardType="decimal-pad"
              style={styles.input}
            />
            <TextInput
              mode="outlined"
              label="Desired ABV (%)"
              value={desiredAbv}
              onChangeText={setDesiredAbv}
              keyboardType="decimal-pad"
              style={styles.input}
            />
            <YeastPicker
              label="Yeast strain"
              yeasts={yeasts}
              isLoading={yeastLoading}
              isError={yeastError}
              value={builderYeastName}
              onChange={setBuilderYeastName}
            />
            <Text variant="labelLarge" style={styles.subLabel}>Nutrient</Text>
            <SegmentedButtons
              value={builderNutrient}
              onValueChange={(v) => setBuilderNutrient(v as NutrientType)}
              buttons={[
                { value: "FO", label: "Fermaid O" },
                { value: "FK", label: "Fermaid K" },
              ]}
              style={styles.segmented}
            />
            {builderResult ? (
              <View>
                <Text variant="bodyLarge">Honey needed: {builderResult.honeyLbs.toFixed(2)} lbs</Text>
                <Text variant="bodyLarge">Estimated OG: {builderResult.estimatedOgSG.toFixed(3)}</Text>
                <Text variant="bodyLarge">
                  TOSNA nutrient: {builderResult.totalNutrientG.toFixed(2)} g ({builderNutrient})
                </Text>
                <Text variant="bodyLarge">Yeast pitch: {builderResult.yeastNeededRange}</Text>
              </View>
            ) : (
              <Text variant="bodyMedium" style={styles.helperText}>
                Enter a batch size, desired ABV, and pick a yeast to see the estimate.
              </Text>
            )}
          </Card.Content>
        </Card>
      </ScrollView>
    </>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, paddingBottom: 32 },
  card: { marginBottom: 16 },
  input: { marginBottom: 12 },
  segmented: { marginBottom: 16 },
  subLabel: { marginBottom: 4, marginTop: 4 },
  subTable: { marginTop: 12 },
  helperText: { marginBottom: 12 },
});
