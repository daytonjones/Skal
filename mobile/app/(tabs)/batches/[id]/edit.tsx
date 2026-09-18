import { View, ActivityIndicator } from "react-native";
import { Text } from "react-native-paper";
import { useLocalSearchParams, router, Stack } from "expo-router";
import BatchForm from "../../../../components/BatchForm";
import { useBatch, useUpdateBatch } from "../../../../hooks/useBatches";

export default function EditBatchScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const batchId = Number(id);
  const { data: batch, isLoading, isError } = useBatch(batchId);
  const updateMutation = useUpdateBatch(batchId);

  if (isError) {
    return (
      <>
        <Stack.Screen options={{ title: "Edit Batch" }} />
        <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
          <Text>Couldn't load this batch.</Text>
        </View>
      </>
    );
  }

  if (isLoading || !batch) {
    return (
      <>
        <Stack.Screen options={{ title: "Edit Batch" }} />
        <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
          <ActivityIndicator />
        </View>
      </>
    );
  }

  return (
    <>
      <Stack.Screen options={{ title: "Edit Batch" }} />
      <BatchForm
        initial={batch}
        submitLabel="Save changes"
        onSubmit={async (input) => {
          await updateMutation.mutateAsync(input);
          router.replace(`/batches/${batchId}`);
        }}
      />
    </>
  );
}
