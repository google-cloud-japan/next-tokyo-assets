#!/bin/bash

curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -d '{"location":"asia-northeast1"}' \
  https://firebasestorage.googleapis.com/v1alpha/projects/$GOOGLE_CLOUD_PROJECT/defaultBucket

