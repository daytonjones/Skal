import { useState } from "react";
import { ScrollView, StyleSheet } from "react-native";
import { TextInput, Button, Text } from "react-native-paper";
import { useLocalSearchParams, router } from "expo-router";
import { useCreateBottleConsumption } from "../../../../hooks/useBatches";

export default function AddConsumptionScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const batchId = Number(id);
  const createMutation = useCreateBottleConsumption(batchId);
  const [date, setDate] = useState("");
  const [quantity, setQuantity] = useState("");
  const [notes, setNotes] = useState("");

  async function handleSubmit() {
    await createMutation.mutateAsync({
      batch: batchId,
      date,
      quantity: Number(quantity),
      notes,
    });
    router.back();
  }

  return (
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
      <Button mode="contained" onPress={handleSubmit} loading={createMutation.isPending}>
        Save
      </Button>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  title: { marginBottom: 16 },
  input: { marginBottom: 12 },
});
