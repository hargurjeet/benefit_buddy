import os
import sys

# Ensure pytest finds all sub-agent and tool packages inside the app/ folder
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
app_dir = os.path.join(project_root, "app")

for d in [app_dir, project_root]:
    if d not in sys.path:
        sys.path.insert(0, d)
