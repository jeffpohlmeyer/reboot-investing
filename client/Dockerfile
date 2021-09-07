FROM node:lts-alpine

RUN npm i -g http-server

WORKDIR /app

COPY client/package*.json ./

RUN npm i

COPY client .

RUN npm run build

EXPOSE 8080
CMD ["http-server", "dist"]
