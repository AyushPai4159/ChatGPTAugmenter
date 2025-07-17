#!/bin/bash

# ChatGPT Augmenter - Docker Build and Run Script

set -e

echo "🐳 ChatGPT Augmenter Docker Setup"
echo "================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  prod, production    Build and run production version"
    echo "  dev, development    Build and run development version with hot reload"
    echo "  build               Build production image only"
    echo "  stop                Stop all running containers"
    echo "  clean               Stop containers and remove images"
    echo "  logs                Show container logs"
    echo "  help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 prod             # Run production version"
    echo "  $0 dev              # Run development version"
    echo "  $0 stop             # Stop all containers"
}

# Get the command
CMD=${1:-prod}

case $CMD in
    "prod"|"production")
        echo "🚀 Building and starting production version..."
        docker-compose up --build
        ;;
    "dev"|"development")
        echo "🔧 Building and starting development version with hot reload..."
        docker-compose --profile dev up --build chatgpt-augmenter-dev
        ;;
    "build")
        echo "🔨 Building production image..."
        docker build -t chatgpt-augmenter .
        echo "✅ Build complete!"
        ;;
    "stop")
        echo "🛑 Stopping all containers..."
        docker-compose down
        docker-compose --profile dev down
        echo "✅ All containers stopped!"
        ;;
    "clean")
        echo "🧹 Cleaning up containers and images..."
        docker-compose down -v
        docker-compose --profile dev down -v
        docker rmi chatgpt-augmenter chatgpt-augmenter-dev 2>/dev/null || true
        echo "✅ Cleanup complete!"
        ;;
    "logs")
        echo "📋 Showing container logs..."
        docker-compose logs -f
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        echo "❌ Unknown command: $CMD"
        echo ""
        show_usage
        exit 1
        ;;
esac
