#!/bin/bash
export USER_ID="shy"

gcloud functions deploy ${USER_ID} \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --entry-point main