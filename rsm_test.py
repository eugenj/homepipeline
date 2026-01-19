#!/usr/bin/env python3

# Mock Lambda context
class MockContext:
    def __init__(self):
        self.aws_request_id = "local-test-12345"

import rsm_monitoring

if __name__ == "__main__":
    result = rsm_monitoring.lambda_handler({}, MockContext())
    print(f"Status: {result['statusCode']}")
    print(f"Response: {result['body']}")
