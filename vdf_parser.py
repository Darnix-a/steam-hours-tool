"""
Steam VDF Parser Module

This module handles parsing Steam's VDF (Valve Data Format) files to extract
Steam account information from the loginusers.vdf configuration file.
"""

import os
import sys
import vdf
import winreg
from typing import List, Dict, Optional


class SteamAccount:
    """Represents a Steam account with its configuration data."""
    
    def __init__(self, steam_id: str, account_name: str, persona_name: str, 
                 most_recent: bool, timestamp: str):
        self.steam_id = steam_id
        self.account_name = account_name
        self.persona_name = persona_name
        self.most_recent = most_recent
        self.timestamp = int(timestamp)
    
    def __str__(self):
        status = " (Most Recent)" if self.most_recent else ""
        return f"{self.persona_name} ({self.account_name}){status}"
    
    def __repr__(self):
        return f"SteamAccount(steam_id='{self.steam_id}', account_name='{self.account_name}', persona_name='{self.persona_name}', most_recent={self.most_recent})"


def find_steam_path() -> Optional[str]:
    """
    Find Steam installation path by checking registry and common locations.
    
    Returns:
        Path to Steam installation directory, or None if not found.
    """
    # Try registry first (most reliable)
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam") as key:
            install_path, _ = winreg.QueryValueEx(key, "InstallPath")
            if os.path.exists(install_path):
                return install_path
    except (OSError, FileNotFoundError):
        pass
    
    # Fallback to common installation paths
    common_paths = [
        r"C:\Program Files (x86)\Steam",
        r"C:\Program Files\Steam",
        os.path.expandvars(r"%LOCALAPPDATA%\Steam")
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    return None


def find_loginusers_vdf() -> Optional[str]:
    """
    Locate the Steam loginusers.vdf configuration file.
    
    Returns:
        Full path to loginusers.vdf file, or None if not found.
    """
    steam_path = find_steam_path()
    if not steam_path:
        return None
    
    loginusers_path = os.path.join(steam_path, "config", "loginusers.vdf")
    return loginusers_path if os.path.exists(loginusers_path) else None


def parse_loginusers_vdf(vdf_path: str) -> List[SteamAccount]:
    """
    Parse the Steam loginusers.vdf file to extract account information.
    
    Args:
        vdf_path: Full path to the loginusers.vdf file
        
    Returns:
        List of SteamAccount objects sorted by most recent first
        
    Raises:
        FileNotFoundError: If the VDF file doesn't exist
        ValueError: If the VDF file is corrupted or has unexpected format
    """
    if not os.path.exists(vdf_path):
        raise FileNotFoundError(f"Steam loginusers.vdf not found at: {vdf_path}")
    
    try:
        with open(vdf_path, 'r', encoding='utf-8') as file:
            data = vdf.load(file)
    except Exception as e:
        raise ValueError(f"Failed to parse VDF file: {e}")
    
    if 'users' not in data:
        raise ValueError("VDF file doesn't contain 'users' section")
    
    accounts = []
    users = data['users']
    
    for steam_id, user_data in users.items():
        try:
            account = SteamAccount(
                steam_id=steam_id,
                account_name=user_data.get('AccountName', 'Unknown'),
                persona_name=user_data.get('PersonaName', 'Unknown'),
                most_recent=user_data.get('MostRecent', '0') == '1',
                timestamp=user_data.get('Timestamp', '0')
            )
            accounts.append(account)
        except KeyError as e:
            print(f"Warning: Skipping incomplete account entry for {steam_id}: missing {e}")
            continue
    
    # Sort by most recent first, then by timestamp (newest first)
    accounts.sort(key=lambda x: (not x.most_recent, -x.timestamp))
    
    return accounts


def get_steam_accounts() -> List[SteamAccount]:
    """
    Get all Steam accounts from the system.
    
    Returns:
        List of SteamAccount objects
        
    Raises:
        SystemExit: If Steam is not found or VDF file cannot be parsed
    """
    vdf_path = find_loginusers_vdf()
    
    if not vdf_path:
        print("❌ Error: Could not locate Steam installation or loginusers.vdf file.")
        print("\nTroubleshooting:")
        print("1. Make sure Steam is installed")
        print("2. Try running Steam at least once to generate the configuration")
        print("3. Check if Steam is installed in a non-standard location")
        sys.exit(1)
    
    try:
        accounts = parse_loginusers_vdf(vdf_path)
        if not accounts:
            print("❌ Error: No Steam accounts found in configuration.")
            print("Please log into Steam at least once to create account data.")
            sys.exit(1)
        
        return accounts
    
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Test the module
    try:
        accounts = get_steam_accounts()
        print(f"Found {len(accounts)} Steam account(s):")
        for i, account in enumerate(accounts, 1):
            print(f"  {i}. {account}")
    except SystemExit:
        pass