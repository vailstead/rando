#!/bin/bash

IMAGE="registry.example.com/my-group/my-image"
CREDS="username:password"  # optional if your registry requires auth

# Get tags
tags=$(skopeo list-tags --creds="$CREDS" docker://$IMAGE | jq -r '.Tags[]')

# Loop through tags and get size
for tag in $tags; do
    info=$(skopeo inspect --creds="$CREDS" docker://$IMAGE:$tag)
    size=$(echo "$info" | jq '.Layers[].Size' | awk '{s+=$1} END {print s}')
    human_size=$(numfmt --to=iec-i --suffix=B $size 2>/dev/null || echo "$size bytes")
    echo "$tag: $human_size"
done
