"""
Command-Line Interface Module

This module provides user interaction functionality including account selection,
input validation, and formatted console output.
"""

import sys
from typing import List, Optional
from colorama import init, Fore, Back, Style
from vdf_parser import SteamAccount

# Initialize colorama for Windows console color support
init(autoreset=True)


def select_account(accounts: List[SteamAccount], account_index: Optional[int] = None) -> SteamAccount:
    """
    Allow user to select a Steam account from the available options.
    
    Args:
        accounts: List of available Steam accounts
        account_index: Pre-selected account index (1-based), or None for interactive selection
        
    Returns:
        Selected SteamAccount object
        
    Raises:
        SystemExit: If invalid account index is provided or user cancels
    """
    if not accounts:
        print("❌ No Steam accounts found.")
        sys.exit(1)
    
    # If only one account, use it automatically
    if len(accounts) == 1:
        print(f"✅ Using Steam account: {Style.BRIGHT}{accounts[0]}")
        return accounts[0]
    
    # If account index is pre-specified, validate and use it
    if account_index is not None:
        if 1 <= account_index <= len(accounts):
            selected = accounts[account_index - 1]
            print(f"✅ Using Steam account: {Style.BRIGHT}{selected}")
            return selected
        else:
            print(f"❌ Error: Invalid account index {account_index}. Valid range: 1-{len(accounts)}")
            sys.exit(1)
    
    # Interactive account selection
    print(f"\n{Fore.CYAN}{Style.BRIGHT}🎮 Steam Account Selection")
    print("=" * 50)
    print(f"Found {len(accounts)} Steam account(s):")
    print()
    
    for i, account in enumerate(accounts, 1):
        # Highlight the most recent account
        if account.most_recent:
            print(f"  {Fore.GREEN}{Style.BRIGHT}[{i}] {account}{Style.RESET_ALL}")
        else:
            print(f"  {Fore.WHITE}[{i}] {account}")
    
    print()
    print(f"{Fore.YELLOW}💡 Press ENTER to select the most recent account")
    print(f"{Fore.WHITE}Or enter a number (1-{len(accounts)}) to choose a specific account")
    print("─" * 50)
    
    while True:
        try:
            user_input = input(f"{Fore.CYAN}Select account: {Style.RESET_ALL}").strip()
            
            # Empty input = select most recent account
            if not user_input:
                most_recent_account = next((acc for acc in accounts if acc.most_recent), accounts[0])
                print(f"✅ Selected: {Style.BRIGHT}{most_recent_account}")
                return most_recent_account
            
            # Parse numeric input
            choice = int(user_input)
            if 1 <= choice <= len(accounts):
                selected = accounts[choice - 1]
                print(f"✅ Selected: {Style.BRIGHT}{selected}")
                return selected
            else:
                print(f"{Fore.RED}❌ Invalid choice. Please enter a number between 1 and {len(accounts)}")
                continue
                
        except ValueError:
            print(f"{Fore.RED}❌ Invalid input. Please enter a number or press ENTER")
            continue
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Cancelled by user.")
            sys.exit(0)


def format_hours(minutes: int) -> str:
    """
    Format minutes as hours with proper formatting.
    
    Args:
        minutes: Time in minutes
        
    Returns:
        Formatted time string (e.g., "123.4 hours")
    """
    if minutes == 0:
        return "0.0 hours"
    
    hours = minutes / 60
    if hours >= 1000:
        return f"{hours:,.1f} hours"
    else:
        return f"{hours:.1f} hours"


def print_banner(account: SteamAccount):
    """
    Print an attractive banner with account information.
    
    Args:
        account: Selected Steam account
    """
    print(f"\n{Back.BLUE}{Fore.WHITE}{Style.BRIGHT}")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 25 + "STEAM HOURS ANALYZER" + " " * 23 + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}{Style.BRIGHT}📊 Account Analysis")
    print("─" * 50)
    print(f"{Fore.WHITE}Player: {Style.BRIGHT}{account.persona_name}")
    print(f"{Fore.WHITE}Account: {account.account_name}")
    print(f"{Fore.WHITE}Steam ID: {account.steam_id}")
    print()


def print_statistics(total_hours: float, total_games: int, 
                    top_alltime: List[tuple], top_recent: List[tuple]):
    """
    Print formatted playtime statistics.
    
    Args:
        total_hours: Total hours played across all games
        total_games: Total number of games in library
        top_alltime: List of (game_name, hours) tuples for all-time top games
        top_recent: List of (game_name, hours) tuples for recent top games
    """
    # Overall statistics
    print(f"{Fore.GREEN}{Style.BRIGHT}📈 Overall Statistics")
    print("─" * 50)
    print(f"{Fore.WHITE}Total Games in Library: {Style.BRIGHT}{total_games:,}")
    print(f"{Fore.WHITE}Total Hours Played: {Style.BRIGHT}{total_hours:,.1f} hours")
    print()
    
    # Top games all-time
    if top_alltime:
        print(f"{Fore.MAGENTA}{Style.BRIGHT}🏆 Top 3 Games (All-Time)")
        print("─" * 50)
        for i, (game_name, hours) in enumerate(top_alltime, 1):
            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else "🔹"
            hours_str = format_hours(int(hours * 60))  # Convert back to minutes for formatting
            print(f"  {medal} {Fore.WHITE}{game_name}: {Style.BRIGHT}{hours_str}")
        print()
    
    # Top games recent (2 weeks)
    if top_recent:
        print(f"{Fore.YELLOW}{Style.BRIGHT}⚡ Top 3 Games (Past 2 Weeks)")
        print("─" * 50)
        for i, (game_name, hours) in enumerate(top_recent, 1):
            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else "🔹"
            hours_str = format_hours(int(hours * 60))  # Convert back to minutes for formatting
            print(f"  {medal} {Fore.WHITE}{game_name}: {Style.BRIGHT}{hours_str}")
        print()
    else:
        print(f"{Fore.YELLOW}{Style.BRIGHT}⚡ Recent Activity (Past 2 Weeks)")
        print("─" * 50)
        print(f"  {Fore.WHITE}No games played in the past 2 weeks")
        print()


def print_error(message: str):
    """
    Print an error message with consistent formatting.
    
    Args:
        message: Error message to display
    """
    print(f"\n{Fore.RED}{Style.BRIGHT}❌ Error: {message}")


def print_warning(message: str):
    """
    Print a warning message with consistent formatting.
    
    Args:
        message: Warning message to display
    """
    print(f"{Fore.YELLOW}⚠️  Warning: {message}")


def print_success(message: str):
    """
    Print a success message with consistent formatting.
    
    Args:
        message: Success message to display
    """
    print(f"{Fore.GREEN}✅ {message}")


def print_info(message: str):
    """
    Print an info message with consistent formatting.
    
    Args:
        message: Info message to display
    """
    print(f"{Fore.CYAN}ℹ️  {message}")


def show_loading_indicator(message: str):
    """
    Show a loading indicator for long-running operations.
    
    Args:
        message: Message to display while loading
    """
    print(f"{Fore.BLUE}⏳ {message}...")


if __name__ == "__main__":
    # Test the CLI module
    from vdf_parser import get_steam_accounts
    
    try:
        accounts = get_steam_accounts()
        selected = select_account(accounts)
        print_banner(selected)
        
        # Test statistics display with dummy data
        dummy_top_alltime = [
            ("Counter-Strike 2", 845.2),
            ("Dota 2", 623.7),
            ("Team Fortress 2", 234.1)
        ]
        dummy_top_recent = [
            ("Baldur's Gate 3", 28.5),
            ("Cyberpunk 2077", 12.3),
            ("Elden Ring", 8.7)
        ]
        
        print_statistics(1703.0, 156, dummy_top_alltime, dummy_top_recent)
        
    except SystemExit:
        pass