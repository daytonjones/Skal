export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Ingredient {
  id: number;
  name: string;
  type: "honey" | "yeast" | "additive";
}

export interface RecipeIngredient {
  id: number;
  ingredient: Ingredient;
  quantity: string;
  order: number;
}

export interface Recipe {
  id: number;
  name: string;
  batch_size: string;
  instructions: string;
  is_public: boolean;
  is_owner: boolean;
  recipe_ingredients: RecipeIngredient[];
}

export interface RecipeIngredientInput {
  ingredient_id: number;
  quantity: string;
  order: number;
}

export interface RecipeInput {
  name: string;
  batch_size: string;
  instructions: string;
  is_public: boolean;
  recipe_ingredients: RecipeIngredientInput[];
}

export interface Batch {
  id: number;
  recipe: number | null;
  name: string;
  batch_size: string;
  og: string;
  fg: string | null;
  primary_date: string;
  secondary_date: string | null;
  bottling_date: string | null;
  notes: string;
  is_public: boolean;
  is_owner: boolean;
  create_must_done: boolean;
  create_must_date: string | null;
  create_must_note: string;
  pitch_yeast_done: boolean;
  pitch_yeast_date: string | null;
  pitch_yeast_note: string;
  fo_24h_done: boolean;
  fo_24h_date: string | null;
  fo_24h_note: string;
  fo_48h_done: boolean;
  fo_48h_date: string | null;
  fo_48h_note: string;
  fo_72h_done: boolean;
  fo_72h_date: string | null;
  fo_72h_note: string;
  fo_1_3_break_done: boolean;
  fo_1_3_break_date: string | null;
  fo_1_3_break_note: string;
  rack_secondary_done: boolean;
  rack_secondary_date: string | null;
  rack_secondary_note: string;
  bottled_done: boolean;
  bottled_date: string | null;
  bottled_note: string;
  bottle_count: number | null;
  storage_location: string;
  stage: "planned" | "active" | "secondary" | "bottled";
  checklist_progress: number;
  abv: number | null;
  bottles_remaining: number | null;
}

export type BatchInput = Omit<
  Batch,
  "id" | "is_owner" | "stage" | "checklist_progress" | "abv" | "bottles_remaining"
>;

export interface TastingNote {
  id: number;
  batch: number;
  date: string;
  aroma: string;
  flavor: string;
  overall: string;
  score: number;
}

export type TastingNoteInput = Omit<TastingNote, "id">;

export interface BottleConsumption {
  id: number;
  batch: number;
  date: string;
  quantity: number;
  notes: string;
}

export type BottleConsumptionInput = Omit<BottleConsumption, "id">;

export interface BatchImage {
  id: number;
  batch: number;
  image: string;
  caption: string;
  order: number;
}

export interface PantryItem {
  id: number;
  ingredient: Ingredient;
  quantity: string;
  notes: string;
}

export interface PantryItemInput {
  ingredient_id: number;
  quantity: string;
  notes: string;
}

export interface Yeast {
  name: string;
  type: string;
  tolerance: number;
  attenuation: number;
  temp_range: string;
  mead_style: string;
  notes: string;
}

export interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  pending_recipe: Record<string, unknown> | null;
  created_at: string;
}

export interface NotificationPrefs {
  email_notifications: boolean;
  notify_tosna: boolean;
  notify_sg_check: boolean;
  notify_rack: boolean;
  notify_bottle: boolean;
}

export interface Me {
  id: number;
  username: string;
  email: string;
  theme: "light" | "dark";
  is_approved: boolean;
  notification_prefs: NotificationPrefs | null;
}
