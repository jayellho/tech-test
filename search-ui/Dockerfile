FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Set build-time environment variables from build args
ARG NEXT_PUBLIC_ES_HOST
ARG NEXT_PUBLIC_ES_INDEX
ENV NEXT_PUBLIC_ES_HOST=$NEXT_PUBLIC_ES_HOST
ENV NEXT_PUBLIC_ES_INDEX=$NEXT_PUBLIC_ES_INDEX

# Build the application (without turbopack)
RUN npx next build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
