# encrypt.py - Encryption tool for Gmail Attachment Downloader

import argparse
import os
import yaml
from cryptography.fernet import Fernet
from encryption_util import CredentialEncryptor
import datetime

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

def save_key_to_file(key, credentials_name, output_dir=None):
    """Save encryption key to a file with warning message."""
    if output_dir is None:
        output_dir = "."
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    key_filename = os.path.join(output_dir, f"encryption_key_{timestamp}.txt")
    
    with open(key_filename, 'w') as f:
        f.write("=============================================================\n")
        f.write("                 ENCRYPTION KEY - KEEP SECURE\n")
        f.write("=============================================================\n\n")
        f.write("This file contains the encryption key for your credentials file.\n")
        f.write("IMPORTANT SECURITY NOTICE:\n")
        f.write("- Store this file in a secure location separate from the encrypted file\n")
        f.write("- Consider using a password manager to store this key\n")
        f.write("- Delete this file after saving the key elsewhere\n")
        f.write("- Anyone with this key can decrypt your credentials\n\n")
        f.write(f"File encrypted: {credentials_name}\n")
        f.write(f"Encryption date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("ENCRYPTION KEY:\n")
        f.write(f"{key}\n\n")
        f.write("To use this key with the Gmail Attachment Downloader:\n")
        f.write("1. Set as environment variable: export GMAIL_ENCRYPTION_KEY='your-key'\n")
        f.write("2. Enter when prompted during application execution\n")
    
    print(f"\nEncryption key saved to: {key_filename}")
    print("IMPORTANT: Store this key securely and delete the file after saving the key elsewhere.")
    
    return key_filename

def main():
    parser = argparse.ArgumentParser(description="Encrypt files for Gmail Attachment Downloader")
    parser.add_argument("--file", "-f", required=True, help="Path to file to encrypt")
    parser.add_argument("--output", "-o", help="Path for encrypted output file")
    parser.add_argument("--config", "-c", default="config.yaml", help="Path to config file")
    parser.add_argument("--key-dir", "-k", help="Directory to save the key file")
    
    args = parser.parse_args()
    
    # Determine output path
    input_file = args.file
    output_path = args.output or f"{input_file}.encrypted"
    
    # Encrypt the file
    result_path, key = CredentialEncryptor.encrypt_file(input_file, output_path)
    
    if result_path:
        # Update config file
        update_config(args.config, os.path.abspath(result_path))
        
        # Save key to file
        key_file = save_key_to_file(key, os.path.basename(input_file), args.key_dir)
        
        print("\nEncryption Summary:")
        print(f"Original file: {input_file}")
        print(f"Encrypted file: {result_path}")
        print(f"Key file: {key_file}")
        print("\nYou can also set the key as an environment variable:")
        print(f"export GMAIL_ENCRYPTION_KEY='{key}'")
        
if __name__ == "__main__":
    main()