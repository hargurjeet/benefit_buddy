#!/bin/bash

# Get project root (parent of .agents)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")")"

HOOK_DIR="$PROJECT_ROOT/.git/hooks"
HOOK_FILE="$HOOK_DIR/pre-push"

if [ ! -d "$HOOK_DIR" ]; then
    echo "Error: .git/hooks directory not found. Make sure this is a Git repository."
    exit 1
fi

echo "Installing Git pre-push hook at $HOOK_FILE..."

cat << 'EOF' > "$HOOK_FILE"
#!/bin/bash

echo "Running pre-push cleanup: removing macOS AppleDouble metadata files (._*)..."
find . -type f -name "._*" -delete

# Remove from Git index if cached
git rm -r --cached -f --ignore-unmatch "._*" "**/._*" 2>/dev/null || true

echo "Cleanup complete. Proceeding with push."
exit 0
EOF

chmod +x "$HOOK_FILE"

echo "Running initial cleanup of existing metadata files..."
find "$PROJECT_ROOT" -type f -name "._*" -delete
git rm -r --cached -f --ignore-unmatch "._*" "**/._*" 2>/dev/null || true

echo "Git pre-push hook successfully installed and initial cleanup done!"
exit 0
