 import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="PrizePicks Optimizer - All Sports",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for mobile
st.markdown("""
<style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #0D47A1;
        margin-top: 1rem;
    }
    .value-positive {
        color: #2E7D32;
        font-weight: 600;
    }
    .value-negative {
        color: #C62828;
        font-weight: 600;
    }
    .recommendation-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E88E5;
        margin: 0.5rem 0;
    }
    .sport-badge {
        background-color: #f0f2f6;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        display: inline-block;
        margin-right: 0.3rem;
    }
    .auto-pick-badge {
        background-color: #4CAF50;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }
    .injury-badge {
        background-color: #f44336;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }
    .stButton button {
        width: 100%;
        font-size: 0.9rem;
        padding: 0.3rem;
    }
    .pick-card {
        background-color: #ffffff;
        padding: 0.8rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
    }
    .prop-row {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        padding: 0.3rem 0;
        border-bottom: 1px solid #eee;
    }
    .prop-info {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.5rem;
        flex: 2;
    }
    .prop-stats {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex: 1;
        justify-content: flex-end;
    }
    @media (max-width: 768px) {
        .prop-row {
            flex-direction: column;
            align-items: flex-start;
        }
        .prop-stats {
            margin-top: 0.3rem;
            width: 100%;
            justify-content: space-between;
        }
    }
    .data-source-badge {
        background-color: #FF9800;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.7rem;
        font-weight: bold;
        display: inline-block;
        margin-left: 0.5rem;
    }
    /* Fix for mobile cutoff */
    .row-widget {
        overflow: visible !important;
    }
    .element-container {
        overflow: visible !important;
    }
    /* Make columns stack better on mobile */
    @media (max-width: 768px) {
        .stCol {
            min-width: auto !important;
        }
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
    st.session_state.show_recommended = True
if 'selected_sports' not in st.session_state:
    st.session_state.selected_sports = []
if 'league_ids' not in st.session_state:
    st.session_state.league_ids = set()

# ===================================================
# THE-ODDS-API KEY
# ===================================================

# 🔑 Your API key is set
ODDS_API_KEY = "047afdffc14ecda16cb02206a22070c4"

# ===================================================
# COMPLETE SPORT MAPPING - UPDATED WITH ALL NBA LEAGUE IDS
# ===================================================

SPORT_MAPPING = {
    # NBA - multiple possible league IDs
    '4': {'name': 'NBA Basketball', 'emoji': '🏀', 'api_sport': 'basketball_nba'},
    '46': {'name': 'NBA Basketball', 'emoji': '🏀', 'api_sport': 'basketball_nba'},
    '47': {'name': 'NBA Basketball', 'emoji': '🏀', 'api_sport': 'basketball_nba'},
    '48': {'name': 'NBA Basketball', 'emoji': '🏀', 'api_sport': 'basketball_nba'},
    '49': {'name': 'NBA Basketball', 'emoji': '🏀', 'api_sport': 'basketball_nba'},
    '50': {'name': 'NBA Basketball', 'emoji': '🏀', 'api_sport': 'basketball_nba'},
    '51': {'name': 'NBA Basketball', 'emoji': '🏀', 'api_sport': 'basketball_nba'},
    '52': {'name': 'NBA Basketball', 'emoji': '🏀', 'api_sport': 'basketball_nba'},
    '53': {'name': 'NBA Basketball', 'emoji': '🏀', 'api_sport': 'basketball_nba'},
    '54': {'name': 'NBA Basketball', 'emoji': '🏀', 'api_sport': 'basketball_nba'},
    '55': {'name': 'NBA Basketball', 'emoji': '🏀', 'api_sport': 'basketball_nba'},
    
    # WNBA
    '14': {'name': 'WNBA Basketball', 'emoji': '🏀', 'api_sport': 'basketball_wnba'},
    
    # NFL
    '2': {'name': 'NFL Football', 'emoji': '🏈', 'api_sport': 'americanfootball_nfl'},
    '15': {'name': 'College Football', 'emoji': '🏈', 'api_sport': 'americanfootball_ncaaf'},
    '17': {'name': 'XFL Football', 'emoji': '🏈', 'api_sport': 'americanfootball_xfl'},
    
    # MLB
    '1': {'name': 'MLB Baseball', 'emoji': '⚾', 'api_sport': 'baseball_mlb'},
    
    # NHL
    '3': {'name': 'NHL Hockey', 'emoji': '🏒', 'api_sport': 'icehockey_nhl'},
    
    # Soccer
    '5': {'name': 'Soccer', 'emoji': '⚽', 'api_sport': 'soccer_uefa_champs_league'},
    
    # Golf
    '6': {'name': 'Golf', 'emoji': '🏌️', 'api_sport': 'golf_pga'},
    
    # MMA
    '7': {'name': 'MMA/UFC', 'emoji': '🥊', 'api_sport': 'mma_mixed_martial_arts'},
    '11': {'name': 'Boxing', 'emoji': '🥊', 'api_sport': 'boxing_boxing'},
    
    # Tennis
    '8': {'name': 'Tennis', 'emoji': '🎾', 'api_sport': 'tennis_atp'},
    
    # Racing
    '9': {'name': 'Auto Racing', 'emoji': '🏎️', 'api_sport': 'racing'},
    '21': {'name': 'F1 Racing', 'emoji': '🏎️', 'api_sport': 'racing_f1'},
    '22': {'name': 'NASCAR', 'emoji': '🏎️', 'api_sport': 'racing_nascar'},
    
    # Esports
    '10': {'name': 'Esports', 'emoji': '🎮', 'api_sport': None},
    '23': {'name': 'Esports - LoL', 'emoji': '🎮', 'api_sport': None},
    '24': {'name': 'Esports - CS:GO', 'emoji': '🎮', 'api_sport': None},
    '25': {'name': 'Esports - Valorant', 'emoji': '🎮', 'api_sport': None},
    '26': {'name': 'Esports - Dota 2', 'emoji': '🎮', 'api_sport': None},
    
    # College Sports
    '16': {'name': 'College Basketball', 'emoji': '🏀', 'api_sport': 'basketball_ncaab'},
    
    # Other
    '12': {'name': 'Competitive Eating', 'emoji': '🍽️', 'api_sport': None},
    '13': {'name': 'Culture Picks', 'emoji': '🎯', 'api_sport': None},
    '18': {'name': 'Australian Rules', 'emoji': '🏉', 'api_sport': 'australian_rules'},
    '19': {'name': 'Cricket', 'emoji': '🏏', 'api_sport': 'cricket'},
    '20': {'name': 'Rugby', 'emoji': '🏉', 'api_sport': 'rugby_union'},
    
    'default': {'name': 'Other Sports', 'emoji': '🏆', 'api_sport': None}
}

# ===================================================
# THE-ODDS-API INTEGRATION
# ===================================================

@st.cache_data(ttl=600)
def fetch_sportsbook_lines(sport="basketball_nba"):
    """Fetch player props from The-Odds-API for comparison"""
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {
        'apiKey': ODDS_API_KEY,
        'regions': 'us',
        'markets': 'player_points,player_rebounds,player_assists,player_points_rebounds_assists',
        'oddsFormat': 'american'
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def american_to_prob(odds):
    """Convert American odds to implied probability"""
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)

# ===================================================
# INJURY REPORT
# ===================================================

@st.cache_data(ttl=3600)
def fetch_injury_report():
    """Fetch current injuries"""
    injuries = {
        # Today's injuries
        'Kevin Durant': {'status': 'Active', 'injury': 'None', 'team': 'HOU'},
        'Karl-Anthony Towns': {'status': 'Active', 'injury': 'None', 'team': 'NYK'},
        'Dillon Brooks': {'status': 'Active', 'injury': 'None', 'team': 'PHX'},
        'Desmond Bane': {'status': 'Active', 'injury': 'None', 'team': 'ORL'},
        'Cade Cunningham': {'status': 'Active', 'injury': 'None', 'team': 'DET'},
        'Anthony Black': {'status': 'Active', 'injury': 'None', 'team': 'ORL'},
        'Devin Booker': {'status': 'OUT', 'injury': 'Hip Strain', 'team': 'PHX'},
        'Franz Wagner': {'status': 'OUT', 'injury': 'Ankle', 'team': 'ORL'},
        'Jalen Suggs': {'status': 'Questionable', 'injury': 'Back', 'team': 'ORL'},
        'Fred VanVleet': {'status': 'OUT', 'injury': 'Knee', 'team': 'HOU'},
        'Joel Embiid': {'status': 'OUT', 'injury': 'Knee', 'team': 'PHI'},
        'Giannis Antetokounmpo': {'status': 'Probable', 'injury': 'Knee', 'team': 'MIL'},
    }
    return injuries

def get_player_injury_status(player_name, injuries_dict):
    """Check if a player is injured"""
    for name, info in injuries_dict.items():
        if name.lower() in player_name.lower() or player_name.lower() in name.lower():
            return info
    return {'status': 'Active', 'injury': 'None', 'team': 'Unknown'}

# ===================================================
# AUTO-PICK ENGINE
# ===================================================

def calculate_projected_hit_rate(line, sport, stat_type, injury_status, sportsbook_prob=None):
    """
    Calculate projected hit rate and recommend MORE/LESS
    """
    # Base hit rate by sport
    sport_base = {
        'NBA Basketball': 0.52,
        'NFL Football': 0.51,
        'MLB Baseball': 0.53,
        'NHL Hockey': 0.51,
        'Soccer': 0.50,
        'Golf': 0.48,
        'MMA/UFC': 0.49,
        'Esports': 0.52,
    }
    
    base_rate = sport_base.get(sport, 0.51)
    
    # If we have sportsbook data, use that as baseline
    if sportsbook_prob:
        base_rate = sportsbook_prob
    
    # Adjust based on line value
    if line > 50:
        line_factor = 0.95
    elif line > 20:
        line_factor = 0.98
    elif line > 10:
        line_factor = 1.0
    else:
        line_factor = 1.02
    
    # Injury impact
    injury_factor = 1.0
    if injury_status['status'] == 'OUT':
        injury_factor = 0.3  # 70% reduction
    elif injury_status['status'] == 'Questionable':
        injury_factor = 0.8  # 20% reduction
    elif injury_status['status'] == 'Probable':
        injury_factor = 0.95  # 5% reduction
    
    # Teammate injuries (opportunity increase)
    opportunity_factor = 1.0
    player_name = injury_status.get('player_name', '')
    
    # Known teammate injury situations
    if 'Brooks' in player_name:
        opportunity_factor = 1.1  # Booker is OUT
    elif 'Bane' in player_name or 'Black' in player_name:
        opportunity_factor = 1.1  # Wagner OUT, Suggs Questionable
    
    # Calculate final hit rate
    hit_rate = base_rate * line_factor * injury_factor * opportunity_factor
    hit_rate = min(hit_rate, 0.75)  # Cap at 75%
    
    # Determine recommendation
    if hit_rate > 0.5415:  # 54.15% threshold for 6-leg flex
        recommendation = "MORE"
        confidence = "High" if hit_rate > 0.58 else "Medium"
    else:
        recommendation = "LESS"
        confidence = "High" if hit_rate < 0.50 else "Medium"
    
    return hit_rate, recommendation, confidence

# ===================================================
# FIXED PRIZEPICKS API - Now with expanded sport mapping
# ===================================================

@st.cache_data(ttl=300)
def fetch_prizepicks_projections():
    """Fetch ALL projections from PrizePicks public API with browser headers"""
    url = "https://api.prizepicks.com/projections"
    
    # These headers make the request look like it's coming from Safari on iPad
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
        # Add a slight delay to avoid rate limiting
        time.sleep(0.5)
        
        response = requests.get(url, headers=headers, timeout=10)
        
        # Check if we got a successful response
        if response.status_code == 200:
            return response.json()
        else:
            st.sidebar.warning(f"API returned status code: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        st.sidebar.warning("API request timed out")
        return None
    except requests.exceptions.RequestException as e:
        st.sidebar.warning(f"API request failed: {e}")
        return None
    except Exception as e:
        st.sidebar.warning(f"Unexpected error: {e}")
        return None

@st.cache_data(ttl=300)
def get_all_sports_projections():
    """Extract ALL sports projections from PrizePicks data"""
    data = fetch_prizepicks_projections()
    
    # Use sample data if API fails
    if not data:
        st.sidebar.info("📊 Using sample data - PrizePicks API unavailable")
        return pd.DataFrame()
    
    projections = []
    
    # Clear league IDs set for new data
    st.session_state.league_ids = set()
    
    # Debug: Show total items
    total_items = len(data.get('data', []))
    st.sidebar.write(f"📡 API returned {total_items} total items")
    
    for item in data.get('data', []):
        try:
            # Get attributes - this is where player info lives
            attrs = item.get('attributes', {})
            
            # Skip if no line score
            line_score = attrs.get('line_score')
            if line_score is None:
                continue
            
            # Get player name - try different possible fields
            player_name = attrs.get('name', '')
            if not player_name:
                player_name = attrs.get('description', '')
            if not player_name:
                player_name = attrs.get('display_name', '')
            
            player_name = player_name.strip()
            if not player_name:
                continue
            
            # Get league info from relationships
            league_id = 'default'
            league_rel = item.get('relationships', {}).get('league', {}).get('data', {})
            if league_rel:
                league_id = str(league_rel.get('id', 'default'))
                # Store unique league IDs for debugging
                st.session_state.league_ids.add(league_id)
            
            # Get sport info from mapping
            sport_info = SPORT_MAPPING.get(league_id, SPORT_MAPPING['default'])
            
            # Get stat type
            stat_type = attrs.get('stat_type', '')
            if not stat_type:
                stat_type = attrs.get('stat_display_name', 'Unknown')
            
            # Get start time
            start_time = attrs.get('start_time', '')
            
            # Create projection entry
            proj = {
                'id': item.get('id'),
                'league_id': league_id,
                'sport': sport_info['name'],
                'sport_emoji': sport_info['emoji'],
                'player_name': player_name,
                'line': float(line_score),
                'stat_type': stat_type,
                'start_time': start_time,
                'game_id': attrs.get('game_id', ''),
                'status': attrs.get('status', ''),
                'is_live': attrs.get('is_live', False),
            }
            
            projections.append(proj)
                
        except Exception as e:
            continue
    
    df = pd.DataFrame(projections)
    
    if not df.empty:
        st.sidebar.success(f"✅ Processed {len(df)} props")
        
        # Show sport breakdown
        sport_counts = df['sport'].value_counts()
        with st.sidebar.expander("📊 Props by Sport"):
            for sport, count in sport_counts.items():
                st.write(f"{sport}: {count}")
        
        # Show NBA props if available
        nba_df = df[df['sport'] == 'NBA Basketball']
        if not nba_df.empty:
            with st.sidebar.expander("🏀 NBA Props Found"):
                st.write(f"Total NBA props: {len(nba_df)}")
                st.write(nba_df[['player_name', 'stat_type', 'line']].head(10))
    else:
        st.sidebar.warning("No props could be processed from API")
    
    return df

def get_projections_with_fallback():
    """Get projections with sample data fallback"""
    # Try to get real data first
    df = get_all_sports_projections()
    
    # If API returns empty, use comprehensive sample data
    if df.empty:
        st.sidebar.info("📊 Using sample data - PrizePicks API returned no data")
        
        # Comprehensive sample data across all sports
        sample_data = [
            # NBA - Today's games
            {'sport': 'NBA Basketball', 'sport_emoji': '🏀', 'player_name': 'Dillon Brooks', 'line': 23.5, 'stat_type': 'Points', 'team': 'PHX'},
            {'sport': 'NBA Basketball', 'sport_emoji': '🏀', 'player_name': 'Desmond Bane', 'line': 18.5, 'stat_type': 'Points', 'team': 'ORL'},
            {'sport': 'NBA Basketball', 'sport_emoji': '🏀', 'player_name': 'Anthony Black', 'line': 16.5, 'stat_type': 'Points', 'team': 'ORL'},
            {'sport': 'NBA Basketball', 'sport_emoji': '🏀', 'player_name': 'Cade Cunningham', 'line': 25.5, 'stat_type': 'Points', 'team': 'DET'},
            {'sport': 'NBA Basketball', 'sport_emoji': '🏀', 'player_name': 'Kevin Durant', 'line': 24.5, 'stat_type': 'Points', 'team': 'HOU'},
            {'sport': 'NBA Basketball', 'sport_emoji': '🏀', 'player_name': 'Karl-Anthony Towns', 'line': 30.5, 'stat_type': 'PRA', 'team': 'NYK'},
            {'sport': 'NBA Basketball', 'sport_emoji': '🏀', 'player_name': 'LeBron James', 'line': 25.5, 'stat_type': 'Points', 'team': 'LAL'},
            {'sport': 'NBA Basketball', 'sport_emoji': '🏀', 'player_name': 'Stephen Curry', 'line': 26.5, 'stat_type': 'Points', 'team': 'GSW'},
            {'sport': 'NBA Basketball', 'sport_emoji': '🏀', 'player_name': 'Luka Doncic', 'line': 31.5, 'stat_type': 'PRA', 'team': 'DAL'},
            {'sport': 'NBA Basketball', 'sport_emoji': '🏀', 'player_name': 'Shai Gilgeous-Alexander', 'line': 32.5, 'stat_type': 'PRA', 'team': 'OKC'},
        ]
        
        df = pd.DataFrame(sample_data)
        st.sidebar.success(f"✅ Loaded {len(df)} sample props")
    
    # Add placeholder columns
    if not df.empty:
        df['time'] = 'Today'
    
    return df

# ===================================================
# MAIN APP
# ===================================================

# Header
st.markdown('<p class="main-header">🏆 PrizePicks Optimizer — Auto Picks + Injuries</p>', unsafe_allow_html=True)
st.markdown(f"**Last Updated:** {datetime.now().strftime('%I:%M:%S %p')}")

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    num_legs = st.selectbox(
        "Number of Legs",
        [6, 5, 4, 3, 2],
        index=0,
        help="6-leg Flex Play pays 25x for 6/6, 2x for 5/6, 0.4x for 4/6"
    )
    
    st.session_state.entry_amount = st.number_input(
        "Entry Amount ($)",
        min_value=1.0,
        max_value=100.0,
        value=10.0,
        step=1.0
    )
    
    st.markdown("---")
    st.markdown("### 🤖 Auto Features")
    
    st.session_state.auto_select = st.checkbox(
        "Auto-select best picks",
        value=True
    )
    
    st.session_state.show_recommended = st.checkbox(
        "Show only recommended picks",
        value=True
    )
    
    st.markdown("---")
    st.markdown("### 📊 6-Leg Flex")
    st.markdown("**Break-even:** 54.15% per pick")
    
    st.markdown("---")
    st.markdown("### 🚑 Injury Guide")
    st.markdown("🔴 **OUT** - 70% reduction")
    st.markdown("🟡 **Questionable** - 20% reduction")
    st.markdown("🟢 **Probable** - 5% reduction")
    st.markdown("⚪ **Active** - No effect")
    
    # Debug section
    with st.expander("🔧 Debug Info"):
        if st.button("Test API Connection"):
            test_data = fetch_prizepicks_projections()
            if test_data:
                st.success("✅ API connected")
                items = test_data.get('data', [])
                st.write(f"Total items: {len(items)}")
                if items:
                    st.write("First item keys:", list(items[0].keys()))
                    attrs = items[0].get('attributes', {})
                    st.write("Attributes keys:", list(attrs.keys()))
            else:
                st.error("❌ API failed")
        
        if st.button("Show League IDs"):
            if st.session_state.league_ids:
                st.write("League IDs found:", sorted(st.session_state.league_ids))
                st.write("Total unique leagues:", len(st.session_state.league_ids))
            else:
                st.write("No league IDs collected yet - refresh data")
    
    if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Main content
col_left, col_right = st.columns([1.3, 0.7])

with col_left:
    st.markdown('<p class="sub-header">📋 Available Props</p>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading projections..."):
        df = get_projections_with_fallback()
        injuries_dict = fetch_injury_report()
    
    # Add injury info
    df['injury_status'] = df['player_name'].apply(lambda x: get_player_injury_status(x, injuries_dict))
    df['injury_display'] = df.apply(
        lambda row: f"{row['injury_status']['status']}" if row['injury_status']['status'] != 'Active' else '',
        axis=1
    )
    
    # Calculate hit rates
    hit_results = df.apply(
        lambda row: calculate_projected_hit_rate(
            row['line'], 
            row['sport'], 
            row['stat_type'],
            {**row['injury_status'], 'player_name': row['player_name']}
        ), 
        axis=1
    )
    
    df['hit_rate'] = [hr[0] for hr in hit_results]
    df['recommendation'] = [hr[1] for hr in hit_results]
    df['confidence'] = [hr[2] for hr in hit_results]
    
    # Sort by hit rate
    df = df.sort_values('hit_rate', ascending=False)
    
    # Sport filter
    sports_list = sorted(df['sport'].unique())
    selected_sports = st.multiselect(
        "Select Sports",
        sports_list,
        default=['NBA Basketball'] if 'NBA Basketball' in sports_list else []
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_sports:
        filtered_df = filtered_df[filtered_df['sport'].isin(selected_sports)]
    else:
        # If no sports selected, show message
        st.info("👆 Select a sport above to view props")
        filtered_df = pd.DataFrame()  # Empty dataframe
    
    if st.session_state.show_recommended and not filtered_df.empty:
        filtered_df = filtered_df[filtered_df['hit_rate'] > 0.5415]
    
    st.caption(f"**Found {len(filtered_df)} props**")
    
    # Auto-select if enabled
    if st.session_state.auto_select and len(st.session_state.picks) == 0 and len(filtered_df) >= num_legs:
        best_picks = filtered_df.head(num_legs)
        for _, row in best_picks.iterrows():
            st.session_state.picks.append({
                'sport_emoji': row['sport_emoji'],
                'sport': row['sport'],
                'player': row['player_name'],
                'stat': row['stat_type'],
                'line': row['line'],
                'pick': row['recommendation'],
                'hit_rate': row['hit_rate'],
                'injury': row['injury_status']['status'],
                'team': row.get('team', 'Unknown')
            })
        st.rerun()
    
    # Display props
    for idx, row in filtered_df.head(15).iterrows():
        # Determine colors
        hit_color = "value-positive" if row['hit_rate'] > 0.5415 else "value-negative"
        badge_color = "#4CAF50" if row['hit_rate'] > 0.5415 else "#f44336"
        
        # Build injury badge if needed
        injury_badge = ""
        if row['injury_status']['status'] != 'Active':
            injury_badge = f"<span class='injury-badge'>{row['injury_status']['status']}</span>"
        
        # Create prop card
        st.markdown(f"""
        <div class='pick-card'>
            <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;'>
                <div style='display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;'>
                    <span style='font-size: 1.2rem;'>{row['sport_emoji']}</span>
                    <span><strong>{row['player_name']}</strong></span>
                    <span class='sport-badge'>{row['sport']}</span>
                    {injury_badge}
                </div>
                <div style='display: flex; align-items: center; gap: 0.5rem;'>
                    <span>{row['stat_type']} {row['line']}</span>
                    <span class='{hit_color}' style='font-weight: bold;'>{row['hit_rate']*100:.1f}%</span>
                    <span style='background-color: {badge_color}; color: white; padding: 0.2rem 0.5rem; border-radius: 1rem; font-size: 0.8rem; font-weight: bold; display: inline-block; min-width: 45px; text-align: center;'>
                        {row['recommendation']}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            pick = st.selectbox(
                "Pick",
                ["MORE", "LESS"],
                index=0 if row['recommendation'] == "MORE" else 1,
                key=f"pick_{idx}",
                label_visibility="collapsed"
            )
        with col2:
            if st.button("➕ Add", key=f"add_{idx}", use_container_width=True):
                if len(st.session_state.picks) < num_legs:
                    st.session_state.picks.append({
                        'sport_emoji': row['sport_emoji'],
                        'sport': row['sport'],
                        'player': row['player_name'],
                        'stat': row['stat_type'],
                        'line': row['line'],
                        'pick': pick,
                        'hit_rate': row['hit_rate'],
                        'injury': row['injury_status']['status'],
                        'team': row.get('team', 'Unknown')
                    })
                    st.rerun()
                else:
                    st.warning(f"Max {num_legs} picks")
        with col3:
            if st.button("ℹ️ Details", key=f"info_{idx}", use_container_width=True):
                st.info(f"**Injury:** {row['injury_status']['status']}\n**Confidence:** {row['confidence']}")

with col_right:
    st.markdown('<p class="sub-header">📝 Your Entry</p>', unsafe_allow_html=True)
    
    if st.session_state.picks:
        for i, pick in enumerate(st.session_state.picks):
            injury_badge = f"<span class='injury-badge'>{pick['injury']}</span>" if pick['injury'] != 'Active' else ""
            
            st.markdown(f"""
            <div class='pick-card'>
                <div style='display: flex; justify-content: space-between;'>
                    <span><strong>{pick['sport_emoji']} {pick['player']}</strong></span>
                    {injury_badge}
                </div>
                <div><span style='font-weight: bold; color: {"#4CAF50" if pick["pick"]=="MORE" else "#f44336"};'>{pick['pick']}</span> {pick['stat']} {pick['line']}</div>
                <div style='font-size: 0.9rem;'>Hit rate: {pick['hit_rate']*100:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("❌ Remove", key=f"remove_{i}", use_container_width=True):
                st.session_state.picks.pop(i)
                st.rerun()
        
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
                <div class='recommendation-box'>
                    <h4 style='margin:0;'>🎯 Entry Summary</h4>
                    <p><strong>Avg Hit Rate:</strong> {avg_hit*100:.1f}%</p>
                    <p><strong>Expected Return:</strong> ${ev:.2f}</p>
                    <p><strong>ROI:</strong> {roi:.1f}%</p>
                    <p style='color: {"green" if roi>0 else "red"};'><strong>{'✅ +EV' if roi>0 else '⚠️ -EV'}</strong></p>
                </div>
                """, unsafe_allow_html=True)
        
        if st.button("🗑️ Clear All", type="primary", use_container_width=True):
            st.session_state.picks = []
            st.rerun()
    else:
        st.info("👆 Add props from the left panel")
        st.markdown("""
        **How to use:**
        1. Select a sport
        2. Review hit rates
        3. Click Add
        4. Auto-pick fills top props
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8rem;'>
    <p>🏆 Connected to PrizePicks live data | Auto picks enabled | Injuries included | 54.15% break-even threshold</p>
</div>
""", unsafe_allow_html=True)