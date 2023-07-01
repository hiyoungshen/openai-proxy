#!/bin/bash

PROXY_URL="PROXY_URL"

curl ${PROXY_URL}/openai \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-xxxxx" \
  -d '{
      "model": "gpt-3.5-turbo",
      "messages": [{"role": "user", "content": "Hello world!"}]
    }'