#!/bin/bash
set -e
mkdir -p /logs/verifier
if pytest /tests/test_feature.py -q; then
  echo "1" > /logs/verifier/reward.txt
else
  echo "0" > /logs/verifier/reward.txt
  exit 1
fi
