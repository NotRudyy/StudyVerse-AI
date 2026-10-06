"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import Image from "next/image";
import { ArrowRight, BookOpen, Check, Eye, EyeOff, LockKeyhole, Mail, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

const API_URL = process.env.NEXT_PUBLIC_API_URL;
type LocalDemoAccount = { name: string; salt: string; passwordHash: string };

async function hashDemoPassword(password: string, saltHex: string) {
  if (!window.crypto?.subtle) throw new Error("Secure local sign-in isn't available in this browser. Use Continue with demo learner.");
  const salt = new Uint8Array(saltHex.match(/.{2}/g)?.map((byte) => Number.parseInt(byte, 16)) ?? []);
  const key = await window.crypto.subtle.importKey("raw", new TextEncoder().encode(password), "PBKDF2", false, ["deriveBits"]);
  const bits = await window.crypto.subtle.deriveBits({ name: "PBKDF2", salt, iterations: 120_000, hash: "SHA-256" }, key, 256);
  return Array.from(new Uint8Array(bits), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setLoading(true);
    try {
      const normalizedEmail = email.trim().toLowerCase();
      if (API_URL) {
        const response = await fetch(API_URL + "/auth/" + (mode === "signup" ? "register" : "login"), {
          method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: normalizedEmail, password }),
        });
        const body = await response.json();
        if (!response.ok) throw new Error(body.detail || "Could not sign in right now.");
        localStorage.setItem("studyverse.token", body.access_token);
        localStorage.setItem("studyverse.email", normalizedEmail);
        localStorage.setItem("studyverse.name", name.trim() || body.user.name || normalizedEmail.split("@")[0]);
      } else {
        const accounts = JSON.parse(localStorage.getItem("studyverse.demoAccounts") || "{}") as Record<string, LocalDemoAccount>;
        if (mode === "signup") {
          if (accounts[normalizedEmail]) throw new Error("An account with this email already exists on this browser. Sign in instead.");
          const salt = Array.from(window.crypto.getRandomValues(new Uint8Array(16)), (byte) => byte.toString(16).padStart(2, "0")).join("");
          accounts[normalizedEmail] = { name: name.trim(), salt, passwordHash: await hashDemoPassword(password, salt) };
          localStorage.setItem("studyverse.demoAccounts", JSON.stringify(accounts));
          localStorage.setItem("studyverse.token", `demo-local:${normalizedEmail}`);
          localStorage.setItem("studyverse.email", normalizedEmail);
          localStorage.setItem("studyverse.name", name.trim());
        } else {
          const account = accounts[normalizedEmail];
          if (!account) throw new Error("No local account exists for this email. Create one here or continue as the demo learner.");
          const candidate = await hashDemoPassword(password, account.salt);
          if (candidate !== account.passwordHash) throw new Error("Email or password didn't match.");
          localStorage.setItem("studyverse.token", `demo-local:${normalizedEmail}`);
          localStorage.setItem("studyverse.email", normalizedEmail);
          localStorage.setItem("studyverse.name", account.name);
        }
      }
      if (name.trim() && mode === "signup") localStorage.setItem("studyverse.name", name.trim());
      router.push(mode === "signup" ? "/onboarding" : "/");
    } catch (err) {
      setError(err instanceof TypeError ? "Can't reach the StudyVerse API. Check that the API is running, or use Continue with demo learner." : err instanceof Error ? err.message : "Could not sign in right now.");
    }
    finally { setLoading(false); }
  }

  return <main className="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-10">
    <div className="pointer-events-none absolute left-1/2 top-[-220px] size-[600px] -translate-x-1/2 rounded-full bg-violet-500/[.08] blur-[100px]" />
    <div className="relative grid w-full max-w-[930px] overflow-hidden rounded-[26px] border border-white/[.075] bg-[#101015]/90 shadow-2xl shadow-black/40 md:grid-cols-[1fr_1fr]">
      <section className="relative hidden min-h-[620px] flex-col justify-between overflow-hidden border-r border-white/[.06] p-8 md:flex lg:p-10">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_35%_28%,rgba(139,92,246,.19),transparent_58%),radial-gradient(ellipse_at_90%_100%,rgba(236,141,199,.1),transparent_52%)]" />
        <div className="grid-dots absolute inset-0 opacity-[.08]" />
        <Image src="/brand/studyverse-ai-lockup.png" alt="StudyVerse AI — Learn, Ask, Grow" width={212} height={167} priority className="relative h-auto w-[175px] mix-blend-lighten" />
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .5 }} className="relative my-10">
          <div className="mb-5 inline-flex items-center gap-1.5 rounded-full border border-violet-300/15 bg-violet-300/[.06] px-2.5 py-1 text-[8px] tracking-[.14em] text-violet-200"><Sparkles size={11} /> LEARN · ASK · GROW</div>
          <h1 className="max-w-sm text-[34px] font-semibold leading-[1.15] tracking-[-.05em]">Your next <span className="gradient-text">aha moment</span> is closer than you think.</h1>
          <p className="mt-4 max-w-sm text-xs leading-6 text-zinc-500">Learn with your own notes, practice what matters, and actually remember the hard stuff.</p>
          <div className="mt-8 space-y-3">{["Answers grounded in your notes", "A plan that adapts as you learn", "Progress that feels like progress"].map((item) => <div key={item} className="flex items-center gap-2.5 text-[10px] text-zinc-400"><span className="flex size-5 items-center justify-center rounded-full border border-emerald-300/15 bg-emerald-300/[.06] text-emerald-200"><Check size={11} /></span>{item}</div>)}</div>
        </motion.div>
        <div className="relative flex items-center gap-2 text-[9px] text-zinc-600"><BookOpen size={12} /> Made for the way your brain actually learns.</div>
      </section>
      <section className="flex min-h-[620px] flex-col justify-center p-6 sm:p-9 lg:p-11">
        <div className="mb-8 flex items-center gap-2.5 md:hidden"><Image src="/brand/studyverse-ai-mark.png" alt="" width={44} height={35} priority className="h-[32px] w-10 object-contain mix-blend-lighten" /><span className="text-xs font-extrabold tracking-[.08em]">STUDYVERSE <span className="text-sky-300">AI</span><span className="mt-1 block text-[8px] font-medium tracking-[.12em] text-zinc-500">LEARN · ASK · GROW</span></span></div>
        <div className="mb-6"><div className="text-[9px] font-bold uppercase tracking-[.17em] text-violet-300">{mode === "signin" ? "GOOD TO HAVE YOU BACK" : "YOUR NEXT CHAPTER STARTS HERE"}</div><h2 className="mt-2 text-[24px] font-semibold tracking-[-.04em]">{mode === "signin" ? "Welcome back." : "Make it yours."}</h2><p className="mt-1.5 text-[10px] text-zinc-500">{mode === "signin" ? "Pick up right where your curiosity left off." : "Create an account and build your learning home."}</p>{!API_URL && <p className="mt-3 rounded-lg border border-sky-300/10 bg-sky-300/[.035] px-3 py-2 text-[9px] leading-4 text-sky-100/70">Local demo mode: accounts stay in this browser. Use a test password; no backend is connected.</p>}</div>
        <div className="mb-5 flex rounded-xl border border-white/[.06] bg-black/10 p-1">{[{key:"signin",label:"Sign in"},{key:"signup",label:"Create account"}].map((item)=><button key={item.key} onClick={() => { setMode(item.key as "signin"|"signup"); setError(""); }} className={`flex-1 rounded-lg py-2 text-[10px] transition ${mode === item.key ? "bg-white/[.08] text-zinc-100" : "text-zinc-500 hover:text-zinc-300"}`}>{item.label}</button>)}</div>
        <form onSubmit={submit} className="space-y-3.5">{mode === "signup" && <label className="block"><span className="mb-1.5 block text-[9px] font-medium text-zinc-400">What should we call you?</span><input value={name} onChange={(event) => setName(event.target.value)} required autoComplete="name" placeholder="Your name" className="focus-ring h-11 w-full rounded-xl border border-white/[.07] bg-white/[.02] px-3 text-[11px] outline-none placeholder:text-zinc-700 focus:border-violet-300/30" /></label>}
          <label className="block"><span className="mb-1.5 block text-[9px] font-medium text-zinc-400">Email</span><span className="relative block"><Mail size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-600"/><input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="email" placeholder="you@school.edu" className="focus-ring h-11 w-full rounded-xl border border-white/[.07] bg-white/[.02] pl-9 pr-3 text-[11px] outline-none placeholder:text-zinc-700 focus:border-violet-300/30" /></span></label>
          <label className="block"><span className="mb-1.5 block text-[9px] font-medium text-zinc-400">Password</span><span className="relative block"><LockKeyhole size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-600"/><input type={showPassword ? "text" : "password"} value={password} onChange={(event) => setPassword(event.target.value)} required minLength={8} autoComplete={mode === "signup" ? "new-password" : "current-password"} placeholder="At least 8 characters" className="focus-ring h-11 w-full rounded-xl border border-white/[.07] bg-white/[.02] pl-9 pr-10 text-[11px] outline-none placeholder:text-zinc-700 focus:border-violet-300/30"/><button type="button" onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? "Hide password" : "Show password"} className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-600 hover:text-zinc-300">{showPassword ? <EyeOff size={14}/> : <Eye size={14}/>}</button></span></label>
          {error && <div role="alert" className="rounded-lg border border-rose-300/15 bg-rose-300/[.04] px-3 py-2 text-[9px] text-rose-200">{error}</div>}
          <Button className="mt-1 w-full" size="lg" type="submit" disabled={loading}>{loading ? "One sec…" : mode === "signin" ? "Sign in" : API_URL ? "Create your account" : "Create local demo account"}<ArrowRight size={14}/></Button>
        </form>
        <div className="my-5 flex items-center gap-3 text-[8px] text-zinc-700"><span className="h-px flex-1 bg-white/[.06]"/>OR<span className="h-px flex-1 bg-white/[.06]"/></div>
        <button onClick={() => router.push("/")} className="focus-ring h-10 rounded-xl border border-white/[.07] text-[10px] text-zinc-400 transition hover:bg-white/[.035] hover:text-white">Continue with demo learner <span className="ml-1 text-violet-300">↗</span></button>
        <p className="mt-5 text-center text-[8px] leading-4 text-zinc-700">By continuing, you agree to use this college demo responsibly. <br/>No payment or external account needed to explore demo mode.</p>
      </section>
    </div>
  </main>;
}
