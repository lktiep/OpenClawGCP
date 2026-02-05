#!/bin/bash
# OpenClaw post-boot setup script
# Run this after VM restarts to restore container state

cd ~/openclaw

# Start containers
sudo docker compose up -d

# Wait for container
sleep 10

# Install tools inside container
sudo docker exec -u root openclaw-openclaw-gateway-1 bash -c "
  apt-get update -qq
  apt-get install -y -qq git python3-pip chromium >/dev/null 2>&1
  
  # GitHub CLI
  if ! command -v gh &> /dev/null; then
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg 2>/dev/null
    chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
    echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main\" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    apt-get update -qq && apt-get install -y -qq gh >/dev/null 2>&1
  fi
  
  # Python packages for multimodal
  pip3 install -q google-cloud-aiplatform cognee playwright --break-system-packages 2>/dev/null
  /home/node/.local/bin/playwright install chromium 2>/dev/null
"

echo "OpenClaw setup complete!"
