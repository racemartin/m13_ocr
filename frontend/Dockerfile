# ============================================================================
# Etape 1 : build de l'application Angular
# ============================================================================
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .
RUN npm run build

# ============================================================================
# Etape 2 : image finale servie par Nginx
# ============================================================================
FROM nginx:alpine

# Copie du build Angular dans le repertoire servi par Nginx
COPY --from=build /app/dist/ffe-frontend/browser /usr/share/nginx/html

# Copie de la configuration Nginx (reverse proxy vers le backend)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
