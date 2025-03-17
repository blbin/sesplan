# Použití oficiálního Node.js image jako základ
FROM node:18-alpine AS build

# Nastavení pracovního adresáře
WORKDIR /app

# Kopírování package.json a package-lock.json a instalace závislostí
COPY package.json package-lock.json ./
RUN npm ci

# Kopírování zdrojového kódu a sestavení aplikace
COPY . .
RUN npm run build

# Použití Nginx pro nasazení
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
