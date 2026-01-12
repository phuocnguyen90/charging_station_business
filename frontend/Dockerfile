FROM node:20-alpine

WORKDIR /app

# Install dependencies based on package.json
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source code
COPY . .

# Build the application
# Note: NEXT_PUBLIC_API_URL should be passed as build arg if different from default
RUN npm run build

# Expose port
EXPOSE 3001

# Start the application
CMD ["npm", "start", "--", "-p", "3001"]
