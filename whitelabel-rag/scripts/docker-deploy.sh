#!/bin/bash

# WhiteLabelRAG Docker Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check environment file
check_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        cp .env.example .env
        print_warning "Please edit .env file and add your GEMINI_API_KEY"
        return 1
    fi
    
    if ! grep -q "GEMINI_API_KEY=" .env || grep -q "GEMINI_API_KEY=$" .env; then
        print_warning "GEMINI_API_KEY not set in .env file"
        return 1
    fi
    
    print_success "Environment configuration found"
    return 0
}

# Build images
build_images() {
    print_status "Building Docker images..."
    
    if [ "$1" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml build
    else
        docker-compose build
    fi
    
    print_success "Images built successfully"
}

# Deploy application
deploy() {
    local mode=$1
    
    print_status "Deploying WhiteLabelRAG in $mode mode..."
    
    if [ "$mode" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml up -d
    elif [ "$mode" = "nginx" ]; then
        docker-compose --profile nginx up -d
    else
        docker-compose up -d
    fi
    
    print_success "Deployment completed"
}

# Check deployment status
check_status() {
    print_status "Checking deployment status..."
    
    # Wait a moment for containers to start
    sleep 5
    
    if [ "$1" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml ps
    else
        docker-compose ps
    fi
    
    # Check health
    print_status "Checking application health..."
    sleep 10
    
    if curl -f http://localhost:5000/health &> /dev/null; then
        print_success "Application is healthy and responding"
        print_success "Access the application at: http://localhost:5000"
    else
        print_warning "Application health check failed. Check logs with:"
        echo "  docker-compose logs -f whitelabel-rag"
    fi
}

# Show usage
usage() {
    echo "WhiteLabelRAG Docker Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build [dev]     Build Docker images"
    echo "  deploy [dev|nginx]  Deploy the application"
    echo "  status [dev]    Check deployment status"
    echo "  logs [dev]      Show application logs"
    echo "  stop [dev]      Stop the application"
    echo "  restart [dev]   Restart the application"
    echo "  clean           Clean up containers and images"
    echo "  help            Show this help message"
    echo ""
    echo "Options:"
    echo "  dev             Use development configuration"
    echo "  nginx           Deploy with Nginx reverse proxy"
    echo ""
    echo "Examples:"
    echo "  $0 deploy              # Deploy in production mode"
    echo "  $0 deploy dev          # Deploy in development mode"
    echo "  $0 deploy nginx        # Deploy with Nginx proxy"
    echo "  $0 logs                # Show production logs"
    echo "  $0 logs dev            # Show development logs"
}

# Show logs
show_logs() {
    if [ "$1" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml logs -f
    else
        docker-compose logs -f
    fi
}

# Stop application
stop_app() {
    print_status "Stopping WhiteLabelRAG..."
    
    if [ "$1" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml down
    else
        docker-compose down
        docker-compose --profile nginx down
    fi
    
    print_success "Application stopped"
}

# Restart application
restart_app() {
    print_status "Restarting WhiteLabelRAG..."
    
    if [ "$1" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml restart
    else
        docker-compose restart
    fi
    
    print_success "Application restarted"
}

# Clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    
    # Stop all containers
    docker-compose down
    docker-compose -f docker-compose.dev.yml down
    docker-compose --profile nginx down
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes (ask for confirmation)
    read -p "Remove unused volumes? This will delete data! (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker volume prune -f
        print_warning "Volumes removed"
    fi
    
    print_success "Cleanup completed"
}

# Main script
main() {
    local command=$1
    local option=$2
    
    # Change to script directory
    cd "$(dirname "$0")/.."
    
    case $command in
        "build")
            check_docker
            build_images $option
            ;;
        "deploy")
            check_docker
            if ! check_env; then
                print_error "Please configure .env file first"
                exit 1
            fi
            build_images $option
            deploy $option
            check_status $option
            ;;
        "status")
            check_status $option
            ;;
        "logs")
            show_logs $option
            ;;
        "stop")
            stop_app $option
            ;;
        "restart")
            restart_app $option
            ;;
        "clean")
            cleanup
            ;;
        "help"|"--help"|"-h")
            usage
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"