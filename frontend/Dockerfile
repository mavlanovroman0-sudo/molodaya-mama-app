FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
EXPOSE 8081 19006
CMD ["npx", "expo", "start", "--web", "--port", "8081", "--host", "lan"]
