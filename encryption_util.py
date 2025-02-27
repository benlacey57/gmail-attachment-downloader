import base64
import os
import getpass
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger('system')

class CredentialEncryptor:
    """Handles encryption and decryption of credential files."""
    
    @staticmethod
    def derive_key_from_password(password):
        """Convert a password into a valid Fernet key."""
        # Ensure the password is exactly 32 bytes for Fernet
        password_bytes = password.encode('utf-8')
        password_padded = password_bytes.ljust(32)[:32]
        return base64.urlsafe_b64encode(password_padded)
    
    @staticmethod
    def generate_key():
        """Generate a random encryption key."""
        return Fernet.generate_key()
    
    @staticmethod
    def encrypt_file(file_path, output_path=None, key=None):
        """
        Encrypt a file using Fernet symmetric encryption.
        
        Args:
            file_path: Path to the file to encrypt
            output_path: Path where encrypted file will be saved (default: file_path + '.encrypted')
            key: Encryption key (if None, will prompt for password)
            
        Returns:
            tuple: (output_path, encryption_key)
        """
        # Determine output path
        if output_path is None:
            output_path = f"{file_path}.encrypted"
        
        # Get encryption key
        if key is None:
            password = getpass.getpass("Enter a password for encryption: ")
            key = CredentialEncryptor.derive_key_from_password(password)
        elif isinstance(key, str):
            key = key.encode()
        
        # Read the file
        try:
            with open(file_path, 'rb') as file:
                data = file.read()
        except FileNotFoundError:
            print(f"Error: File {file_path} not found.")
            return None, None
        
        # Encrypt the data
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data)
        
        # Write the encrypted data
        with open(output_path, 'wb') as file:
            file.write(encrypted_data)
        
        print(f"File encrypted successfully to {output_path}")
        print(f"IMPORTANT: Save this key in a secure location: {key.decode()}")
        print("You'll need this key to decrypt the file later.")
        
        return output_path, key.decode()
    
    @staticmethod
    def decrypt_file(encrypted_file, output_file=None, key=None):
        """
        Decrypt a file using Fernet symmetric encryption.
        
        Args:
            encrypted_file: Path to the encrypted file
            output_file: Path where decrypted file will be saved (default: temporary file)
            key: Decryption key (if None, will prompt for password)
            
        Returns:
            str: Path to the decrypted file
        """
        # Determine output path
        if output_file is None:
            output_file = f"temp_credentials_{os.getpid()}.json"
        
        # Get decryption key
        if key is None:
            # Try to get key from environment variable
            env_key = os.environ.get("GMAIL_ENCRYPTION_KEY")
            if env_key:
                key = env_key.encode()
            else:
                password = getpass.getpass("Enter password for decryption: ")
                key = CredentialEncryptor.derive_key_from_password(password)
        elif isinstance(key, str):
            key = key.encode()
        
        # Read the encrypted file
        try:
            with open(encrypted_file, 'rb') as file:
                encrypted_data = file.read()
        except FileNotFoundError:
            logger.error(f"Error: Encrypted file {encrypted_file} not found.")
            return None
        
        # Decrypt the data
        try:
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None
        
        # Write the decrypted data
        with open(output_file, 'wb') as file:
            file.write(decrypted_data)
        
        logger.info(f"File decrypted successfully to {output_file}")
        
        return output_file

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Encrypt or decrypt credential files")
    parser.add_argument("--encrypt", action="store_true", help="Encrypt a file")
    parser.add_argument("--decrypt", action="store_true", help="Decrypt a file")
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--key", help="Encryption/decryption key")
    
    args = parser.parse_args()
    
    if args.encrypt:
        CredentialEncryptor.encrypt_file(args.input, args.output, args.key)
    elif args.decrypt:
        CredentialEncryptor.decrypt_file(args.input, args.output, args.key)
    else:
        print("Please specify either --encrypt or --decrypt")
