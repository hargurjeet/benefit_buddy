---
name: clean-mac-files
description: Automatically cleans up macOS metadata files (._*) and configures Git hooks to prevent pushing them.
---

# clean-mac-files

This skill ensures that macOS metadata files (specifically `._*` AppleDouble files, which cause noise in repositories) are automatically cleaned up and prevented from being pushed to GitHub.

## Instructions for the Agent

When this skill is triggered or when the user wants to configure macOS file cleanup:

1.  **Install Git Hooks**:
    Install a `pre-push` Git hook that deletes all `._*` files in the repository directory and removes them from the Git cache before any push goes through.
2.  **Run Clean Commands**:
    Execute a recursive deletion of all `._*` files and ensure `.gitignore` lists `._*` and `.DS_Store`.

## Hook Script Template

The Git pre-push hook should be saved to `.git/hooks/pre-push` with executable permissions:

```bash
#!/bin/bash

# Clean files in the working tree
echo "Cleaning up macOS AppleDouble metadata files (._*)..."
find . -type f -name "._*" -delete

# Remove from Git index in case they were staged
git rm -r --cached -f --ignore-unmatch "._*" "**/._*" 2>/dev/null || true

echo "macOS metadata files cleaned successfully. Proceeding with push..."
exit 0
```
