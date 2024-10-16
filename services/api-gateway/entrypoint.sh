#!/bin/sh

PUBLIC_KEY=$(cat /tmp/keycloak_public_key.pem)
sed "s|\${PUBLIC_KEY}|$PUBLIC_KEY|g" /usr/local/kong/declarative/kong.yml.template > /usr/local/kong/declarative/kong.yml

exec /docker-entrypoint.sh kong docker-start
