# API reference

Base URL: `http://localhost:8000/api/v1` · Interactive OpenAPI: `http://localhost:8000/docs`.

Protected routes use `Authorization: Bearer <access_token>`. Tokens expire after 12 hours. Auth payload passwords must be at least 8 characters.

| Method | Path | Auth | Purpose |
|---|---|---:|---|
| GET | `/health` | no | Status and active demo/AI configuration |
| POST | `/auth/register` | no | Create student and return JWT |
| POST | `/auth/login` | no | Verify credentials and return JWT |
| POST | `/onboarding` | yes | Save profile, subjects, exam date, schedule and learning style |
| GET | `/dashboard` | no | Seeded dashboard snapshot for the demo |
| GET | `/study-packs` | yes | Seeded packs plus the current student’s uploads |
| POST | `/materials` | yes | Multipart upload, extraction, chunk creation and StudyPack stub |
| POST | `/tutor/chat` | yes | Grounded tutor answer, mode and cited note excerpts |
| GET | `/practice/next?topic=...` | yes | Next adaptive question (demo question bank currently seeded) |
| POST | `/practice/submit` | yes | Grade response and record confidence gap / mastery signal |
| GET | `/mistakes` | yes | List this student's open confidence-gap mistakes |
| POST | `/mistakes/{mistake_id}/review` | yes | Resolve a mistake and award review XP |
| GET | `/flashcards/due` | yes | List due cards |
| POST | `/flashcards/{card_id}/review` | yes | Update card interval with an SM-2-style schedule |
| POST | `/assessments/boss-battle` | yes | Create a timed, hint-free assessment session |
| GET | `/mastery` | yes | Concept mastery and prerequisite edges |
| GET | `/planner/today` | no | Today's recommended study blocks |
| POST | `/focus/complete` | yes | Record a completed focus session and award XP |
| GET | `/wrapped` | no | Weekly activity summary |
| GET | `/rooms` | no | Public study-room directory |
| POST | `/rooms` | yes | Create a room |
| POST | `/rooms/{room_id}/join` | yes | Join a room with capacity validation |

## Example: grounded tutor

```bash
curl -X POST http://localhost:8000/api/v1/tutor/chat \
  -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"Can Dijkstra handle negative edges?","mode":"socratic","subject":"DSA"}'
```

The response includes `answer`, `mode`, `grounded`, `demo_mode`, and `citations[]` with source, excerpt, and retrieval score.

## Upload constraints

`POST /materials` accepts a multipart `file` and optional `subject`. Allowed formats: PDF, PPTX, DOCX, PNG/JPG/WEBP, TXT, and Markdown. The current limit is 20 MiB. Image OCR is opportunistic and requires Tesseract + Pillow in the worker image; without them, image files are retained for later processing and return zero extracted characters.
