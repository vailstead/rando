#!/bin/bash

# Config
GITLAB_URL="https://gitlab.com"
PROJECT_PATH="my-group/my-project"
IMAGE_NAME="my-image"  # e.g., "cache", "web", etc.
PRIVATE_TOKEN="your_access_token"

# Get the project ID
PROJECT_ID=$(curl -s --header "PRIVATE-TOKEN: $PRIVATE_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$(urlencode $PROJECT_PATH)" | jq '.id')

# List container repositories
REPOS=$(curl -s --header "PRIVATE-TOKEN: $PRIVATE_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/registry/repositories")

# Get the registry repository ID for the given image name
REPO_ID=$(echo "$REPOS" | jq ".[] | select(.path==\"$IMAGE_NAME\") | .id")

if [ -z "$REPO_ID" ]; then
  echo "Image repository \"$IMAGE_NAME\" not found."
  exit 1
fi

# List all tags for that repository
TAGS=$(curl -s --header "PRIVATE-TOKEN: $PRIVATE_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/registry/repositories/$REPO_ID/tags" | jq -c '.[]')

# Loop through tags and sum sizes
TOTAL=0
echo "$TAGS" | while read -r tag; do
  SIZE=$(echo "$tag" | jq '.total_size')
  if [[ "$SIZE" != "null" ]]; then
    TOTAL=$((TOTAL + SIZE))
  fi
done

# Output result
echo "Total image size for all tags in \"$IMAGE_NAME\": $(numfmt --to=iec --suffix=B <<< $TOTAL)"
