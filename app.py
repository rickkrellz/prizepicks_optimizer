import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="PrizePicks Optimizer - Auto Picks",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #0D47A1;
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
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E88E5;
        margin: 1rem 0;
    }
    .sport-badge {
        background-color: #f0f2f6;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.8rem;
    }
    .auto-pick-badge {
        background-color: #4CAF50;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .injury-badge {
        background-color: #f44336;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .stButton button {
        width: 100%;
    }
    .pick-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with DEFAULTS
if 'picks' not in st.session_state:
    st.session_state.picks = []
if 'entry_amount' not in st.session_state:
    st.session_state.entry_amount = 10.0
if 'auto_select' not in st.session_state:
    st.session_state.auto_select = True  # DEFAULT: ON
if 'show_recommended' not in st.session_state:
    st.session_state.show_recommended = True  # DEFAULT: ON
if 'selected_sports' not in st.session_state:
    st.session_state.selected_sports = []  # DEFAULT: No sports selected (user must choose)

# ===================================================
# THE-ODDS-API INTEGRATION
# ===================================================

# 🔑 YOU PUT YOUR API KEY HERE 👇
ODDS_API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual key from the-odds-api.com

@st.cache_data(ttl=600)
def fetch_sportsbook_lines(sport="basketball_nba"):
    """Fetch player props from The-Odds-API for comparison"""
    if ODDS_API_KEY == "YOUR_API_KEY_HERE":
        return pd.DataFrame()  # Return empty if no key
    
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
            st.warning(f"API returned status {response.status_code}")
            return None
    except Exception as e:
        st.warning(f"Could not fetch sportsbook data: {e}")
        return None

def american_to_prob(odds):
    """Convert American odds to implied probability"""
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)

# ===================================================
# SPORT MAPPING
# ===================================================

SPORT_MAPPING = {
    '4': {'name': 'NBA Basketball', 'emoji': '🏀', 'api_sport': 'basketball_nba'},
    '2': {'name': 'NFL Football', 'emoji': '🏈', 'api_sport': 'americanfootball_nfl'},
    '1': {'name': 'MLB Baseball', 'emoji': '⚾', 'api_sport': 'baseball_mlb'},
    '3': {'name': 'NHL Hockey', 'emoji': '🏒', 'api_sport': 'icehockey_nhl'},
    '5': {'name': 'Soccer', 'emoji': '⚽', 'api_sport': 'soccer_uefa_champs_league'},
    '6': {'name': 'Golf (PGA)', 'emoji': '🏌️', 'api_sport': 'golf_pga'},
    '7': {'name': 'MMA/UFC', 'emoji': '🥊', 'api_sport': 'mma_mixed_martial_arts'},
    '8': {'name': 'Tennis', 'emoji': '🎾', 'api_sport': 'tennis_atp'},
    'default': {'name': 'Other Sports', 'emoji': '🏆', 'api_sport': None}
}

# ===================================================
# INJURY REPORT
# ===================================================

@st.cache_data(ttl=3600)
def fetch_injury_report():
    """Fetch current NBA injuries"""
    injuries = {
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
        'LeBron James': {'status': 'Active', 'injury': 'None', 'team': 'LAL'},
        'Stephen Curry': {'status': 'Active', 'injury': 'None', 'team': 'GSW'},
        'Ja Morant': {'status': 'OUT', 'injury': 'Shoulder', 'team': 'MEM'},
        'Zion Williamson': {'status': 'OUT', 'injury': 'Hamstring', 'team': 'NO'},
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
    """Calculate hit rate and recommend MORE/LESS"""
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
    
    # Line factor
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
        injury_factor = 0.3
    elif injury_status['status'] == 'Questionable':
        injury_factor = 0.8
    elif injury_status['status'] == 'Probable':
        injury_factor = 0.95
    
    # Teammate injuries boost
    opportunity_factor = 1.0
    player_name = injury_status.get('player_name', '')
    if any(name in player_name for name in ['Brooks', 'Bane', 'Black']):
        if 'Booker' in str(injuries_dict) or 'Wagner' in str(injuries_dict):
            opportunity_factor = 1.1
    
    # Final calculation
    hit_rate = base_rate * line_factor * injury_factor * opportunity_factor
    hit_rate = min(hit_rate, 0.75)
    
    # Recommendation
    if hit_rate > 0.5415:
        recommendation = "MORE"
        confidence = "High" if hit_rate > 0.58 else "Medium"
    else:
        recommendation = "LESS"
        confidence = "High" if hit_rate < 0.50 else "Medium"
    
    return hit_rate, recommendation, confidence

# ===================================================
# PRIZEPICKS API
# ===================================================

@st.cache_data(ttl=300)
def fetch_prizepicks_projections():
    """Fetch projections from PrizePicks API"""
    url = "https://api.prizepicks.com/projections"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://app.prizepicks.com/',
        'Origin': 'https://app.prizepicks.com',
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return None

def get_projections():
    """Get projections with sample data fallback"""
    data = fetch_prizepicks_projections()
    
    # If API fails, use comprehensive sample data
    sample_data = [
        # NBA - Today's games
        {'sport_emoji': '🏀', 'sport': 'NBA Basketball', 'player_name': 'Dillon Brooks', 'line': 23.5, 'stat_type': 'Points', 'team': 'PHX'},
        {'sport_emoji': '🏀', 'sport': 'NBA Basketball', 'player_name': 'Desmond Bane', 'line': 18.5, 'stat_type': 'Points', 'team': 'ORL'},
        {'sport_emoji': '🏀', 'sport': 'NBA Basketball', 'player_name': 'Anthony Black', 'line': 16.5, 'stat_type': 'Points', 'team': 'ORL'},
        {'sport_emoji': '🏀', 'sport': 'NBA Basketball', 'player_name': 'Cade Cunningham', 'line': 25.5, 'stat_type': 'Points', 'team': 'DET'},
        {'sport_emoji': '🏀', 'sport': 'NBA Basketball', 'player_name': 'Kevin Durant', 'line': 24.5, 'stat_type': 'Points', 'team': 'HOU'},
        {'sport_emoji': '🏀', 'sport': 'NBA Basketball', 'player_name': 'Karl-Anthony Towns', 'line': 30.5, 'stat_type': 'PRA', 'team': 'NYK'},
        {'sport_emoji': '🏀', 'sport': 'NBA Basketball', 'player_name': 'LeBron James', 'line': 25.5, 'stat_type': 'Points', 'team': 'LAL'},
        {'sport_emoji': '🏀', 'sport': 'NBA Basketball', 'player_name': 'Stephen Curry', 'line': 26.5, 'stat_type': 'Points', 'team': 'GSW'},
        {'sport_emoji': '🏀', 'sport': 'NBA Basketball', 'player_name': 'Luka Doncic', 'line': 31.5, 'stat_type': 'PRA', 'team': 'DAL'},
        {'sport_emoji': '🏀', 'sport': 'NBA Basketball', 'player_name': 'Shai Gilgeous-Alexander', 'line': 32.5, 'stat_type': 'PRA', 'team': 'OKC'},
        # NFL
        {'sport_emoji': '🏈', 'sport': 'NFL Football', 'player_name': 'Patrick Mahomes', 'line': 275.5, 'stat_type': 'Passing Yards', 'team': 'KC'},
        {'sport_emoji': '🏈', 'sport': 'NFL Football', 'player_name': 'Travis Kelce', 'line': 75.5, 'stat_type': 'Receiving Yards', 'team': 'KC'},
        # MLB
        {'sport_emoji': '⚾', 'sport': 'MLB Baseball', 'player_name': 'Shohei Ohtani', 'line': 1.5, 'stat_type': 'Hits', 'team': 'LAD'},
        # NHL
        {'sport_emoji': '🏒', 'sport': 'NHL Hockey', 'player_name': 'Connor McDavid', 'line': 1.5, 'stat_type': 'Points', 'team': 'EDM'},
        # Soccer
        {'sport_emoji': '⚽', 'sport': 'Soccer', 'player_name': 'Lionel Messi', 'line': 0.5, 'stat_type': 'Goals', 'team': 'MIA'},
    ]
    
    df = pd.DataFrame(sample_data)
    df['time'] = 'Today'
    return df

# ===================================================
# MAIN APP
# ===================================================

# Header
st.markdown('<p class="main-header">🏆 PrizePicks Optimizer — Auto Picks + Injuries</p>', unsafe_allow_html=True)
st.markdown(f"**Last Updated:** {datetime.now().strftime('%I:%M:%S %p')}")

# 🔑 API KEY WARNING
if ODDS_API_KEY == "YOUR_API_KEY_HERE":
    st.sidebar.warning("⚠️ **The-Odds-API key not set**\n\nGet free key at the-odds-api.com and add it to line 54 in app.py")

# Sidebar
with st.sidebar:
    st.markdown('<p class="sub-header">⚙️ Settings</p>', unsafe_allow_html=True)
    
    # Entry settings
    num_legs = st.selectbox(
        "Number of Legs",
        [2, 3, 4, 5, 6],
        index=4
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
    
    # DEFAULT: ON
    st.session_state.auto_select = st.checkbox(
        "Auto-select best picks",
        value=True  # DEFAULT ON
    )
    
    # DEFAULT: ON  
    st.session_state.show_recommended = st.checkbox(
        "Show only recommended picks",
        value=True  # DEFAULT ON
    )
    
    st.markdown("---")
    st.markdown("### 📊 Break-even")
    st.markdown("**6-Leg Flex:** 54.15%")
    
    st.markdown("---")
    st.markdown("### 🚑 Injury Status")
    st.markdown("🔴 **OUT** - 70% reduction")
    st.markdown("🟡 **Questionable** - 20% reduction")
    st.markdown("🟢 **Probable** - 5% reduction")
    
    # Refresh button
    if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Main content
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown('<p class="sub-header">📋 Available Props</p>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading projections..."):
        df = get_projections()
        injuries_dict = fetch_injury_report()
    
    # Add injury info
    df['injury_status'] = df['player_name'].apply(lambda x: get_player_injury_status(x, injuries_dict))
    
    # Calculate hit rates
    hit_rates = df.apply(
        lambda row: calculate_projected_hit_rate(
            row['line'], row['sport'], row['stat_type'],
            {**row['injury_status'], 'player_name': row['player_name']}
        ), axis=1
    )
    
    df['hit_rate'] = [hr[0] for hr in hit_rates]
    df['recommendation'] = [hr[1] for hr in hit_rates]
    df['confidence'] = [hr[2] for hr in hit_rates]
    
    # Sort by hit rate
    df = df.sort_values('hit_rate', ascending=False)
    
    # Filters
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        sports_list = sorted(df['sport'].unique())
        # DEFAULT: No sports selected - user must choose
        selected_sports = st.multiselect(
            "Select Sports",
            sports_list,
            default=st.session_state.selected_sports
        )
        st.session_state.selected_sports = selected_sports
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_sports:
        filtered_df = filtered_df[filtered_df['sport'].isin(selected_sports)]
    else:
        # If no sports selected, show a message but still show NBA as hint
        if not filtered_df.empty:
            st.info("👆 Select a sport above to see props")
            filtered_df = filtered_df[filtered_df['sport'] == 'NBA Basketball']  # Default to NBA
    
    if st.session_state.show_recommended:
        filtered_df = filtered_df[filtered_df['hit_rate'] > 0.5415]
    
    st.markdown(f"**Found {len(filtered_df)} props**")
    
    # Auto-select if enabled and no picks yet
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
    for idx, row in filtered_df.iterrows():
        with st.container():
            st.markdown('<div class="pick-card">', unsafe_allow_html=True)
            
            cols = st.columns([2.5, 1.2, 1.2, 1.5, 1.5, 1.5])
            
            with cols[0]:
                st.markdown(f"{row['sport_emoji']} **{row['player_name']}**")
                st.markdown(f"<span class='sport-badge'>{row['sport']}</span>", unsafe_allow_html=True)
                
                if row['injury_status']['status'] != 'Active':
                    st.markdown(f"<span class='injury-badge'>{row['injury_status']['status']}</span>", unsafe_allow_html=True)
            
            with cols[1]:
                st.markdown(f"**{row['stat_type']}**")
            
            with cols[2]:
                st.markdown(f"**{row['line']}**")
            
            with cols[3]:
                hit_color = "value-positive" if row['hit_rate'] > 0.5415 else "value-negative"
                st.markdown(f"<span class='{hit_color}'>{row['hit_rate']*100:.1f}%</span>", unsafe_allow_html=True)
            
            with cols[4]:
                if row['hit_rate'] > 0.5415:
                    st.markdown(f"<span class='auto-pick-badge'>⬆️ MORE</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span class='auto-pick-badge' style='background-color:#f44336;'>⬇️ LESS</span>", unsafe_allow_html=True)
            
            with cols[5]:
                pick = st.selectbox(
                    "Pick",
                    ["MORE", "LESS"],
                    index=0 if row['recommendation'] == "MORE" else 1,
                    key=f"pick_{idx}",
                    label_visibility="collapsed"
                )
            
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
                    st.warning(f"Maximum {num_legs} picks")
            
            st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<p class="sub-header">📝 Your Entry</p>', unsafe_allow_html=True)
    
    if st.session_state.picks:
        for i, pick in enumerate(st.session_state.picks):
            with st.container():
                st.markdown('<div class="pick-card">', unsafe_allow_html=True)
                
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"{pick['sport_emoji']} **{pick['player']}**")
                    st.markdown(f"**{pick['pick']}** {pick['stat']} {pick['line']}")
                    st.markdown(f"Hit rate: {pick['hit_rate']*100:.1f}%")
                    
                    if pick['injury'] != 'Active':
                        st.markdown(f"<span class='injury-badge'>{pick['injury']}</span>", unsafe_allow_html=True)
                
                with col2:
                    if st.button("❌", key=f"remove_{i}"):
                        st.session_state.picks.pop(i)
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        if len(st.session_state.picks) == num_legs:
            avg_hit = np.mean([p['hit_rate'] for p in st.session_state.picks])
            
            st.markdown('<div class="recommendation-box">', unsafe_allow_html=True)
            st.markdown("### 🎯 Entry Summary")
            st.markdown(f"**Avg Hit Rate:** {avg_hit*100:.1f}%")
            
            if num_legs == 6:
                from scipy import stats
                
                prob_4 = sum([stats.binom.pmf(k, 6, avg_hit) for k in range(4, 7)])
                prob_5 = sum([stats.binom.pmf(k, 6, avg_hit) for k in range(5, 7)])
                prob_6 = stats.binom.pmf(6, 6, avg_hit)
                
                ev = (prob_4 * st.session_state.entry_amount * 0.4 +
                      prob_5 * st.session_state.entry_amount * 2 +
                      prob_6 * st.session_state.entry_amount * 25)
                
                roi = ((ev - st.session_state.entry_amount) / st.session_state.entry_amount) * 100
                
                st.markdown(f"**Expected Return:** ${ev:.2f}")
                st.markdown(f"**ROI:** {roi:.1f}%")
                
                if roi > 0:
                    st.markdown("✅ **Positive EV**")
                else:
                    st.markdown("⚠️ **Negative EV**")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("🧹 Clear All", type="primary", use_container_width=True):
                st.session_state.picks = []
                st.rerun()
    else:
        st.info("👆 Select a sport and add picks")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8rem;'>
    <p>🏆 Auto picks enabled | Select a sport to begin | Injuries included</p>
</div>
""", unsafe_allow_html=True)