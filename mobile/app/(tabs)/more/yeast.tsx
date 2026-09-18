import { useState, useMemo } from "react";
import { FlatList, View, StyleSheet } from "react-native";
import { Text, List, TextInput, ActivityIndicator } from "react-native-paper";
import { Stack } from "expo-router";
import { useYeast } from "../../../hooks/useYeast";

export default function YeastScreen() {
  const { data, isLoading, isError } = useYeast();
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    if (!data) return [];
    const q = search.trim().toLowerCase();
    if (!q) return data;
    return data.filter((y) => y.name.toLowerCase().includes(q) || y.mead_style.toLowerCase().includes(q));
  }, [data, search]);

  if (isLoading) {
    return (
      <>
        <Stack.Screen options={{ title: "Yeast Reference" }} />
        <View style={styles.center}>
          <ActivityIndicator />
        </View>
      </>
    );
  }

  if (isError) {
    return (
      <>
        <Stack.Screen options={{ title: "Yeast Reference" }} />
        <View style={styles.center}>
          <Text>Couldn't load the yeast reference.</Text>
        </View>
      </>
    );
  }

  return (
    <>
      <Stack.Screen options={{ title: "Yeast Reference" }} />
      <View style={styles.container}>
      <TextInput
        mode="outlined"
        label="Search by name or style"
        value={search}
        onChangeText={setSearch}
        style={styles.search}
      />
      <FlatList
        data={filtered}
        keyExtractor={(item) => item.name}
        renderItem={({ item }) => (
          <List.Item
            title={item.name}
            description={`${item.mead_style} — ${item.attenuation}% attenuation, ${item.temp_range}`}
          />
        )}
      />
      </View>
    </>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 8 },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  search: { marginBottom: 8 },
});
