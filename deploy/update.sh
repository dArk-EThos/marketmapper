#!/bin/bash
###############################################################################
# Market Mapper — Deployment Update Script
# Pull latest code, install deps, migrate, collect static, restart service
###############################################################################
set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

DEPLOY_DIR="/opt/marketmapper"

info() { echo -e "${BLUE}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }

cd "${DEPLOY_DIR}"

info "Pulling latest code..."
git pull

info "Installing dependencies..."
source .venv/bin/activate
pip install -r requirements.txt -q

info "Running migrations..."
python manage.py migrate --noinput

info "Collecting static files..."
python manage.py collectstatic --noinput

deactivate

info "Restarting service..."
sudo systemctl restart marketmapper

echo ""
success "Market Mapper deployed successfully! 🚀"
echo -e "  Check status: ${BLUE}systemctl status marketmapper${NC}"
