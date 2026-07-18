# DRZAuthenticator Language Support Documentation

## Overview

The DRZAuthenticator application includes full internationalization support with built-in language switching capabilities. The application currently supports English (en), Portuguese (pt), and Spanish (es) languages.

## Installation

The language support is already included in the application's source code. No additional installation steps are required beyond the standard setup:

1. Clone or download the repository
2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python src/main.py
   ```

## Usage Guide

### Switching Languages

To switch languages within the application:

1. Navigate to the main menu
2. Select option `6` for "Options"
3. Choose from the language selection screen:
   - Option `1`: English
   - Option `2`: Português
   - Option `3`: Español
   - Option `0`: Return to main menu

### Language Persistence

The application remembers your language preference throughout the session. The currently selected language will be used for all subsequent user interface elements, prompts, and messages until you change it again.

## Technical Details

### Implementation Approach

The language support is implemented using a translation key-value system:

1. **Translation Files**: Each supported language has its own JSON file (`lang_en.json`, `lang_pt.json`, `lang_es.json`)
2. **Dynamic Loading**: Language files are loaded dynamically when the application initializes or when changing languages
3. **Fallback System**: If a requested language file is not found, the system falls back to English

### How It Works

1. **Initialization**:
   - The app starts with default language `en`
   - Translation keys are loaded from appropriate JSON files

2. **String Retrieval**:
   ```python
   def get_text(self, key):
       """Get translated text for a given key."""
       return self.translations.get(key, key)  # fallback to key if not found
   ```

3. **Language Switching**:
   - The `set_language()` method handles language changes
   - Translation files are reloaded with `load_language()`
   - All UI elements update automatically to the new language

### Supported Languages

| Language   | Code | Notes |
|------------|------|-------|
| English    | en   | Default language |
| Portuguese | pt   | Brazilian Portuguese |
| Spanish    | es   | Castilian Spanish |

### Adding New Languages

To add a new language:

1. Create a new translation file following the same format as existing files:
   ```bash
   cp src/lang_en.json src/lang_[new_code].json
   ```
2. Translate all key-value pairs in the new file
3. Modify the `handle_language_selection()` method in `totp_app.py` to include the new language option

## Supported UI Elements

All user interface elements are now translatable:

- Main menu titles and options
- Input prompts
- Status messages
- Error messages
- Table headers
- Help text
- Dialog boxes

## Performance Considerations

- Language files are loaded once at initialization
- Translation lookups are fast O(1) operations
- No performance impact during runtime operation
- Fallback system ensures no crashes if translations are missing

## Troubleshooting

### Language Not Working

If language changes aren't taking effect:
1. Verify that the translation files exist in `src/` directory
2. Check that JSON files are properly formatted
3. Ensure the language code matches the filename (e.g., `lang_es.json` for Spanish)

### Missing Translations

The system provides a fallback to English strings when translations are missing, ensuring the application remains usable even with incomplete translations.

## Example Translation File Structure

```json
{
    "menu_title": "TOTP Application Menu",
    "menu_option_1": "Add New Authentication Key",
    "prompt_key_name": "Enter key name",
    "error_empty_name": "Key name cannot be empty!",
    "help_text": "Help information for the application..."
}
```

## File Locations

- Main application: `src/totp_app.py`
- Translation files: `src/lang_en.json`, `src/lang_pt.json`, `src/lang_es.json`
- Entry point: `src/main.py`