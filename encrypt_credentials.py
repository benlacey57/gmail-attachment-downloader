import argparse
from encryption_util import CredentialEncryptor
import yaml
import os

def update_config(config_path, encrypted_path):
    """Update config file with encrypted credentials path."""
    try:
        # Load existing config
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Update credentials section
        if 'gmail' not in config:
            config['gmail'] = {}
        
        config['gmail']['credentials_mode'] = 'encrypted'
        config['gmail']['encrypted_credentials_file'] = encrypted_path
        
        # Write updated config
        with open(config_path, 'w') as file:
            yaml.dump(config, file)
            
        print(f"Updated config file {config_path} with encrypted credentials path")
        
    except Exception as e:
        print(f"Failed to update config file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Encrypt Google API credentials")
    parser.add_argument("--credentials", default="credentials.json", help="Path to credentials file")
    parser.add_argument("--output", help="Path for encrypted output file")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    
    args = parser.parse_args()
    
    # Determine output path
    output_path = args.output or f"{args.credentials}.encrypted"
    
    # Encrypt the file
    result_path, key = CredentialEncryptor.encrypt_file(args.credentials, output_path)
    
    if result_path:
        # Update config file
        update_config(args.config, os.path.abspath(result_path))
        
        print("\nSAVE YOUR KEY:")
        print("==============")
        print(f"{key}")
        print("\nYou can also set this as an environment variable:")
        print(f"export GMAIL_ENCRYPTION_KEY='{key}'")
        
if __name__ == "__main__":
    main()