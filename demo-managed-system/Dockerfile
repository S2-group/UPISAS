FROM node:21
# Create app directory
WORKDIR /usr/src/app
# Install app dependencies
COPY package*.json ./
RUN npm install
# Bundle app source
COPY . .
# Run forever (the HTTP server should be started by exec_run)
CMD [ "sleep", "infinity" ]
