import { apiClient } from "@/lib/axios";
import type { WalletData } from "@/types/api";

export async function getWallet(): Promise<WalletData> {
  const response = await apiClient.get("/wallet");
  const raw = response.data as { balance?: number | string };
  const balanceNum = raw.balance != null ? Number(raw.balance) : 1000;
  return {
    balance: balanceNum,
    currency: "INR",
  };
}

export async function getWalletTransactions() {
  const response = await apiClient.get("/wallet/transactions");
  const rawData = response.data;
  if (Array.isArray(rawData)) {
    return rawData.map((item: any) => ({
      id: item.id,
      title: item.description || item.transaction_type || "Transaction",
      label: item.description || item.transaction_type || "Transaction",
      amount: item.amount != null ? Number(item.amount) : 0,
      type: item.transaction_type,
      createdAt: item.created_at,
    }));
  }
  const data = rawData as WalletData;
  return data.transactions ?? [];
}

