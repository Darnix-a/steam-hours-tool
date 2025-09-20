"""
Statistics Processing Module

This module handles processing of Steam game data to generate playtime statistics,
rankings, and aggregated metrics.
"""

from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
from steam_api import GameData


@dataclass
class PlaytimeStatistics:
    """Container for processed playtime statistics."""
    total_hours: float
    total_games: int
    games_with_playtime: int
    top_alltime: List[Tuple[str, float]]  # (game_name, hours)
    top_recent: List[Tuple[str, float]]   # (game_name, hours)
    raw_games_data: List[GameData]


def minutes_to_hours(minutes: int) -> float:
    """
    Convert minutes to hours with proper rounding.
    
    Args:
        minutes: Time in minutes
        
    Returns:
        Time in hours, rounded to 1 decimal place
    """
    return round(minutes / 60.0, 1)


def process_playtime_statistics(games: List[GameData]) -> PlaytimeStatistics:
    """
    Process game data to generate comprehensive playtime statistics.
    
    Args:
        games: List of GameData objects from Steam API
        
    Returns:
        PlaytimeStatistics object with processed data
    """
    if not games:
        return PlaytimeStatistics(
            total_hours=0.0,
            total_games=0,
            games_with_playtime=0,
            top_alltime=[],
            top_recent=[],
            raw_games_data=[]
        )
    
    # Calculate total playtime
    total_minutes = sum(game.playtime_forever for game in games)
    total_hours = minutes_to_hours(total_minutes)
    
    # Count games with actual playtime
    games_with_playtime = len([game for game in games if game.playtime_forever > 0])
    
    # Get top games by all-time playtime (exclude games with 0 playtime)
    played_games = [game for game in games if game.playtime_forever > 0]
    top_alltime_games = sorted(played_games, key=lambda x: x.playtime_forever, reverse=True)[:3]
    top_alltime = [(game.name, minutes_to_hours(game.playtime_forever)) for game in top_alltime_games]
    
    # Get top games by recent playtime (past 2 weeks)
    recent_games = [game for game in games if game.playtime_2weeks > 0]
    top_recent_games = sorted(recent_games, key=lambda x: x.playtime_2weeks, reverse=True)[:3]
    top_recent = [(game.name, minutes_to_hours(game.playtime_2weeks)) for game in top_recent_games]
    
    return PlaytimeStatistics(
        total_hours=total_hours,
        total_games=len(games),
        games_with_playtime=games_with_playtime,
        top_alltime=top_alltime,
        top_recent=top_recent,
        raw_games_data=games
    )


def merge_owned_and_recent_data(owned_games: List[GameData], 
                               recent_games: List[GameData]) -> List[GameData]:
    """
    Merge owned games data with recent games data to get complete playtime information.
    
    The Steam API sometimes provides more accurate recent playtime data in the
    GetRecentlyPlayedGames endpoint, so this function merges the data to ensure
    we have the most complete information.
    
    Args:
        owned_games: Games from GetOwnedGames API call
        recent_games: Games from GetRecentlyPlayedGames API call
        
    Returns:
        Merged list of GameData with updated recent playtime information
    """
    # Create a lookup dict for recent games by appid
    recent_lookup = {game.appid: game for game in recent_games}
    
    # Update owned games with recent playtime data if available
    merged_games = []
    for game in owned_games:
        if game.appid in recent_lookup:
            recent_game = recent_lookup[game.appid]
            # Use the recent game's 2-week playtime data
            updated_game = GameData(
                appid=game.appid,
                name=game.name,
                playtime_forever=max(game.playtime_forever, recent_game.playtime_forever),
                playtime_2weeks=recent_game.playtime_2weeks,
                img_icon_url=game.img_icon_url or recent_game.img_icon_url,
                img_logo_url=game.img_logo_url or recent_game.img_logo_url
            )
            merged_games.append(updated_game)
        else:
            merged_games.append(game)
    
    return merged_games


def find_games_by_criteria(games: List[GameData], min_hours: float = None, 
                          max_hours: float = None, name_contains: str = None) -> List[GameData]:
    """
    Find games matching specific criteria.
    
    Args:
        games: List of GameData objects
        min_hours: Minimum playtime in hours (optional)
        max_hours: Maximum playtime in hours (optional)
        name_contains: Game name must contain this string (case-insensitive, optional)
        
    Returns:
        Filtered list of GameData objects
    """
    filtered_games = games
    
    if min_hours is not None:
        min_minutes = int(min_hours * 60)
        filtered_games = [game for game in filtered_games if game.playtime_forever >= min_minutes]
    
    if max_hours is not None:
        max_minutes = int(max_hours * 60)
        filtered_games = [game for game in filtered_games if game.playtime_forever <= max_minutes]
    
    if name_contains is not None:
        search_term = name_contains.lower()
        filtered_games = [game for game in filtered_games if search_term in game.name.lower()]
    
    return filtered_games


def get_playtime_breakdown(games: List[GameData]) -> Dict[str, Any]:
    """
    Get a detailed breakdown of playtime statistics.
    
    Args:
        games: List of GameData objects
        
    Returns:
        Dictionary with detailed playtime breakdown
    """
    if not games:
        return {
            "total_games": 0,
            "played_games": 0,
            "unplayed_games": 0,
            "total_hours": 0.0,
            "average_hours_per_played_game": 0.0,
            "median_hours": 0.0,
            "games_by_range": {
                "0_hours": 0,
                "0_to_1_hours": 0,
                "1_to_10_hours": 0,
                "10_to_50_hours": 0,
                "50_to_100_hours": 0,
                "100_plus_hours": 0
            }
        }
    
    # Basic counts
    total_games = len(games)
    played_games = [game for game in games if game.playtime_forever > 0]
    played_count = len(played_games)
    unplayed_count = total_games - played_count
    
    # Total hours
    total_minutes = sum(game.playtime_forever for game in games)
    total_hours = minutes_to_hours(total_minutes)
    
    # Average hours per played game
    avg_hours = minutes_to_hours(total_minutes / played_count) if played_count > 0 else 0.0
    
    # Median hours (only for played games)
    if played_games:
        sorted_playtimes = sorted([game.playtime_forever for game in played_games])
        mid = len(sorted_playtimes) // 2
        if len(sorted_playtimes) % 2 == 0:
            median_minutes = (sorted_playtimes[mid-1] + sorted_playtimes[mid]) / 2
        else:
            median_minutes = sorted_playtimes[mid]
        median_hours = minutes_to_hours(median_minutes)
    else:
        median_hours = 0.0
    
    # Games by playtime range
    ranges = {
        "0_hours": 0,
        "0_to_1_hours": 0,
        "1_to_10_hours": 0,
        "10_to_50_hours": 0,
        "50_to_100_hours": 0,
        "100_plus_hours": 0
    }
    
    for game in games:
        hours = minutes_to_hours(game.playtime_forever)
        if hours == 0:
            ranges["0_hours"] += 1
        elif hours <= 1:
            ranges["0_to_1_hours"] += 1
        elif hours <= 10:
            ranges["1_to_10_hours"] += 1
        elif hours <= 50:
            ranges["10_to_50_hours"] += 1
        elif hours <= 100:
            ranges["50_to_100_hours"] += 1
        else:
            ranges["100_plus_hours"] += 1
    
    return {
        "total_games": total_games,
        "played_games": played_count,
        "unplayed_games": unplayed_count,
        "total_hours": total_hours,
        "average_hours_per_played_game": avg_hours,
        "median_hours": median_hours,
        "games_by_range": ranges
    }


if __name__ == "__main__":
    # Test the statistics module with dummy data
    test_games = [
        GameData(appid=730, name="Counter-Strike 2", playtime_forever=50730, playtime_2weeks=180),  # 845.5h, 3h recent
        GameData(appid=570, name="Dota 2", playtime_forever=37422, playtime_2weeks=0),            # 623.7h, 0h recent
        GameData(appid=440, name="Team Fortress 2", playtime_forever=14046, playtime_2weeks=45),   # 234.1h, 0.75h recent
        GameData(appid=1086940, name="Baldur's Gate 3", playtime_forever=1710, playtime_2weeks=1710), # 28.5h, 28.5h recent
        GameData(appid=1091500, name="Cyberpunk 2077", playtime_forever=738, playtime_2weeks=738),   # 12.3h, 12.3h recent
        GameData(appid=1245620, name="ELDEN RING", playtime_forever=522, playtime_2weeks=0),        # 8.7h, 0h recent
        GameData(appid=271590, name="Grand Theft Auto V", playtime_forever=0, playtime_2weeks=0),   # 0h, 0h recent
    ]
    
    print("Testing statistics processing...")
    stats = process_playtime_statistics(test_games)
    
    print(f"Total hours: {stats.total_hours}")
    print(f"Total games: {stats.total_games}")
    print(f"Games with playtime: {stats.games_with_playtime}")
    
    print("\nTop 3 all-time:")
    for i, (name, hours) in enumerate(stats.top_alltime, 1):
        print(f"  {i}. {name}: {hours:.1f} hours")
    
    print("\nTop 3 recent:")
    for i, (name, hours) in enumerate(stats.top_recent, 1):
        print(f"  {i}. {name}: {hours:.1f} hours")
    
    print("\nPlaytime breakdown:")
    breakdown = get_playtime_breakdown(test_games)
    print(f"  Played games: {breakdown['played_games']}/{breakdown['total_games']}")
    print(f"  Average hours per played game: {breakdown['average_hours_per_played_game']:.1f}")
    print(f"  Median hours: {breakdown['median_hours']:.1f}")
    
    print("\nGames by playtime range:")
    for range_name, count in breakdown['games_by_range'].items():
        range_display = range_name.replace('_', ' ').replace('to', '-').title()
        print(f"  {range_display}: {count} games")