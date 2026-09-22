import { ScrollView, View, StyleSheet } from "react-native";
import { Text, List, Divider } from "react-native-paper";
import { Stack } from "expo-router";

const MEAD_TYPES: { title: string; description: string }[] = [
  { title: "Acerglyn", description: "Made with maple syrup in addition to honey, providing rich, sweet flavors." },
  { title: "Bochet", description: "Mead made by caramelizing the honey before fermentation, imparting rich, toasty flavors." },
  { title: "Braggot", description: "A blend of mead and beer, often including malted barley." },
  { title: "Capsicumel", description: "Mead infused with chili peppers, adding a spicy kick to the traditional honey profile." },
  { title: "Coffeemel", description: "Mead with the addition of coffee. Cold-brewed coffee is a great option here as it has a lower acidity." },
  { title: "Cyser", description: "A type of melomel made with apples or apple juice, blending mead with cider." },
  { title: "Hippocras", description: "A pyment variant spiced with herbs and spices, similar to mulled wine." },
  { title: "Hydromel", description: "A low-alcohol mead, often lighter and more refreshing." },
  { title: "Melomel", description: "Mead that includes fruit. Common fruits include berries, apples, and stone fruits." },
  { title: "Metheglin", description: "Mead infused with spices or herbs, such as cinnamon, ginger, or cloves." },
  { title: "Morat", description: "A melomel made specifically with mulberries, resulting in deep, rich berry flavors." },
  { title: "Omphacomel", description: "Made with verjuice (the juice of unripe grapes), yielding a tart and tangy flavor profile." },
  { title: "Oxymel", description: "Includes vinegar—sometimes used as a base for medicinal herb tonics." },
  { title: "Pyment", description: "Made with grapes or grape juice, combining mead with wine." },
  { title: "Rhodomel", description: "Mead made with roses or rose petals, often floral and aromatic." },
  { title: "Sack Mead", description: "A stronger, sweeter mead with higher honey content, often aged for longer periods." },
  { title: "Tej", description: "Traditional Ethiopian mead using \"gesho,\" an herb that plays a role similar to hops." },
  { title: "Traditional Mead", description: "Just honey, water, and yeast—the simplest form of mead." },
];

const BREWING_TERMS: { title: string; description: string }[] = [
  { title: "ABV (Alcohol by Volume)", description: "Measurement of alcohol content, expressed as a percentage of total volume." },
  { title: "Aeration", description: "Adding oxygen to wort or must to promote yeast health and fermentation." },
  { title: "Attenuation", description: "Percentage of sugar converted to alcohol and CO₂—indicates completeness of fermentation." },
  { title: "Brix", description: "Scale for sugar content in a solution; useful for honey or fruit juice concentration." },
  { title: "Flocculation", description: "Yeast cells clump and settle, helping to clarify the beverage." },
  { title: "Gravity", description: "Density relative to water; Original vs Final Gravity tracks fermentation progress." },
  { title: "Hydrometer", description: "Instrument for measuring specific gravity and estimating potential alcohol." },
  { title: "Krausen", description: "Foamy head on actively fermenting beer; shows vigorous yeast activity." },
  { title: "Must", description: "Unfermented honey-water mix for mead—analogous to crushed fruit for wine." },
  { title: "Pitching", description: "Introducing yeast to wort or must to start fermentation." },
  { title: "Racking", description: "Transferring fermented liquid off sediment to another vessel." },
  { title: "Secondary Fermentation", description: "Aging phase in a new vessel for clarification and flavor development." },
  { title: "Sparging", description: "Rinsing grains with hot water to extract remaining sugars after the mash." },
  { title: "Wort", description: "Sugar-rich liquid extracted during brewing that yeast will ferment." },
  { title: "Yeast Nutrient", description: "Additives ensuring yeast has the minerals and nitrogen it needs for a robust fermentation." },
];

export default function MeadHistoryScreen() {
  return (
    <>
      <Stack.Screen options={{ title: "Mead History" }} />
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <Text variant="titleMedium" style={styles.sectionTitle}>
          History of Mead
        </Text>

        <Text variant="bodyMedium" style={styles.paragraph}>
          Long before clay pots, vineyards, or even the idea of farming, our distant ancestors
          probably discovered mead the way you might stumble on a forgotten bottle of kombucha in
          the back of the fridge: by accident. Imagine a rainstorm filling a hollow tree that bees
          had stocked with honey. A little wild yeast drops in, the mix ferments, and—voilà—someone
          curious (or thirsty) tastes humanity's first buzz. That happy accident could have happened
          as far back as 20,000–40,000 years ago in southern Africa.
        </Text>

        <Text variant="bodyMedium" style={styles.paragraph}>
          Fast-forward to 7000 BCE in northern China. Archaeologists analysing Neolithic pottery
          from Jiahu found chemical fingerprints of honey blended with rice and fruit—proof that
          people were deliberately brewing what we'd now call a fruit mead. That makes it the oldest
          confirmed alcoholic beverage in the archaeological record, beating out both wine and beer.
        </Text>

        <Text variant="bodyMedium" style={styles.paragraph}>
          • Ethiopia & East Africa — tej: honey, water and gesho leaves, once reserved for royalty,
          still poured at celebrations today.{"\n"}
          • India's Rig-Veda (≈ 1700 BCE): hymns praise honeyed drinks (madhu) as gifts of the gods.
          {"\n"}
          • Greece & Egypt: Aristotle analysed mead; jars in Tutankhamun's tomb once held it.{"\n"}
          • Celtic & Norse lore: rivers of mead in the Celtic afterlife and Odin's stolen "Mead of
          Poetry" for inspiring mortal bards. Our word honeymoon? A month's supply of mead for
          newly-weds.
        </Text>

        <Text variant="bodyMedium" style={styles.paragraph}>
          When medieval monks got involved, the drink levelled-up. Abbey records describe herb-laced
          metheglins and fruit-packed melomels. In Poland and Lithuania, dense woodland honey
          produced rich styles like półtorak and dwójniak—still legally protected regional
          specialities today.
        </Text>

        <Text variant="bodyMedium" style={styles.paragraph}>
          Then came sugar, rum and cheap imported wine. By the 1600s mead was losing its throne to
          beverages that cost less to make and travelled better in barrels. Outside Europe, though,
          traditions in Ethiopia, Kenya, Russia (medovukha) and Finland (sima) carried on
          uninterrupted.
        </Text>

        <Text variant="bodyMedium" style={styles.paragraph}>
          The modern comeback began in the 1960s home-brewing scene, blossomed with U.S. craft
          producers in the 1990s, and today counts hundreds of commercial meaderies worldwide. From
          champagne-dry sparklers to hazy, dry-hopped "session" cans, mead is once again on the
          cutting edge of fermentation science.
        </Text>

        <Text variant="bodyMedium" style={styles.paragraph}>
          So, next time you lift a glass—whether it's a traditional golden pour or a tart
          pineapple-infused pét-nat—you're tapping into tens of thousands of years of human
          curiosity, cooperation with bees, and the universal desire to turn something sweet into
          something just a little bit stronger. Skål!
        </Text>

        <Divider style={styles.divider} />

        <List.Accordion title="Types of Mead" left={(props) => <List.Icon {...props} icon="book-open-page-variant" />}>
          {MEAD_TYPES.map((item) => (
            <List.Item key={item.title} title={item.title} description={item.description} titleNumberOfLines={2} descriptionNumberOfLines={4} />
          ))}
        </List.Accordion>

        <List.Accordion title="Brewing & Fermenting Terms" left={(props) => <List.Icon {...props} icon="flask-outline" />}>
          {BREWING_TERMS.map((item) => (
            <List.Item key={item.title} title={item.title} description={item.description} titleNumberOfLines={2} descriptionNumberOfLines={4} />
          ))}
        </List.Accordion>
      </ScrollView>
    </>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { padding: 16, paddingBottom: 32 },
  sectionTitle: { marginBottom: 8 },
  paragraph: { marginBottom: 12 },
  divider: { marginVertical: 12 },
});
