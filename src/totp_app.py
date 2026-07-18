import time
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
    
    def clear_screen(self):
        """Clear the terminal screen."""
        self.console.clear()
    
    def display_menu(self):
        """Display the main menu."""
        self.clear_screen()
        table = Table(title="TOTP Application Menu", show_header=False)
        table.add_column("Option", style="cyan")
        table.add_column("Description", style="magenta")
        
        table.add_row("1", "Add New Authentication Key")
        table.add_row("2", "Show All Passwords (Dynamic)")
        table.add_row("3", "List All Keys")
        table.add_row("4", "Remove Key")
        table.add_row("5", "Help")
        table.add_row("0", "Exit")
        
        self.console.print(Panel(table, title="Main Menu"))
    
    def add_key(self):
        """Add a new authentication key."""
        self.clear_screen()
        print("[bold blue]Add New Authentication Key[/bold blue]")
        
        name = Prompt.ask("Enter key name")
        if not name.strip():
            print("[red]Key name cannot be empty![/red]")
            time.sleep(2)
            return
            
        secret = Prompt.ask("Enter base32 secret")
        if not secret.strip():
            print("[red]Secret cannot be empty![/red]")
            time.sleep(2)
            return
            
        if self.storage.add_key(name, secret):
            print(f"[green]Successfully added key: {name}[/green]")
        else:
            print(f"[red]Failed to add key: {name} (already exists)[/red]")
            
        time.sleep(2)
    
    def show_passwords(self):
        """Display all passwords with dynamic updates."""
        self.clear_screen()
        print("[bold blue]Current TOTP Passwords[/bold blue]")
        
        keys = self.storage.get_keys()
        if not keys:
            print("[yellow]No keys found. Add some keys first.[/yellow]")
            time.sleep(2)
            return
            
        while True:
            self.clear_screen()
            print("[bold blue]Current TOTP Passwords (Auto-updating) - Press Ctrl+C to return[/bold blue]")
            
            # Create table for current passwords
            table = Table(title="TOTP Keys", show_header=True, header_style="bold magenta")
            table.add_column("Name", style="cyan")
            table.add_column("Password", style="green")
            table.add_column("Expires In", style="yellow")
            table.add_column("Status", style="blue")
            
            updated = False
            for key in keys:
                try:
                    totp = pyotp.TOTP(key['secret'])
                    password = totp.now()
                    remaining = 30 - (int(time.time()) % 30)
                    status = "Valid" if remaining > 0 else "Expired"
                    
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
                print("[yellow]No valid passwords to display.[/yellow]")
            
            try:
                time.sleep(1)  # Update every second to show countdown
                # Check if user wants to exit (Ctrl+C)
            except KeyboardInterrupt:
                break
    
    def list_keys(self):
        """List all stored keys."""
        self.clear_screen()
        print("[bold blue]Stored TOTP Keys[/bold blue]")
        
        keys = self.storage.get_keys()
        if not keys:
            print("[yellow]No keys found.[/yellow]")
        else:
            table = Table(title="TOTP Keys", show_header=True, header_style="bold magenta")
            table.add_column("Name", style="cyan")
            table.add_column("Created At", style="green")
            
            for key in keys:
                table.add_row(key['name'], key['created_at'])
                
            self.console.print(table)
        
        input("\nPress Enter to continue...")
    
    def remove_key(self):
        """Remove an existing key."""
        self.clear_screen()
        print("[bold blue]Remove Authentication Key[/bold blue]")
        
        keys = self.storage.get_keys()
        if not keys:
            print("[yellow]No keys found.[/yellow]")
            time.sleep(2)
            return
            
        # Display available keys
        table = Table(title="Available Keys", show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Created At", style="green")
        
        for i, key in enumerate(keys):
            table.add_row(key['name'], key['created_at'])
            
        self.console.print(table)
        
        name = Prompt.ask("\nEnter the name of the key to remove")
        
        if self.storage.remove_key(name):
            print(f"[green]Successfully removed key: {name}[/green]")
        else:
            print(f"[red]Key '{name}' not found![/red]")
            
        time.sleep(2)
    
    def show_help(self):
        """Display help information."""
        self.clear_screen()
        print("[bold blue]TOTP Application Help[/bold blue]")
        
        help_text = """
This application manages Time-based One-Time Passwords (TOTP) for multi-factor authentication.
Features:
- Add new authentication keys with custom names
- View dynamic passwords that automatically update every 30 seconds
- List all stored keys
- Remove existing keys

Requirements:
- Base32 encoded secrets for TOTP generation
- All data is stored in a JSON file called 'totp_keys.json'

For more information about TOTP:
https://en.wikipedia.org/wiki/Time-based_one-time_password
        """
        
        self.console.print(Panel(help_text))
        input("\nPress Enter to continue...")
    
    def run(self):
        """Main application loop."""
        while self.running:
            self.display_menu()
            choice = Prompt.ask("Select an option", default="0")
            
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
            elif choice == "0":
                print("[yellow]Goodbye![/yellow]")
                self.running = False
            else:
                print("[red]Invalid option. Please try again.[/red]")
                time.sleep(2)