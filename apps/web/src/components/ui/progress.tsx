"use client";
import * as ProgressPrimitive from "@radix-ui/react-progress";
import { cn } from "@/lib/utils";

export function Progress({ className, value, indicatorClassName }: { className?: string; value: number; indicatorClassName?: string }) {
  return <ProgressPrimitive.Root className={cn("relative h-2 w-full overflow-hidden rounded-full bg-white/[.08]", className)} value={value}>
    <ProgressPrimitive.Indicator className={cn("h-full w-full flex-1 rounded-full bg-gradient-to-r from-violet-500 to-fuchsia-400 transition-transform", indicatorClassName)} style={{ transform: `translateX(-${100 - Math.max(0, Math.min(100, value))}%)` }} />
  </ProgressPrimitive.Root>;
}
