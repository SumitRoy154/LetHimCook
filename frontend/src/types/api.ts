export interface ApiErrorPayload {
  detail?: string | Record<string, unknown> | Array<unknown>;
  message?: string;
  error?: string;
}

export interface ApiListResponse<T> {
  data?: T[];
  items?: T[];
  results?: T[];
  payload?: T[];
}

export interface AuthUser {
  id?: number | string;
  email?: string;
  username?: string;
  name?: string;
  displayName?: string;
  avatarUrl?: string;
  role?: string;
}

export interface AuthSession {
  accessToken?: string;
  refreshToken?: string;
  tokenType?: string;
  expiresAt?: string | number;
  user?: AuthUser | null;
}

export interface WalletTransaction {
  id?: number | string;
  label?: string;
  title?: string;
  amount?: number;
  type?: string;
  status?: string;
  createdAt?: string;
  metadata?: Record<string, unknown>;
}

export interface WalletData {
  balance?: number;
  currency?: string;
  transactions?: WalletTransaction[];
}

export interface InventoryItem {
  id?: number | string;
  name?: string;
  quantity?: number | string;
  qty?: number | string;
  unit?: string;
  status?: string;
  emoji?: string;
  price?: number | string;
  category?: string;
}

export interface InventoryData {
  items?: InventoryItem[];
}

export interface OrderInput {
  dishName: string;
  dish_name?: string;
  notes?: string;
}

export interface OrderRecord {
  id?: number | string;
  dishName?: string;
  dish_name?: string;
  status?: string;
  total?: number;
  cost?: number;
  total_cost?: number;
  reward_received?: number;
  wallet_reward?: number;
  ingredients?: string[];
  shopping_summary?: any[];
  cooking_session?: any;
  judge_review?: any;
  createdAt?: string;
  updatedAt?: string;
}

export interface RecipeIngredient {
  name?: string;
  qty?: string;
  quantity?: string | number;
  price?: string | number;
  emoji?: string;
  icon?: string;
}

export interface RecipeData {
  dishName?: string;
  dish_name?: string;
  title?: string;
  ingredients?: RecipeIngredient[];
  steps?: string[];
  timeMinutes?: number;
  difficulty?: string;
  cost?: number;
}

export interface ReviewCategory {
  name?: string;
  score?: number;
  comment?: string;
  icon?: string;
  positive?: boolean;
}

export interface ReviewData {
  dishName?: string;
  dish_name?: string;
  score?: number;
  rating?: number;
  categories?: ReviewCategory[];
  reward?: number;
  comment?: string;
  review?: string;
}

export interface WorkflowStep {
  id?: number | string;
  name?: string;
  label?: string;
  status?: string;
  progress?: number;
  timestamp?: string;
}

export interface WorkflowExecution {
  executionId?: string;
  execution_id?: string;
  stage?: string;
  steps?: WorkflowStep[];
  progress?: number;
  status?: string;
}
