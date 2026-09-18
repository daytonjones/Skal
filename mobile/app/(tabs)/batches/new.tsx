import { router } from "expo-router";
import BatchForm from "../../../components/BatchForm";
import { useCreateBatch } from "../../../hooks/useBatches";

export default function NewBatchScreen() {
  const createMutation = useCreateBatch();

  return (
    <BatchForm
      submitLabel="Create batch"
      onSubmit={async (input) => {
        const batch = await createMutation.mutateAsync(input);
        router.replace(`/batches/${batch.id}`);
      }}
    />
  );
}
