#!/bin/bash

# Load environment variables
source .env

KEYCLOAK_URL="http://localhost:8080/auth"
REALM="pkms-realm"
CLIENT_ID="pkms-client"

# Wait for Keycloak to be ready
echo "Waiting for Keycloak to start..."
until curl -s "$KEYCLOAK_URL" > /dev/null; do
    sleep 5
done

echo "Keycloak is ready. Authenticating..."

# Get admin access token
ADMIN_TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$KEYCLOAK_ADMIN" \
    -d "password=$KEYCLOAK_ADMIN_PASSWORD" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" | jq -r '.access_token')

echo "Checking if realm exists..."

# Check if realm exists
REALM_EXISTS=$(curl -s -o /dev/null -w "%{http_code}" "$KEYCLOAK_URL/admin/realms/$REALM" \
    -H "Authorization: Bearer $ADMIN_TOKEN")

if [ $REALM_EXISTS == "200" ]; then
    echo "Realm $REALM already exists. Skipping creation."
else
    echo "Creating realm..."
    curl -s -X POST "$KEYCLOAK_URL/admin/realms" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"realm\":\"$REALM\",\"enabled\":true}"
fi

echo "Checking if client exists..."

# Check if client exists
CLIENT_ID_ENCODED=$(echo -n $CLIENT_ID | jq -sRr @uri)
CLIENT_EXISTS=$(curl -s -o /dev/null -w "%{http_code}" "$KEYCLOAK_URL/admin/realms/$REALM/clients?clientId=$CLIENT_ID_ENCODED" \
    -H "Authorization: Bearer $ADMIN_TOKEN")

# Create or update client
CLIENT_DATA='{
    "clientId": "'"$CLIENT_ID"'",
    "publicClient": false,
    "redirectUris": ["http://localhost:3000/*"],
    "webOrigins": ["+"],
    "directAccessGrantsEnabled": true,
    "authorizationServicesEnabled": true,
    "serviceAccountsEnabled": true,
    "standardFlowEnabled": true
}'

if [ $CLIENT_EXISTS == "200" ]; then
    echo "Client $CLIENT_ID already exists. Updating..."
    CLIENT_UUID=$(curl -s "$KEYCLOAK_URL/admin/realms/$REALM/clients?clientId=$CLIENT_ID_ENCODED" \
        -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[0].id')
    curl -s -X PUT "$KEYCLOAK_URL/admin/realms/$REALM/clients/$CLIENT_UUID" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$CLIENT_DATA"
else
    echo "Creating client..."
    curl -s -X POST "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$CLIENT_DATA"
fi

# Function to create or update test user
create_or_update_test_user() {
    local max_retries=3
    local retry_count=0

    while [ $retry_count -lt $max_retries ]; do
        echo "Checking if test user exists (Attempt $((retry_count + 1)))..."
        USER_EXISTS=$(curl -s -o /dev/null -w "%{http_code}" "$KEYCLOAK_URL/admin/realms/$REALM/users?username=testuser" \
            -H "Authorization: Bearer $ADMIN_TOKEN")

        if [ $USER_EXISTS == "200" ]; then
            echo "Test user exists. Attempting to update..."
            USER_ID=$(curl -s "$KEYCLOAK_URL/admin/realms/$REALM/users?username=testuser" \
                -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[0].id')
            
            if [ -n "$USER_ID" ] && [ "$USER_ID" != "null" ]; then
                # Update user details
                UPDATE_RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null -X PUT "$KEYCLOAK_URL/admin/realms/$REALM/users/$USER_ID" \
                    -H "Authorization: Bearer $ADMIN_TOKEN" \
                    -H "Content-Type: application/json" \
                    -d '{
                        "username": "testuser",
                        "enabled": true,
                        "emailVerified": true,
                        "firstName": "Test",
                        "lastName": "User",
                        "email": "user@example.com",
                        "requiredActions": []
                    }')
                
                if [ $UPDATE_RESPONSE == "204" ]; then
                    echo "User updated successfully."
                    # Reset password
                    curl -s -X PUT "$KEYCLOAK_URL/admin/realms/$REALM/users/$USER_ID/reset-password" \
                        -H "Authorization: Bearer $ADMIN_TOKEN" \
                        -H "Content-Type: application/json" \
                        -d '{"type":"password","value":"testpassword","temporary":false}'
                    echo "Password reset successfully."
                    return 0
                else
                    echo "Failed to update user. HTTP response: $UPDATE_RESPONSE"
                fi
            else
                echo "Failed to retrieve user ID. Creating new user..."
            fi
        fi

        echo "Creating test user..."
        CREATE_RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$KEYCLOAK_URL/admin/realms/$REALM/users" \
            -H "Authorization: Bearer $ADMIN_TOKEN" \
            -H "Content-Type: application/json" \
            -d '{
                "username": "testuser",
                "enabled": true,
                "emailVerified": true,
                "firstName": "Test",
                "lastName": "User",
                "email": "user@example.com",
                "credentials": [{"type": "password", "value": "testpassword", "temporary": false}],
                "requiredActions": []
            }')
        
        if [ $CREATE_RESPONSE == "201" ]; then
            echo "Test user created successfully."
            return 0
        else
            echo "Failed to create user. HTTP response: $CREATE_RESPONSE"
        fi

        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            echo "Retrying in 5 seconds..."
            sleep 5
        fi
    done

    echo "Failed to create or update test user after $max_retries attempts."
    return 1
}

# Create or update test user in development environment
if [ "$ENVIRONMENT" = "development" ]; then
    create_or_update_test_user
    if [ $? -eq 0 ]; then
        echo "Test user setup completed successfully."
    else
        echo "Test user setup failed."
    fi
else
    echo "Production environment detected. Skipping test user creation/update."
fi

echo "Keycloak initialization completed."
