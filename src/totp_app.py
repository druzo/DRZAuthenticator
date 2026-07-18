import time
import json
import os
import pyotp
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import print
from totp_storage import TOTPStorage

class TOTPApp:
    """Main TOTP application class with CLI interface."""
    
    def __init__(self):
        self.storage = TOTPStorage()
        self.console = Console()
        self.running = True
        self.language = "en"  # Default language
        self.translations = {}
        self.load_language(self.language)
    
    def clear_screen(self):
        """Clear the terminal screen."""
        self.console.clear()
    
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
        self.load_language(lang_code)
    
    def display_menu(self):
        """Display the main menu."""
        self.clear_screen()
        table = Table(title=self.get_text("menu_title"), show_header=False)
        table.add_column("Option", style="cyan")
        table.add_column("Description", style="magenta")
        
        table.add_row("1", self.get_text("menu_option_1"))
        table.add_row("2", self.get_text("menu_option_2"))
        table.add_row("3", self.get_text("menu_option_3"))
        table.add_row("4", self.get_text("menu_option_4"))
        table.add_row("5", self.get_text("menu_option_5"))
        table.add_row("6", "Options")
        table.add_row("0", self.get_text("menu_option_0"))
        
        self.console.print(Panel(table, title="Main Menu"))
    
    def add_key(self):
        """Add a new authentication key."""
        self.clear_screen()
        print(self.get_text("status_add_key"))
        
        name = Prompt.ask(self.get_text("prompt_key_name"))
        if not name.strip():
            print(f"[red]{self.get_text('error_empty_name')}[/red]")
            time.sleep(2)
            return
            
        secret = Prompt.ask(self.get_text("prompt_secret"))
        if not secret.strip():
            print(f"[red]{self.get_text('error_empty_secret')}[/red]")
            time.sleep(2)
            return
            
        if self.storage.add_key(name, secret):
            print(f"[green]Successfully added key: {name}[/green]")
        else:
            print(f"[red]{self.get_text('error_duplicate_key').format(name=name)}[/red]")
            
        time.sleep(2)
    
    def show_passwords(self):
        """Display all passwords with dynamic updates."""
        self.clear_screen()
        print(self.get_text("status_show_passwords"))
        
        keys = self.storage.get_keys()
        if not keys:
            print(f"[yellow]{self.get_text('error_no_keys_found')}[/yellow]")
            time.sleep(2)
            return
            
        while True:
            self.clear_screen()
            print(self.get_text("status_show_passwords_dynamic"))
            
            # Create table for current passwords
            table = Table(title=self.get_text("table_header_name"), show_header=True, header_style="bold magenta")
            table.add_column(self.get_text("table_header_name"), style="cyan")
            table.add_column(self.get_text("table_header_password"), style="green")
            table.add_column(self.get_text("table_header_expires"), style="yellow")
            table.add_column(self.get_text("table_header_status"), style="blue")
            
            updated = False
            for key in keys:
                try:
                    totp = pyotp.TOTP(key['secret'])
                    password = totp.now()
                    remaining = 30 - (int(time.time()) % 30)
                    status = self.get_text("table_cell_valid") if remaining > 0 else self.get_text("table_cell_expired")
                    
                    table.add_row(
                        key['name'],
                        password,
                        f"{remaining}s",
                        status
                    )
                    updated = True
                except Exception as e:
                    table.add_row(key['name'], "[red]Error[/red]", "N/A", f"[red]{str(e)}[/red]")
            
            self.console.print(table)
            
            if not updated:
                print(f"[yellow]{self.get_text('error_no_passwords')}[/yellow]")
            
            try:
                time.sleep(1)  # Update every second to show countdown
                # Check if user wants to exit (Ctrl+C)
            except KeyboardInterrupt:
                break
    
    def list_keys(self):
        """List all stored keys."""
        self.clear_screen()
        print(self.get_text("status_list_keys"))
        
        keys = self.storage.get_keys()
        if not keys:
            print(f"[yellow]{self.get_text('error_no_keys_found')}[/yellow]")
        else:
            table = Table(title=self.get_text("table_header_name"), show_header=True, header_style="bold magenta")
            table.add_column(self.get_text("table_header_name"), style="cyan")
            table.add_column(self.get_text("table_header_created"), style="green")
            
            for key in keys:
                table.add_row(key['name'], key['created_at'])
                
            self.console.print(table)
        
        input("\nPress Enter to continue...")
    
    def remove_key(self):
        """Remove an existing key."""
        self.clear_screen()
        print(self.get_text("status_remove_key"))
        
        keys = self.storage.get_keys()
        if not keys:
            print(f"[yellow]{self.get_text('error_no_keys_found')}[/yellow]")
            time.sleep(2)
            return
            
        # Display available keys
        table = Table(title=self.get_text("table_header_name"), show_header=True, header_style="bold magenta")
        table.add_column(self.get_text("table_header_name"), style="cyan")
        table.add_column(self.get_text("table_header_created"), style="green")
        
        for i, key in enumerate(keys):
            table.add_row(key['name'], key['created_at'])
            
        self.console.print(table)
        
        name = Prompt.ask(self.get_text("prompt_remove_key"))
        
        if self.storage.remove_key(name):
            print(f"[green]Successfully removed key: {name}[/green]")
        else:
            print(f"[red]{self.get_text('error_key_not_found').format(name=name)}[/red]")
            
        time.sleep(2)
    
    def show_help(self):
        """Display help information."""
        self.clear_screen()
        print(self.get_text("status_help"))
        
        help_text = self.get_text("help_text")
        
        self.console.print(Panel(help_text))
        input("\nPress Enter to continue...")
    
    def handle_language_selection(self):
        """Handle language selection."""
        while True:
            self.clear_screen()
            table = Table(title="Select Language", show_header=False)
            table.add_column("Option", style="cyan")
            table.add_column("Language", style="magenta")
            
            table.add_row("1", "English")
            table.add_row("2", "Português")
            table.add_row("3", "Español")
            table.add_row("0", "Back to Main Menu")
            
            self.console.print(Panel(table, title="Language Selection"))
            choice = Prompt.ask("Select a language", default="0")
            
            if choice == "1":
                self.set_language("en")
                print("[green]Language changed to English[/green]")
                time.sleep(1)
                break
            elif choice == "2":
                self.set_language("pt")
                print("[green]Idioma alterado para Português[/green]")
                time.sleep(1)
                break
            elif choice == "3":
                self.set_language("es")
                print("[green]Idioma cambiado a Español[/green]")
                time.sleep(1)
                break
            elif choice == "0":
                break
            else:
                print("[red]Invalid option. Please try again.[/red]")
                time.sleep(2)
    
    def run(self):
        """Main application loop."""
        while self.running:
            self.display_menu()
            choice = Prompt.ask(self.get_text("prompt_select_option"), default="0")
            
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
            elif choice == "0":
                print(self.get_text("message_goodbye"))
                self.running = False
            else:
                print(self.get_text("error_invalid_option"))
                time.sleep(2)