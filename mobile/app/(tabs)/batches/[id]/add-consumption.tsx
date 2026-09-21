import { useState } from "react";
import { ScrollView, StyleSheet } from "react-native";
import { TextInput, Button, Text, HelperText } from "react-native-paper";
import { useLocalSearchParams, router, Stack } from "expo-router";
import { useCreateBottleConsumption } from "../../../../hooks/useBatches";
import { firstErrorMessage } from "../../../../lib/errors";

export default function AddConsumptionScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const batchId = Number(id);
  const createMutation = useCreateBottleConsumption(batchId);
  const [date, setDate] = useState("");
  const [quantity, setQuantity] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit() {
    setError(null);
    try {
      await createMutation.mutateAsync({
        batch: batchId,
        date,
        quantity: Number(quantity),
        notes,
      });
      router.back();
    } catch (err) {
      setError(firstErrorMessage(err));
    }
  }

  return (
    <>
      <Stack.Screen options={{ title: "Log Consumption" }} />
      <ScrollView contentContainerStyle={styles.container}>
      <Text variant="titleMedium" style={styles.title}>Log bottle consumption</Text>
      <TextInput mode="outlined" label="Date (YYYY-MM-DD)" value={date} onChangeText={setDate} style={styles.input} />
      <TextInput
        mode="outlined"
        label="Quantity"
        value={quantity}
        onChangeText={setQuantity}
        keyboardType="number-pad"
        style={styles.input}
      />
      <TextInput mode="outlined" label="Notes" value={notes} onChangeText={setNotes} style={styles.input} />
      {error ? <HelperText type="error">{error}</HelperText> : null}
      <Button mode="contained" onPress={handleSubmit} loading={createMutation.isPending}>
        Save
      </Button>
      </ScrollView>
    </>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  title: { marginBottom: 16 },
  input: { marginBottom: 12 },
});
