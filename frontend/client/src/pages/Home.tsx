"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useRef, useState } from "react";
import CursorGlow from "@/components/CursorGlow";
import GrainOverlay from "@/components/GrainOverlay";
import ProgressIndicator from "@/components/ProgressIndicator";
import SectionCooking from "@/components/sections/SectionCooking";
import SectionFinalDish from "@/components/sections/SectionFinalDish";
import SectionFooter from "@/components/sections/SectionFooter";
import SectionHowItWorks from "@/components/sections/SectionHowItWorks";
import SectionIntro from "@/components/sections/SectionIntro";
import SectionInventory from "@/components/sections/SectionInventory";
import SectionJudgeAI from "@/components/sections/SectionJudgeAI";
import SectionNextOrder from "@/components/sections/SectionNextOrder";
import SectionOrder from "@/components/sections/SectionOrder";
import SectionShopping from "@/components/sections/SectionShopping";
import AuthModal from "@/components/AuthModal";
import OrderHistoryModal from "@/components/OrderHistoryModal";
import { useAuthStore, useInventoryStore, useOrderStore, useReviewStore, useWalletStore, useWorkflowStore } from "@/store";
import type { InventoryItem, RecipeIngredient, ReviewCategory } from "@/types/api";
import { createOrder, getOrders, getOrderById } from "@/services/order";
import { getInventory } from "@/services/inventory";
import { getRecipe } from "@/services/recipe";
import { getReviewByDish } from "@/services/review";
import { getWallet } from "@/services/wallet";
import { getWorkflowHistory } from "@/services/workflow";
import { motion } from "framer-motion";

interface ShoppingItem {
  name: string;
  qty: string;
  price: string;
  icon: string;
}

interface PantryItem {
  name: string;
  emoji: string;
  status: string;
}

interface CookingStep {
  emoji: string;
  text: string;
}

type CookingStage =
  | "intro"
  | "order"
  | "shopping"
  | "inventory"
  | "cooking"
  | "judge-ai"
  | "final-dish"
  | "next-order"
  | "how-it-works"
  | "footer";

const stageOrder: CookingStage[] = [
  "intro",
  "order",
  "shopping",
  "inventory",
  "cooking",
  "judge-ai",
  "final-dish",
  "next-order",
  "how-it-works",
  "footer",
];

const fallbackIcons = ["🧀", "🍅", "🧈", "🥛", "🧅", "🧄", "🫚", "🌶️"];
const fallbackStepIcons = ["🥬", "🔪", "🍅", "🔥", "🧈", "🥘", "🫕"];

const permanentStaples: PantryItem[] = [];

function formatPrice(value: number | string | undefined) {
  if (value == null || value === "") return "₹0";
  if (typeof value === "number") return `₹${value}`;
  return value.startsWith("₹") ? value : `₹${value}`;
}

function asNumber(value: number | string | undefined) {
  if (value == null || value === "") return 0;
  if (typeof value === "number") return value;
  const parsed = Number(String(value).replace(/[^0-9.]/g, ""));
  return Number.isFinite(parsed) ? parsed : 0;
}

function getEarnedCoins(orderData: {
  reward_received?: number | string;
  wallet_reward?: number | string;
  bonus_coins?: number | string;
  reward_coins?: number | string;
  reward?: number | string;
}, fallbackCost: number) {
  const rewardValue =
    asNumber(orderData.reward_received) ||
    asNumber(orderData.wallet_reward) ||
    asNumber(orderData.bonus_coins) ||
    asNumber(orderData.reward_coins) ||
    asNumber(orderData.reward);

  if (rewardValue > 0) {
    return rewardValue;
  }

  return fallbackCost > 0 ? fallbackCost * 2 : 0;
}

function getDishName(order: { dishName?: string; dish_name?: string } | undefined, fallback: string) {
  return order?.dishName ?? order?.dish_name ?? fallback;
}

function extractIngredients(raw: any): RecipeIngredient[] {
  if (!raw) return [];
  if (Array.isArray(raw)) return raw;
  if (typeof raw === "object") {
    if (Array.isArray(raw.items)) return raw.items;
    if (Array.isArray(raw.ingredients)) return raw.ingredients;
  }
  return [];
}

function extractName(ing: any): string {
  if (!ing) return "Ingredient";
  if (typeof ing === "string") return ing;
  if (typeof ing.name === "string") return ing.name;
  if (typeof ing.ingredient === "string") return ing.ingredient;
  if (typeof ing.name === "object") return extractName(ing.name);
  return String(ing.name || ing || "Ingredient");
}

function mapShoppingItems(rawIngredients: any): ShoppingItem[] {
  const items = extractIngredients(rawIngredients);
  return items
    .filter((ing) => {
      const name = extractName(ing).toLowerCase();
      return !name.includes("salt") && !name.includes("water") && !name.includes("spice") && !name.includes("oil");
    })
    .map((ingredient, index) => {
      const name = extractName(ingredient);
      return {
        name,
        qty: String(ingredient.qty ?? ingredient.quantity ?? "1 item"),
        price: formatPrice(ingredient.price ?? (index + 1) * 15),
        icon: ingredient.icon ?? ingredient.emoji ?? fallbackIcons[index % fallbackIcons.length],
      };
    });
}

function mapPantryItems(rawIngredients: any, shoppingItems: ShoppingItem[]): PantryItem[] {
  const ingredients = extractIngredients(rawIngredients);
  if (!ingredients.length) {
    return [];
  }

  const recipeItems: PantryItem[] = ingredients.map((ing, idx) => {
    const name = extractName(ing);
    const isPurchased = shoppingItems.some((s) => s.name.toLowerCase() === name.toLowerCase());
    return {
      name,
      emoji: ing.emoji ?? ing.icon ?? fallbackIcons[idx % fallbackIcons.length],
      status: isPurchased ? "Purchased" : "Kitchen Staple",
    };
  });

  return recipeItems;
}

function mapCookingSteps(steps: string[] | undefined): CookingStep[] {
  return (steps ?? []).map((step, index) => ({
    emoji: fallbackStepIcons[index % fallbackStepIcons.length],
    text: step,
  }));
}

function buildSuggestions(orders: { dishName?: string; dish_name?: string }[], currentDish: string) {
  const unique = Array.from(
    new Set(
      orders
        .map((order) => getDishName(order, ""))
        .concat([currentDish, "Paneer Butter Masala", "Masala Dosa", "Chicken Biryani", "Butter Chicken", "Pasta Carbonara"])
        .filter(Boolean)
    )
  );
  return unique.slice(0, 6);
}

export default function Home() {
  const [stage, setStage] = useState<CookingStage>("intro");
  const [currentDish, setCurrentDish] = useState("");
  const [coinsEarned, setCoinsEarned] = useState(0);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [historyModalOpen, setHistoryModalOpen] = useState(false);
  const [aiErrorBanner, setAiErrorBanner] = useState<string | null>(null);
  const [activeOrderId, setActiveOrderId] = useState<number | null>(null);

  const sectionRefs = useRef<Map<string, HTMLDivElement>>(new Map());
  const queryClient = useQueryClient();

  const user = useAuthStore((state) => state.user);
  const accessToken = useAuthStore((state) => state.accessToken);
  const clearSession = useAuthStore((state) => state.clearSession);

  const setWallet = useWalletStore((state) => state.setWallet);
  const setWalletLoading = useWalletStore((state) => state.setLoading);
  const setWalletError = useWalletStore((state) => state.setError);
  const walletStoreBalance = useWalletStore((state) => state.balance);

  const setInventory = useInventoryStore((state) => state.setInventory);
  const setInventoryLoading = useInventoryStore((state) => state.setLoading);

  const setOrders = useOrderStore((state) => state.setOrders);
  const setOrdersLoading = useOrderStore((state) => state.setLoading);

  const setExecutions = useWorkflowStore((state) => state.setExecutions);
  const setWorkflowLoading = useWorkflowStore((state) => state.setLoading);
  const activeExecution = useWorkflowStore((state) => state.activeExecution);

  const setReview = useReviewStore((state) => state.setReview);
  const setReviewLoading = useReviewStore((state) => state.setLoading);

  const walletQuery = useQuery({
    queryKey: ["wallet"],
    queryFn: getWallet,
    enabled: Boolean(accessToken),
  });
  const inventoryQuery = useQuery({
    queryKey: ["inventory"],
    queryFn: getInventory,
    enabled: Boolean(accessToken),
  });
  const ordersQuery = useQuery({
    queryKey: ["orders"],
    queryFn: getOrders,
    enabled: Boolean(accessToken),
  });
  const workflowHistoryQuery = useQuery({
    queryKey: ["workflow-history"],
    queryFn: getWorkflowHistory,
    enabled: Boolean(accessToken),
  });
  const recipeQuery = useQuery({
    queryKey: ["recipe", currentDish],
    queryFn: () => getRecipe(currentDish),
    enabled: Boolean(currentDish && accessToken),
  });
  const reviewQuery = useQuery({
    queryKey: ["review", currentDish],
    queryFn: () => getReviewByDish(currentDish),
    enabled: Boolean(currentDish && accessToken),
  });

  const createOrderMutation = useMutation({
    mutationFn: createOrder,
    onMutate: () => setAiErrorBanner(null),
    onSuccess: async (createdOrder) => {
      const nextDish = getDishName(createdOrder, currentDish);
      setCurrentDish(nextDish);
      if (createdOrder.id) {
        setActiveOrderId(Number(createdOrder.id));
      }
      setStage("order");

      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["orders"] }),
        queryClient.invalidateQueries({ queryKey: ["wallet"] }),
        queryClient.invalidateQueries({ queryKey: ["inventory"] }),
        queryClient.invalidateQueries({ queryKey: ["workflow-history"] }),
        queryClient.invalidateQueries({ queryKey: ["recipe", nextDish] }),
        queryClient.invalidateQueries({ queryKey: ["review", nextDish] }),
      ]);
    },
    onError: (err: any) => {
      const msg = String(err?.response?.data?.detail || err?.message || "");
      if (msg.includes("429") || msg.includes("quota") || err?.response?.status === 429) {
        setAiErrorBanner("AI services are currently unavailable. We are out of AI tokens. Please try again later.");
      } else {
        setAiErrorBanner(`Error processing order: ${msg || "Kitchen error"}`);
      }
    },
  });

  const [walletGlow, setWalletGlow] = useState<"red" | "green" | null>(null);
  const prevWalletRef = useRef<number | null>(null);

  // Queue of pending target stages to pace step-by-step
  const targetStageQueueRef = useRef<CookingStage[]>([]);
  const isPacingRef = useRef(false);

  const processStageQueue = useCallback(async () => {
    if (isPacingRef.current) return;
    isPacingRef.current = true;

    while (targetStageQueueRef.current.length > 0) {
      const nextStage = targetStageQueueRef.current.shift()!;
      setStage(nextStage);

      // Wait for section animations to complete before moving to the next section
      const stageDelays: Record<string, number> = {
        order: 2200,      // Order card + stamp spring animation (~2.2s)
        shopping: 2500,   // Shopping items list stagger (~2.5s)
        inventory: 2200,  // Pantry grid appearance (~2.2s)
        cooking: 3000,    // Multi-step cooking progression (~3.0s)
        "judge-ai": 2500, // AI Assessment evaluation & typewriter text (~2.5s)
        "final-dish": 2000,
      };

      const delay = stageDelays[nextStage] || 2000;
      await new Promise((resolve) => setTimeout(resolve, delay));
    }

    isPacingRef.current = false;
  }, []);

  const queueStageTransition = useCallback((targetStage: CookingStage) => {
    const currentIndex = stageOrder.indexOf(stage);
    const targetIndex = stageOrder.indexOf(targetStage);

    if (targetIndex <= currentIndex) return;

    // Enqueue all intermediate stages step-by-step
    for (let i = currentIndex + 1; i <= targetIndex; i++) {
      const stepStage = stageOrder[i];
      if (!targetStageQueueRef.current.includes(stepStage)) {
        targetStageQueueRef.current.push(stepStage);
      }
    }

    processStageQueue();
  }, [stage, processStageQueue]);

  // Real backend order polling with smooth paced stage pipeline
  useEffect(() => {
    if (!activeOrderId || !accessToken) return;

    const interval = setInterval(async () => {
      try {
        const orderData = await getOrderById(activeOrderId);
        const st = (orderData?.status || "").toUpperCase();

        if (st === "PENDING" || st === "INITIALIZATION") {
          queueStageTransition("order");
        } else if (st === "SHOPPING") {
          queueStageTransition("shopping");
        } else if (st === "COOKING") {
          queueStageTransition("cooking");
        } else if (st === "JUDGING" || st === "REVIEW") {
          queueStageTransition("judge-ai");
        } else if (st === "COMPLETED") {
          queueStageTransition("final-dish");
          const cost = Number(orderData.total_cost || orderData.total || orderData.cost || 0);
          const earned = getEarnedCoins(orderData, cost);
          setCoinsEarned(earned);

          const cachedWallet = queryClient.getQueryData<{ balance?: number; currency?: string; transactions?: any[] }>(["wallet"]);
          const currentBalance = cachedWallet?.balance ?? walletStoreBalance ?? 0;
          const creditedBalance = currentBalance + earned;

          setWallet({
            balance: creditedBalance,
            currency: cachedWallet?.currency ?? "INR",
            transactions: cachedWallet?.transactions ?? [],
          });

          queryClient.setQueryData(["wallet"], (previous: any) => ({
            ...(previous ?? {}),
            balance: creditedBalance,
            currency: cachedWallet?.currency ?? previous?.currency ?? "INR",
            transactions: cachedWallet?.transactions ?? previous?.transactions ?? [],
          }));

          queryClient.invalidateQueries({ queryKey: ["wallet"] });
          queryClient.invalidateQueries({ queryKey: ["orders"] });
          clearInterval(interval);
          setActiveOrderId(null);
        } else if (st === "FAILED") {
          setAiErrorBanner("AI services are currently unavailable. We are out of AI tokens. Please try again later.");
        }
      } catch {
        // Polling error fallback
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [activeOrderId, accessToken, queueStageTransition]);

  const isManualScrollingRef = useRef(false);

  const scrollToSection = useCallback((name: CookingStage) => {
    const element = sectionRefs.current.get(name);
    if (element) {
      isManualScrollingRef.current = true;
      element.scrollIntoView({ behavior: "smooth", block: "start" });
      setTimeout(() => {
        isManualScrollingRef.current = false;
      }, 800);
    }
  }, []);

  const handleSelectStage = useCallback((selectedStage: CookingStage) => {
    setStage(selectedStage);
    scrollToSection(selectedStage);
  }, [scrollToSection]);

  // ScrollSpy: Update active stage dynamically based on scroll position
  useEffect(() => {
    const handleScroll = () => {
      if (isManualScrollingRef.current) return;
      const scrollPosition = window.scrollY + window.innerHeight / 3;

      for (let i = stageOrder.length - 1; i >= 0; i--) {
        const stageName = stageOrder[i];
        const element = sectionRefs.current.get(stageName);
        if (element) {
          const top = element.offsetTop;
          if (scrollPosition >= top) {
            setStage((prev) => (prev !== stageName ? stageName : prev));
            break;
          }
        }
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    if (walletQuery.data) setWallet(walletQuery.data);
    setWalletLoading(walletQuery.isFetching);
    if (walletQuery.error) setWalletError(String(walletQuery.error));

    const currentBal = walletQuery.data?.balance ?? walletStoreBalance;
    if (currentBal != null && prevWalletRef.current != null) {
      if (currentBal < prevWalletRef.current) {
        setWalletGlow("red");
        const t = setTimeout(() => setWalletGlow(null), 2500);
        return () => clearTimeout(t);
      } else if (currentBal > prevWalletRef.current) {
        setWalletGlow("green");
        const t = setTimeout(() => setWalletGlow(null), 2500);
        return () => clearTimeout(t);
      }
    }
    prevWalletRef.current = currentBal;
  }, [setWallet, setWalletError, setWalletLoading, walletQuery.data, walletQuery.error, walletQuery.isFetching, walletStoreBalance]);

  useEffect(() => {
    if (inventoryQuery.data) setInventory(inventoryQuery.data);
    setInventoryLoading(inventoryQuery.isFetching);
  }, [inventoryQuery.data, inventoryQuery.isFetching, setInventory, setInventoryLoading]);

  useEffect(() => {
    if (ordersQuery.data) setOrders(ordersQuery.data);
    setOrdersLoading(ordersQuery.isFetching);
  }, [ordersQuery.data, ordersQuery.isFetching, setOrders, setOrdersLoading]);

  useEffect(() => {
    if (workflowHistoryQuery.data) setExecutions(workflowHistoryQuery.data);
    setWorkflowLoading(workflowHistoryQuery.isFetching);
  }, [setExecutions, setWorkflowLoading, workflowHistoryQuery.data, workflowHistoryQuery.isFetching]);

  useEffect(() => {
    if (reviewQuery.data) {
      setReview(reviewQuery.data);
    }
    setReviewLoading(reviewQuery.isFetching);
  }, [reviewQuery.data, reviewQuery.isFetching, setReview, setReviewLoading]);

  const shoppingItems = mapShoppingItems(recipeQuery.data?.ingredients);
  const pantryItems = mapPantryItems(recipeQuery.data?.ingredients, shoppingItems);
  const cookingSteps = mapCookingSteps(recipeQuery.data?.steps);
  const suggestions = buildSuggestions(ordersQuery.data ?? [], currentDish);

  const walletBalance = walletQuery.data?.balance ?? walletStoreBalance;
  const totalCost = recipeQuery.data?.cost ?? shoppingItems.reduce((sum, item) => sum + asNumber(item.price), 0);
  const ingredientCount = shoppingItems.length || pantryItems.length || 0;
  const geminiReviewText = reviewQuery.data?.categories?.[0]?.comment || reviewQuery.data?.comment || "Exceptional flavor harmony and presentation evaluated by Gemini Pro AI.";
  const agentName = "Planner AI (Groq - Llama 3.3 70B)";

  const handleStartCooking = async (dishName: string) => {
    if (!accessToken) {
      setAuthModalOpen(true);
      return;
    }

    setCurrentDish(dishName);
    setStage("order");

    try {
      await createOrderMutation.mutateAsync({ dishName, dish_name: dishName });
    } catch {
      // Errors handled via mutation onError
    }
  };

  const registerSection = (name: string) => (element: HTMLDivElement | null) => {
    if (element) sectionRefs.current.set(name, element);
  };

  // Requirement 1: Unauthenticated Single Full-Screen Landing View
  if (!accessToken || !user) {
    return (
      <div className="bg-[#0a0a0a] h-screen w-screen overflow-hidden relative flex flex-col items-center justify-center p-6 text-center">
        <CursorGlow />
        <GrainOverlay />

        {/* Ambient Glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-lime-500/[0.06] blur-[220px] pointer-events-none" />

        <div className="relative z-10 max-w-xl mx-auto flex flex-col items-center">
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="mb-4"
            style={{ fontFamily: "'Grand Hotel', cursive", fontSize: "clamp(3.5rem, 10vw, 6.5rem)", lineHeight: 1 }}
          >
            <span className="text-white/90">Let Him </span>
            <span className="text-gradient-lime">Cook !!</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-gray-400 text-base md:text-lg mb-8 leading-relaxed font-body"
            style={{ fontFamily: "'Lato', sans-serif" }}
          >
            An autonomous AI cooking simulator powered by multi-agent LLMs 
            <br />(Groq Llama, Anthropic Claude, and Google Gemini)
          </motion.p>

          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="glass-strong p-8 rounded-2xl border border-white/10 shadow-2xl mb-8 w-full max-w-md text-center"
          >
            <p className="text-amber-400 text-xs uppercase tracking-widest font-mono font-bold mb-2">Starting Gift</p>
            <h3 className="text-2xl font-bold text-white mb-2 font-body" style={{ fontFamily: "'Lato', sans-serif" }}>
              Get 1000 Free Coins
            </h3>
            <p className="text-gray-400 text-xs mb-6 font-body">
              Claim your starting wallet balance to order ingredients and run your autonomous AI kitchen.
            </p>

            <button
              type="button"
              onClick={() => setAuthModalOpen(true)}
              className="w-full py-4 rounded-xl bg-gradient-to-r from-lime-400 to-emerald-400 text-black font-bold text-base tracking-wide hover:scale-[1.02] active:scale-[0.98] transition-all shadow-[0_0_25px_rgba(163,230,53,0.5)] font-body"
              style={{ fontFamily: "'Lato', sans-serif" }}
            >
              Login / Register to claim your 1000 Coins
            </button>
          </motion.div>
        </div>

        <AuthModal open={authModalOpen} onOpenChange={setAuthModalOpen} />
      </div>
    );
  }

  // Authenticated Main Application Experience
  return (
    <div className="bg-[#0a0a0a] min-h-screen overflow-x-hidden">
      <CursorGlow />
      <GrainOverlay />

      {/* Floating Header Bar */}
      <div className="fixed top-4 right-4 z-50 flex items-center gap-2">
        <button
          type="button"
          onClick={() => setHistoryModalOpen(true)}
          className="glass rounded-full px-3.5 py-2 flex items-center gap-1.5 shadow-lg shadow-black/20 hover:bg-white/10 transition-all text-xs font-semibold text-gray-300 font-body"
        >
          <span>📜</span>
          <span className="hidden sm:inline">History</span>
        </button>

        <motion.div
          animate={
            walletGlow === "red"
              ? { scale: [1, 1.08, 1, 1.08, 1], boxShadow: ["0 0 0px rgba(239,68,68,0)", "0 0 25px rgba(239,68,68,0.9)", "0 0 0px rgba(239,68,68,0)", "0 0 25px rgba(239,68,68,0.9)", "0 0 0px rgba(239,68,68,0)"] }
              : walletGlow === "green"
              ? { scale: [1, 1.08, 1, 1.08, 1], boxShadow: ["0 0 0px rgba(52,211,153,0)", "0 0 25px rgba(52,211,153,0.9)", "0 0 0px rgba(52,211,153,0)", "0 0 25px rgba(52,211,153,0.9)", "0 0 0px rgba(52,211,153,0)"] }
              : {}
          }
          transition={{ duration: 1.8 }}
          className={`glass rounded-full px-4 py-2 flex items-center gap-2 shadow-lg transition-all border ${
            walletGlow === "red"
              ? "border-red-500 bg-red-500/20"
              : walletGlow === "green"
              ? "border-emerald-400 bg-emerald-400/20"
              : "border-white/10"
          }`}
        >
          <div className="w-6 h-6 rounded-full bg-gradient-to-br from-yellow-400 to-amber-600 flex items-center justify-center text-xs font-bold text-black font-body">
            ₹
          </div>
          <div>
            <p className="text-[8px] text-gray-400 font-medium tracking-wider uppercase font-body">Wallet</p>
            <p className={`text-sm font-bold font-mono text-white tabular-nums ${walletQuery.isLoading && !walletBalance ? "animate-pulse" : ""}`}>
              {walletBalance == null ? "—" : `₹${walletBalance}`}
            </p>
          </div>
        </motion.div>

        <div className="glass rounded-full px-3.5 py-2 flex items-center gap-2 shadow-lg shadow-black/20 font-body">
          <span className="w-2 h-2 rounded-full bg-lime-400 animate-pulse" />
          <span className="text-xs font-semibold text-white">{user?.username || user?.name || "Chef"}</span>
          <button
            type="button"
            onClick={() => clearSession()}
            className="text-[10px] text-gray-400 hover:text-red-400 uppercase tracking-wider ml-1 underline transition-colors"
          >
            Logout
          </button>
        </div>
      </div>

      {/* AI Token Error Banner */}
      {aiErrorBanner && (
        <div className="fixed top-16 left-1/2 -translate-x-1/2 z-50 max-w-lg w-full px-4">
          <div className="bg-red-900/90 border border-red-500 text-white text-xs p-3.5 rounded-xl shadow-2xl backdrop-blur-md flex items-center justify-between font-body">
            <span>⚠️ {aiErrorBanner}</span>
            <button type="button" onClick={() => setAiErrorBanner(null)} className="text-gray-300 hover:text-white font-bold ml-2">✕</button>
          </div>
        </div>
      )}

      <AuthModal open={authModalOpen} onOpenChange={setAuthModalOpen} />
      <OrderHistoryModal open={historyModalOpen} onOpenChange={setHistoryModalOpen} />

      <ProgressIndicator currentStage={stage} stages={stageOrder} onSelectStage={(s) => handleSelectStage(s as CookingStage)} />

      <div className="w-full">
        {/* Section 1: Intro & Order Input */}
        <div ref={registerSection("intro")}>
          <SectionIntro
            isActive={stage === "intro"}
            coins={walletBalance ?? 0}
            onStart={handleStartCooking}
            currentDish={currentDish}
            isLoading={createOrderMutation.isPending}
          />
        </div>

        {/* Section 2: Order Accepted */}
        <div ref={registerSection("order")}>
          <SectionOrder
            isActive={stage === "order" || stage === "shopping" || stage === "inventory" || stage === "cooking" || stage === "judge-ai" || stage === "final-dish" || stage === "next-order" || stage === "how-it-works" || stage === "footer"}
            dish={currentDish}
            orderId={activeOrderId || undefined}
            estimatedCost={recipeQuery.data?.cost ?? totalCost ?? undefined}
            ingredientCount={ingredientCount || undefined}
            agentName={agentName}
          />
        </div>

        {/* Section 3: Shopping */}
        <div ref={registerSection("shopping")}>
          <SectionShopping
            isActive={stage === "shopping" || stage === "inventory" || stage === "cooking" || stage === "judge-ai" || stage === "final-dish" || stage === "next-order" || stage === "how-it-works" || stage === "footer"}
            ingredients={shoppingItems}
            total={totalCost}
          />
        </div>

        {/* Section 4: Inventory */}
        <div ref={registerSection("inventory")}>
          <SectionInventory
            isActive={stage === "inventory" || stage === "cooking" || stage === "judge-ai" || stage === "final-dish" || stage === "next-order" || stage === "how-it-works" || stage === "footer"}
            items={pantryItems}
          />
        </div>

        {/* Section 5: Cooking */}
        <div ref={registerSection("cooking")}>
          <SectionCooking
            isActive={stage === "cooking" || stage === "judge-ai" || stage === "final-dish" || stage === "next-order" || stage === "how-it-works" || stage === "footer"}
            steps={cookingSteps}
          />
        </div>

        {/* Section 6: AI Culinary Assessment */}
        <div ref={registerSection("judge-ai")}>
          <SectionJudgeAI
            isActive={stage === "judge-ai" || stage === "final-dish" || stage === "next-order" || stage === "how-it-works" || stage === "footer"}
            dish={currentDish}
            reviewText={geminiReviewText}
          />
        </div>

        {/* Section 7: Final Dish */}
        <div ref={registerSection("final-dish")}>
          <SectionFinalDish
            isActive={stage === "final-dish" || stage === "next-order" || stage === "how-it-works" || stage === "footer"}
            coinsEarned={coinsEarned}
            dishName={currentDish}
          />
        </div>

        {/* Section 8: Ready for Next Order */}
        <div ref={registerSection("next-order")}>
          <SectionNextOrder onSubmit={handleStartCooking} suggestions={suggestions} />
        </div>

        {/* Section 9: How It Works */}
        <div ref={registerSection("how-it-works")}>
          <SectionHowItWorks />
        </div>

        {/* Section 10: Footer */}
        <div ref={registerSection("footer")}>
          <SectionFooter />
        </div>
      </div>
    </div>
  );
}
