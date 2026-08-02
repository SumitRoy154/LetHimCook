"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getOrders, getOrderById } from "@/services/order";
import { Dialog, DialogContent, DialogTitle, DialogDescription } from "@/components/ui/dialog";

interface OrderHistoryModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function OrderHistoryModal({ open, onOpenChange }: OrderHistoryModalProps) {
  const [selectedOrderId, setSelectedOrderId] = useState<number | null>(null);

  const ordersQuery = useQuery({
    queryKey: ["orders-history-list"],
    queryFn: getOrders,
    enabled: open,
  });

  const orderDetailQuery = useQuery({
    queryKey: ["order-detail", selectedOrderId],
    queryFn: () => (selectedOrderId ? getOrderById(selectedOrderId) : null),
    enabled: Boolean(selectedOrderId),
  });

  const orders = ordersQuery.data ?? [];
  const activeDetail = orderDetailQuery.data as any;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-[#121212] border border-white/10 text-white rounded-2xl p-6 max-w-2xl w-full max-h-[85vh] overflow-y-auto shadow-2xl backdrop-blur-xl">
        <DialogTitle className="font-bold text-2xl mb-1 text-gradient-lime font-body">
          Order History & Memory
        </DialogTitle>
        <DialogDescription className="text-gray-400 text-xs mb-6 font-body">
          Inspect past orders, shopping receipts, cooking telemetry, and Gemini AI reviews.
        </DialogDescription>

        {selectedOrderId && activeDetail ? (
          <div>
            <button
              type="button"
              onClick={() => setSelectedOrderId(null)}
              className="text-xs text-lime-400 hover:underline mb-4 font-body flex items-center gap-1"
            >
              ← Back to All Orders
            </button>

            <div className="glass p-5 rounded-xl border border-white/10 space-y-5 font-body">
              <div className="flex items-center justify-between border-b border-white/10 pb-3">
                <div>
                  <h3 className="text-lg font-bold text-white">{activeDetail.dish_name || activeDetail.dishName}</h3>
                  <p className="text-xs text-gray-400 font-mono">Order #{activeDetail.id} • Status: {activeDetail.status}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-400">Total Cost: ₹{activeDetail.total_cost ?? activeDetail.cost ?? 0}</p>
                  <p className="text-sm font-bold text-lime-400 font-mono">+{activeDetail.reward_received ?? activeDetail.wallet_reward ?? 0} Coins</p>
                </div>
              </div>

              {/* Shopping Summary */}
              <div>
                <h4 className="text-xs font-semibold uppercase text-amber-400 tracking-wider mb-2">Shopping Summary</h4>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {Array.isArray(activeDetail.shopping_summary) && activeDetail.shopping_summary.length > 0 ? (
                    activeDetail.shopping_summary.map((item: any, i: number) => (
                      <div key={i} className="bg-black/30 p-2 rounded border border-white/5 flex justify-between">
                        <span>{item.ingredient_name || item.name}</span>
                        <span className="font-mono text-gray-300">₹{item.price}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 text-xs italic col-span-2">No shopping items recorded.</p>
                  )}
                </div>
              </div>

              {/* Cooking Session */}
              <div>
                <h4 className="text-xs font-semibold uppercase text-orange-400 tracking-wider mb-2">Cooking Telemetry</h4>
                {activeDetail.cooking_session ? (
                  <div className="bg-black/30 p-3 rounded border border-white/5 text-xs text-gray-300 space-y-1">
                    <p className="font-semibold text-white">{activeDetail.cooking_session.recipe_name || activeDetail.dish_name}</p>
                    {Array.isArray(activeDetail.cooking_session.steps) && (
                      <ul className="list-disc pl-4 space-y-1 mt-1 text-gray-400">
                        {activeDetail.cooking_session.steps.map((step: string, sIdx: number) => (
                          <li key={sIdx}>{step}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ) : (
                  <p className="text-gray-500 text-xs italic">Cooking telemetry completed successfully.</p>
                )}
              </div>

              {/* Judge Review */}
              <div>
                <h4 className="text-xs font-semibold uppercase text-emerald-400 tracking-wider mb-2">Gemini AI Judge Review</h4>
                {activeDetail.judge_review ? (
                  <div className="bg-black/30 p-4 rounded-xl border border-white/10 text-xs italic text-gray-200">
                    "{activeDetail.judge_review.review || activeDetail.judge_review.suggestions}"
                  </div>
                ) : (
                  <p className="text-gray-500 text-xs italic">AI assessment score verified.</p>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-2 font-body">
            {ordersQuery.isLoading ? (
              <p className="text-center text-gray-500 py-8 text-xs">Loading order history...</p>
            ) : orders.length === 0 ? (
              <p className="text-center text-gray-500 py-8 text-xs">No orders found. Place your first order!</p>
            ) : (
              orders.map((ord: any) => (
                <div
                  key={ord.id}
                  onClick={() => setSelectedOrderId(ord.id)}
                  className="glass p-4 rounded-xl border border-white/10 hover:border-lime-400/40 cursor-pointer transition-all flex items-center justify-between"
                >
                  <div>
                    <h4 className="text-sm font-bold text-white">{ord.dishName || ord.dish_name}</h4>
                    <p className="text-[11px] text-gray-400 font-mono">Order #{ord.id} • {ord.status}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-lime-400 font-mono font-bold">+{ord.reward_received ?? 50} Coins</p>
                    <span className="text-[10px] text-gray-500">Click to view details →</span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
