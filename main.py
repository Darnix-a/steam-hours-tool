"""
Steam Hours Analyzer - Main Application

A tool to analyze Steam playtime statistics across all games in your library.
Shows total hours played, top 3 games by all-time playtime, and top 3 games
played in the past 2 weeks.

Author: Steam Hours Tool
Version: 1.0.0
"""

import sys
import argparse
from typing import Optional

# Import our custom modules
from vdf_parser import get_steam_accounts, SteamAccount
from steam_api import get_api_key, SteamAPIClient, SteamAPIError
from stats import process_playtime_statistics, merge_owned_and_recent_data
from cli import (
    select_account, print_banner, print_statistics, print_error, 
    print_warning, print_success, print_info, show_loading_indicator
)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze Steam playtime statistics for your game library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Interactive mode
  python main.py --account 1        # Use first account (non-interactive)
  STEAM_API_KEY=xyz python main.py  # Use environment variable for API key
  
Account numbers correspond to the order shown when running interactively.
The most recent account is usually #1.
"""
    )
    
    parser.add_argument(
        '--account', '-a',
        type=int,
        metavar='N',
        help='Select account by number (1-based index, skips interactive selection)'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='Steam Hours Analyzer 1.0.0'
    )
    
    return parser.parse_args()


def main():
    """Main application entry point."""
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Step 1: Get available Steam accounts
        print_info("Scanning for Steam accounts...")
        try:
            accounts = get_steam_accounts()
        except SystemExit:
            return 1
        
        # Step 2: Select Steam account
        try:
            selected_account = select_account(accounts, args.account)
        except SystemExit:
            return 1
        
        # Step 3: Get Steam Web API key
        print_info("Setting up Steam Web API access...")
        try:
            api_key = get_api_key()
        except SystemExit:
            return 1
        
        # Step 4: Initialize Steam API client
        try:
            client = SteamAPIClient(api_key)
        except Exception as e:
            print_error(f"Failed to initialize Steam API client: {e}")
            return 1
        
        # Display banner
        print_banner(selected_account)
        
        # Step 5: Fetch player summary (for verification)
        show_loading_indicator("Verifying account access")
        try:
            player_summary = client.get_player_summary(selected_account.steam_id)
            verified_name = player_summary.get('personaname', 'Unknown')
            
            if verified_name != selected_account.persona_name:
                print_warning(f"Steam profile name has changed: '{selected_account.persona_name}' → '{verified_name}'")
            
        except SteamAPIError as e:
            print_error(f"Failed to verify account: {e}")
            print_info("This might indicate a private profile or invalid API key")
            return 1
        
        # Step 6: Fetch owned games
        show_loading_indicator("Fetching game library")
        try:
            owned_games = client.get_owned_games(selected_account.steam_id)
            if not owned_games:
                print_warning("No games found in library. This might indicate a private profile.")
                return 0
            
            print_success(f"Found {len(owned_games)} games in library")
            
        except SteamAPIError as e:
            print_error(f"Failed to fetch game library: {e}")
            return 1
        
        # Step 7: Fetch recently played games
        show_loading_indicator("Fetching recent activity")
        try:
            recent_games = client.get_recently_played_games(selected_account.steam_id)
            recent_count = len(recent_games)
            
            if recent_count > 0:
                print_info(f"Found {recent_count} recently played games (past 2 weeks)")
            else:
                print_info("No recent activity found (past 2 weeks)")
            
        except SteamAPIError as e:
            print_warning(f"Failed to fetch recent activity: {e}")
            recent_games = []  # Continue without recent data
        
        # Step 8: Merge game data and process statistics
        show_loading_indicator("Processing statistics")
        try:
            # Merge owned games with recent games for complete data
            merged_games = merge_owned_and_recent_data(owned_games, recent_games)
            
            # Process playtime statistics
            stats = process_playtime_statistics(merged_games)
            
            print_success("Statistics processed successfully")
            
        except Exception as e:
            print_error(f"Failed to process statistics: {e}")
            return 1
        
        # Step 9: Display results
        print_statistics(
            total_hours=stats.total_hours,
            total_games=stats.total_games,
            top_alltime=stats.top_alltime,
            top_recent=stats.top_recent
        )
        
        # Additional info if no playtime found
        if stats.total_hours == 0:
            print_info("No playtime data found. This might indicate:")
            print("  • Private Steam profile")
            print("  • No games have been played")
            print("  • API access restrictions")
        
        return 0
        
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user")
        return 130  # Standard exit code for SIGINT
    
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        print_info("Please report this issue if it persists")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)