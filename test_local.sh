#!/bin/bash

# Install dependencies first
# pip3 install -r requirements.txt

# Test the RSM monitoring function directly
echo "Testing RSM Monitoring:"
python3 -c "
from rsm_monitoring import lambda_handler
import json
result = lambda_handler({}, None)
print(json.dumps(result, indent=2))
"
