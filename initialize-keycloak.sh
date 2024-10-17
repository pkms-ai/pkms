#!/bin/bash

# Load environment variables
source .env

KEYCLOAK_URL="${KEYCLOAK_URL:-http://localhost/auth}"
REALM="${KEYCLOAK_REALM}"
CLIENT_ID="${KEYCLOAK_CLIENT_ID}"

# Function to make authenticated requests
make_request() {
    local method=$1
    local url=$2
    local data=$3
    curl -s -X "$method" "$url" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        ${data:+-d "$data"}
}

# Wait for Keycloak to be ready
echo "Waiting for Keycloak to start..."
while ! curl -s "$KEYCLOAK_URL" > /dev/null; do
    sleep 5
done

echo "Keycloak is ready. Authenticating..."

# Get admin access token
ADMIN_TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
    -d "client_id=admin-cli" \
    -d "username=$KEYCLOAK_ADMIN" \
    -d "password=$KEYCLOAK_ADMIN_PASSWORD" \
    -d "grant_type=password" | jq -r '.access_token')

echo "Successfully obtained admin token."

# Create realm if it doesn't exist
if ! make_request GET "$KEYCLOAK_URL/admin/realms/$REALM" | grep -q "\"realm\":\"$REALM\""; then
    echo "Creating realm $REALM..."
    make_request POST "$KEYCLOAK_URL/admin/realms" "{\"realm\":\"$REALM\",\"enabled\":true}"
fi

# Create client if it doesn't exist
if ! make_request GET "$KEYCLOAK_URL/admin/realms/$REALM/clients?clientId=$CLIENT_ID" | grep -q "\"clientId\":\"$CLIENT_ID\""; then
    echo "Creating client $CLIENT_ID..."
    make_request POST "$KEYCLOAK_URL/admin/realms/$REALM/clients" '{
        "clientId": "'"$CLIENT_ID"'",
        "publicClient": false,
        "redirectUris": ["http://localhost:3000/*"],
        "webOrigins": ["+"],
        "directAccessGrantsEnabled": true,
        "authorizationServicesEnabled": true,
        "serviceAccountsEnabled": true,
        "standardFlowEnabled": true
    }'
fi

# Retrieve client secret
CLIENT_UUID=$(make_request GET "$KEYCLOAK_URL/admin/realms/$REALM/clients?clientId=$CLIENT_ID" | jq -r '.[0].id')
CLIENT_SECRET=$(make_request GET "$KEYCLOAK_URL/admin/realms/$REALM/clients/$CLIENT_UUID/client-secret" | jq -r '.value')

# Update .env file with client secret
if grep -q "KEYCLOAK_CLIENT_SECRET=" .env; then
    # Check if running on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS (BSD sed) requires an empty string for the backup extension
        sed -i "" "s/KEYCLOAK_CLIENT_SECRET=.*/KEYCLOAK_CLIENT_SECRET=$CLIENT_SECRET/" .env
    else
        # Linux (GNU sed) works without the backup extension
        sed -i "s/KEYCLOAK_CLIENT_SECRET=.*/KEYCLOAK_CLIENT_SECRET=$CLIENT_SECRET/" .env
    fi
    echo "Client secret has been updated in .env file."
else
    echo "KEYCLOAK_CLIENT_SECRET=$CLIENT_SECRET" >> .env
    echo "Client secret has been appended to .env file."
fi

# Create test user in development environment
if [ "$ENVIRONMENT" = "development" ]; then
    echo "Creating test user..."
    make_request POST "$KEYCLOAK_URL/admin/realms/$REALM/users" '{
        "username": "testuser",
        "enabled": true,
        "emailVerified": true,
        "firstName": "Test",
        "lastName": "User",
        "email": "user@example.com",
        "credentials": [{"type": "password", "value": "testpassword", "temporary": false}]
    }'
fi
echo ""
echo "Keycloak initialization completed."
