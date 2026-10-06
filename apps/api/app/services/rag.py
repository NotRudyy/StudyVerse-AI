from app.demo_data import SOURCE_CHUNKS
from app.services.documents import split_chunks


def retrieve(query: str, limit: int = 3, extra_materials: list[dict] | None = None) -> list[dict]:
    tokens = {token.strip(".,?!:;()[]{}'’\"").lower() for token in query.split() if len(token) > 2}
    ranked = []
    source_items = list(SOURCE_CHUNKS)
    for material in extra_materials or []:
        for index, chunk in enumerate(split_chunks(material.get("extracted_text", ""))):
            source_items.append({"title": material["filename"], "text": chunk, "page": index + 1})
    for item in source_items:
        haystack = (item["title"] + " " + item["text"]).lower()
        score = sum(1 for token in tokens if token in haystack)
        if score:
            ranked.append((score, item))
    if not ranked:
        ranked = [(1, item) for item in SOURCE_CHUNKS]
    ranked.sort(key=lambda row: row[0], reverse=True)
    return [
        {"text": item["text"], "citation": item["title"] + ", p. " + str(item["page"]), "score": score}
        for score, item in ranked[:limit]
    ]
