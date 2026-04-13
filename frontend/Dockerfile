FROM node:20-alpine AS base

WORKDIR /app

# ── deps layer (cached unless package.json changes) ─────────────────────────
FROM base AS deps

COPY package.json .
RUN npm install --frozen-lockfile

# ── development image ────────────────────────────────────────────────────────
FROM deps AS development

COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ── build stage ──────────────────────────────────────────────────────────────
FROM deps AS builder

COPY . .
RUN npm run build

# ── production image (nginx) ─────────────────────────────────────────────────
FROM nginx:1.25-alpine AS production

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
