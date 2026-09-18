import { View, ActivityIndicator } from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import BatchForm from "../../../../components/BatchForm";
import { useBatch, useUpdateBatch } from "../../../../hooks/useBatches";

export default function EditBatchScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const batchId = Number(id);
  const { data: batch, isLoading } = useBatch(batchId);
  const updateMutation = useUpdateBatch(batchId);

  if (isLoading || !batch) {
    return (
      <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
        <ActivityIndicator />
      </View>
    );
  }

  return (
    <BatchForm
      initial={batch}
      submitLabel="Save changes"
      onSubmit={async (input) => {
        await updateMutation.mutateAsync(input);
        router.replace(`/batches/${batchId}`);
      }}
    />
  );
}
