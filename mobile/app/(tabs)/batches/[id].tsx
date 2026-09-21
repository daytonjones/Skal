import { useState } from "react";
import { View, ScrollView, StyleSheet, Image } from "react-native";
import { Text, ActivityIndicator, Button, List, ProgressBar, Chip, HelperText } from "react-native-paper";
import { useLocalSearchParams, router, Stack } from "expo-router";
import * as ImagePicker from "expo-image-picker";
import {
  useBatch,
  useTastingNotes,
  useBottleConsumption,
  useBatchImages,
  useUploadBatchImage,
  useDeleteBatch,
} from "../../../hooks/useBatches";
import { firstErrorMessage } from "../../../lib/errors";

export default function BatchDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const batchId = Number(id);
  const { data: batch, isLoading, isError } = useBatch(batchId);
  const { data: tastingNotes } = useTastingNotes(batchId);
  const { data: consumption } = useBottleConsumption(batchId);
  const { data: images } = useBatchImages(batchId);
  const uploadImage = useUploadBatchImage(batchId);
  const deleteMutation = useDeleteBatch();
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (isLoading) {
    return (
      <>
        <Stack.Screen options={{ title: "Batch" }} />
        <View style={styles.center}>
          <ActivityIndicator />
        </View>
      </>
    );
  }

  if (isError || !batch) {
    return (
      <>
        <Stack.Screen options={{ title: "Batch" }} />
        <View style={styles.center}>
          <Text>Couldn't load this batch.</Text>
        </View>
      </>
    );
  }

  async function handlePickPhoto() {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.8,
    });
    if (result.canceled || !result.assets?.[0]) return;
    setUploading(true);
    try {
      await uploadImage.mutateAsync({ uri: result.assets[0].uri, caption: "" });
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete() {
    setError(null);
    try {
      await deleteMutation.mutateAsync(batchId);
      router.back();
    } catch (err) {
      setError(firstErrorMessage(err));
    }
  }

  return (
    <>
      <Stack.Screen options={{ title: "Batch" }} />
      <ScrollView contentContainerStyle={styles.container}>
      <Text variant="headlineMedium">{batch.name}</Text>
      <Chip style={styles.chip}>{batch.stage}</Chip>
      <ProgressBar progress={batch.checklist_progress / 100} style={styles.progress} />
      <Text variant="bodyMedium">OG {batch.og}{batch.fg ? ` / FG ${batch.fg}` : ""}</Text>
      {batch.abv != null ? <Text variant="bodyMedium">ABV: {batch.abv}%</Text> : null}
      {batch.bottle_count != null ? (
        <Text variant="bodyMedium">Bottles remaining: {batch.bottles_remaining}</Text>
      ) : null}
      {batch.notes ? <Text variant="bodyMedium" style={styles.section}>{batch.notes}</Text> : null}

      <List.Section title="Tasting notes">
        {(tastingNotes?.results ?? []).map((note) => (
          <List.Item key={note.id} title={`${note.date} — ${note.score}/10`} description={note.overall} />
        ))}
        {batch.is_owner ? (
          <Button mode="text" onPress={() => router.push(`/batches/${batchId}/add-tasting-note`)}>
            Add tasting note
          </Button>
        ) : null}
      </List.Section>

      <List.Section title="Bottle consumption">
        {(consumption?.results ?? []).map((c) => (
          <List.Item key={c.id} title={`${c.date} — ${c.quantity} bottle(s)`} description={c.notes} />
        ))}
        {batch.is_owner && batch.bottled_done ? (
          <Button mode="text" onPress={() => router.push(`/batches/${batchId}/add-consumption`)}>
            Log consumption
          </Button>
        ) : null}
      </List.Section>

      <List.Section title="Photos">
        <ScrollView horizontal>
          {(images?.results ?? []).map((img) => (
            <Image key={img.id} source={{ uri: img.image }} style={styles.photo} />
          ))}
        </ScrollView>
        {batch.is_owner ? (
          <Button mode="text" onPress={handlePickPhoto} loading={uploading} disabled={uploading}>
            Add photo
          </Button>
        ) : null}
      </List.Section>

      {error ? <HelperText type="error">{error}</HelperText> : null}
      {batch.is_owner ? (
        <>
          <Button mode="outlined" onPress={() => router.push(`/batches/${batchId}/edit`)} style={styles.button}>
            Edit
          </Button>
          <Button
            mode="outlined"
            textColor="red"
            onPress={handleDelete}
            loading={deleteMutation.isPending}
            style={styles.button}
          >
            Delete
          </Button>
        </>
      ) : null}
      </ScrollView>
    </>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  chip: { alignSelf: "flex-start", marginVertical: 8 },
  progress: { marginBottom: 12 },
  section: { marginTop: 12 },
  photo: { width: 100, height: 100, marginRight: 8, borderRadius: 4 },
  button: { marginTop: 12 },
});
