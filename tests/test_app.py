import time
from unittest.mock import Mock, patch
from totp_app import TOTPApp

def test_init():
    """Test TOTPApp initialization."""
    app = TOTPApp()
    assert hasattr(app, 'storage')
    assert hasattr(app, 'console')
    assert app.running is True
    assert app.language == "en"

def test_clear_screen():
    """Test clear screen functionality."""
    app = TOTPApp()
    with patch.object(app.console, 'clear') as mock_clear:
        app.clear_screen()
        mock_clear.assert_called_once()

def test_print_centered():
    """Test centered text printing."""
    app = TOTPApp()
    with patch.object(app.console, 'print') as mock_print:
        app.print_centered("test")
        mock_print.assert_called_once()

def test_ask_centered():
    """Test centered prompt functionality."""
    app = TOTPApp()
    with patch('rich.prompt.Prompt.ask', return_value="test_input") as mock_ask:
        result = app.ask_centered("test prompt")
        assert result == "test_input"
        mock_ask.assert_called_once()

def test_wait_for_enter():
    """Test wait for enter functionality."""
    app = TOTPApp()
    with patch('builtins.input', return_value=""):
        app.wait_for_enter()  # Should not raise exception

@patch('totp_app.Console')
def test_print_banner(mock_console_class):
    """Test banner printing."""
    mock_console = Mock()
    mock_console_class.return_value = mock_console
    
    app = TOTPApp()
    app.print_banner()
    
    # Check that console.print was called with expected arguments
    assert mock_console.print.called

@patch('totp_app.open')
def test_load_language_success(mock_open):
    """Test successful language loading."""
    mock_file = Mock()
    mock_file.read.return_value = '{"test_key": "test_value"}'
    mock_open.return_value.__enter__.return_value = mock_file
    
    app = TOTPApp()
    app.load_language("en")
    
    assert app.translations == {"test_key": "test_value"}

def test_get_text():
    """Test text translation."""
    app = TOTPApp()
    app.translations = {"test_key": "translated_value"}
    
    result = app.get_text("test_key")
    assert result == "translated_value"
    
    # Test fallback behavior
    result = app.get_text("nonexistent")
    assert result == "nonexistent"

@patch('totp_app.Console')
def test_display_menu(mock_console_class):
    """Test menu display."""
    mock_console = Mock()
    mock_console_class.return_value = mock_console
    
    app = TOTPApp()
    app.display_menu()
    
    # Should have printed the menu and banner
    assert mock_console.print.call_count >= 2

@patch('totp_app.TOTPApp.ask_centered')
@patch('totp_app.TOTPEncryptedStorage.add_key')
def test_add_key_valid_input(mock_storage_add, mock_ask_centered):
    """Test adding key with valid input."""
    mock_ask_centered.side_effect = ["test_name", "test_secret"]
    mock_storage_add.return_value = True
    
    app = TOTPApp()
    app.add_key()
    
    # Verify methods were called
    assert mock_ask_centered.call_count == 2
    mock_storage_add.assert_called_once_with("test_name", "test_secret")

@patch('totp_app.TOTPApp.ask_centered')
@patch('totp_app.TOTPEncryptedStorage.add_key')
def test_add_key_empty_name(mock_storage_add, mock_ask_centered):
    """Test adding key with empty name."""
    mock_ask_centered.side_effect = ["", "test_secret"]
    
    app = TOTPApp()
    with patch('time.sleep') as mock_sleep:
        app.add_key()
        
        # Should show error and sleep
        assert mock_sleep.called
        mock_storage_add.assert_not_called()

@patch('totp_app.TOTPApp.ask_centered')
@patch('totp_app.TOTPEncryptedStorage.add_key')
def test_add_key_empty_secret(mock_storage_add, mock_ask_centered):
    """Test adding key with empty secret."""
    mock_ask_centered.side_effect = ["test_name", ""]
    
    app = TOTPApp()
    with patch('time.sleep') as mock_sleep:
        app.add_key()
        
        # Should show error and sleep
        assert mock_sleep.called
        mock_storage_add.assert_not_called()

@patch('totp_app.TOTPEncryptedStorage.get_keys')
def test_show_passwords_no_keys(mock_get_keys):
    """Test showing passwords when no keys exist."""
    mock_get_keys.return_value = []
    
    app = TOTPApp()
    with patch.object(app, 'clear_screen'), \
         patch.object(app, 'print_centered'), \
         patch('time.sleep') as mock_sleep:
        app.show_passwords()
        
        # Should sleep
        assert mock_sleep.called

def test_handle_language_selection():
    """Test language selection handling."""
    
    # Test with multiple valid options
    app = TOTPApp()
    with patch('totp_app.TOTPApp.ask_centered', side_effect=['1', '0']), \
         patch.object(app, 'clear_screen'), \
         patch.object(app, 'print_centered'), \
         patch('time.sleep'):
        # This should complete without errors
        app.handle_language_selection()

def test_run_menu():
    """Test main run loop with valid menu option."""
    
    app = TOTPApp()
    
    # Mock the necessary methods
    with patch.object(app, 'display_menu'), \
         patch('totp_app.TOTPApp.ask_centered', return_value="0"), \
         patch.object(app, 'print_centered'):
        # Should not raise exception
        app.run()