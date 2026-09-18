import { useState, useRef } from "react";
import { View, FlatList, KeyboardAvoidingView, Platform, StyleSheet } from "react-native";
import { Text, TextInput, IconButton, ActivityIndicator, Card, Button } from "react-native-paper";
import { router } from "expo-router";
import { useBjornMessages, useSendBjornMessage, useSaveBjornRecipe } from "../../../hooks/useBjorn";
import { ApiError } from "../../../lib/apiFetch";

export default function BjornScreen() {
  const { data, isLoading, isError, error } = useBjornMessages();
  const sendMutation = useSendBjornMessage();
  const saveRecipeMutation = useSaveBjornRecipe();
  const [input, setInput] = useState("");
  const listRef = useRef<FlatList>(null);

  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator />
      </View>
    );
  }

  if (isError) {
    if (error instanceof ApiError && error.status === 404) {
      return (
        <View style={styles.center}>
          <Text>Bjorn isn't enabled on this server.</Text>
        </View>
      );
    }
    return (
      <View style={styles.center}>
        <Text>Couldn't load Bjorn right now.</Text>
      </View>
    );
  }

  async function handleSend() {
    if (!input.trim()) return;
    const text = input;
    setInput("");
    await sendMutation.mutateAsync(text);
    listRef.current?.scrollToEnd({ animated: true });
  }

  async function handleSaveRecipe(messageId: number) {
    const recipe = await saveRecipeMutation.mutateAsync(messageId);
    router.push(`/recipes/${recipe.id}`);
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      keyboardVerticalOffset={80}
    >
      <FlatList
        ref={listRef}
        data={data?.results ?? []}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <Card style={[styles.bubble, item.role === "user" ? styles.userBubble : styles.assistantBubble]}>
            <Card.Content>
              <Text>{item.content}</Text>
              {item.pending_recipe ? (
                <Button mode="text" onPress={() => handleSaveRecipe(item.id)} loading={saveRecipeMutation.isPending}>
                  Save to My Recipes
                </Button>
              ) : null}
            </Card.Content>
          </Card>
        )}
        contentContainerStyle={styles.list}
      />
      <View style={styles.inputRow}>
        <TextInput
          mode="outlined"
          placeholder="Ask Bjorn..."
          value={input}
          onChangeText={setInput}
          style={styles.input}
        />
        <IconButton icon="send" onPress={handleSend} loading={sendMutation.isPending} />
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  list: { padding: 12 },
  bubble: { marginBottom: 8, maxWidth: "85%" },
  userBubble: { alignSelf: "flex-end" },
  assistantBubble: { alignSelf: "flex-start" },
  inputRow: { flexDirection: "row", alignItems: "center", padding: 8 },
  input: { flex: 1, marginRight: 8 },
});
