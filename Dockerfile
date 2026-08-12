FROM node:22-alpine AS frontend
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY index.html tsconfig.json tsconfig.node.json vite.config.ts ./
COPY src ./src
RUN pnpm build
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend ./backend
COPY --from=frontend /app/dist ./dist
ENV INBOXOPS_ENV=production AUTOMATION_ENABLED=true PORT=8000
EXPOSE 8000
CMD ["sh","-c","uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
