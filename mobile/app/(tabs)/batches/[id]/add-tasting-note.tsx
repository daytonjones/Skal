import { useState } from "react";
import { View, ScrollView, StyleSheet } from "react-native";
import { TextInput, Button, Text } from "react-native-paper";
import { useLocalSearchParams, router } from "expo-router";
import { useCreateTastingNote } from "../../../../hooks/useBatches";

export default function AddTastingNoteScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const batchId = Number(id);
  const createMutation = useCreateTastingNote(batchId);
  const [date, setDate] = useState("");
  const [aroma, setAroma] = useState("");
  const [flavor, setFlavor] = useState("");
  const [overall, setOverall] = useState("");
  const [score, setScore] = useState("");

  async function handleSubmit() {
    await createMutation.mutateAsync({
      batch: batchId,
      date,
      aroma,
      flavor,
      overall,
      score: Number(score),
    });
    router.back();
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text variant="titleMedium" style={styles.title}>New tasting note</Text>
      <TextInput mode="outlined" label="Date (YYYY-MM-DD)" value={date} onChangeText={setDate} style={styles.input} />
      <TextInput mode="outlined" label="Aroma" value={aroma} onChangeText={setAroma} style={styles.input} />
      <TextInput mode="outlined" label="Flavor" value={flavor} onChangeText={setFlavor} style={styles.input} />
      <TextInput mode="outlined" label="Overall" value={overall} onChangeText={setOverall} style={styles.input} />
      <TextInput
        mode="outlined"
        label="Score (1-10)"
        value={score}
        onChangeText={setScore}
        keyboardType="number-pad"
        style={styles.input}
      />
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
