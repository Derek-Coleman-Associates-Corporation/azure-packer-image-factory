#!/bin/bash
set -e

echo "Triggering automated GitHub Actions pipelines for Phase 2 Expansion profiles..."

# The version we are building
IMAGE_VERSION="2026.03.07"

# Define the list of profiles to trigger.
# Note: sql2025-ws2025-enterprise was already triggered manaually to test the API.
# Note: ubuntu-server-2404-minimal was baked manually locally.
PROFILES=(
  "sql2025-ws2025-standard:2025"
  "sql2025-ws2025-developer:2025"
  "sql2019-ws2022-enterprise:2019"
  "sql2019-ws2022-standard:2019"
  "sql2019-ws2022-developer:2019"
  "sql2019-ws2022-enterprise-gen1:2019"
  "sql2019-ws2022-standard-gen1:2019"
  "sql2019-ws2022-developer-gen1:2019"
  "ubuntu-server-2404-minimal-gen1:24.04"
  "ubuntu-server-2204-minimal:22.04"
  "ubuntu-server-2204-minimal-gen1:22.04"
)

for entry in "${PROFILES[@]}"; do
  # Parse profile and os_version
  PROFILE_ID="${entry%%:*}"
  OS_VERSION="${entry##*:}"

  echo "Dispatching workflow for profile: $PROFILE_ID (OS Version: $OS_VERSION)"
  
  gh workflow run packer-build.yml \
    -f profile_path="profiles/$PROFILE_ID" \
    -f os_version="$OS_VERSION" \
    -f image_version="$IMAGE_VERSION"
    
  echo "Workflow dispatched successfully for $PROFILE_ID."
  echo "--------------------------------------------------------"
  # Optional: Sleep to prevent hitting GitHub API rate limits
  sleep 2
done

echo "All unattended automated build workflows have been dispatched to GitHub Actions!"
