import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.backends import default_backend
import base64
import json

def derive_key_from_password(password: str, salt: bytes) -> bytes:
    """
    Derive a key from password using Argon2.
    
    Args:
        password (str): The password to derive key from
        salt (bytes): Salt value for key derivation
        
    Returns:
        bytes: Derived key for encryption
    """
    # Use the exact signature supported by installed cryptography version
    # This is a simplified approach compatible with older versions
    kdf = Argon2id(
        salt=salt,
        length=32,
        iterations=3,
        lanes=1,
        memory_cost=102400
    )
    return kdf.derive(password.encode())

def encrypt_data(data: str, password: str) -> bytes:
    """
    Encrypt data using password.
    
    Args:
        data (str): Data to encrypt
        password (str): Password for encryption
        
    Returns:
        bytes: Encrypted data with salt prepended
    """
    # Generate random salt
    salt = os.urandom(16)
    
    # Derive key from password
    key = derive_key_from_password(password, salt)
    
    # Create Fernet key from derived key
    fernet_key = base64.urlsafe_b64encode(key)
    fernet = Fernet(fernet_key)
    
    # Encrypt data
    encrypted_data = fernet.encrypt(data.encode())
    
    # Prepend salt to encrypted data
    return salt + encrypted_data

def decrypt_data(encrypted_data: bytes, password: str) -> str:
    """
    Decrypt data using password.
    
    Args:
        encrypted_data (bytes): Encrypted data with prepended salt
        password (str): Password for decryption
        
    Returns:
        str: Decrypted data
    """
    # Extract salt from beginning
    salt = encrypted_data[:16]
    encrypted_content = encrypted_data[16:]
    
    # Derive key from password and salt
    key = derive_key_from_password(password, salt)
    
    # Create Fernet key from derived key
    fernet_key = base64.urlsafe_b64encode(key)
    fernet = Fernet(fernet_key)
    
    # Decrypt data
    decrypted_data = fernet.decrypt(encrypted_content)
    
    return decrypted_data.decode()

def load_encrypted_keys(filename: str, password: str) -> list:
    """
    Load encrypted keys from file.
    
    Args:
        filename (str): Path to the encrypted keys file
        password (str): Password for decryption
        
    Returns:
        list: List of key objects
    """
    try:
        if not os.path.exists(filename):
            return []
        
        with open(filename, 'rb') as f:
            encrypted_data = f.read()
            
        decrypted_data = decrypt_data(encrypted_data, password)
        return json.loads(decrypted_data)
    
    except Exception as e:
        raise ValueError(f"Failed to load encrypted keys: {str(e)}")

def save_encrypted_keys(filename: str, keys: list, password: str) -> bool:
    """
    Save keys to file encrypted with password.
    
    Args:
        filename (str): Path to the keys file
        keys (list): List of key objects to save
        password (str): Password for encryption
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Convert keys to JSON string
        json_data = json.dumps(keys, indent=2)
        
        # Encrypt the data
        encrypted_data = encrypt_data(json_data, password)
        
        # Write to file
        with open(filename, 'wb') as f:
            f.write(encrypted_data)
            
        return True
    
    except Exception as e:
        raise ValueError(f"Failed to save encrypted keys: {str(e)}")

def encrypt_data(data: str, password: str) -> bytes:
    """
    Encrypt data using password.
    
    Args:
        data (str): Data to encrypt
        password (str): Password for encryption
        
    Returns:
        bytes: Encrypted data with salt prepended
    """
    # Generate random salt
    salt = os.urandom(16)
    
    # Derive key from password
    key = derive_key_from_password(password, salt)
    
    # Create Fernet key from derived key
    fernet_key = base64.urlsafe_b64encode(key)
    fernet = Fernet(fernet_key)
    
    # Encrypt data
    encrypted_data = fernet.encrypt(data.encode())
    
    # Prepend salt to encrypted data
    return salt + encrypted_data

def decrypt_data(encrypted_data: bytes, password: str) -> str:
    """
    Decrypt data using password.
    
    Args:
        encrypted_data (bytes): Encrypted data with prepended salt
        password (str): Password for decryption
        
    Returns:
        str: Decrypted data
    """
    # Extract salt from beginning
    salt = encrypted_data[:16]
    encrypted_content = encrypted_data[16:]
    
    # Derive key from password and salt
    key = derive_key_from_password(password, salt)
    
    # Create Fernet key from derived key
    fernet_key = base64.urlsafe_b64encode(key)
    fernet = Fernet(fernet_key)
    
    # Decrypt data
    decrypted_data = fernet.decrypt(encrypted_content)
    
    return decrypted_data.decode()

def load_encrypted_keys(filename: str, password: str) -> list:
    """
    Load encrypted keys from file.
    
    Args:
        filename (str): Path to the encrypted keys file
        password (str): Password for decryption
        
    Returns:
        list: List of key objects
    """
    try:
        if not os.path.exists(filename):
            return []
        
        with open(filename, 'rb') as f:
            encrypted_data = f.read()
            
        decrypted_data = decrypt_data(encrypted_data, password)
        return json.loads(decrypted_data)
    
    except Exception as e:
        raise ValueError(f"Failed to load encrypted keys: {str(e)}")

def save_encrypted_keys(filename: str, keys: list, password: str) -> bool:
    """
    Save keys to file encrypted with password.
    
    Args:
        filename (str): Path to the keys file
        keys (list): List of key objects to save
        password (str): Password for encryption
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Convert keys to JSON string
        json_data = json.dumps(keys, indent=2)
        
        # Encrypt the data
        encrypted_data = encrypt_data(json_data, password)
        
        # Write to file
        with open(filename, 'wb') as f:
            f.write(encrypted_data)
            
        return True
    
    except Exception as e:
        raise ValueError(f"Failed to save encrypted keys: {str(e)}")
