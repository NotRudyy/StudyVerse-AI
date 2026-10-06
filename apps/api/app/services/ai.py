from app.config import settings


def ai_is_configured() -> bool:
    return bool(settings.use_vertex_ai or settings.gemini_api_key)


def _client():
    from google import genai

    if settings.use_vertex_ai:
        return genai.Client(vertexai=True, project=settings.google_cloud_project, location=settings.google_cloud_location)
    return genai.Client(api_key=settings.gemini_api_key)


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if settings.demo_mode or not ai_is_configured() or not texts:
        return []
    from google.genai import types

    client = _client()
    vectors: list[list[float]] = []
    for start in range(0, len(texts), 64):
        response = await client.aio.models.embed_content(
            model=settings.gemini_embedding_model,
            contents=texts[start : start + 64],
            config=types.EmbedContentConfig(output_dimensionality=768),
        )
        vectors.extend([embedding.values for embedding in response.embeddings or []])
    return vectors


async def generate_answer(prompt: str, context: list[dict], mode: str) -> str:
    if settings.demo_mode or not ai_is_configured():
        return _demo_answer(prompt, context, mode)

    client = _client()
    snippets = "\n\n".join("[" + item["citation"] + "] " + item["text"] for item in context)
    instructions = {
        "learn": "Explain clearly, then give a short example.",
        "hint": "Give only a small, progressive hint. Do not reveal the full solution.",
        "socratic": "Ask guiding questions and wait for the learner to reason.",
        "exam": "Use concise exam-style wording and point values.",
    }[mode]
    response = await client.aio.models.generate_content(
        model=settings.gemini_model,
        contents="You are Nova, a patient study tutor. " + instructions + " Answer from the supplied notes. Say when notes do not support a claim.\n\nNOTES:\n" + snippets + "\n\nQUESTION:\n" + prompt,
    )
    return response.text or "I couldn't form a clear answer from those notes. Try asking in another way."


def _demo_answer(prompt: str, context: list[dict], mode: str) -> str:
    terms = prompt.lower()
    if "negative" in terms or "dijkstra" in terms:
        return "Bellman–Ford is the safe pick when edges can be negative. Dijkstra’s greedy step assumes all weights are non-negative; Bellman–Ford relaxes every edge repeatedly and can also flag a negative cycle. What tells you a negative cycle exists?"
    if "base case" in terms or "recursion" in terms:
        return "For a recursive graph search, stop exploring a neighbor when it is already in the visited set. That guard is what keeps cycles from sending your function around forever. Want to trace a tiny triangle graph together?"
    if mode == "hint":
        return "Tiny hint: check whether the algorithm makes an assumption about the sign of each edge weight before you choose it."
    return "Let's build the idea from your notes: breadth-first search uses a queue and explores one level at a time. On an unweighted graph, that makes the first visit to a node its shortest path by edge count. Can you explain why a queue helps preserve that order?"
