import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import time
import random
import pytz

# Page config
st.set_page_config(
    page_title="PrizePicks Player Props Only",
    page_icon="🏀",
    layout="wide"
)

# Set timezone to Central Time
central_tz = pytz.timezone('US/Central')
utc_tz = pytz.UTC

def get_central_time():
    utc_now = datetime.now(utc_tz)
    central_now = utc_now.astimezone(central_tz)
    return central_now

# HIGH CONTRAST CSS - Fixed button colors
st.markdown("""
<style>
    /* Main header */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #FFFFFF;
        text-align: center;
        margin-bottom: 0.5rem;
        background-color: #1E88E5;
        padding: 1rem;
        border-radius: 10px;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #FFFFFF;
        background-color: #0D47A1;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* API Status indicators */
    .api-status {
        display: flex;
        gap: 2rem;
        margin: 1rem 0;
        padding: 1rem;
        background-color: #2C3E50;
        border-radius: 10px;
        border: 1px solid #1E88E5;
        justify-content: center;
        flex-wrap: wrap;
    }
    .api-status-item {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        font-size: 1.1rem;
    }
    .status-dot {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        display: inline-block;
    }
    .status-dot.green {
        background-color: #2E7D32;
        box-shadow: 0 0 15px #2E7D32;
        animation: pulse-green 2s infinite;
    }
    .status-dot.yellow {
        background-color: #FFC107;
        box-shadow: 0 0 15px #FFC107;
        animation: pulse-yellow 2s infinite;
    }
    .status-dot.red {
        background-color: #C62828;
        box-shadow: 0 0 15px #C62828;
        animation: pulse-red 2s infinite;
    }
    
    @keyframes pulse-green {
        0% { box-shadow: 0 0 0 0 rgba(46, 125, 50, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(46, 125, 50, 0); }
        100% { box-shadow: 0 0 0 0 rgba(46, 125, 50, 0); }
    }
    @keyframes pulse-yellow {
        0% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 193, 7, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0); }
    }
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(198, 40, 40, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(198, 40, 40, 0); }
        100% { box-shadow: 0 0 0 0 rgba(198, 40, 40, 0); }
    }
    
    /* Sport badges */
    .badge-nba { background-color: #17408B; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
    .badge-nhl { background-color: #000000; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
    .badge-mlb { background-color: #041E42; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
    .badge-pga { background-color: #0A4C33; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
    .badge-tennis { background-color: #CC5500; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
    .badge-soccer { background-color: #006400; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
    .badge-mma { background-color: #8B0000; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
    .badge-esports { background-color: #4B0082; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
    .badge-nascar { background-color: #8B4513; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
    .badge-cbb { background-color: #FF4500; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
    .badge-unrivaled { background-color: #FF69B4; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
    .badge-ohockey { background-color: #000080; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
    .badge-other { background-color: #555555; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
    
    /* MORE/LESS badges */
    .more-badge { background-color: #2E7D32; color: #FFFFFF; padding: 0.3rem 1rem; border-radius: 25px; font-weight: bold; font-size: 0.9rem; display: inline-block; min-width: 70px; text-align: center; border: 2px solid #FFFFFF; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
    .less-badge { background-color: #C62828; color: #FFFFFF; padding: 0.3rem 1rem; border-radius: 25px; font-weight: bold; font-size: 0.9rem; display: inline-block; min-width: 70px; text-align: center; border: 2px solid #FFFFFF; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
    
    /* Hit rate colors */
    .hit-high { color: #FFFFFF; font-weight: bold; font-size: 1.1rem; background-color: #2E7D32; padding: 0.2rem 0.5rem; border-radius: 8px; border: 1px solid #FFFFFF; }
    .hit-low { color: #FFFFFF; font-weight: bold; font-size: 1.1rem; background-color: #C62828; padding: 0.2rem 0.5rem; border-radius: 8px; border: 1px solid #FFFFFF; }
    
    /* Cards */
    .prop-card {
        background-color: #2C3E50;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #1E88E5;
        margin: 0.5rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        color: #FFFFFF;
    }
    .entry-card {
        background-color: #34495E;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #1E88E5;
        color: #FFFFFF;
        border: 1px solid #FFFFFF;
    }
    .summary-box {
        background-color: #1E3A5F;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #FFFFFF;
        border: 2px solid #1E88E5;
    }
    
    /* Player name */
    .player-name {
        font-size: 1.2rem;
        font-weight: 700;
        color: #FFFFFF;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    /* Stat line */
    .stat-line {
        background-color: #ECF0F1;
        color: #2C3E50;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.95rem;
        display: inline-block;
        font-weight: 600;
        border: 1px solid #1E88E5;
    }
    
    /* Buttons - FIXED */
    div.stButton > button:first-child {
        width: 100%;
        border-radius: 20px;
        font-weight: 600;
        background-color: #1E88E5 !important;
        color: #FFFFFF !important;
        border: 2px solid #FFFFFF !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #0D47A1 !important;
        color: #FFFFFF !important;
        border: 2px solid #FFFFFF !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #FFFFFF;
        font-size: 0.9rem;
        padding: 1rem;
        background-color: #2C3E50;
        border-radius: 10px;
        margin-top: 2rem;
        border: 1px solid #1E88E5;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #2C3E50;
    }
    
    /* Text colors */
    p, span, div, label {
        color: #FFFFFF !important;
    }
    
    /* Select box */
    .stSelectbox label, .stMultiselect label {
        color: #FFFFFF !important;
        font-weight: 600;
    }
    
    /* Success/Error messages */
    .stAlert {
        background-color: #2C3E50 !important;
        color: #FFFFFF !important;
        border: 1px solid #1E88E5 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'picks' not in st.session_state:
    st.session_state.picks = []
if 'entry_amount' not in st.session_state:
    st.session_state.entry_amount = 10.0
if 'auto_select' not in st.session_state:
    st.session_state.auto_select = True
if 'show_recommended' not in st.session_state:
    st.session_state.show_recommended = False
if 'api_status' not in st.session_state:
    st.session_state.api_status = {
        'prizepicks': 'checking',
        'odds_api': 'checking'
    }

# ===================================================
# THE-ODDS-API KEY
# ===================================================

ODDS_API_KEY = "047afdffc14ecda16cb02206a22070c4"

# ===================================================
# COMPLETE SPORT MAPPING - ALL LEAGUES
# ===================================================

SPORT_MAPPING = {
    # MLB
    '1': {'name': 'MLB', 'emoji': '⚾', 'badge': 'badge-mlb'},
    
    # MMA
    '12': {'name': 'MMA', 'emoji': '🥊', 'badge': 'badge-mma'},
    
    # Esports / Gaming
    '121': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    '145': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    '159': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    '161': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    '174': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    '176': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    '265': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    '383': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    '80': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    '82': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    '84': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    
    # Golf
    '131': {'name': 'Golf', 'emoji': '⛳', 'badge': 'badge-pga'},
    
    # MLB Season
    '190': {'name': 'MLB', 'emoji': '⚾', 'badge': 'badge-mlb'},
    
    # NBA Quarters
    '192': {'name': 'NBA', 'emoji': '🏀', 'badge': 'badge-nba'},
    
    # College Basketball
    '20': {'name': 'CBB', 'emoji': '🏀', 'badge': 'badge-cbb'},
    '290': {'name': 'CBB', 'emoji': '🏀', 'badge': 'badge-cbb'},
    
    # Curling
    '277': {'name': 'Curling', 'emoji': '🥌', 'badge': 'badge-other'},
    
    # Handball
    '284': {'name': 'Handball', 'emoji': '🤾', 'badge': 'badge-other'},
    
    # Unrivaled
    '288': {'name': 'Unrivaled', 'emoji': '🏀', 'badge': 'badge-unrivaled'},
    
    # Olympic Hockey
    '379': {'name': 'Olympic Hockey', 'emoji': '🏒', 'badge': 'badge-ohockey'},
    
    # NASCAR
    '4': {'name': 'NASCAR', 'emoji': '🏎️', 'badge': 'badge-nascar'},
    
    # Boxing
    '42': {'name': 'Boxing', 'emoji': '🥊', 'badge': 'badge-mma'},
    
    # MLB
    '43': {'name': 'MLB', 'emoji': '⚾', 'badge': 'badge-mlb'},
    
    # Tennis
    '5': {'name': 'Tennis', 'emoji': '🎾', 'badge': 'badge-tennis'},
    
    # NBA
    '7': {'name': 'NBA', 'emoji': '🏀', 'badge': 'badge-nba'},
    
    # NHL
    '8': {'name': 'NHL', 'emoji': '🏒', 'badge': 'badge-nhl'},
    
    'default': {'name': 'Other', 'emoji': '🏆', 'badge': 'badge-other'}
}

# ===================================================
# STRICT PLAYER NAME VALIDATION - FILTER OUT TEAMS
# ===================================================

# List of known team names and patterns
TEAM_INDICATORS = [
    # Soccer teams
    'Nottm Forest', 'Crystal Palace', 'St. Pauli', 'Manchester', 'Liverpool', 
    'Chelsea', 'Arsenal', 'Tottenham', 'Newcastle', 'Leicester', 'Everton',
    'Wolverhampton', 'Southampton', 'Brighton', 'West Ham', 'Aston Villa',
    'Brentford', 'Fulham', 'Bournemouth', 'Nottingham', 'Wolves', 'Leeds',
    'Sheffield', 'Middlesbrough', 'Blackburn', 'Preston', 'Hull', 'Sunderland',
    'Birmingham', 'Norwich', 'Watford', 'Stoke', 'QPR', 'Millwall', 'Cardiff',
    'Swansea', 'Bristol', 'Reading', 'Coventry', 'Rotherham', 'Plymouth',
    'Ipswich', 'Oxford', 'Cambridge', 'Charlton', 'Derby', 'Portsmouth',
    'Bolton', 'Wigan', 'Blackpool', 'Barnsley', 'Burton', 'Accrington',
    'Morecambe', 'Salford', 'Harrogate', 'Bradford', 'Carlisle', 'Barrow',
    'Tranmere', 'Crewe', 'Doncaster', 'Gillingham', 'Wimbledon', 'Crawley',
    'Swindon', 'Walsall', 'Mansfield', 'Colchester', 'Newport', 'Sutton',
    'Stevenage', 'Hartlepool', 'Halifax', 'Aldershot', 'Bromley', 'Boreham Wood',
    'Dagenham', 'Eastleigh', 'Solihull', 'Maidenhead', 'Wrexham', 'Chesterfield',
    'York', 'Darlington', 'Scunthorpe', 'Boston', 'Kidderminster', 'Hereford',
    'Gloucester', 'Fylde', 'Altrincham', 'Southport', 'Blyth', 'Buxton',
    'Banbury', 'Brackley', 'Chorley', 'Curzon', 'Darlington', 'Farsley',
    'Gateshead', 'Guiseley', 'Leamington', 'Nuneaton', 'Peterborough Sports',
    'Rushall', 'South Shields', 'Spennymoor', 'Warrington', 'Worksop',
    
    # Soccer patterns
    'FC', 'United', 'City', 'Rovers', 'County', 'Albion', 'Athletic',
    'Wanderers', 'Town', 'Forest', 'Villa', 'Palace', 'Hotspur', 'Ham',
    'North End', 'Orient', 'Vale', 'Dale', 'Ville', 'Star', 'Centenary',
    'All Stars', 'Olympic', 'Olympiakos', 'PAOK', 'Panathinaikos', 'AEK',
    'Fenerbahce', 'Galatasaray', 'Besiktas', 'Trabzonspor', 'Basaksehir',
    'Ajax', 'PSV', 'Feyenoord', 'AZ', 'Twente', 'Utrecht', 'Sparta',
    'Heerenveen', 'NEC', 'Willem II', 'Go Ahead', 'Heracles', 'Fortuna',
    'Volendam', 'Emmen', 'RKC', 'Excelsior', 'Almere', 'Jong', 'Young Boys',
    'Basel', 'Luzern', 'St. Gallen', 'Sion', 'Lugano', 'Lausanne',
    'Winterthur', 'Grasshopper', 'Servette', 'Zurich', 'Thun', 'Aarau',
    'Schaffhausen', 'Bellinzona', 'Wil', 'Vaduz', 'Rapperswil', 'Baden',
    'Breitenrain', 'Cham', 'Delemont', 'Kriens', 'Stade Lausanne',
    'Xamax', 'Etoile', 'Carouge', 'SLO', 'Brussels', 'Genk', 'Gent',
    'Antwerp', 'Union', 'Brugge', 'Standard', 'Mechelen', 'Westerlo',
    'Eupen', 'Kortrijk', 'OH Leuven', 'Charleroi', 'Cercle', 'Zulte',
    'Waregem', 'Dender', 'Lommel', 'Deinze', 'Patro', 'Francs Borains',
    'RWDM', 'Molenbeek', 'Beerschot', 'Lierse', 'Thes', 'Dessel',
    'Heist', 'Hoogstraten', 'Kapellen', 'Olympia', 'Pepingen',
    'Rebecq', 'Sint-Eloois', 'Tienen', 'Turnhout', 'Ursel', 'Wezel',
    
    # Other sports teams
    'All Blacks', 'Wallabies', 'Springboks', 'Lions', 'Sharks', 'Bulls',
    'Stormers', 'Hurricanes', 'Chiefs', 'Crusaders', 'Highlanders', 'Blues',
    'Brumbies', 'Reds', 'Waratahs', 'Force', 'Rebels', 'Sunwolves',
    'Dragons', 'Ospreys', 'Scarlets', 'Cardiff', 'Edinburgh', 'Glasgow',
    'Leinster', 'Munster', 'Ulster', 'Connacht', 'Benetton', 'Zebre',
    'Bath', 'Exeter', 'Gloucester', 'Harlequins', 'Leicester', 'Newcastle',
    'Northampton', 'Sale', 'Saracens', 'Wasps', 'Worcester', 'Bristol',
    'London Irish', 'London Welsh', 'London Scottish', 'Richmond',
    'Blackheath', 'Rosslyn Park', 'Plymouth Albion', 'Cornish Pirates',
    'Jersey Reds', 'Ealing', 'Bedford', 'Coventry', 'Doncaster', 'Ampthill',
    'Caldy', 'Cambridge', 'Chinnor', 'Darlington', 'Hartpury', 'Rams',
    'Richmond', 'Rosslyn', 'Sale FC', 'Sheffield', 'Taunton', 'Tonbridge',
]

def is_player_name(name):
    """Strict check for real player names only - filter out teams"""
    if not name or len(name) < 5:
        return False
    
    # List of team codes (3-letter abbreviations)
    team_codes = [
        'ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND',
        'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHX',
        'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS',
        'ANA', 'ARI', 'BUF', 'CGY', 'CAR', 'CBJ', 'EDM', 'FLA', 'LAK', 'MTL', 'NSH', 'NJD',
        'NYI', 'NYR', 'OTT', 'PIT', 'SJS', 'SEA', 'STL', 'TBL', 'VAN', 'VGK', 'WPG',
        'ARS', 'CHE', 'LIV', 'MCI', 'MUN', 'TOT', 'EVE', 'NEW', 'LEI', 'WHU', 'AVL', 'SOU',
        'WOL', 'BHA', 'BUR', 'CRY', 'FUL', 'BRE', 'BOU', 'NOT', 'LEE', 'SHU', 'MID', 'HUL',
        'SUN', 'BLA', 'BIR', 'NOR', 'WAT', 'STK', 'QPR', 'MIL', 'CAR', 'SWA', 'BRI', 'REA',
        'COV', 'ROT', 'PLY', 'IPS', 'OXF', 'CAM', 'CHA', 'POR', 'BOL', 'WIG', 'BAR', 'SAL',
    ]
    
    # Check if it's a team code
    if name.upper() in team_codes:
        return False
    
    # Check if it's a single word and all caps (likely a team)
    if name.isupper() and len(name) <= 6:
        return False
    
    # Check if it matches any known team names
    for team in TEAM_INDICATORS:
        if team.lower() in name.lower():
            return False
    
    # Check for common team patterns
    name_lower = name.lower()
    team_patterns = [' fc', ' united', ' city', ' rovers', ' county', ' albion', 
                     ' athletic', ' wanderers', ' town', ' forest', ' villa', 
                     ' palace', ' hotspur', ' ham', ' north end', ' orient', 
                     ' vale', ' dale', ' star', ' olympic', ' olympiakos', 
                     ' fenerbahce', ' galatasaray', ' besiktas', ' ajax', ' psv', 
                     ' feyenoord', ' young boys', ' basel', ' luzern', ' st. gallen',
                     ' grasshopper', ' servette', ' zurich', ' thun', ' vaduz']
    
    for pattern in team_patterns:
        if pattern in name_lower:
            return False
    
    # Must have at least a first and last name
    parts = name.split()
    if len(parts) < 2:
        return False
    
    # Each part should be at least 2 characters
    for part in parts:
        if len(part) < 2:
            return False
        # Check for initials (like "L. James")
        if len(part) == 2 and part[1] == '.':
            continue
    
    # If it has a number, likely not a player
    if any(char.isdigit() for char in name):
        return False
    
    return True

# ===================================================
# API STATUS CHECK
# ===================================================

def check_apis():
    """Check status of both APIs"""
    pp_status = 'red'
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://app.prizepicks.com/',
            'Origin': 'https://app.prizepicks.com',
            'Connection': 'keep-alive',
        }
        response = requests.get("https://api.prizepicks.com/projections", headers=headers, timeout=10)
        if response.status_code == 200:
            pp_status = 'green'
        elif response.status_code == 403:
            pp_status = 'yellow'
        else:
            pp_status = 'red'
    except:
        pp_status = 'red'
    
    odds_status = 'red'
    try:
        url = f"https://api.the-odds-api.com/v4/sports/?apiKey={ODDS_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            odds_status = 'green'
        else:
            odds_status = 'yellow'
    except:
        odds_status = 'red'
    
    return {'prizepicks': pp_status, 'odds_api': odds_status}

# ===================================================
# INJURY REPORT
# ===================================================

@st.cache_data(ttl=3600)
def fetch_injury_report():
    injuries = {
        'Kevin Durant': {'status': 'Active'},
        'Karl-Anthony Towns': {'status': 'Active'},
        'Dillon Brooks': {'status': 'Active'},
        'Desmond Bane': {'status': 'Active'},
        'Cade Cunningham': {'status': 'Active'},
        'Anthony Black': {'status': 'Active'},
        'Devin Booker': {'status': 'OUT'},
        'Franz Wagner': {'status': 'OUT'},
        'Jalen Suggs': {'status': 'Questionable'},
        'LeBron James': {'status': 'Active'},
        'Stephen Curry': {'status': 'Active'},
        'Luka Doncic': {'status': 'Active'},
        'Giannis Antetokounmpo': {'status': 'Active'},
        'Joel Embiid': {'status': 'Active'},
        'Nikola Jokic': {'status': 'Active'},
        'Shai Gilgeous-Alexander': {'status': 'Active'},
    }
    return injuries

def get_player_injury_status(player_name, injuries_dict):
    for name, info in injuries_dict.items():
        if name.lower() in player_name.lower():
            return info
    return {'status': 'Active'}

# ===================================================
# HIT RATE CALCULATOR
# ===================================================

def calculate_projected_hit_rate(line, sport, injury_status):
    base_rates = {
        'NBA': 0.52,
        'NHL': 0.51,
        'MLB': 0.53,
        'CBB': 0.51,
        'Soccer': 0.50,
        'PGA': 0.48,
        'Golf': 0.48,
        'Tennis': 0.50,
        'MMA': 0.49,
        'Boxing': 0.49,
        'Esports': 0.52,
        'NASCAR': 0.50,
        'Olympic Hockey': 0.51,
        'Curling': 0.50,
        'Handball': 0.50,
        'Unrivaled': 0.50,
    }
    
    base_rate = base_rates.get(sport, 0.51)
    
    if line > 30:
        line_factor = 0.96
    elif line > 20:
        line_factor = 0.98
    elif line > 10:
        line_factor = 1.0
    else:
        line_factor = 1.02
    
    injury_factor = 1.0
    if injury_status['status'] == 'OUT':
        injury_factor = 0.3
    elif injury_status['status'] == 'Questionable':
        injury_factor = 0.8
    
    random_factor = random.uniform(0.94, 1.06)
    
    hit_rate = base_rate * line_factor * injury_factor * random_factor
    hit_rate = min(hit_rate, 0.75)
    hit_rate = max(hit_rate, 0.25)
    
    return hit_rate

# ===================================================
# PRIZEPICKS API - FIXED
# ===================================================

@st.cache_data(ttl=300)
def fetch_prizepicks_projections():
    url = "https://api.prizepicks.com/projections"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://app.prizepicks.com/',
        'Origin': 'https://app.prizepicks.com',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
    }
    
    try:
        time.sleep(0.5)
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            st.session_state.api_status['prizepicks'] = 'green'
            return response.json()
        elif response.status_code == 403:
            st.session_state.api_status['prizepicks'] = 'yellow'
            return None
        else:
            st.session_state.api_status['prizepicks'] = 'red'
            return None
            
    except Exception as e:
        st.session_state.api_status['prizepicks'] = 'red'
        return None

@st.cache_data(ttl=300)
def get_player_projections_only():
    """Get ONLY player props, no team props"""
    data = fetch_prizepicks_projections()
    
    if not data:
        return pd.DataFrame()
    
    projections = []
    unknown_leagues = set()
    filtered_teams = []
    
    for item in data.get('data', []):
        try:
            attrs = item.get('attributes', {})
            line_score = attrs.get('line_score')
            if line_score is None:
                continue
            
            player_name = (attrs.get('name') or attrs.get('description') or '').strip()
            if not player_name:
                continue
            
            # STRICT filtering - only real player names
            if not is_player_name(player_name):
                filtered_teams.append(player_name)
                continue
            
            league_id = 'default'
            league_rel = item.get('relationships', {}).get('league', {}).get('data', {})
            if league_rel:
                league_id = str(league_rel.get('id', 'default'))
            
            sport_info = SPORT_MAPPING.get(league_id, SPORT_MAPPING['default'])
            
            # Track unknown leagues for debugging
            if league_id not in SPORT_MAPPING and league_id != 'default':
                unknown_leagues.add(f"{league_id}: {player_name[:30]}")
            
            stat_type = attrs.get('stat_type') or 'Unknown'
            game_id = attrs.get('game_id', '')
            
            projections.append({
                'league_id': league_id,
                'sport': sport_info['name'],
                'sport_emoji': sport_info['emoji'],
                'badge_class': sport_info['badge'],
                'player_name': player_name,
                'line': float(line_score),
                'stat_type': stat_type,
                'game_id': game_id,
            })
        except:
            continue
    
    # Store debug info
    if unknown_leagues:
        st.session_state.unknown_leagues = unknown_leagues
    if filtered_teams:
        st.session_state.filtered_teams = list(set(filtered_teams))[:20]
    
    return pd.DataFrame(projections)

# ===================================================
# MAIN APP
# ===================================================

current_time = get_central_time()

# Check API status
st.session_state.api_status = check_apis()

# Header
st.markdown('<p class="main-header">🏀 PrizePicks Player Props Only</p>', unsafe_allow_html=True)

# API Status
st.markdown('<div class="api-status">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    pp_dot = st.session_state.api_status['prizepicks']
    status_text = "Connected" if pp_dot == 'green' else "Limited" if pp_dot == 'yellow' else "Offline"
    st.markdown(f"""
    <div class='api-status-item'>
        <span class='status-dot {pp_dot}'></span>
        <span><strong>PrizePicks:</strong> {status_text}</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    odds_dot = st.session_state.api_status['odds_api']
    status_text = "Connected" if odds_dot == 'green' else "Limited" if odds_dot == 'yellow' else "Offline"
    st.markdown(f"""
    <div class='api-status-item'>
        <span class='status-dot {odds_dot}'></span>
        <span><strong>Odds API:</strong> {status_text}</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='api-status-item'>
        <span>🕐</span>
        <span><strong>Updated:</strong> {current_time.strftime('%I:%M:%S %p CT')}</span>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.session_state.debug_mode = st.checkbox("🔧 Debug Mode", value=False)

st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    num_legs = st.selectbox("Number of Legs", [6, 5, 4, 3, 2], index=0)
    st.session_state.entry_amount = st.number_input("Entry Amount ($)", 1.0, 100.0, 10.0)
    
    st.markdown("---")
    st.markdown("### 🤖 Auto Features")
    st.session_state.auto_select = st.checkbox("Auto-select best picks", value=True)
    st.session_state.show_recommended = st.checkbox("Show only recommended ( >54.15%)", value=False)
    
    st.markdown("---")
    st.markdown("### 📊 6-Leg Flex")
    st.markdown("**Break-even:** 54.15% per pick")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Load data
with st.spinner("Loading player props from PrizePicks..."):
    df = get_player_projections_only()
    injuries_dict = fetch_injury_report()

# Show filtered teams in debug mode
if st.session_state.debug_mode and 'filtered_teams' in st.session_state:
    with st.sidebar.expander("🚫 Filtered Out Teams", expanded=False):
        for team in st.session_state.filtered_teams[:10]:
            st.write(f"• {team}")

# If API fails, use sample data
if df.empty:
    st.info("📢 PrizePicks API limited - Using sample player props")
    
    sample_data = [
        {'sport': 'NBA', 'sport_emoji': '🏀', 'badge_class': 'badge-nba', 'player_name': 'LeBron James', 'line': 25.5, 'stat_type': 'Points'},
        {'sport': 'NBA', 'sport_emoji': '🏀', 'badge_class': 'badge-nba', 'player_name': 'Stephen Curry', 'line': 26.5, 'stat_type': 'Points'},
        {'sport': 'NBA', 'sport_emoji': '🏀', 'badge_class': 'badge-nba', 'player_name': 'Kevin Durant', 'line': 24.5, 'stat_type': 'Points'},
        {'sport': 'NBA', 'sport_emoji': '🏀', 'badge_class': 'badge-nba', 'player_name': 'Giannis Antetokounmpo', 'line': 32.5, 'stat_type': 'PRA'},
        {'sport': 'NHL', 'sport_emoji': '🏒', 'badge_class': 'badge-nhl', 'player_name': 'Connor McDavid', 'line': 1.5, 'stat_type': 'Points'},
        {'sport': 'MLB', 'sport_emoji': '⚾', 'badge_class': 'badge-mlb', 'player_name': 'Shohei Ohtani', 'line': 1.5, 'stat_type': 'Hits'},
        {'sport': 'Tennis', 'sport_emoji': '🎾', 'badge_class': 'badge-tennis', 'player_name': 'Novak Djokovic', 'line': 12.5, 'stat_type': 'Games'},
        {'sport': 'Soccer', 'sport_emoji': '⚽', 'badge_class': 'badge-soccer', 'player_name': 'Lionel Messi', 'line': 0.5, 'stat_type': 'Goals'},
        {'sport': 'PGA', 'sport_emoji': '⛳', 'badge_class': 'badge-pga', 'player_name': 'Scottie Scheffler', 'line': 68.5, 'stat_type': 'Round Score'},
        {'sport': 'MMA', 'sport_emoji': '🥊', 'badge_class': 'badge-mma', 'player_name': 'Jon Jones', 'line': 45.5, 'stat_type': 'Strikes'},
    ]
    
    df = pd.DataFrame(sample_data)

if not df.empty:
    # Add injury status
    df['injury_status'] = df['player_name'].apply(lambda x: get_player_injury_status(x, injuries_dict))
    
    # Calculate hit rates
    df['hit_rate'] = df.apply(lambda row: calculate_projected_hit_rate(
        row['line'], row['sport'], row['injury_status']), axis=1)
    df['recommendation'] = df['hit_rate'].apply(lambda x: 'MORE' if x > 0.5415 else 'LESS')
    df = df.sort_values('hit_rate', ascending=False)

# Sidebar stats
st.sidebar.markdown(f"**Player Props:** {len(df):,}")
st.sidebar.markdown(f"**MORE:** {len(df[df['recommendation']=='MORE']):,}")
st.sidebar.markdown(f"**LESS:** {len(df[df['recommendation']=='LESS']):,}")

# Show all available sports in sidebar
with st.sidebar.expander("📊 Available Sports", expanded=True):
    for sport, count in df['sport'].value_counts().items():
        pct = (count/len(df))*100
        st.markdown(f"**{sport}**: {count} props ({pct:.1f}%)")

# Debug section for unknown leagues
if st.session_state.debug_mode and 'unknown_leagues' in st.session_state:
    with st.expander("🔍 Debug: Unknown League IDs", expanded=True):
        st.markdown('<div style="background-color:#1E1E1E; color:#00FF00; padding:1rem; border-radius:5px; font-family:monospace;">', unsafe_allow_html=True)
        for item in list(st.session_state.unknown_leagues)[:20]:
            st.write(item)
        st.markdown('</div>', unsafe_allow_html=True)

# Main content
col_left, col_right = st.columns([1.3, 0.7])

with col_left:
    st.markdown('<p class="section-header">📋 Available Player Props</p>', unsafe_allow_html=True)
    
    # Sport filter
    sports_list = sorted(df['sport'].unique())
    selected_sports = st.multiselect("Select Sports", sports_list, default=[])
    
    # Apply filters
    filtered_df = df.copy()
    if selected_sports:
        filtered_df = filtered_df[filtered_df['sport'].isin(selected_sports)]
    else:
        filtered_df = df.copy()
    
    if st.session_state.show_recommended and not filtered_df.empty:
        filtered_df = filtered_df[filtered_df['hit_rate'] > 0.5415]
    
    st.caption(f"**Showing {len(filtered_df)} player props**")
    
    # Auto-select
    if st.session_state.auto_select and len(st.session_state.picks) == 0 and len(filtered_df) >= num_legs:
        for _, row in filtered_df.head(num_legs).iterrows():
            st.session_state.picks.append({
                'sport_emoji': row['sport_emoji'],
                'sport': row['sport'],
                'badge_class': row['badge_class'],
                'player': row['player_name'],
                'stat': row['stat_type'],
                'line': row['line'],
                'pick': row['recommendation'],
                'hit_rate': row['hit_rate'],
            })
        st.rerun()
    
    # Display props
    for idx, row in filtered_df.head(30).iterrows():
        with st.container():
            hit_class = "hit-high" if row['hit_rate'] > 0.5415 else "hit-low"
            badge_class = row['badge_class']
            
            st.markdown(f"""
            <div class='prop-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span class='player-name'>{row['sport_emoji']} {row['player_name']}</span>
                        <span class='{badge_class}' style='margin-left: 8px;'>{row['sport']}</span>
                    </div>
                    <span class='{hit_class}'>{row['hit_rate']*100:.1f}%</span>
                </div>
                <div style='margin: 8px 0;'>
                    <span class='stat-line'>{row['stat_type']}: {row['line']:.1f}</span>
                </div>
                <div style='display: flex; gap: 10px; align-items: center;'>
                    <span class='{"more-badge" if row["recommendation"]=="MORE" else "less-badge"}'>
                        {row['recommendation']}
                    </span>
            """, unsafe_allow_html=True)
            
            if st.button("➕ Add", key=f"add_{idx}"):
                if len(st.session_state.picks) < num_legs:
                    st.session_state.picks.append({
                        'sport_emoji': row['sport_emoji'],
                        'sport': row['sport'],
                        'badge_class': row['badge_class'],
                        'player': row['player_name'],
                        'stat': row['stat_type'],
                        'line': row['line'],
                        'pick': row['recommendation'],
                        'hit_rate': row['hit_rate'],
                    })
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<p class="section-header">📝 Your Entry</p>', unsafe_allow_html=True)
    
    if st.session_state.picks:
        for i, pick in enumerate(st.session_state.picks):
            with st.container():
                st.markdown(f"""
                <div class='entry-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <span class='player-name'>{pick['sport_emoji']} {pick['player']}</span>
                        <span class='{"more-badge" if pick["pick"]=="MORE" else "less-badge"}' style='padding:0.2rem 0.8rem; font-size:0.8rem;'>
                            {pick['pick']}
                        </span>
                    </div>
                    <div style='margin: 0.5rem 0;'>{pick['stat']} {pick['line']:.1f}</div>
                    <div style='color: #FFFFFF; background-color: {"#2E7D32" if pick["hit_rate"] > 0.5415 else "#C62828"}; padding: 0.2rem 0.8rem; border-radius: 20px; display: inline-block;'>
                        Hit rate: {pick['hit_rate']*100:.1f}%
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("❌ Remove", key=f"remove_{i}"):
                    st.session_state.picks.pop(i)
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        if len(st.session_state.picks) == num_legs:
            avg_hit = np.mean([p['hit_rate'] for p in st.session_state.picks])
            
            if num_legs == 6:
                from scipy import stats
                prob_4 = sum([stats.binom.pmf(k, 6, avg_hit) for k in range(4, 7)])
                prob_5 = sum([stats.binom.pmf(k, 6, avg_hit) for k in range(5, 7)])
                prob_6 = stats.binom.pmf(6, 6, avg_hit)
                
                ev = (prob_4 * st.session_state.entry_amount * 0.4 +
                      prob_5 * st.session_state.entry_amount * 2 +
                      prob_6 * st.session_state.entry_amount * 25)
                
                roi = ((ev - st.session_state.entry_amount) / st.session_state.entry_amount) * 100
                
                st.markdown(f"""
                <div class='summary-box'>
                    <h4 style='margin:0 0 1rem 0;'>🎯 Entry Summary</h4>
                    <p><strong>Avg Hit Rate:</strong> {avg_hit*100:.1f}%</p>
                    <p><strong>Expected Return:</strong> ${ev:.2f}</p>
                    <p><strong>ROI:</strong> {roi:.1f}%</p>
                    <p style='color: {"#2E7D32" if roi>0 else "#C62828"}; font-weight:bold; font-size:1.2rem; background-color: #FFFFFF; padding: 0.3rem 1rem; border-radius: 25px; display: inline-block;'>
                        {'✅ +EV' if roi>0 else '⚠️ -EV'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        if st.button("🗑️ Clear All", type="primary", use_container_width=True):
            st.session_state.picks = []
            st.rerun()
    else:
        st.info("👆 Add player props from the left panel")

# Footer
st.markdown("---")
st.markdown(f"""
<div class='footer'>
    <p>🏀 {len(df):,} player props | 
    <span style='color:#FFFFFF; background-color:#2E7D32; padding:0.2rem 0.5rem; border-radius:20px;'>{len(df[df['recommendation']=='MORE']):,} MORE</span> / 
    <span style='color:#FFFFFF; background-color:#C62828; padding:0.2rem 0.5rem; border-radius:20px;'>{len(df[df['recommendation']=='LESS']):,} LESS</span>
    </p>
</div>
""", unsafe_allow_html=True)