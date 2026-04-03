#!/bin/bash
# Quick Backup Script for Existing Wesza Installation
# Run this BEFORE deploying the new version

set -e

BACKUP_DIR="/opt/backups/wesza-backup-$(date +%Y%m%d-%H%M%S)"
WESZA_DIR="/opt/wesza"

echo "╔══════════════════════════════════════════════════╗"
echo "║     Wesza Pre-Deployment Backup Script          ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Check if wesza directory exists
if [ ! -d "$WESZA_DIR" ]; then
    echo "✓ No existing Wesza installation found at $WESZA_DIR"
    echo "  Skipping backup..."
    exit 0
fi

echo "Found existing Wesza installation at: $WESZA_DIR"
echo ""

# Create backup directory
echo "Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Backup application files
echo "Backing up application files..."
cp -r "$WESZA_DIR" "$BACKUP_DIR/wesza-app"

# Backup Docker volumes if they exist
if docker volume ls | grep -q wesza; then
    echo "Backing up Docker volumes..."
    docker run --rm \
        -v wesza_redis-data:/source:ro \
        -v "$BACKUP_DIR/docker-volumes:/backup" \
        alpine tar czf /backup/redis-data.tar.gz -C /source .
fi

# Export Docker container configurations
echo "Exporting Docker container configurations..."
docker ps -a --format "{{.ID}} {{.Names}} {{.Image}}" > "$BACKUP_DIR/container-list.txt" 2>/dev/null || true
docker compose -C "$WESZA_DIR" config > "$BACKUP_DIR/docker-compose.yml" 2>/dev/null || true

# Backup environment file (with sensitive data warning)
if [ -f "$WESZA_DIR/.env" ]; then
    echo "⚠️  Backing up .env file (contains sensitive credentials)"
    cp "$WESZA_DIR/.env" "$BACKUP_DIR/env-backup.txt"
    chmod 600 "$BACKUP_DIR/env-backup.txt"
fi

# Create manifest
cat > "$BACKUP_DIR/BACKUP_MANIFEST.txt" << EOF
Wesza Platform Backup Manifest
==============================
Backup Date: $(date)
Source Directory: $WESZA_DIR
Backup Location: $BACKUP_DIR

Contents:
- wesza-app/ (complete application code)
- docker-volumes/ (Redis data if applicable)
- container-list.txt (Docker container info)
- docker-compose.yml (Compose configuration)
- env-backup.txt (Environment variables - SENSITIVE!)

To Restore:
1. Stop current containers: cd /opt/wesza && docker compose down
2. Copy backup back: cp -r $BACKUP_DIR/wesza-app/* /opt/wesza/
3. Restore .env: cp $BACKUP_DIR/env-backup.txt /opt/wesza/.env
4. Start services: docker compose up -d

EOF

# Set secure permissions
chmod 700 "$BACKUP_DIR"
chmod -R 600 "$BACKUP_DIR/env-backup.txt" 2>/dev/null || true

# Show backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║           Backup Completed Successfully!         ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "Backup Location: $BACKUP_DIR"
echo "Backup Size: $BACKUP_SIZE"
echo ""
echo "Contents:"
ls -lah "$BACKUP_DIR"
echo ""
echo "✓ You can now safely proceed with deployment!"
echo "  To restore this backup later, see BACKUP_MANIFEST.txt"
