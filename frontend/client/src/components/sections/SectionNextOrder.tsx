import { motion } from "framer-motion";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

/**
 * Section — READY FOR NEXT ORDER
 * User types in their next dish request
 * Clean input field with submit button validated via React Hook Form & Zod
 */

interface SectionNextOrderProps {
  onSubmit: (dish: string) => void;
  suggestions: string[];
}

const orderSchema = z.object({
  dishName: z.string().min(1, "Please enter a dish name").max(150, "Dish name is too long"),
});

type OrderFormData = z.infer<typeof orderSchema>;

export default function SectionNextOrder({ onSubmit, suggestions }: SectionNextOrderProps) {
  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm<OrderFormData>({
    resolver: zodResolver(orderSchema),
    defaultValues: { dishName: "" },
  });

  const onFormSubmit = (data: OrderFormData) => {
    onSubmit(data.dishName.trim());
    reset();
  };

  const handleSuggestion = (name: string) => {
    setValue("dishName", name, { shouldValidate: true });
  };

  return (
    <section className="relative w-full min-h-screen flex items-center justify-center py-20 px-6">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0a] via-lime-950/5 to-[#0a0a0a]" />

      {/* Content */}
      <div className="relative z-10 text-center max-w-xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <p className="text-lime-400 text-xs font-medium tracking-[0.4em] uppercase mb-4 font-body" style={{ fontFamily: "'Lato', sans-serif" }}>
            Hungry Again?
          </p>

          <h2
            className="text-white/90 mb-4"
            style={{ fontFamily: "'Grand Hotel', cursive", fontSize: "clamp(2rem, 6vw, 4rem)", lineHeight: 1.1 }}
          >
            Ready for Your <span className="text-gradient-lime">Next Order?</span>
          </h2>

          <p className="text-gray-400 text-base mb-8 font-body" style={{ fontFamily: "'Lato', sans-serif" }}>
            Type any dish you'd like our AI chefs to prepare.
          </p>

          {/* Input Form */}
          <motion.form
            onSubmit={handleSubmit(onFormSubmit)}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
            className="mb-6"
          >
            <div className="glass-strong flex flex-col gap-1 px-5 py-4 max-w-md mx-auto">
              <div className="flex items-center gap-3">
                <svg className="w-5 h-5 text-gray-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                </svg>
                <input
                  type="text"
                  {...register("dishName")}
                  placeholder="Type your dish name..."
                  className="flex-1 bg-transparent text-white text-base font-body placeholder:text-gray-600 outline-none"
                  style={{ fontFamily: "'Lato', sans-serif" }}
                />
                <button
                  type="submit"
                  className="px-5 py-2 rounded-full bg-lime-400 text-black text-sm font-bold font-body hover:bg-lime-300 transition-colors flex-shrink-0"
                  style={{ fontFamily: "'Lato', sans-serif" }}
                >
                  Cook
                </button>
              </div>
              {errors.dishName && (
                <p className="text-red-400 text-xs text-left pl-8 mt-1 font-body">{errors.dishName.message}</p>
              )}
            </div>
          </motion.form>

          {/* Suggestions */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.5 }}
            className="flex flex-wrap items-center justify-center gap-2"
          >
            <span className="text-[10px] text-gray-600 uppercase tracking-wider font-body">Suggestions:</span>
            {suggestions.map((name) => (
              <button
                key={name}
                type="button"
                onClick={() => handleSuggestion(name)}
                className="text-xs text-gray-400 hover:text-lime-400 px-3 py-1 rounded-full border border-white/5 hover:border-lime-400/30 transition-all font-body"
                style={{ fontFamily: "'Lato', sans-serif" }}
              >
                {name}
              </button>
            ))}
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}

