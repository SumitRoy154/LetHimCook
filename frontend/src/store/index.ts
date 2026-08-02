import { createJSONStorage, persist, type StateStorage } from "zustand/middleware";
import { create } from "zustand";
import type {
  AuthSession,
  AuthUser,
  InventoryData,
  InventoryItem,
  OrderRecord,
  ReviewData,
  ReviewCategory,
  WalletData,
  WalletTransaction,
  WorkflowExecution,
  WorkflowStep,
} from "@/types/api";
import { AUTH_STORAGE_KEY } from "@/constants";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  isHydrated: boolean;
  setSession: (session: AuthSession) => void;
  setUser: (user: AuthUser | null) => void;
  clearSession: () => void;
  markHydrated: () => void;
}

interface WalletState {
  balance: number | null;
  currency: string;
  transactions: WalletTransaction[];
  isLoading: boolean;
  error: string | null;
  setWallet: (wallet: WalletData) => void;
  setTransactions: (transactions: WalletTransaction[]) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

interface InventoryState {
  items: InventoryItem[];
  isLoading: boolean;
  error: string | null;
  setInventory: (inventory: InventoryData) => void;
  setItems: (items: InventoryItem[]) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

interface OrderState {
  orders: OrderRecord[];
  activeOrder: OrderRecord | null;
  isLoading: boolean;
  error: string | null;
  setOrders: (orders: OrderRecord[]) => void;
  setActiveOrder: (order: OrderRecord | null) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

interface WorkflowState {
  executions: WorkflowExecution[];
  activeExecution: WorkflowExecution | null;
  steps: WorkflowStep[];
  progress: number;
  isLoading: boolean;
  error: string | null;
  setWorkflow: (execution: WorkflowExecution) => void;
  setExecutions: (executions: WorkflowExecution[]) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

interface ReviewState {
  score: number | null;
  categories: ReviewCategory[];
  reward: number | null;
  isLoading: boolean;
  error: string | null;
  setReview: (review: ReviewData) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const memoryStorage: StateStorage = {
  getItem: () => null,
  setItem: () => undefined,
  removeItem: () => undefined,
};

const getClientStorage = () => (typeof window === "undefined" ? memoryStorage : localStorage);

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      isHydrated: false,
      setSession: (session) =>
        set({
          accessToken: session.accessToken ?? null,
          refreshToken: session.refreshToken ?? null,
          user: session.user ?? null,
        }),
      setUser: (user) => set({ user }),
      clearSession: () => set({ accessToken: null, refreshToken: null, user: null }),
      markHydrated: () => set({ isHydrated: true }),
    }),
    {
      name: AUTH_STORAGE_KEY,
      storage: createJSONStorage(getClientStorage),
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
      onRehydrateStorage: () => (state) => {
        state?.markHydrated();
      },
    }
  )
);

export const useWalletStore = create<WalletState>((set) => ({
  balance: null,
  currency: "INR",
  transactions: [],
  isLoading: false,
  error: null,
  setWallet: (wallet) =>
    set({
      balance: wallet.balance ?? null,
      currency: wallet.currency ?? "INR",
      transactions: wallet.transactions ?? [],
      error: null,
    }),
  setTransactions: (transactions) => set({ transactions }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  reset: () => set({ balance: null, currency: "INR", transactions: [], isLoading: false, error: null }),
}));

export const useInventoryStore = create<InventoryState>((set) => ({
  items: [],
  isLoading: false,
  error: null,
  setInventory: (inventory) => set({ items: inventory.items ?? [], error: null }),
  setItems: (items) => set({ items }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  reset: () => set({ items: [], isLoading: false, error: null }),
}));

export const useOrderStore = create<OrderState>((set) => ({
  orders: [],
  activeOrder: null,
  isLoading: false,
  error: null,
  setOrders: (orders) => set({ orders, error: null }),
  setActiveOrder: (activeOrder) => set({ activeOrder }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  reset: () => set({ orders: [], activeOrder: null, isLoading: false, error: null }),
}));

export const useWorkflowStore = create<WorkflowState>((set) => ({
  executions: [],
  activeExecution: null,
  steps: [],
  progress: 0,
  isLoading: false,
  error: null,
  setWorkflow: (execution) =>
    set({
      activeExecution: execution,
      steps: execution.steps ?? [],
      progress: execution.progress ?? 0,
      error: null,
    }),
  setExecutions: (executions) => set({ executions }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  reset: () => set({ executions: [], activeExecution: null, steps: [], progress: 0, isLoading: false, error: null }),
}));

export const useReviewStore = create<ReviewState>((set) => ({
  score: null,
  categories: [],
  reward: null,
  isLoading: false,
  error: null,
  setReview: (review) =>
    set({
      score: review.score ?? review.rating ?? null,
      categories: review.categories ?? [],
      reward: review.reward ?? null,
      error: null,
    }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  reset: () => set({ score: null, categories: [], reward: null, isLoading: false, error: null }),
}));
