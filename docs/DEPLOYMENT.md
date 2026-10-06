# Deployment: Vercel + Google Cloud Run

This is a deployment plan, not an automatic deployment. Create separate development and production projects, and do not use demo seed accounts with real student information.

## 1. Provision Google Cloud

1. Create a GCP project and enable Cloud Run, Artifact Registry, Cloud SQL Admin, Cloud Storage, Secret Manager, and Vertex AI or Gemini API access.
2. Create a private Cloud SQL PostgreSQL 16 instance. Enable pgvector (`CREATE EXTENSION vector`) and apply `apps/api/migrations` from a controlled migration job.
3. Create a private Redis instance (Memorystore or a managed Redis provider) reachable by the API and worker.
4. Create a private GCS bucket with uniform bucket-level access, public access prevention, lifecycle retention, and a dedicated service account with only required object permissions.
5. Store `DATABASE_URL`, `REDIS_URL`, `GEMINI_API_KEY` (if using API key access), `GCS_BUCKET`, and `JWT_SECRET` in Secret Manager. Prefer Workload Identity / attached service accounts over a downloaded service-account key.

## 2. Deploy API and worker to Cloud Run

1. Build the API image from `apps/api/Dockerfile`; configure Cloud Run ingress and VPC connector/private IP access for Cloud SQL and Redis.
2. Deploy the API with `DEMO_MODE=false`, `DATABASE_URL`, `REDIS_URL`, `GEMINI_MODEL`, `GCS_BUCKET`, `GOOGLE_CLOUD_PROJECT`, and a high-entropy `JWT_SECRET` mounted from Secret Manager. For Gemini API-key auth, set `GEMINI_API_KEY`; for Vertex AI, set `USE_VERTEX_AI=true` and grant the Cloud Run service account Vertex AI access.
3. Set `CORS_ORIGINS` to a JSON array containing the exact HTTPS Vercel domain and custom domain. Do not use `*` for authenticated browser traffic.
4. Set Cloud Run minimum/maximum instances, CPU/memory based on document extraction load, concurrency conservatively, request timeout above the supported file size behavior, and health check to `/api/v1/health`.
5. Deploy the same image as a worker service/job using `celery -A app.workers.celery_app.celery_app worker --loglevel=INFO`; set `--concurrency` and autoscaling based on queue depth. Keep it on private networking.
6. Run `alembic upgrade head` as a one-off migration job before routing traffic. Back up the DB and validate restore before a student pilot.

## 3. Deploy web to Vercel

1. Import the repository; configure the build to run from the pnpm workspace root with `apps/web` as the Next.js app. Keep `pnpm-lock.yaml` at the repository root for lockfile detection.
2. Configure `NEXT_PUBLIC_API_URL` to the HTTPS Cloud Run API URL plus `/api/v1`. This value is public by design; never place tokens or secrets in `NEXT_PUBLIC_*` variables.
3. Configure production CORS allowlist in the API for the exact Vercel domain. Add preview domains intentionally or use a separate preview API.
4. Add a custom domain, HTTPS, and Vercel preview deployment checks. Verify sign-in, onboarding, upload, citation rendering, quiz submission, and timeout behavior against the deployed API.

## 4. Production checklist

- Enforce email verification, password reset, login throttling, bot protection, request IDs, and token revocation/refresh policy.
- Complete client integration for the remaining local-only room, mistake-review, and flashcard flows.
- Document retention, export, and deletion behavior. Add malware scanning and MIME sniffing for uploads.
- Set CSP/security headers, strict CORS, rate limits, database backups, Redis TLS, GCS lifecycle rules, alerts, and cost budgets.
- Add real end-to-end testing, accessibility checks, privacy review, and incident response before public launch.
