# NexusKnowledge Project

This repository contains the source code and documentation for the NexusKnowledge system, a local-first, single-user AI conversation management and knowledge synthesis tool.

## Overview

This project follows a strict, AI-driven development process. Please refer to the documents in the `docs/` directory and `AGENTS.md` for a complete overview of the architecture and operating procedures.

## Getting Started (Ubuntu 24.04 Desktop)

### **Step 1: One-Time Environment Setup**

1.  **Install Prerequisites**: Open a terminal and install Docker, VS Code, and other essential tools:
    ```bash
    # Add Docker's official GPG key & set up the repository (run these commands one by one)
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    # Install Docker Engine, CLI, and Containerd
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    # Add your user to the docker group to run docker without sudo
    sudo usermod -aG docker $USER
    # Install VS Code
    sudo apt-get install -y wget gpg
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
    sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
    echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null
    rm -f packages.microsoft.gpg
    sudo apt-get install -y apt-transport-https
    sudo apt-get update
    sudo apt-get install -y code
    ```
    **IMPORTANT:** After running these commands, you must **log out and log back in** for the `docker` group changes to take effect.

2.  **Set Environment Variables**: Add your API keys (`GITHUB_USERNAME`, `GITHUB_PAT_KEY`, etc.) to your `~/.bashrc` file.
    ```bash
    echo 'export GITHUB_USERNAME="your_github_username"' >> ~/.bashrc
    echo 'export GITHUB_PAT_KEY="github_pat_..._with_read_packages_scope"' >> ~/.bashrc
    echo 'export XAI_API_KEY="your_grok_api_key"' >> ~/.bashrc
    echo 'export DEEPSEEK_API_KEY="your_deepseek_api_key"' >> ~/.bashrc
    source ~/.bashrc
    ```

3.  **Authenticate Docker**: In the terminal, run the one-time Docker login command:
    ```bash
    echo $GITHUB_PAT_KEY | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin
    ```
    You should see a "Login Succeeded" message.

### **Step 2: Launch the Project Environment**

1.  **Launch Your IDE from Terminal**: From your terminal, run:
    ```bash
    cd /path/to/your/project && code .
    ```
2.  **Build the Devcontainer**: Once VS Code opens, it will detect the `.devcontainer` directory and prompt you to **"Reopen in Container"**. Click it. The container will now build successfully.

### **Step 3: YOLO Mode Initialization (Required for Each Session)**

Before giving the agent a major task, grant it permission to run its tools non-stop.

1.  **Grant `WriteFile` Permission:** In the chat, ask the agent to: `"Create a file named test.txt with 'hello'."` When prompted, click the dropdown next to "Accept" and choose **"Always Accept"**.
2.  **Grant `Shell` Permission:** Ask the agent to: `"List files using ls."` When prompted, choose **"Always Accept"**.
3.  **Clean Up:** Delete `test.txt`.

### **Step 4: Kickoff**

The Gemini YOLO agent is now fully prepared. Provide it with the "Final Kickoff Prompt" from `prompts.md`.
