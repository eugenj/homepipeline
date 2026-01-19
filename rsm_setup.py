#!/usr/bin/env python3

import json
import os
import boto3
from getpass import getpass
from botocore.exceptions import ClientError

def setup_local_credentials():
    """Setup local secure credential storage"""
    
    print("RSM Portal Credential Setup - Local Storage")
    print("=" * 45)
    
    email = input("Email (default: evgeny.zhuravlev@gmail.com): ").strip()
    if not email:
        email = "evgeny.zhuravlev@gmail.com"
    
    password = getpass("Password: ")
    
    credentials = {
        'email': email,
        'password': password
    }
    
    credential_file = os.path.expanduser('~/.rsm_credentials')
    
    with open(credential_file, 'w') as f:
        json.dump(credentials, f)
    
    # Set restrictive permissions
    try:
        os.chmod(credential_file, 0o600)
        print(f"✅ Credentials stored securely in {credential_file}")
        print("   File permissions set to 600 (owner read/write only)")
    except:
        print(f"⚠️  Credentials stored in {credential_file}")
        print("   Could not set restrictive permissions")
    
    return credentials

def setup_aws_secrets():
    """Setup AWS Secrets Manager storage"""
    
    print("\nRSM Portal Credential Setup - AWS Secrets Manager")
    print("=" * 50)
    
    # Check if local credentials exist
    credential_file = os.path.expanduser('~/.rsm_credentials')
    
    if os.path.exists(credential_file):
        use_local = input("Use existing local credentials? (y/n): ").lower()
        if use_local == 'y':
            with open(credential_file, 'r') as f:
                credentials = json.load(f)
        else:
            credentials = setup_local_credentials()
    else:
        print("No local credentials found. Creating new ones...")
        credentials = setup_local_credentials()
    
    # Upload to AWS Secrets Manager
    try:
        session = boto3.session.Session()
        client = session.client('secretsmanager', region_name='us-east-1')
        
        # Try to create the secret
        try:
            response = client.create_secret(
                Name='rsm-credentials',
                Description='RSM Parent Portal credentials',
                SecretString=json.dumps(credentials)
            )
            print(f"✅ Secret created successfully: {response['ARN']}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceExistsException':
                # Secret exists, update it
                response = client.update_secret(
                    SecretId='rsm-credentials',
                    SecretString=json.dumps(credentials)
                )
                print(f"✅ Secret updated successfully: {response['ARN']}")
            else:
                raise e
                
    except Exception as e:
        print(f"❌ Failed to setup AWS Secrets Manager: {e}")
        print("Make sure you have AWS CLI configured with proper permissions")
        return False
    
    return True

def main():
    print("RSM Portal Credential Setup")
    print("=" * 30)
    print("1. Local storage only")
    print("2. AWS Secrets Manager (recommended for Lambda)")
    print("3. Both local and AWS")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '1':
        setup_local_credentials()
        print("\n✅ Local credentials setup complete")
        
    elif choice == '2':
        if setup_aws_secrets():
            print("\n✅ AWS Secrets Manager setup complete")
        
    elif choice == '3':
        credentials = setup_local_credentials()
        print("\n" + "="*50)
        if setup_aws_secrets():
            print("\n✅ Both local and AWS setup complete")
        
    else:
        print("Invalid choice. Please run again and select 1, 2, or 3.")
        return
    
    print("\nCredentials are now ready for use with rsm_monitoring.py")

if __name__ == "__main__":
    main()
