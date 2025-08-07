# ChatGPT Augmenter - Docker Setup

This application combines a React.js frontend with a Flask backend, all containerized with Docker for easy deployment and development.

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed on your system
- No need to install Node.js, Python, or any dependencies locally!

### Production Deployment

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd ChatGPTAugmenter
   ```

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001

### Development with Hot Reload

For development with automatic code reloading:

```bash
docker-compose --profile dev up --build chatgpt-augmenter-dev
```

This will:
- Start the React development server with hot reload
- Start the Flask backend in development mode
- Mount your local code as volumes for real-time updates

Access the development version at:
- Frontend: http://localhost:3001
- Backend API: http://localhost:5002

## Manual Docker Commands

### Build the production image:
```bash
docker build -t chatgpt-augmenter .
```

### Run the production container:
```bash
docker run -p 3000:3000 -p 5001:5001 chatgpt-augmenter
```

### Build the development image:
```bash
docker build -f Dockerfile.dev -t chatgpt-augmenter-dev .
```

### Run the development container:
```bash
docker run -p 3001:3000 -p 5002:5000 -v $(pwd)/react-app:/app/react-app -v $(pwd)/backend:/app/backend chatgpt-augmenter-dev
```

## Application Structure

```
ChatGPTAugmenter/
├── Dockerfile              # Production Docker build
├── Dockerfile.dev          # Development Docker build
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore           # Docker ignore file
├── react-app/              # React.js frontend
│   ├── package.json
│   ├── src/
│   └── public/
├── backend/                 # Flask backend
│   ├── app.py
│   ├── requirements.txt
│   └── data/
└── README.md
```

## Features

- **React Frontend**: Modern React.js application with components for input monitoring and search results
- **Flask Backend**: Python API for document search and processing
- **Docker Integration**: Fully containerized with production and development configurations
- **Hot Reload**: Development setup supports real-time code changes
- **Volume Mounting**: Persistent data storage for document embeddings

## Environment Variables

You can customize the application by setting environment variables:

- `FLASK_ENV`: Set to 'development' or 'production'
- `PYTHONPATH`: Python module search path (automatically set in Docker)

## Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop development services
docker-compose --profile dev down
```

## Troubleshooting

### Port Conflicts
If ports 3000 or 5000 are already in use, modify the ports in `docker-compose.yml`:

```yaml
ports:
  - "3002:3000"  # Use port 3002 instead of 3000
  - "5002:5000"  # Use port 5002 instead of 5000
```

### Container Not Starting
Check the logs:
```bash
docker-compose logs chatgpt-augmenter
```

### Development Hot Reload Not Working
Ensure you're using the development profile:
```bash
docker-compose --profile dev up chatgpt-augmenter-dev
```

## Contributing

1. Use the development Docker setup for coding
2. Make your changes in the `react-app/` or `backend/` directories
3. Test using the development container
4. Build and test the production container before committing

This Docker setup eliminates the need to manage Node.js versions, Python environments, or dependency installations locally!
