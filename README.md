# Steam Hours Tool - Complete Usage Guide

## 🎯 What This Tool Does

The Steam Hours Tool is a complete solution for analyzing your Steam gaming statistics. It automatically:

1. **Detects all Steam accounts** logged into your system
2. **Lets you choose which account to analyze** (or picks the most recent one)
3. **Fetches your complete game library** via Steam Web API
4. **Calculates total playtime** across all games
5. **Shows your top 3 most-played games** of all time
6. **Shows your top 3 games** from the past 2 weeks
7. **Presents everything in a beautiful, colorized format**

## 🚀 Quick Start

### Step 1: Get Your Steam Web API Key
1. Visit: https://steamcommunity.com/dev/apikey
2. Log in with your Steam account
3. Enter any domain name (e.g., "localhost")
4. Copy the generated API key

### Step 2: Run the Tool
```powershell
python main.py
```

The tool will guide you through:
- Account selection (if you have multiple Steam accounts)
- API key setup (first time only)
- Data fetching and analysis
- Results display


### Account Numbers
When you run the tool interactively, it shows all your Steam accounts:
- **Account 1**: Most recently used (recommended)
- **Account 2+**: Other accounts, sorted by last login

### API Key Management
The tool stores your API key securely after first use:
- Location: `%APPDATA%\steam-hours-tool\apikey.txt`
- The file is created automatically when you enter your API key
- Delete the file to re-enter a new API key

## 🏗️ Project Structure

```
steam-hours-tool/
├── main.py           # Main application entry point
├── vdf_parser.py     # Steam account detection and VDF parsing
├── steam_api.py      # Steam Web API client with error handling
├── stats.py          # Playtime statistics processing
├── cli.py            # Console UI and user interaction
├── requirements.txt  # Python dependencies
├── pyproject.toml    # Python packaging configuration
├── README.md         # Comprehensive documentation
└── USAGE_GUIDE.md    # This file
```

## 🛠️ Technical Features

### Robust Error Handling
- **Private profiles**: Graceful detection and user-friendly messages
- **Network issues**: Automatic retries with exponential backoff
- **Rate limiting**: Respects Steam API limits with intelligent delays
- **Invalid API keys**: Clear troubleshooting guidance

### Multi-Account Support
- Automatically scans Windows Registry for Steam installation
- Parses Steam VDF configuration files to find all logged-in accounts
- Sorts accounts by most recent use for easy selection

### Comprehensive Statistics
- Total hours played across entire library
- Game library size and breakdown
- All-time top games rankings
- Recent activity analysis (past 2 weeks)
- Proper time formatting (handles 1000+ hour games)

### Beautiful Console Output
- Color-coded sections using `colorama`
- Unicode box drawing characters for professional appearance
- Emoji indicators for different data types
- Responsive formatting that works in any terminal width

## 🔍 Troubleshooting

### "No Steam accounts found"
**Problem**: Tool can't locate Steam installation or configuration
**Solution**: 
- Make sure Steam is installed
- Run Steam at least once to create configuration files
- Check if Steam is installed in a non-standard location

### "Failed to fetch game library"
**Problem**: API can't access your games
**Solution**:
- Set your Steam profile to **Public**
- Verify your API key is correct and active
- Check that your account isn't restricted

### "Profile is private"
**Problem**: Steam profile privacy settings block access
**Solution**:
1. Open Steam → View → Settings → Privacy
2. Set "My Profile" to **Public**
3. Set "Game Details" to **Public**
4. Re-run the tool

### Rate Limiting
**Problem**: Too many API requests in short time
**Solution**: 
- Wait 5-10 minutes before trying again
- The tool automatically handles rate limiting, but manual requests can trigger limits

## 🎮 Supported Data

### Game Library Data
- **All owned games** (including free games)
- **Total playtime** for each game (all-time)
- **Recent playtime** for each game (past 2 weeks)
- **Game names** and metadata

### Account Information
- **Steam Display Name** (Persona Name)
- **Account Name** (login username)
- **Steam ID** (64-bit identifier)
- **Last login timestamp**

### Statistics Generated
- **Total hours played** across entire library
- **Top 3 games by all-time playtime**
- **Top 3 games by recent playtime** (2 weeks)
- **Game library size** (total owned games)

## 🚨 Important Notes

### Privacy & Security
- Your API key is stored **locally only**
- No data is sent to external servers (except Steam's official API)
- Profile privacy settings are fully respected
- Tool follows Steam's API terms of service

### Requirements
- **Windows** (uses Windows Registry to locate Steam)
- **Python 3.13+** (tested with 3.13.3)
- **Steam installed** with at least one account logged in
- **Steam Web API key** (free from Steam)
- **Internet connection** for API calls

### Performance
- **Fast execution**: Usually completes in 5-15 seconds
- **Rate limiting**: Respectful of Steam API limits
- **Error recovery**: Robust handling of network issues
- **Memory efficient**: Processes data in memory without large storage

This tool gives you deep insights into your Steam gaming habits with professional presentation and bulletproof reliability!