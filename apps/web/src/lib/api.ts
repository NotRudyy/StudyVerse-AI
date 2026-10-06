const apiUrl = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");

function token() {
  return typeof window === "undefined" ? "" : window.localStorage.getItem("studyverse.token") ?? "";
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T | null> {
  if (!apiUrl || !token()) return null;
  const headers = new Headers(init.headers);
  headers.set("Authorization", "Bearer " + token());
  if (init.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const response = await fetch(apiUrl + path, { ...init, headers });
  const body = await response.json();
  if (!response.ok) throw new Error(body.detail || "The StudyVerse API request failed.");
  return body as T;
}

export async function uploadMaterial(file: File) {
  const form = new FormData();
  form.set("file", file);
  return request<{ material: { id: string; status: string }; studypack: { flashcards_generated: number } }>("/materials", { method: "POST", body: form });
}

export async function askNova(message: string, mode: string) {
  return request<{ answer: string; citations: { source: string; excerpt: string }[] }>("/tutor/chat", { method: "POST", body: JSON.stringify({ message, mode: mode.toLowerCase() }) });
}

export async function submitPractice(questionId: string, answerIndex: number, confidence: number) {
  return request<{ correct: boolean; confidence_gap: boolean; explanation: string }>("/practice/submit", { method: "POST", body: JSON.stringify({ question_id: questionId, answer_index: answerIndex, confidence }) });
}

export async function completeFocus(topic: string, durationMinutes: number) {
  return request<{ session: { xp_earned: number }; streak: number }>("/focus/complete", { method: "POST", body: JSON.stringify({ topic, duration_minutes: durationMinutes }) });
}

export async function createBossBattle() {
  return request<{ id: string; name: string; question_count: number; duration_minutes: number }>("/assessments/boss-battle", { method: "POST", body: "{}" });
}

export async function saveOnboarding(profile: { name: string; program: string; subjects: string[]; examDate: string; dailyMinutes: number; style: string }) {
  return request<{ saved: boolean; plan: { next_step: string } }>("/onboarding", { method: "POST", body: JSON.stringify({ display_name: profile.name || "Learner", program: profile.program, subjects: profile.subjects, exam_date: profile.examDate || null, daily_minutes: profile.dailyMinutes, learning_style: profile.style }) });
}
