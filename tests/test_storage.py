import json
import os
import tempfile
from unittest.mock import patch
from totp_storage import TOTPStorage

def test_init_creates_file():
    """Test that TOTPStorage initializes and creates file if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "test_keys.json")
        storage = TOTPStorage(filename)
        
        # Check file was created
        assert os.path.exists(filename)
        
        # Check file contains empty list
        with open(filename, 'r') as f:
            data = json.load(f)
            assert data == []

def test_load_keys_empty():
    """Test loading keys from empty file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "empty.json")
        with open(filename, 'w') as f:
            json.dump([], f)
        
        storage = TOTPStorage(filename)
        keys = storage.load_keys()
        assert keys == []

def test_load_keys_with_data():
    """Test loading keys from file with data."""
    test_data = [
        {"name": "test1", "secret": "SECRET1", "created_at": "2023-01-01T00:00:00"},
        {"name": "test2", "secret": "SECRET2", "created_at": "2023-01-02T00:00:00"}
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "data.json")
        with open(filename, 'w') as f:
            json.dump(test_data, f)
        
        storage = TOTPStorage(filename)
        keys = storage.load_keys()
        assert keys == test_data

def test_save_keys_success():
    """Test saving keys successfully."""
    test_data = [{"name": "test", "secret": "SECRET", "created_at": "2023-01-01T00:00:00"}]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "save_test.json")
        storage = TOTPStorage(filename)
        
        success = storage.save_keys(test_data)
        assert success is True
        
        # Verify content
        with open(filename, 'r') as f:
            data = json.load(f)
            assert data == test_data

def test_save_keys_failure():
    """Test saving keys fails gracefully."""
    # This test mocks the file write operation to simulate failure
    with patch('builtins.open', side_effect=IOError("Mocked permission error")):
        storage = TOTPStorage("/tmp/test_keys.json")
        success = storage.save_keys([{"test": "data"}])
        assert success is False

def test_add_key_new():
    """Test adding a new key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "add_test.json")
        storage = TOTPStorage(filename)
        
        # Add key
        result = storage.add_key("test_key", "SECRET123")
        assert result is True
        
        # Verify key was added
        keys = storage.load_keys()
        assert len(keys) == 1
        assert keys[0]['name'] == "test_key"
        assert keys[0]['secret'] == "SECRET123"

def test_add_key_duplicate():
    """Test adding duplicate key fails."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "duplicate_test.json")
        storage = TOTPStorage(filename)
        
        # Add first key
        storage.add_key("test_key", "SECRET123")
        
        # Try to add duplicate
        result = storage.add_key("test_key", "SECRET456")
        assert result is False
        
        # Verify only one key exists
        keys = storage.load_keys()
        assert len(keys) == 1

def test_remove_key_existing():
    """Test removing existing key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "remove_test.json")
        storage = TOTPStorage(filename)
        
        # Add keys
        storage.add_key("key1", "SECRET1")
        storage.add_key("key2", "SECRET2")
        
        # Remove one
        result = storage.remove_key("key1")
        assert result is True
        
        # Verify key was removed
        keys = storage.load_keys()
        assert len(keys) == 1
        assert keys[0]['name'] == "key2"

def test_remove_key_nonexistent():
    """Test removing non-existent key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "nonexist_test.json")
        storage = TOTPStorage(filename)
        
        result = storage.remove_key("nonexistent")
        assert result is False
        
        # Verify no keys
        keys = storage.load_keys()
        assert len(keys) == 0

def test_get_keys():
    """Test getting all keys."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "get_test.json")
        storage = TOTPStorage(filename)
        
        # Add some keys
        storage.add_key("key1", "SECRET1")
        storage.add_key("key2", "SECRET2")
        
        keys = storage.get_keys()
        assert len(keys) == 2
        assert keys[0]['name'] == "key1"
        assert keys[1]['name'] == "key2"
