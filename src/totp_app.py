import time
import json
import os
import pyotp
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.align import Align
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
    
    def print_banner(self):
        """Print a colorful big emphasized DRZ Authenticator banner."""
        banner_lines = [
            r"                      [bold red] ___   [/][bold orange3] ____  [/][bold yellow] _____ [/]",
            r"                      [bold red]|  _ \ [/][bold orange3]|  _ \ [/][bold yellow]|__  / [/]",
            r"                      [bold red]| | | |[/][bold orange3] |_) | [/][bold yellow]/ /   [/]",
            r"                      [bold red]| |_| |[/][bold orange3]  _ <  [/][bold yellow]/ /_   [/]",
            r"                      [bold red]|____/ [/][bold orange3]|_| \_ [/][bold yellow]\____| [/]",
            r"",
            r"[bold green3]    _         _   _    [/][bold cyan1]          _   _     [/][bold purple]         _            [/]",
            r"[bold green3]   / \  _   _| |_| |__ [/][bold cyan1]  ___ _ _| |_(_) ___[/][bold purple]  __ _| |_ ___  _ __  [/]",
            r"[bold green3]  / _ \| | | | __| '_ \ [/][bold cyan1] / _ \ '_| __| |/ __[/][bold purple]|/ _` | __/ _ \| '__| [/]",
            r"[bold green3] / ___ \ |_| | |_| | |[/][bold cyan1]  __/ | | |_| | (__[/][bold purple]| (_| | || (_) | |    [/]",
            r"[bold green3]/_/   \_\__,_|\__|_| |_[/][bold cyan1]|\___|_|  \__|_|\___[/][bold purple]|\__,_|\__\___/|_|    [/]"
        ]
        banner_text = "\n".join(banner_lines)
        self.console.print(Align.center(Panel(banner_text, style="bold magenta", border_style="cyan", padding=(1, 2), expand=False)))
    
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
        self.print_banner()
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
        
        self.console.print(Align.center(Panel(table, title="Main Menu", expand=False)))
    
    def add_key(self):
        """Add a new authentication key."""
        self.clear_screen()
        self.print_centered(self.get_text("status_add_key"))
        print()  # Add an empty line for breathing room
        
        name = self.ask_centered(self.get_text("prompt_key_name"))
        if not name.strip():
            print()
            self.print_centered(f"[red]{self.get_text('error_empty_name')}[/red]")
            time.sleep(2)
            return
            
        print()
        secret = self.ask_centered(self.get_text("prompt_secret"))
        if not secret.strip():
            print()
            self.print_centered(f"[red]{self.get_text('error_empty_secret')}[/red]")
            time.sleep(2)
            return
            
        print()
        if self.storage.add_key(name, secret):
            self.print_centered(f"[green]Successfully added key: {name}[/green]")
        else:
            self.print_centered(f"[red]{self.get_text('error_duplicate_key').format(name=name)}[/red]")
            
        time.sleep(2)
    
    def show_passwords(self):
        """Display all passwords with dynamic updates."""
        self.clear_screen()
        self.print_centered(self.get_text("status_show_passwords"))
        
        keys = self.storage.get_keys()
        if not keys:
            self.print_centered(f"[yellow]{self.get_text('error_no_keys_found')}[/yellow]")
            time.sleep(2)
            return
            
        while True:
            self.clear_screen()
            self.print_centered(self.get_text("status_show_passwords_dynamic"))
            print()
            
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
            
            self.console.print(Align.center(table))
            
            if not updated:
                self.print_centered(f"[yellow]{self.get_text('error_no_passwords')}[/yellow]")
            
            try:
                time.sleep(1)  # Update every second to show countdown
                # Check if user wants to exit (Ctrl+C)
            except KeyboardInterrupt:
                break
    
    def list_keys(self):
        """List all stored keys."""
        self.clear_screen()
        self.print_centered(self.get_text("status_list_keys"))
        print()
        
        keys = self.storage.get_keys()
        if not keys:
            self.print_centered(f"[yellow]{self.get_text('error_no_keys_found')}[/yellow]")
        else:
            table = Table(title=self.get_text("table_header_name"), show_header=True, header_style="bold magenta")
            table.add_column(self.get_text("table_header_name"), style="cyan")
            table.add_column(self.get_text("table_header_created"), style="green")
            
            for key in keys:
                table.add_row(key['name'], key['created_at'])
                
            self.console.print(Align.center(table))
        
        self.wait_for_enter()
    
    def remove_key(self):
        """Remove an existing key."""
        self.clear_screen()
        self.print_centered(self.get_text("status_remove_key"))
        print()
        
        keys = self.storage.get_keys()
        if not keys:
            self.print_centered(f"[yellow]{self.get_text('error_no_keys_found')}[/yellow]")
            time.sleep(2)
            return
            
        # Display available keys
        table = Table(title=self.get_text("table_header_name"), show_header=True, header_style="bold magenta")
        table.add_column(self.get_text("table_header_name"), style="cyan")
        table.add_column(self.get_text("table_header_created"), style="green")
        
        for i, key in enumerate(keys):
            table.add_row(key['name'], key['created_at'])
            
        self.console.print(Align.center(table))
        print()
        
        name = self.ask_centered(self.get_text("prompt_remove_key"))
        print()
        
        if self.storage.remove_key(name):
            self.print_centered(f"[green]Successfully removed key: {name}[/green]")
        else:
            self.print_centered(f"[red]{self.get_text('error_key_not_found').format(name=name)}[/red]")
            
        time.sleep(2)
    
    def show_help(self):
        """Display help information."""
        self.clear_screen()
        self.print_centered(self.get_text("status_help"))
        print()
        
        help_text = self.get_text("help_text")
        
        self.console.print(Align.center(Panel(help_text, expand=False)))
        self.wait_for_enter()
    
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
            
            self.console.print(Align.center(Panel(table, title="Language Selection", expand=False)))
            print()
            choice = self.ask_centered("Select a language", default="0")
            print()
            
            if choice == "1":
                self.set_language("en")
                self.print_centered("[green]Language changed to English[/green]")
                time.sleep(1)
                break
            elif choice == "2":
                self.set_language("pt")
                self.print_centered("[green]Idioma alterado para Português[/green]")
                time.sleep(1)
                break
            elif choice == "3":
                self.set_language("es")
                self.print_centered("[green]Idioma cambiado a Español[/green]")
                time.sleep(1)
                break
            elif choice == "0":
                break
            else:
                self.print_centered("[red]Invalid option. Please try again.[/red]")
                time.sleep(2)
    
    def run(self):
        """Main application loop."""
        while self.running:
            self.display_menu()
            print()
            choice = self.ask_centered(self.get_text("prompt_select_option"), default="0")
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
            elif choice == "0":
                self.print_centered(self.get_text("message_goodbye"))
                self.running = False
            else:
                self.print_centered(self.get_text("error_invalid_option"))
                time.sleep(2)