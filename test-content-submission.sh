#!/bin/bash

# File: test-content-submission.sh

# Load environment variables
source .env

# Keycloak settings
KEYCLOAK_URL="http://localhost/auth"
REALM="${KEYCLOAK_REALM}"
CLIENT_ID="pkms-client"
CLIENT_SECRET="CbSDVXo8qI2m2OuBCoazbDvnhwCdMSwL"

# Content submission settings
CONTENT_SUBMISSION_URL="http://localhost/api/content-submission/submit"

# Debug function
debug() {
    echo "[DEBUG] $1"
}

# Get access token
debug "Keycloak URL: $KEYCLOAK_URL"
debug "Realm: $REALM"
debug "Client ID: $CLIENT_ID"
debug "Client Secret: $CLIENT_SECRET"

echo "Obtaining access token..."
TOKEN_RESPONSE=$(curl -v -X POST "$KEYCLOAK_URL/realms/$REALM/protocol/openid-connect/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=password" \
     -d "client_id=$CLIENT_ID" \
     -d "client_secret=$CLIENT_SECRET" \
     -d "username=testuser" \
     -d "password=testpassword" 2>&1)

debug "Token response: $TOKEN_RESPONSE"

# Extract the access token using jq instead of grep
ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '{.*}' | jq -r '.access_token')

if [ -z "$ACCESS_TOKEN" ]; then
    echo "Failed to obtain access token. Response:"
    echo "$TOKEN_RESPONSE"
    exit 1
fi

echo "Access token obtained successfully."
debug "Access token: $ACCESS_TOKEN"

# Extract user ID from the token
USER_ID=$(echo "$ACCESS_TOKEN" | jq -R 'split(".")[1] | @base64d | fromjson | .sub')
debug "User ID: $USER_ID"

# echo "Submitting content..."
# SUBMISSION_RESPONSE=$(curl -v -X POST "$CONTENT_SUBMISSION_URL" \
#      -H "Content-Type: application/json" \
#      -H "Authorization: Bearer $ACCESS_TOKEN" \
#      -d "{
#        \"content\": \"This is a fascinating article about AI: https://example.com/ai-article\",
#        \"user_id\": $USER_ID
#      }" 2>&1)

# echo "Submission response:"
# debug "Raw submission response: $SUBMISSION_RESPONSE"
# echo "$SUBMISSION_RESPONSE" | jq '.' || echo "$SUBMISSION_RESPONSE"
