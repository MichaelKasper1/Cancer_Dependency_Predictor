# 1. Use an official Node.js runtime as a parent image
FROM node:16

# 2. Set the working directory
WORKDIR /app

# 3. Copy the package files and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# 4. Copy the rest of the application code
COPY . .

# 5. Build the frontend for production
RUN npm run build

# 6. Expose the port the frontend runs on
EXPOSE 3000

# 7. Serve the built frontend
CMD ["npm", "run", "serve"]