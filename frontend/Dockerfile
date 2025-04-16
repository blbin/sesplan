# Použití oficiálního Node.js image jako základ
FROM node:18-alpine AS build

# Nastavení pracovního adresáře
WORKDIR /app

# Kopírování package.json a instalace závislostí
COPY package.json package-lock.json ./
RUN npm ci

# Kopírování zdrojového kódu a sestavení aplikace
COPY . .
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

# Použití Nginx pro nasazení
FROM nginx:alpine

# Kopírování sestavených souborů
COPY --from=build /app/dist /usr/share/nginx/html

# Vytvoření konfiguračního souboru Nginx pro SPA
RUN echo 'server { \
    listen 80; \
    server_name _; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    # Konfigurace pro SPA - všechny cesty směřují na index.html \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    \
    # Cache konfigurace pro statické soubory \
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ { \
        expires 30d; \
        add_header Cache-Control "public, no-transform"; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
