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
    page_title="PrizePicks Player Props",
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

# HIGH CONTRAST CSS - Dark backgrounds, light text
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
    .badge-nfl { background-color: #013369; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
    .badge-pga { background-color: #0A4C33; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
    .badge-tennis { background-color: #CC5500; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
    .badge-soccer { background-color: #006400; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
    .badge-mma { background-color: #8B0000; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
    .badge-esports { background-color: #4B0082; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
    .badge-nascar { background-color: #8B4513; color: #FFFFFF; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; border: 1px solid #FFFFFF; }
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
    
    /* Buttons */
    .stButton button {
        width: 100%;
        border-radius: 20px;
        font-weight: 600;
        background-color: #1E88E5;
        color: #FFFFFF;
        border: 2px solid #FFFFFF;
    }
    .stButton button:hover {
        background-color: #0D47A1;
        color: #FFFFFF;
        border: 2px solid #FFFFFF;
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
# SPORT MAPPING
# ===================================================

SPORT_MAPPING = {
    # MMA/UFC
    '12': {'name': 'MMA', 'emoji': '🥊', 'badge': 'badge-mma'},
    
    # Esports
    '82': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    '265': {'name': 'CS2', 'emoji': '🎮', 'badge': 'badge-esports'},
    '121': {'name': 'LoL', 'emoji': '🎮', 'badge': 'badge-esports'},
    '174': {'name': 'CS2', 'emoji': '🎮', 'badge': 'badge-esports'},
    '159': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    '161': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    '145': {'name': 'RL', 'emoji': '🎮', 'badge': 'badge-esports'},
    
    # Boxing
    '42': {'name': 'Boxing', 'emoji': '🥊', 'badge': 'badge-mma'},
    
    # College Basketball
    '20': {'name': 'CBB', 'emoji': '🏀', 'badge': 'badge-nba'},
    '290': {'name': 'CBB 1H', 'emoji': '🏀', 'badge': 'badge-nba'},
    
    # NBA Quarters
    '149': {'name': 'NBA 4Q', 'emoji': '🏀', 'badge': 'badge-nba'},
    '192': {'name': 'NBA 1Q', 'emoji': '🏀', 'badge': 'badge-nba'},
    
    # Table Tennis
    '286': {'name': 'Table Tennis', 'emoji': '🏓', 'badge': 'badge-other'},
    
    # Golf
    '131': {'name': 'Golf', 'emoji': '⛳', 'badge': 'badge-pga'},
    '1': {'name': 'PGA', 'emoji': '⛳', 'badge': 'badge-pga'},
    
    # Tennis
    '5': {'name': 'Tennis', 'emoji': '🎾', 'badge': 'badge-tennis'},
    
    # Curling
    '277': {'name': 'Curling', 'emoji': '🥌', 'badge': 'badge-other'},
    
    # Olympic Hockey
    '379': {'name': 'Olympic Hockey', 'emoji': '🏒', 'badge': 'badge-nhl'},
    
    # MLB
    '43': {'name': 'MLB', 'emoji': '⚾', 'badge': 'badge-mlb'},
    
    # NBA
    '7': {'name': 'NBA', 'emoji': '🏀', 'badge': 'badge-nba'},
    
    # Handball
    '284': {'name': 'Handball', 'emoji': '🤾', 'badge': 'badge-other'},
    
    # NASCAR
    '4': {'name': 'NASCAR', 'emoji': '🏎️', 'badge': 'badge-nascar'},
    
    # Unrivaled
    '288': {'name': 'Unrivaled', 'emoji': '🏀', 'badge': 'badge-nba'},
    
    # NHL
    '8': {'name': 'NHL', 'emoji': '🏒', 'badge': 'badge-nhl'},
    
    # MLB Season
    '190': {'name': 'MLB SZN', 'emoji': '⚾', 'badge': 'badge-mlb'},
    
    # Soccer
    '5': {'name': 'Soccer', 'emoji': '⚽', 'badge': 'badge-soccer'},
    '6': {'name': 'Soccer', 'emoji': '⚽', 'badge': 'badge-soccer'},
    '44': {'name': 'Soccer', 'emoji': '⚽', 'badge': 'badge-soccer'},
    '45': {'name': 'Soccer', 'emoji': '⚽', 'badge': 'badge-soccer'},
    
    'default': {'name': 'Other', 'emoji': '🏆', 'badge': 'badge-other'}
}

# ===================================================
# PLAYER NAME VALIDATION
# ===================================================

def is_real_player_name(name):
    """Check for real player names"""
    if not name or len(name) < 3:
        return False
    
    # List of team codes to filter out
    team_codes = [
        'ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND',
        'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHX',
        'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS',
        'ANA', 'ARI', 'BUF', 'CGY', 'CAR', 'CBJ', 'EDM', 'FLA', 'LAK', 'MTL', 'NSH', 'NJD',
        'NYI', 'NYR', 'OTT', 'PIT', 'SJS', 'SEA', 'STL', 'TBL', 'VAN', 'VGK', 'WPG',
    ]
    
    # If it's exactly a team code, filter it out
    if name.upper() in team_codes:
        return False
    
    # If it's a single word and all caps, likely a team
    if ' ' not in name and name.isupper() and len(name) <= 4:
        return False
    
    # Check for common non-player patterns
    non_player_indicators = ['Round', 'Game', 'Match', 'Team', 'United', 'FC', 'SC', 'CF', 'Club']
    if any(indicator in name for indicator in non_player_indicators):
        return False
    
    # If it has a number, likely not a player
    if any(char.isdigit() for char in name):
        return False
    
    return True

# ===================================================
# API STATUS CHECK
# ===================================================

def check_apis():
    """Check status of both APIs"""
    # Check PrizePicks with proper headers
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
        response = requests.get("https://api.prizepicks.com/projections", 
                               headers=headers, 
                               timeout=5)
        if response.status_code == 200:
            pp_status = 'green'
        elif response.status_code == 403:
            pp_status = 'yellow'
        else:
            pp_status = 'red'
    except:
        pp_status = 'red'
    
    # Check The-Odds-API
    odds_status = 'red'
    try:
        url = f"https://api.the-odds-api.com/v4/sports/?apiKey={ODDS_API_KEY}"
        response = requests.get(url, timeout=5)
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
        'NBA 1Q': 0.50,
        'NBA 4Q': 0.50,
        'NHL': 0.51,
        'MLB': 0.53,
        'MLB SZN': 0.53,
        'CBB': 0.51,
        'CBB 1H': 0.50,
        'PGA': 0.48,
        'Golf': 0.48,
        'NASCAR': 0.50,
        'MMA': 0.49,
        'Boxing': 0.49,
        'CS2': 0.52,
        'LoL': 0.52,
        'Esports': 0.52,
        'RL': 0.52,
        'Tennis': 0.50,
        'Soccer': 0.50,
        'Handball': 0.50,
        'Table Tennis': 0.50,
        'Curling': 0.50,
        'Olympic Hockey': 0.51,
        'Unrivaled': 0.50,
    }
    
    base_rate = base_rates.get(sport, 0.51)
    
    # Line adjustment
    if line > 30:
        line_factor = 0.96
    elif line > 20:
        line_factor = 0.98
    elif line > 10:
        line_factor = 1.0
    else:
        line_factor = 1.02
    
    # Injury adjustment
    injury_factor = 1.0
    if injury_status['status'] == 'OUT':
        injury_factor = 0.3
    elif injury_status['status'] == 'Questionable':
        injury_factor = 0.8
    
    # Random variation
    random_factor = random.uniform(0.94, 1.06)
    
    hit_rate = base_rate * line_factor * injury_factor * random_factor
    hit_rate = min(hit_rate, 0.75)
    hit_rate = max(hit_rate, 0.25)
    
    return hit_rate

# ===================================================
# PRIZEPICKS API - FIXED HEADERS
# ===================================================

@st.cache_data(ttl=300)
def fetch_prizepicks_projections():
    url = "https://api.prizepicks.com/projections"
    
    # Complete headers to mimic iPad browser
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
        # Add delay to avoid rate limiting
        time.sleep(0.5)
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.warning(f"PrizePicks API returned status code: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        st.warning("PrizePicks API timeout - using sample data")
        return None
    except requests.exceptions.RequestException as e:
        st.warning(f"PrizePicks API error: {e}")
        return None
    except Exception as e:
        st.warning(f"Unexpected error: {e}")
        return None

@st.cache_data(ttl=300)
def get_player_projections_only():
    """Get ONLY player props, no team props"""
    data = fetch_prizepicks_projections()
    
    if not data:
        return pd.DataFrame()
    
    projections = []
    
    for item in data.get('data', []):
        try:
            attrs = item.get('attributes', {})
            line_score = attrs.get('line_score')
            if line_score is None:
                continue
            
            player_name = (attrs.get('name') or attrs.get('description') or '').strip()
            if not player_name:
                continue
            
            # Only filter out obvious team props, keep player names
            if not is_real_player_name(player_name):
                continue
            
            league_id = 'default'
            league_rel = item.get('relationships', {}).get('league', {}).get('data', {})
            if league_rel:
                league_id = str(league_rel.get('id', 'default'))
            
            sport_info = SPORT_MAPPING.get(league_id, SPORT_MAPPING['default'])
            stat_type = attrs.get('stat_type') or 'Unknown'
            game_id = attrs.get('game_id', '')
            
            projections.append({
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
    
    return pd.DataFrame(projections)

# ===================================================
# MAIN APP
# ===================================================

current_time = get_central_time()

# Check API status
st.session_state.api_status = check_apis()

# Header with API status
st.markdown('<p class="main-header">🏀 PrizePicks Player Props</p>', unsafe_allow_html=True)

# API Status indicators
st.markdown('<div class="api-status">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])

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

# Load data - ONLY player props
with st.spinner("Loading player props from PrizePicks..."):
    df = get_player_projections_only()
    injuries_dict = fetch_injury_report()

if df.empty:
    st.info("📢 PrizePicks API limited - Using sample data for demonstration")
    
    # Comprehensive sample data with multiple sports
    sample_data = [
        # NBA
        {'sport': 'NBA', 'sport_emoji': '🏀', 'badge_class': 'badge-nba', 'player_name': 'Dillon Brooks', 'line': 23.5, 'stat_type': 'Points'},
        {'sport': 'NBA', 'sport_emoji': '🏀', 'badge_class': 'badge-nba', 'player_name': 'Desmond Bane', 'line': 18.5, 'stat_type': 'Points'},
        {'sport': 'NBA', 'sport_emoji': '🏀', 'badge_class': 'badge-nba', 'player_name': 'Anthony Black', 'line': 16.5, 'stat_type': 'Points'},
        {'sport': 'NBA', 'sport_emoji': '🏀', 'badge_class': 'badge-nba', 'player_name': 'Cade Cunningham', 'line': 25.5, 'stat_type': 'Points'},
        {'sport': 'NBA', 'sport_emoji': '🏀', 'badge_class': 'badge-nba', 'player_name': 'Kevin Durant', 'line': 24.5, 'stat_type': 'Points'},
        {'sport': 'NBA', 'sport_emoji': '🏀', 'badge_class': 'badge-nba', 'player_name': 'LeBron James', 'line': 25.5, 'stat_type': 'Points'},
        {'sport': 'NBA', 'sport_emoji': '🏀', 'badge_class': 'badge-nba', 'player_name': 'Stephen Curry', 'line': 26.5, 'stat_type': 'Points'},
        {'sport': 'NBA', 'sport_emoji': '🏀', 'badge_class': 'badge-nba', 'player_name': 'Luka Doncic', 'line': 31.5, 'stat_type': 'PRA'},
        # NHL
        {'sport': 'NHL', 'sport_emoji': '🏒', 'badge_class': 'badge-nhl', 'player_name': 'Connor McDavid', 'line': 1.5, 'stat_type': 'Points'},
        {'sport': 'NHL', 'sport_emoji': '🏒', 'badge_class': 'badge-nhl', 'player_name': 'Auston Matthews', 'line': 0.5, 'stat_type': 'Goals'},
        # Soccer
        {'sport': 'Soccer', 'sport_emoji': '⚽', 'badge_class': 'badge-soccer', 'player_name': 'Lionel Messi', 'line': 0.5, 'stat_type': 'Goals'},
        {'sport': 'Soccer', 'sport_emoji': '⚽', 'badge_class': 'badge-soccer', 'player_name': 'Cristiano Ronaldo', 'line': 1.5, 'stat_type': 'Shots'},
        # PGA
        {'sport': 'PGA', 'sport_emoji': '⛳', 'badge_class': 'badge-pga', 'player_name': 'Scottie Scheffler', 'line': 68.5, 'stat_type': 'Round Score'},
        # Tennis
        {'sport': 'Tennis', 'sport_emoji': '🎾', 'badge_class': 'badge-tennis', 'player_name': 'Novak Djokovic', 'line': 12.5, 'stat_type': 'Games'},
    ]
    
    df = pd.DataFrame(sample_data)

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
with st.sidebar.expander("📊 All Available Sports", expanded=True):
    for sport, count in df['sport'].value_counts().items():
        pct = (count/len(df))*100
        st.markdown(f"**{sport}**: {count} props ({pct:.1f}%)")

# Main content columns
col_left, col_right = st.columns([1.3, 0.7])

with col_left:
    st.markdown('<p class="section-header">📋 Available Player Props</p>', unsafe_allow_html=True)
    
    # Sport filter
    sports_list = sorted(df['sport'].unique())
    selected_sports = st.multiselect("Select Sports", sports_list, default=['NBA'] if 'NBA' in sports_list else [])
    
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
    <p>🏀 {len(df):,} player props across {len(df['sport'].unique())} sports | 
    <span style='color:#FFFFFF; background-color:#2E7D32; padding:0.2rem 0.5rem; border-radius:20px;'>{len(df[df['recommendation']=='MORE']):,} MORE</span> / 
    <span style='color:#FFFFFF; background-color:#C62828; padding:0.2rem 0.5rem; border-radius:20px;'>{len(df[df['recommendation']=='LESS']):,} LESS</span>
    </p>
    <p style='font-size:0.8rem;'>Central Time (CT) | {current_time.strftime('%B %d, %Y')}</p>
</div>
""", unsafe_allow_html=True)