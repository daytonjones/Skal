import { useState } from "react";
import { ScrollView, View, StyleSheet } from "react-native";
import { TextInput, Button, Switch, Text, HelperText } from "react-native-paper";
import type { Batch, BatchInput } from "../api/types";
import { firstErrorMessage } from "../lib/errors";

interface Props {
  initial?: Batch;
  onSubmit: (input: Partial<BatchInput>) => Promise<void>;
  submitLabel: string;
}

const CHECKLIST_STEPS: Array<{ key: keyof BatchInput & string; label: string }> = [
  { key: "create_must_done", label: "Create must" },
  { key: "pitch_yeast_done", label: "Pitch yeast" },
  { key: "fo_24h_done", label: "24h fermentation check" },
  { key: "fo_48h_done", label: "48h fermentation check" },
  { key: "fo_72h_done", label: "72h fermentation check" },
  { key: "fo_1_3_break_done", label: "1/3 break" },
  { key: "rack_secondary_done", label: "Rack to secondary" },
  { key: "bottled_done", label: "Bottled" },
];

export default function BatchForm({ initial, onSubmit, submitLabel }: Props) {
  const [name, setName] = useState(initial?.name ?? "");
  const [batchSize, setBatchSize] = useState(initial?.batch_size ?? "5.0");
  const [og, setOg] = useState(initial?.og ?? "");
  const [fg, setFg] = useState(initial?.fg ?? "");
  const [primaryDate, setPrimaryDate] = useState(initial?.primary_date ?? "");
  const [notes, setNotes] = useState(initial?.notes ?? "");
  const [bottleCount, setBottleCount] = useState(
    initial?.bottle_count != null ? String(initial.bottle_count) : ""
  );
  const [storageLocation, setStorageLocation] = useState(initial?.storage_location ?? "");
  const [isPublic, setIsPublic] = useState(initial?.is_public ?? false);
  const [checklist, setChecklist] = useState<Record<string, boolean>>(
    Object.fromEntries(CHECKLIST_STEPS.map((s) => [s.key, (initial as any)?.[s.key] ?? false]))
  );
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit() {
    setSubmitting(true);
    setError(null);
    try {
      await onSubmit({
        name,
        batch_size: batchSize,
        og,
        fg: fg || null,
        primary_date: primaryDate,
        notes,
        bottle_count: bottleCount ? Number(bottleCount) : null,
        storage_location: storageLocation,
        is_public: isPublic,
        ...checklist,
      } as Partial<BatchInput>);
    } catch (err) {
      setError(firstErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <TextInput mode="outlined" label="Name" value={name} onChangeText={setName} style={styles.input} />
      <TextInput
        mode="outlined"
        label="Batch size (gal)"
        value={batchSize}
        onChangeText={setBatchSize}
        keyboardType="decimal-pad"
        style={styles.input}
      />
      <TextInput mode="outlined" label="OG" value={og} onChangeText={setOg} keyboardType="decimal-pad" style={styles.input} />
      <TextInput mode="outlined" label="FG (optional)" value={fg} onChangeText={setFg} keyboardType="decimal-pad" style={styles.input} />
      <TextInput
        mode="outlined"
        label="Primary date (YYYY-MM-DD)"
        value={primaryDate}
        onChangeText={setPrimaryDate}
        style={styles.input}
      />
      <TextInput mode="outlined" label="Notes" value={notes} onChangeText={setNotes} multiline style={styles.input} />
      <TextInput
        mode="outlined"
        label="Bottle count"
        value={bottleCount}
        onChangeText={setBottleCount}
        keyboardType="number-pad"
        style={styles.input}
      />
      <TextInput
        mode="outlined"
        label="Storage location"
        value={storageLocation}
        onChangeText={setStorageLocation}
        style={styles.input}
      />
      <View style={styles.row}>
        <Text>Public</Text>
        <Switch value={isPublic} onValueChange={setIsPublic} />
      </View>

      <Text variant="titleMedium" style={styles.sectionTitle}>Checklist</Text>
      {CHECKLIST_STEPS.map((step) => (
        <View key={step.key} style={styles.row}>
          <Text>{step.label}</Text>
          <Switch
            value={checklist[step.key]}
            onValueChange={(v) => setChecklist((prev) => ({ ...prev, [step.key]: v }))}
          />
        </View>
      ))}

      {error ? <HelperText type="error">{error}</HelperText> : null}
      <Button mode="contained" onPress={handleSubmit} loading={submitting} disabled={submitting} style={styles.submit}>
        {submitLabel}
      </Button>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  input: { marginBottom: 12 },
  row: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 12 },
  sectionTitle: { marginTop: 8, marginBottom: 8 },
  submit: { marginTop: 24 },
});
