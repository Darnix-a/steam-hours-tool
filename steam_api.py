"""
Steam Web API Client Module

This module provides a client for interacting with Steam's Web API to fetch
game library data, playtime statistics, and other account information.
"""

import os
import sys
import time
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class GameData:
    """Represents game data from Steam API."""
    appid: int
    name: str
    playtime_forever: int  # in minutes
    playtime_2weeks: int = 0  # in minutes, default to 0 if not present
    img_icon_url: str = ""
    img_logo_url: str = ""


class SteamAPIError(Exception):
    """Custom exception for Steam API errors."""
    pass


class SteamAPIClient:
    """Steam Web API client with error handling and rate limiting."""
    
    BASE_URL = "https://api.steampowered.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Steam-Hours-Tool/1.0'
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.2  # 200ms between requests
    
    def _rate_limit(self):
        """Enforce rate limiting between API requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict[str, Any], 
                     max_retries: int = 3) -> Dict[str, Any]:
        """
        Make a request to the Steam API with error handling and retries.
        
        Args:
            endpoint: API endpoint (relative to BASE_URL)
            params: Request parameters
            max_retries: Maximum number of retry attempts
            
        Returns:
            JSON response data
            
        Raises:
            SteamAPIError: If the API request fails or returns an error
        """
        # Add API key to parameters
        params['key'] = self.api_key
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        for attempt in range(max_retries + 1):
            try:
                self._rate_limit()
                
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                # Check for Steam API-specific errors
                if 'response' not in data:
                    raise SteamAPIError(f"Invalid API response format: {data}")
                
                return data['response']
                
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:  # Rate limited
                    if attempt < max_retries:
                        wait_time = (2 ** attempt) * 1.0  # Exponential backoff
                        print(f"Rate limited, waiting {wait_time:.1f}s before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise SteamAPIError("Rate limit exceeded. Please try again later.")
                elif response.status_code == 401:
                    raise SteamAPIError("Invalid API key. Please check your Steam Web API key.")
                elif response.status_code == 403:
                    raise SteamAPIError("Access forbidden. Check API key permissions or account privacy settings.")
                else:
                    raise SteamAPIError(f"HTTP error {response.status_code}: {e}")
            
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    wait_time = (2 ** attempt) * 1.0
                    print(f"Network error, retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise SteamAPIError(f"Network error: {e}")
            
            except json.JSONDecodeError as e:
                raise SteamAPIError(f"Invalid JSON response: {e}")
        
        raise SteamAPIError(f"Max retries ({max_retries}) exceeded")
    
    def get_owned_games(self, steam_id: str) -> List[GameData]:
        """
        Get the list of games owned by a Steam user.
        
        Args:
            steam_id: Steam 64-bit ID
            
        Returns:
            List of GameData objects
            
        Raises:
            SteamAPIError: If the API request fails
        """
        params = {
            'steamid': steam_id,
            'include_appinfo': '1',
            'include_played_free_games': '1',
            'format': 'json'
        }
        
        try:
            data = self._make_request('IPlayerService/GetOwnedGames/v0001/', params)
        except SteamAPIError as e:
            raise SteamAPIError(f"Failed to fetch owned games: {e}")
        
        if 'games' not in data:
            # User might have no games or private profile
            return []
        
        games = []
        for game_data in data['games']:
            game = GameData(
                appid=game_data.get('appid', 0),
                name=game_data.get('name', 'Unknown Game'),
                playtime_forever=game_data.get('playtime_forever', 0),
                playtime_2weeks=game_data.get('playtime_2weeks', 0),
                img_icon_url=game_data.get('img_icon_url', ''),
                img_logo_url=game_data.get('img_logo_url', '')
            )
            games.append(game)
        
        return games
    
    def get_recently_played_games(self, steam_id: str) -> List[GameData]:
        """
        Get recently played games for a Steam user.
        
        Args:
            steam_id: Steam 64-bit ID
            
        Returns:
            List of GameData objects for recently played games
            
        Raises:
            SteamAPIError: If the API request fails
        """
        params = {
            'steamid': steam_id,
            'count': 0,  # 0 = return all recent games
            'format': 'json'
        }
        
        try:
            data = self._make_request('IPlayerService/GetRecentlyPlayedGames/v0001/', params)
        except SteamAPIError as e:
            raise SteamAPIError(f"Failed to fetch recently played games: {e}")
        
        if 'games' not in data:
            return []
        
        games = []
        for game_data in data['games']:
            game = GameData(
                appid=game_data.get('appid', 0),
                name=game_data.get('name', 'Unknown Game'),
                playtime_forever=game_data.get('playtime_forever', 0),
                playtime_2weeks=game_data.get('playtime_2weeks', 0),
                img_icon_url=game_data.get('img_icon_url', ''),
                img_logo_url=game_data.get('img_logo_url', '')
            )
            games.append(game)
        
        return games
    
    def get_player_summary(self, steam_id: str) -> Dict[str, Any]:
        """
        Get player summary information.
        
        Args:
            steam_id: Steam 64-bit ID
            
        Returns:
            Player summary data
            
        Raises:
            SteamAPIError: If the API request fails
        """
        params = {
            'steamids': steam_id,
            'format': 'json'
        }
        
        try:
            data = self._make_request('ISteamUser/GetPlayerSummaries/v0002/', params)
        except SteamAPIError as e:
            raise SteamAPIError(f"Failed to fetch player summary: {e}")
        
        if 'players' not in data or not data['players']:
            raise SteamAPIError("Player not found or profile is private")
        
        return data['players'][0]


def get_api_key() -> str:
    """
    Get Steam Web API key from environment variable or user input.
    
    Returns:
        Steam Web API key
        
    Raises:
        SystemExit: If no API key is provided
    """
    # Check environment variable first
    api_key = os.environ.get('STEAM_API_KEY')
    if api_key:
        return api_key
    
    # Check for stored API key file
    api_key_file = os.path.expandvars(r'%APPDATA%\steam-hours-tool\apikey.txt')
    if os.path.exists(api_key_file):
        try:
            with open(api_key_file, 'r') as f:
                stored_key = f.read().strip()
                if stored_key:
                    return stored_key
        except Exception:
            pass
    
    # Prompt user for API key
    print("🔑 Steam Web API Key Required")
    print("═" * 50)
    print("To use this tool, you need a Steam Web API key.")
    print("\n📋 How to get your API key:")
    print("1. Go to: https://steamcommunity.com/dev/apikey")
    print("2. Log in with your Steam account")
    print("3. Enter any domain name (e.g., 'localhost')")
    print("4. Copy the generated API key")
    print("\n🔒 Your API key will be stored securely for future use.")
    print("─" * 50)
    
    api_key = input("Enter your Steam Web API key: ").strip()
    
    if not api_key:
        print("❌ Error: No API key provided.")
        sys.exit(1)
    
    # Store the API key for future use
    try:
        os.makedirs(os.path.dirname(api_key_file), exist_ok=True)
        with open(api_key_file, 'w') as f:
            f.write(api_key)
        print(f"✅ API key stored in: {api_key_file}")
    except Exception as e:
        print(f"⚠️  Warning: Could not store API key: {e}")
    
    return api_key


if __name__ == "__main__":
    # Test the Steam API client
    try:
        api_key = get_api_key()
        client = SteamAPIClient(api_key)
        
        # Test with a public Steam ID (replace with actual ID for testing)
        test_steam_id = "76561199469631140"  # Darnix's ID from VDF
        
        print(f"Testing Steam API with Steam ID: {test_steam_id}")
        
        try:
            summary = client.get_player_summary(test_steam_id)
            print(f"Player: {summary.get('personaname', 'Unknown')}")
            
            games = client.get_owned_games(test_steam_id)
            print(f"Total games: {len(games)}")
            
            recent_games = client.get_recently_played_games(test_steam_id)
            print(f"Recently played games: {len(recent_games)}")
            
        except SteamAPIError as e:
            print(f"❌ API Error: {e}")
            
    except SystemExit:
        pass