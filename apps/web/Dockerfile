FROM node:22-alpine AS base
RUN corepack enable
WORKDIR /repo
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/web/package.json apps/web/package.json
COPY apps/web ./apps/web
RUN pnpm install --frozen-lockfile --filter web...
ARG NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_OUTPUT_STANDALONE=true
RUN pnpm --filter web build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=base /repo/apps/web/.next/standalone ./
COPY --from=base /repo/apps/web/.next/static ./apps/web/.next/static
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
