NexusKnowledge Project
This repository contains the source code and documentation for the NexusKnowledge system, a local-first, single-user AI conversation management and knowledge synthesis tool.

Overview
This project follows a strict, AI-driven development process. Please refer to the documents in the docs/ directory and AGENTS.md for a complete overview of the architecture and operating procedures.

Getting Started (Ubuntu 24.04 Desktop)
Step 1: One-Time Environment Setup
Install Prerequisites: Open a terminal and install Docker, VS Code, and other essential tools:

# Add Docker's official GPG key & set up the repository (run these commands one by one)

sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL [https://download.docker.com/linux/ubuntu/gpg](https://download.docker.com/linux/ubuntu/gpg) -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] [https://download.docker.com/linux/ubuntu](https://download.docker.com/linux/ubuntu) $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install Docker Engine, CLI, and Containerd

sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to the docker group to run docker without sudo

sudo usermod -aG docker $USER

# Install VS Code

sudo apt-get install -y wget gpg
wget -qO- [https://packages.microsoft.com/keys/microsoft.asc](https://packages.microsoft.com/keys/microsoft.asc) | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] [https://packages.microsoft.com/repos/code](https://packages.microsoft.com/repos/code) stable main" | sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null
rm -f packages.microsoft.gpg
sudo apt-get install -y apt-transport-https
sudo apt-get update
sudo apt-get install -y code

IMPORTANT: After running these commands, you must log out and log back in for the docker group changes to take effect.

Set Environment Variables: Add your API keys (GITHUB_USERNAME, GITHUB_PAT_KEY, etc.) to your ~/.bashrc file. Refer to docs/ENV.md for the full list.

echo 'export GITHUB*USERNAME="your_github_username"' >> ~/.bashrc
echo 'export GITHUB_PAT_KEY="github_pat*...\_with_read_packages_scope"' >> ~/.bashrc
echo 'export XAI_API_KEY="your_grok_api_key"' >> ~/.bashrc
echo 'export DEEPSEEK_API_KEY="your_deepseek_api_key"' >> ~/.bashrc
source ~/.bashrc

Authenticate Docker: In the terminal, run the one-time Docker login command:

echo $GITHUB_PAT_KEY | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin

You should see a "Login Succeeded" message.

Step 2: Performance Tuning (Important for Stability)
To prevent VS Code from freezing, you must ensure Docker has enough system resources.

Open Docker Desktop.

Go to Settings > Resources.

Increase Memory: Allocate a significant portion of your system's RAM to Docker. For a system with 64GB, allocating 24GB to 32GB is a good starting point.

Increase CPUs: Allocate at least half of your available CPU cores. For a 24-core system, allocating 12 to 16 cores is recommended.

Click "Apply & Restart".

Step 3: Launch the Project Environment
Launch Docker Compose: From your terminal, navigate to the project root and run:

docker-compose up --build -d

This will build and start all necessary services, including the Celery worker. The `app` container runs database migrations automatically using `python scripts/run_migrations.py` before serving the API.

If you are running the stack outside Docker, apply the migrations manually:

```bash
python scripts/run_migrations.py
```

Execute a Sample Task: To execute a sample asynchronous task, shell into the app container:

docker exec -it nexus-app bash

Then, from within the container's bash, run the following Python commands:

python
from nexus_knowledge.tasks import long_running_api_call
long_running_api_call.delay("Hello from Celery!")
exit()

You can observe the worker processing the task in the docker-compose logs:

docker-compose logs -f worker

To validate the MLflow integration, log a dummy experiment (the CLI will reuse the `MLFLOW_TRACKING_URI` environment variable or default to `http://localhost:5000`):

```bash
python scripts/log_dummy_experiment.py
```

Queue a sample ingestion payload (replace the JSON body with your data). The API returns a `rawDataId` you can poll for status:

````bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
        "sourceType": "deepseek_chat",
        "sourceId": "demo-conversation",
        "content": {
          "messages": [
            {"role": "user", "content": "Hello", "timestamp": "2025-01-01T00:00:00Z"},
            {"role": "assistant", "content": "Hi there!", "timestamp": "2025-01-01T00:00:05Z"}
          ]
        }
      }'

curl http://localhost:8000/api/v1/ingest/<rawDataId>

Once a payload is normalized you can queue the sentiment analysis job and check its status:

```bash
curl -X POST http://localhost:8000/api/v1/analysis \
  -H "Content-Type: application/json" \
  -d '{"rawDataId": "<rawDataId>"}'

curl http://localhost:8000/api/v1/analysis/<rawDataId>

After analysis completes you can generate and inspect correlation candidates:

```bash
curl -X POST http://localhost:8000/api/v1/correlation \
  -H "Content-Type: application/json" \
  -d '{"rawDataId": "<rawDataId>"}'

curl http://localhost:8000/api/v1/correlation/<rawDataId>
````

Run a hybrid search across stored conversation turns:

```bash
curl "http://localhost:8000/api/v1/search?q=hybrid+search&limit=5"
```

Run the automated test suite from your activated virtual environment:

```bash
./.venv/bin/pytest
```

Launch the lightweight UI at <http://localhost:8000/> to run searches and submit feedback.

Step 4: YOLO Mode Initialization (Required for Each Session)
Before giving the agent a major task, grant it permission to run its tools non-stop.

Grant WriteFile Permission: In the chat, ask the agent to: "Create a file named test.txt with 'hello'." When prompted, click the dropdown next to "Accept" and choose "Always Accept".

Grant Shell Permission: Ask the agent to: "List files using ls." When prompted, choose "Always Accept".

Clean Up: Delete test.txt.

Step 5: Kickoff
The GPT Orchestrator (via Codex) is now fully prepared. Provide it with the "Final Kickoff Prompt" from `prompts.md`.
