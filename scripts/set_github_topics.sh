#!/usr/bin/env bash
# Set GitHub repository topics via REST API. Requires a GitHub token with repo scope.
# Usage:
#   export GITHUB_TOKEN=ghp_xxx
#   ./scripts/set_github_topics.sh dyra-12 Machine-Theory-Of-Mind

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <owner> <repo>"
  exit 1
fi

OWNER="$1"
REPO="$2"

if [ -z "$GITHUB_TOKEN" ]; then
  echo "Set GITHUB_TOKEN environment variable with a Personal Access Token that has repo:public_repo scope."
  exit 1
fi

API_URL="https://api.github.com/repos/${OWNER}/${REPO}/topics"

JSON='{"names":["computational-psychiatry","theory-of-mind","bayesian-ai","social-intelligence"]}'

curl -X PUT \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$JSON" \
  "$API_URL"

echo
echo "Requested topics set for ${OWNER}/${REPO}. Verify on GitHub repository page." 
