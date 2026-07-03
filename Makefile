# Copyright (c) 2026 MyCompany LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

.PHONY: install playground

# Install dependencies in editable mode
install:
	/Volumes/HardDisk/git_projects/adk_env/bin/pip install -e .

# Launch the ADK development playground UI on port 8000
playground:
	/Volumes/HardDisk/git_projects/adk_env/bin/adk web --port 8000 ./
