# Python Debug Dojo AI proxy — Express reference image.
FROM node:20-alpine

WORKDIR /app

# Install deps first for better layer caching.
COPY package.json package-lock.json* ./
RUN npm install --omit=dev

COPY server.js ./

# Drop root — the node:alpine image ships a non-root `node` user.
USER node

ENV PORT=8080
EXPOSE 8080

# ANTHROPIC_API_KEY (and optionally ALLOWED_ORIGIN / ANTHROPIC_MODEL) must be
# passed at runtime, e.g. `docker run -e ANTHROPIC_API_KEY=... -p 8080:8080 ...`.
CMD ["node", "server.js"]
