# StudyVerse AI — college viva brief

## 30-second project intro

StudyVerse AI is a personalized study platform that helps a learner move from uploaded class material to actual recall. It organizes notes into StudyPacks, offers a citation-grounded AI tutor, checks understanding through adaptive questions and confidence ratings, turns mistakes into a revision queue, and adjusts the next study plan. A demo mode lets evaluators explore the full interface without paid API keys.

## Problem and idea

Students often keep notes in one place, ask questions in another, and track revision somewhere else. A generic chatbot can answer quickly but may skip prerequisites or create answer dependency. StudyVerse keeps the learning loop visible and gives the student the next useful action.

## Demo walkthrough

1. **Dashboard:** explain the exam countdown, mission, mastery signal, streak, and Nova recommendation.
2. **StudyPacks:** upload a course file; explain extraction, chunking, citations, and generated study artifacts.
3. **Nova:** switch between Learn, Hint, Socratic, and Exam modes. Point out source citations under answers.
4. **Practice:** choose an answer and confidence level. Show how confident-but-wrong work becomes a misconception signal.
5. **Mistake Lab / Skill tree:** explain that the system tracks a cause and prerequisite, not just a score.
6. **Planner / Focus:** finish the loop with a small schedule and a timed sprint.
7. **Study Wrapped:** show weekly effort and mastery changes as an encouraging retrospective.

## Architecture explanation

Next.js + TypeScript renders the responsive interface. FastAPI validates requests and owns learning endpoints. PostgreSQL stores student and learning records; pgvector stores 768-dimensional Gemini embeddings for student-scoped note retrieval. Redis carries work to Celery. The file adapter writes to local ignored storage in development and GCS when configured. Gemini is optional: deterministic mock responses make the demo reproducible, and real calls are enabled by configuration.

## RAG in plain terms

RAG stands for retrieval-augmented generation. First, a document is extracted and split into small passages. When a student asks a question, the system finds the most relevant passages and gives them to the language model as context. The UI shows citations so the student can trace an explanation to their material. This repository chunks notes, stores embeddings in pgvector when live Gemini is configured, and ranks retrieved material for the same student. The demo uses transparent keyword retrieval so it stays free and repeatable.

## Questions you may get

**How do you reduce hallucinations?** Retrieve from the student's material, instruct the tutor to stay within that context, return citations, and show when evidence is missing. RAG lowers risk; it does not guarantee factual correctness.

**How is learning personalized?** Quiz correctness, confidence, recent mistakes, exam dates, time availability, and topic prerequisites feed mastery and planning signals.

**Why ask for confidence?** A correct answer with low confidence and an incorrect answer with high confidence imply different next steps. The second can flag a misconception for review.

**What is the main limitation?** Demo data is synthetic, and the present demo retrieval uses keyword ranking. A production rollout needs vector retrieval constrained by each student's file permissions, more complete auth flows, and a privacy/security review.

**How can the project grow?** Add model evaluation, source quality feedback, a stronger spaced-repetition scheduler, teacher-managed cohorts, accessible offline revision, and privacy-preserving study rooms.

## Ethics and safeguards

The tutor should coach rather than replace the student's work. Exam mode can hide hints; citations help source checking. Study data is sensitive and should be private by default, retained only as long as needed, and never used to make high-impact decisions about a student.
