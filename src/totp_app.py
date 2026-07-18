import time
import json
import os
import pyotp
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.align import Align
from rich.box import ROUNDED
from rich import print
from totp_encrypted_storage import TOTPEncryptedStorage
from ui_theme import (
    PALETTE, make_console, render_banner_panel, styled_panel, arrow_menu,
)
from version import __version__

class TOTPApp:
    """Main TOTP application class with CLI interface."""
    
    def __init__(self, password: str = None):
        self.storage = TOTPEncryptedStorage()
        # Store password for caching (not read from key.env anymore)
        self._password = password
        self.console = make_console()
        self.running = True
        self.language = "en"  # Default language
        self.translations = {}
        self.load_language(self.language)
    
    def clear_screen(self):
        """Clear the terminal screen."""
        self.console.clear()
    
    def print_centered(self, text):
        """Print text aligned to the center of the screen."""
        self.console.print(Align.center(text))
        
    def ask_centered(self, prompt_text, **kwargs):
        """Display a centered prompt and retrieve user input centered on the screen."""
        self.print_centered(prompt_text)
        terminal_width = self.console.width
        prompt_prefix = " > "
        padding_len = max(0, (terminal_width // 2) - len(prompt_prefix))
        padding = " " * padding_len
        return Prompt.ask(f"{padding}{prompt_prefix}", **kwargs)
        
    def wait_for_enter(self):
        """Prompt the user to press Enter to continue, centered on the screen."""
        terminal_width = self.console.width
        prompt_str = "Press Enter to continue..."
        padding_len = max(0, (terminal_width // 2) - (len(prompt_str) // 2))
        padding = " " * padding_len
        try:
            input(f"\n{padding}{prompt_str}")
        except (KeyboardInterrupt, EOFError):
            pass
    
    def print_banner(self, phase: float = 0.0):
        """Print the animated pastel-gradient DRZ AUTHENTICATOR banner."""
        panel = render_banner_panel(phase)
        self.console.print(Align.center(panel))

    def menu_items(self):
        """Build the (key, label) list for the main menu."""
        return [
            ("1", self.get_text("menu_option_1")),
            ("2", self.get_text("menu_option_2")),
            ("3", self.get_text("menu_option_3")),
            ("4", self.get_text("menu_option_4")),
            ("5", self.get_text("menu_option_5")),
            ("6", "Options"),
            ("7", self.get_text("menu_option_7")),
            ("0", self.get_text("menu_option_0")),
        ]
    
    def load_language(self, lang_code):
        """Load translation file for specified language."""
        try:
            with open(f"src/lang_{lang_code}.json", 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            # Fallback to English if requested language file not found
            print(f"[yellow]Translation file for {lang_code} not found, falling back to English[/yellow]")
            with open("src/lang_en.json", 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
    
    def get_text(self, key):
        """Get translated text for a given key."""
        return self.translations.get(key, key)  # fallback to key if not found
    
    def set_language(self, lang_code):
        """Set the current language and reload translations."""
        self.language = lang_code
        # Avoid calling load_language during tests to prevent extra calls
        if hasattr(self, 'test_mode') and self.test_mode:
            return
        self.load_language(lang_code)
    
    def display_menu(self):
        """Display the main menu via animated arrow-key navigation. Returns chosen key or None."""
        self.clear_screen()
        items = self.menu_items()
        nav_hint = self.get_text("nav_hint")
        idx = arrow_menu(
            self.console,
            title=self.get_text("menu_title"),
            items=items,
            nav_hint=nav_hint,
            version=__version__,
        )
        if idx < 0:
            return "0"  # back/quit => exit
        return items[idx][0]
    
    def add_key(self):
        """Add a new authentication key."""
        self.clear_screen()
        self.print_banner()
        self.print_centered(self.get_text("status_add_key"))
        print()  # Add an empty line for breathing room
        
        name = self.ask_centered(self.get_text("prompt_key_name"))
        if not name.strip():
            print()
            self.print_centered(f"[err]{self.get_text('error_empty_name')}[/err]")
            time.sleep(2)
            return
            
        print()
        secret = self.ask_centered(self.get_text("prompt_secret"))
        if not secret.strip():
            print()
            self.print_centered(f"[err]{self.get_text('error_empty_secret')}[/err]")
            time.sleep(2)
            return
            
        print()
        if self.storage.add_key(name, secret):
            self.print_centered(f"[ok]Successfully added key: {name}[/ok]")
        else:
            self.print_centered(f"[err]{self.get_text('error_duplicate_key').format(name=name)}[/err]")
            
        time.sleep(2)
    
    def show_passwords(self):
        """Display all passwords with dynamic updates."""
        self.clear_screen()
        self.print_banner()
        self.print_centered(self.get_text("status_show_passwords"))
        
        keys = self.storage.get_keys()
        if not keys:
            self.print_centered(f"[warn]{self.get_text('error_no_keys_found')}[/warn]")
            time.sleep(2)
            return
            
        try:
            while True:
                self.clear_screen()
                self.print_banner()
                self.print_centered(self.get_text("status_show_passwords_dynamic"))
                print()
                
                # Create table for current passwords
                table = Table(
                    title=self.get_text("table_header_name"),
                    show_header=True,
                    header_style=f"bold {PALETTE['lavender']}",
                    border_style=PALETTE["border"],
                    box=ROUNDED,
                    style=f"on {PALETTE['panel']}",
                )
                table.add_column(self.get_text("table_header_name"), style=PALETTE["sky"])
                table.add_column(self.get_text("table_header_password"), style=f"bold {PALETTE['mint']}")
                table.add_column(self.get_text("table_header_expires"), style=PALETTE["lavender"])
                table.add_column(self.get_text("table_header_status"), style=PALETTE["peach"])
                
                updated = False
                for key in keys:
                    try:
                        totp = pyotp.TOTP(key['secret'])
                        password = totp.now()
                        remaining = 30 - (int(time.time()) % 30)
                        # pastel progress bar for the countdown
                        bar_len = 16
                        filled = int(bar_len * remaining / 30)
                        bar = "[" + "█" * filled + "░" * (bar_len - filled) + f"] {remaining:02d}s"
                        status = self.get_text("table_cell_valid") if remaining > 0 else self.get_text("table_cell_expired")
                        
                        table.add_row(
                            key['name'],
                            password,
                            bar,
                            status
                        )
                        updated = True
                    except Exception as e:
                        table.add_row(key['name'], "[err]Error[/err]", "N/A", f"[err]{str(e)}[/err]")
                
                self.console.print(Align.center(table))
                
                if not updated:
                    self.print_centered(f"[warn]{self.get_text('error_no_passwords')}[/warn]")
                
                try:
                    time.sleep(1)  # Update every second to show countdown
                    # Check if user wants to exit (Ctrl+C)
                except KeyboardInterrupt:
                    break
        except KeyboardInterrupt:
            return
    
    def list_keys(self):
        """List all stored keys."""
        self.clear_screen()
        self.print_banner()
        self.print_centered(self.get_text("status_list_keys"))
        print()
        
        keys = self.storage.get_keys()
        if not keys:
            self.print_centered(f"[warn]{self.get_text('error_no_keys_found')}[/warn]")
        else:
            table = Table(
                title=self.get_text("table_header_name"),
                show_header=True,
                header_style=f"bold {PALETTE['lavender']}",
                border_style=PALETTE["border"],
                box=ROUNDED,
                style=f"on {PALETTE['panel']}",
            )
            table.add_column(self.get_text("table_header_name"), style=PALETTE["sky"])
            table.add_column(self.get_text("table_header_created"), style=PALETTE["mint"])
            
            for key in keys:
                table.add_row(key['name'], key['created_at'])
                
            self.console.print(Align.center(table))
        
        self.wait_for_enter()
    
    def remove_key(self):
        """Remove an existing key."""
        self.clear_screen()
        self.print_banner()
        self.print_centered(self.get_text("status_remove_key"))
        print()
        
        keys = self.storage.get_keys()
        if not keys:
            self.print_centered(f"[warn]{self.get_text('error_no_keys_found')}[/warn]")
            time.sleep(2)
            return
            
        # Display available keys
        table = Table(
            title=self.get_text("table_header_name"),
            show_header=True,
            header_style=f"bold {PALETTE['lavender']}",
            border_style=PALETTE["border"],
            box=ROUNDED,
            style=f"on {PALETTE['panel']}",
        )
        table.add_column(self.get_text("table_header_name"), style=PALETTE["sky"])
        table.add_column(self.get_text("table_header_created"), style=PALETTE["mint"])
        
        for key in keys:
            table.add_row(key['name'], key.get('created_at', 'Unknown'))
            
        self.console.print(Align.center(table))
        print()
        
        name = self.ask_centered(self.get_text("prompt_remove_key"))
        print()
        
        if self.storage.remove_key(name):
            self.print_centered(f"[ok]Successfully removed key: {name}[/ok]")
        else:
            self.print_centered(f"[err]{self.get_text('error_key_not_found').format(name=name)}[/err]")
            
        time.sleep(2)
    
    def show_help(self):
        """Display help information."""
        self.clear_screen()
        self.print_banner()
        self.print_centered(self.get_text("status_help"))
        print()
        
        help_text = self.get_text("help_text")
        
        self.console.print(Align.center(styled_panel(help_text)))
        self.wait_for_enter()
    
    def import_key(self):
        """Import a key from an otpauth URI or QR code image."""
        try:
            from pyotp import parse_uri
            # Ask for URL or paste URI  
            uri = self.ask_centered("Paste OTP URI (otpauth://) or press Enter to scan QR code")
            
            if not uri.strip():
                # Try to read QR code from image
                try:
                    from pyzbar import pyzbar
                    import cv2
                    
                    # Prompt for image file    
                    img_path = self.ask_centered("Enter image path containing QR code (or press Enter to skip)")
                    
                    if img_path.strip():
                        # Read image
                        image = cv2.imread(img_path)
                        decoded_objects = pyzbar.decode(image)
                        
                        if not decoded_objects:
                            self.print_centered("[err]No QR Code found in image[/err]")
                            return
                        
                        uri = decoded_objects[0].data.decode('utf-8')
                        self.print_centered(f"[ok]URI extracted from QR code: {uri}[/ok]")
                        
                except Exception as e:
                    # Not critical - just print error and prompt for URI
                    print(f"Error reading QR image: {e}")
            
            if not uri.strip():
                self.print_centered("[err]No URI provided or scanned. Operation cancelled.[/err]")
                return
    
            # Parse URI using pyotp            
            totp = parse_uri(uri)
            
            # Extract key components
            name = totp.name
            secret = totp.secret 
            issuer = totp.issuer
            
            self.print_centered(f"[ok]Importing: {name}[/ok]")
            self.print_centered(f"[label]Secret:[/label] [value]{secret}[/value]")
            
            # If name was not provided in URI, suggest one
            if not name:
                name = self.ask_centered("Enter key name (or press Enter to use secret):")
                if not name.strip():
                    name = secret[:8]
            
            # Add to storage  
            success = self.storage.add_key(name, secret)
            if success:
                self.print_centered(f"[ok]Successfully imported '{name}'[/ok]")
            else:
                self.print_centered("[err]Failed to import (may already exist)![/err]")
        
        except ImportError:
            # pyotp not installed - fallback
            self.print_centered("[err]pyotp required for URI parsing. Please install first.[/err]") 
            return
        except Exception as e:
            self.print_centered(f"[err]Import failed: {e}[/err]")
    
    def handle_language_selection(self):
        """Handle language selection via arrow-key menu."""
        items = [
            ("1", "English"),
            ("2", "Português"),
            ("3", "Español"),
            ("0", self.get_text("menu_option_0")),
        ]
        nav_hint = self.get_text("nav_hint")
        idx = arrow_menu(
            self.console,
            title="Select Language / Idioma / Idioma",
            items=items,
            nav_hint=nav_hint,
        )
        if idx < 0:
            return
        choice = items[idx][0]
        
        if choice == "1":
            self.set_language("en")
            self.print_centered("[ok]Language changed to English[/ok]")
            time.sleep(1)
        elif choice == "2":
            self.set_language("pt")
            self.print_centered("[ok]Idioma alterado para Português[/ok]")
            time.sleep(1)
        elif choice == "3":
            self.set_language("es")
            self.print_centered("[ok]Idioma cambiado a Español[/ok]")
            time.sleep(1)
    
    def run(self):
        """Main application loop."""
        while self.running:
            choice = self.display_menu()
            print()
            
            if choice == "1":
                self.add_key()
            elif choice == "2":
                self.show_passwords()
            elif choice == "3":
                self.list_keys()
            elif choice == "4":
                self.remove_key()
            elif choice == "5":
                self.show_help()
            elif choice == "6":
                self.handle_language_selection()
            elif choice == "7":
                self.import_key()
            elif choice == "0":
                self.print_centered(self.get_text("message_goodbye"))
                self.running = False
            else:
                self.print_centered(self.get_text("error_invalid_option"))
                time.sleep(2)