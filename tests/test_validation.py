import pytest
from totp_encrypted_storage import TOTPEncryptedStorage

def test_validate_secret_valid():
    """Test that valid base32 secrets are accepted."""
    storage = TOTPEncryptedStorage()
    
    # Valid TOTP secrets (base32 encoded)
    valid_secrets = [
        "JBSWY3DPEHPK3PXP",  # Google Authenticator default
        "AAAAAA",            # Simple valid secret  
    ]
    
    for secret in valid_secrets:
        assert storage.validate_secret(secret) == True

def test_validate_secret_invalid():
    """Test that invalid secrets are rejected."""
    storage = TOTPEncryptedStorage()
    
    # These should be false
    invalid_secrets = [
        "",                  # Empty
        "ABCD!",             # Invalid character  
    ]
    
    for secret in invalid_secrets:
        assert storage.validate_secret(secret) == False

def test_validate_secret_whitespace():
    """Test that whitespace is handled correctly."""
    storage = TOTPEncryptedStorage()
    
    # Valid with spaces - should strip and validate
    valid_with_spaces = [
        "JBS WY3DPEHPK3PXP",
        " ABCDEFGHIJKLMNOPQRSTUVWXYZ234567 ",
    ]
    
    for secret in valid_with_spaces:
        assert storage.validate_secret(secret) == True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])