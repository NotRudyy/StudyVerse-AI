import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva("focus-ring inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl text-sm font-semibold transition-all disabled:pointer-events-none disabled:opacity-50", {
  variants: {
    variant: {
      primary: "bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white shadow-[0_8px_26px_rgba(139,92,246,.22)] hover:brightness-110 active:scale-[.98]",
      secondary: "border border-white/10 bg-white/[.045] text-white hover:bg-white/[.09]",
      ghost: "text-zinc-400 hover:bg-white/[.06] hover:text-white",
      outline: "border border-violet-300/25 bg-violet-300/[.06] text-violet-100 hover:bg-violet-300/[.12]",
      danger: "bg-rose-500/10 text-rose-200 hover:bg-rose-500/20",
    },
    size: { default: "h-10 px-4", sm: "h-8 rounded-lg px-3 text-xs", lg: "h-12 px-5", icon: "size-10 p-0" },
  },
  defaultVariants: { variant: "primary", size: "default" },
});

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> { asChild?: boolean }
export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({ className, variant, size, asChild = false, ...props }, ref) => {
  const Comp = asChild ? Slot : "button";
  return <Comp ref={ref} className={cn(buttonVariants({ variant, size, className }))} {...props} />;
});
Button.displayName = "Button";
