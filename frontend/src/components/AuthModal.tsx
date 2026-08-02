"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion, AnimatePresence } from "framer-motion";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { login, register, type LoginPayload, type RegisterPayload } from "@/services/auth";
import { useAuthStore } from "@/store";
import { Dialog, DialogContent, DialogTitle, DialogDescription } from "@/components/ui/dialog";

const loginSchema = z.object({
  identifier: z.string().min(3, "Username or Email must be at least 3 characters"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

const registerSchema = z.object({
  username: z.string().min(3, "Username must be at least 3 characters").max(50, "Username too long"),
  email: z.string().email("Invalid email address"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

type LoginFormData = z.infer<typeof loginSchema>;
type RegisterFormData = z.infer<typeof registerSchema>;

interface AuthModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  defaultTab?: "login" | "register";
}

export default function AuthModal({ open, onOpenChange, defaultTab = "login" }: AuthModalProps) {
  const [tab, setTab] = useState<"login" | "register">(defaultTab);
  const [apiError, setApiError] = useState<string | null>(null);

  const setSession = useAuthStore((state) => state.setSession);
  const queryClient = useQueryClient();

  const loginForm = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: { identifier: "", password: "" },
  });

  const registerForm = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: { username: "", email: "", password: "" },
  });

  const loginMutation = useMutation({
    mutationFn: (data: LoginFormData) => login({ identifier: data.identifier, password: data.password }),
    onSuccess: (session) => {
      setSession(session);
      setApiError(null);
      onOpenChange(false);
      loginForm.reset();
      queryClient.invalidateQueries({ queryKey: ["wallet"] });
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
      queryClient.invalidateQueries({ queryKey: ["orders"] });
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.detail || err?.response?.data?.message || err?.message || "Login failed";
      setApiError(typeof msg === "string" ? msg : "Invalid credentials");
    },
  });

  const registerMutation = useMutation({
    mutationFn: (data: RegisterFormData) => register({ username: data.username, email: data.email, password: data.password }),
    onSuccess: (session) => {
      setSession(session);
      setApiError(null);
      onOpenChange(false);
      registerForm.reset();
      queryClient.invalidateQueries({ queryKey: ["wallet"] });
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
      queryClient.invalidateQueries({ queryKey: ["orders"] });
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.detail || err?.response?.data?.message || err?.message || "Registration failed";
      setApiError(typeof msg === "string" ? msg : "Registration failed. Try a different username or email.");
    },
  });

  const onLoginSubmit = (data: LoginFormData) => {
    setApiError(null);
    loginMutation.mutate(data);
  };

  const onRegisterSubmit = (data: RegisterFormData) => {
    setApiError(null);
    registerMutation.mutate(data);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-[#121212] border border-white/10 text-white rounded-2xl p-6 max-w-md w-full shadow-2xl backdrop-blur-xl">
        <DialogTitle className="text-center font-bold text-2xl mb-1 text-gradient-lime font-body">
          {tab === "login" ? "Welcome Back" : "Create Account"}
        </DialogTitle>
        <DialogDescription className="text-center text-gray-400 text-xs mb-6 font-body">
          {tab === "login" ? "Log in to cook meals, manage inventory, and earn rewards." : "Register to receive 1000 starting coins and your AI kitchen."}
        </DialogDescription>

        {/* Tab Switcher */}
        <div className="flex bg-black/40 rounded-xl p-1 mb-6 border border-white/5 font-body">
          <button
            type="button"
            onClick={() => { setTab("login"); setApiError(null); }}
            className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
              tab === "login" ? "bg-lime-400 text-black shadow-md" : "text-gray-400 hover:text-white"
            }`}
          >
            Login
          </button>
          <button
            type="button"
            onClick={() => { setTab("register"); setApiError(null); }}
            className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
              tab === "register" ? "bg-lime-400 text-black shadow-md" : "text-gray-400 hover:text-white"
            }`}
          >
            Register
          </button>
        </div>

        {apiError && (
          <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-xs p-3 rounded-lg mb-4 text-center font-medium font-body">
            {apiError}
          </div>
        )}

        <AnimatePresence mode="wait">
          {tab === "login" ? (
            <motion.form
              key="login"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              onSubmit={loginForm.handleSubmit(onLoginSubmit)}
              className="space-y-4 font-body"
            >
              <div>
                <label className="block text-xs text-gray-400 font-medium mb-1 uppercase tracking-wider">Username or Email</label>
                <input
                  type="text"
                  {...loginForm.register("identifier")}
                  placeholder="Enter username or email"
                  className="w-full bg-black/40 border border-white/10 focus:border-lime-400 rounded-xl px-4 py-2.5 text-sm text-white outline-none transition-colors"
                />
                {loginForm.formState.errors.identifier && (
                  <p className="text-red-400 text-[11px] mt-1">{loginForm.formState.errors.identifier.message}</p>
                )}
              </div>

              <div>
                <label className="block text-xs text-gray-400 font-medium mb-1 uppercase tracking-wider">Password</label>
                <input
                  type="password"
                  {...loginForm.register("password")}
                  placeholder="••••••••"
                  className="w-full bg-black/40 border border-white/10 focus:border-lime-400 rounded-xl px-4 py-2.5 text-sm text-white outline-none transition-colors"
                />
                {loginForm.formState.errors.password && (
                  <p className="text-red-400 text-[11px] mt-1">{loginForm.formState.errors.password.message}</p>
                )}
              </div>

              <button
                type="submit"
                disabled={loginMutation.isPending}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-lime-400 to-emerald-400 text-black font-bold text-sm tracking-wide hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                {loginMutation.isPending ? "Logging in..." : "Log In"}
              </button>
            </motion.form>
          ) : (
            <motion.form
              key="register"
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              onSubmit={registerForm.handleSubmit(onRegisterSubmit)}
              className="space-y-4 font-body"
            >
              <div>
                <label className="block text-xs text-gray-400 font-medium mb-1 uppercase tracking-wider">Username</label>
                <input
                  type="text"
                  {...registerForm.register("username")}
                  placeholder="Choose a username"
                  className="w-full bg-black/40 border border-white/10 focus:border-lime-400 rounded-xl px-4 py-2.5 text-sm text-white outline-none transition-colors"
                />
                {registerForm.formState.errors.username && (
                  <p className="text-red-400 text-[11px] mt-1">{registerForm.formState.errors.username.message}</p>
                )}
              </div>

              <div>
                <label className="block text-xs text-gray-400 font-medium mb-1 uppercase tracking-wider">Email Address</label>
                <input
                  type="email"
                  {...registerForm.register("email")}
                  placeholder="name@example.com"
                  className="w-full bg-black/40 border border-white/10 focus:border-lime-400 rounded-xl px-4 py-2.5 text-sm text-white outline-none transition-colors"
                />
                {registerForm.formState.errors.email && (
                  <p className="text-red-400 text-[11px] mt-1">{registerForm.formState.errors.email.message}</p>
                )}
              </div>

              <div>
                <label className="block text-xs text-gray-400 font-medium mb-1 uppercase tracking-wider">Password</label>
                <input
                  type="password"
                  {...registerForm.register("password")}
                  placeholder="At least 6 characters"
                  className="w-full bg-black/40 border border-white/10 focus:border-lime-400 rounded-xl px-4 py-2.5 text-sm text-white outline-none transition-colors"
                />
                {registerForm.formState.errors.password && (
                  <p className="text-red-400 text-[11px] mt-1">{registerForm.formState.errors.password.message}</p>
                )}
              </div>

              <button
                type="submit"
                disabled={registerMutation.isPending}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-lime-400 to-emerald-400 text-black font-bold text-sm tracking-wide hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                {registerMutation.isPending ? "Registering..." : "Create Account (+1000 Coins)"}
              </button>
            </motion.form>
          )}
        </AnimatePresence>
      </DialogContent>
    </Dialog>
  );
}
