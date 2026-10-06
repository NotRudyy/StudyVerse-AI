import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "StudyVerse AI — Make every study session count",
  description: "Your AI powered study universe. Learn smarter, remember longer, and show up ready.",
  icons: { icon: "/brand/studyverse-ai-mark.png", apple: "/brand/studyverse-ai-mark.png" },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
