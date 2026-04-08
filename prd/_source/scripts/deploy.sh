#!/bin/bash

# SiliconSoul Deployment Script

set -e

echo "========================================"
echo "🚀 SiliconSoul Deployment"
echo "========================================"
echo ""

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"
LOG_DIR="${PROJECT_DIR}/logs"
PID_FILE="${LOG_DIR}/siliconsoul.pid"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}ℹ${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi

    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is required but not installed"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Setup environment
setup_environment() {
    log_info "Setting up environment..."

    # Create virtual environment if not exists
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        log_success "Virtual environment created"
    fi

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    # Install dependencies
    log_info "Installing dependencies..."
    pip3 install -r "$PROJECT_DIR/requirements.txt" > /dev/null 2>&1
    log_success "Dependencies installed"
}

# Create directories
create_directories() {
    log_info "Creating directories..."

    mkdir -p "$LOG_DIR"
    mkdir -p "${PROJECT_DIR}/data"
    mkdir -p "${PROJECT_DIR}/config"

    log_success "Directories created"
}

# Run tests
run_tests() {
    log_info "Running tests..."

    cd "$PROJECT_DIR"
    python3 -m pytest tests/ -q --tb=short

    if [ $? -eq 0 ]; then
        log_success "All tests passed"
    else
        log_error "Tests failed"
        exit 1
    fi
}

# Security check
security_check() {
    log_info "Running security checks..."

    bash "$PROJECT_DIR/scripts/security_check.sh" > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        log_success "Security checks passed"
    else
        log_warn "Security checks showed warnings"
    fi
}

# Start service
start_service() {
    log_info "Starting SiliconSoul service..."

    if [ -f "$PID_FILE" ]; then
        existing_pid=$(cat "$PID_FILE")
        if kill -0 "$existing_pid" 2>/dev/null; then
            log_warn "Service already running (PID: $existing_pid)"
            return
        fi
    fi

    cd "$PROJECT_DIR"

    # Start in background
    nohup python3 -m src.cli.main > "$LOG_DIR/siliconsoul.log" 2>&1 &

    sleep 2

    if [ -f "$PID_FILE" ]; then
        log_success "Service started (PID: $(cat $PID_FILE))"
    else
        log_error "Failed to start service"
        exit 1
    fi
}

# Health check
health_check() {
    log_info "Performing health check..."

    # Check if service is responsive
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        log_success "Service is healthy"
    else
        log_warn "Health check endpoint not accessible (service may still be starting)"
    fi
}

# Print summary
print_summary() {
    echo ""
    echo "========================================"
    echo "✅ Deployment Complete"
    echo "========================================"
    echo ""
    echo "📍 Project: $PROJECT_DIR"
    echo "📍 Logs: $LOG_DIR"
    echo "📍 Version: $(cat $PROJECT_DIR/VERSION)"
    echo ""
    echo "🚀 Service: $([ -f $PID_FILE ] && echo 'Running' || echo 'Not running')"
    echo "🌐 API: http://localhost:8000"
    echo ""
    echo "Commands:"
    echo "  Start:   $0 start"
    echo "  Stop:    $0 stop"
    echo "  Restart: $0 restart"
    echo "  Logs:    tail -f $LOG_DIR/siliconsoul.log"
    echo ""
}

# Main deployment flow
main() {
    case "${1:-deploy}" in
        deploy)
            check_prerequisites
            setup_environment
            create_directories
            run_tests
            security_check
            start_service
            health_check
            print_summary
            ;;
        start)
            setup_environment
            start_service
            ;;
        stop)
            if [ -f "$PID_FILE" ]; then
                pid=$(cat "$PID_FILE")
                kill "$pid"
                rm "$PID_FILE"
                log_success "Service stopped"
            else
                log_warn "Service not running"
            fi
            ;;
        restart)
            "$0" stop
            sleep 1
            "$0" start
            ;;
        status)
            if [ -f "$PID_FILE" ]; then
                pid=$(cat "$PID_FILE")
                if kill -0 "$pid" 2>/dev/null; then
                    log_success "Service running (PID: $pid)"
                else
                    log_error "Service not running"
                fi
            else
                log_error "Service not running"
            fi
            ;;
        *)
            echo "Usage: $0 {deploy|start|stop|restart|status}"
            exit 1
            ;;
    esac
}

main "$@"
