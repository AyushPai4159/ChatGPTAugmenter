# 🐳 ChatGPT Augmenter - Docker Quick Start

## Prerequisites
- Docker and Docker Compose installed
- No other dependencies needed!

## 🚀 Quick Commands

### Production (Recommended)
```bash
# Build and run everything
./docker-run.sh prod

# Or using docker-compose directly
docker-compose up --build
```

**Note**: On first run, Docker will automatically run your setup scripts (`delete.sh` and `load.sh`) to initialize the model and data. This may take a few minutes. Subsequent runs will skip setup since the model data is persisted in a Docker volume.

### Development with Hot Reload
```bash
# Build and run development version
./docker-run.sh dev

# Or using docker-compose directly
docker-compose --profile dev up --build chatgpt-augmenter-dev
```

### Other Useful Commands
```bash
# Just build the image
./docker-run.sh build

# Stop all containers
./docker-run.sh stop

# Clean up everything
./docker-run.sh clean

# View logs
./docker-run.sh logs

# Get help
./docker-run.sh help
```

## 🌐 Access Points

### Production Mode
- **React Dev Server**: http://localhost:3000 (with hot reload)
- **Flask API**: http://localhost:5001
- **Health Check**: http://localhost:5001/health

### Development Mode  
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:5002
- **Health Check**: http://localhost:5002/health

## 📁 What Docker Does

1. **Installs Node.js** and runs `npm install` for React dependencies
2. **Installs Python** and runs `pip install` for Flask dependencies  
3. **Builds React app** for production
4. **Configures Flask** to serve both API and React frontend
5. **Sets up CORS** for proper communication
6. **Runs your setup scripts** automatically:
   - If `my_model_dir` doesn't exist, runs setup (calls `delete.sh` and `load.sh`)
   - If `my_model_dir` exists, skips setup and starts normally
7. **Persists model data** using Docker volumes (setup only runs once)
8. **Exposes ports** 3000 and 5000

## 🔧 Development Workflow

1. **Start development container**:
   ```bash
   ./docker-run.sh dev
   ```

2. **Edit code** in `react-app/` or `backend/` directories

3. **See changes automatically** - hot reload is enabled!

4. **Test production build**:
   ```bash
   ./docker-run.sh stop
   ./docker-run.sh prod
   ```

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
./docker-run.sh logs

# Try cleaning up
./docker-run.sh clean
./docker-run.sh prod
```

### Port already in use
Edit `docker-compose.yml` and change ports:
```yaml
ports:
  - "3002:3000"  # Use port 3002 instead of 3000
  - "5003:5001"  # Use port 5003 instead of 5001
```

### Want to see what's inside the container
```bash
# Get into running container
docker exec -it chatgpt-augmenter-app bash

# Or for development
docker exec -it chatgpt-augmenter-dev sh
```

### Force re-run setup process
```bash
# Remove the model volume to trigger setup again
docker-compose down
docker volume rm chatgptaugmenter_chatgpt_model_data
docker-compose up --build
```

## 🎯 Benefits of This Docker Setup

✅ **No local Node.js/Python setup needed**  
✅ **Consistent environment across machines**  
✅ **Easy deployment**  
✅ **Hot reload for development**  
✅ **Production-ready build process**  
✅ **Automatic dependency management**

That's it! Your entire React + Flask application is now Dockerized! 🎉
