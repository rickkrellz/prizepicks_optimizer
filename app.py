import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time
import pytz
import re

# Page config
st.set_page_config(
    page_title="PrizePicks Player Props",
    page_icon="🏀",
    layout="wide"
)

# Set timezone
central_tz = pytz.timezone('US/Central')
utc_tz = pytz.UTC

def get_central_time():
    utc_now = datetime.now(utc_tz)
    central_now = utc_now.astimezone(central_tz)
    return central_now

# Clean CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: white;
        text-align: center;
        background-color: #1E88E5;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: white;
        background-color: #0D47A1;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .prop-card {
        background-color: #2C3E50;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #1E88E5;
        margin: 0.5rem 0;
        color: white;
    }
    
    .league-badge {
        background-color: #FF6B6B;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-left: 8px;
    }
    
    .stat-line {
        background-color: #ECF0F1;
        color: #2C3E50;
        padding: 0.2rem 0.8rem;
        border-radius: 16px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin: 8px 0;
    }
    
    .stButton button {
        width: 100%;
        border-radius: 20px;
        font-weight: 600;
        background-color: #1E88E5;
        color: white;
        border: 2px solid white;
    }
    
    .footer {
        text-align: center;
        color: white;
        padding: 1rem;
        background-color: #2C3E50;
        border-radius: 8px;
        margin-top: 2rem;
    }
    
    .player-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: #2E7D32;
    }
    
    .team-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: #C62828;
    }
    
    .filter-note {
        background-color: #FFD700;
        color: black;
        padding: 0.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'picks' not in st.session_state:
    st.session_state.picks = []
if 'entry_amount' not in st.session_state:
    st.session_state.entry_amount = 10.0
if 'show_players_only' not in st.session_state:
    st.session_state.show_players_only = False

# Sport names based on league IDs
LEAGUE_NAMES = {
    '7': 'NBA',
    '82': 'Esports',
    '5': 'Tennis',
    '192': 'NBA',
    '190': 'MLB',
    '8': 'NHL',
    '20': 'CBB',
    '265': 'Esports',
    '84': 'Esports',
    '145': 'Esports',
    '43': 'MLB',
    '1': 'Golf',
    '121': 'Esports',
    '159': 'Esports',
    '288': 'Unrivaled',
    '176': 'Esports',
    '4': 'NASCAR',
    '290': 'CBB',
    '161': 'Esports',
    '174': 'Esports',
    '12': 'MMA',
    '42': 'Boxing',
    '80': 'Esports',
    '131': 'Golf',
    '277': 'Curling',
    '284': 'Handball',
    '379': 'Olympic Hockey',
    '383': 'Esports',
    '345': 'Other',
}

# Simple API call
@st.cache_data(ttl=300)
def fetch_prizepicks_projections():
    url = "https://api.prizepicks.com/projections"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Accept': 'application/json',
        'Referer': 'https://app.prizepicks.com/',
    }
    try:
        time.sleep(0.5)
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

@st.cache_data(ttl=300)
def get_all_projections():
    data = fetch_prizepicks_projections()
    
    if not data:
        return pd.DataFrame()
    
    projections = []
    league_counts = {}
    
    for item in data.get('data', []):
        try:
            attrs = item.get('attributes', {})
            line_score = attrs.get('line_score')
            if line_score is None:
                continue
            
            player_name = (attrs.get('name') or attrs.get('description') or '').strip()
            if not player_name:
                continue
            
            # Get league ID
            league_id = 'unknown'
            league_rel = item.get('relationships', {}).get('league', {}).get('data', {})
            if league_rel:
                league_id = str(league_rel.get('id', 'unknown'))
                league_counts[league_id] = league_counts.get(league_id, 0) + 1
            
            # Get sport name
            sport = LEAGUE_NAMES.get(league_id, f'League {league_id}')
            
            projections.append({
                'league_id': league_id,
                'sport': sport,
                'player_name': player_name,
                'line': float(line_score),
                'stat_type': attrs.get('stat_type', 'Unknown'),
            })
        except:
            continue
    
    st.session_state.league_counts = league_counts
    return pd.DataFrame(projections)

# ===================================================
# MAIN APP
# ===================================================

current_time = get_central_time()

st.markdown('<p class="main-header">🏀 PrizePicks Player Props</p>', unsafe_allow_html=True)

# Status and controls
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown(f"**Last Updated:** {current_time.strftime('%I:%M:%S %p CT')}")
with col2:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
with col3:
    st.session_state.show_players_only = st.checkbox("👤 Show Players Only", value=False)

# Load data
with st.spinner("Loading props..."):
    df = get_all_projections()

if df.empty:
    st.error("No data loaded")
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    num_legs = st.selectbox("Number of Legs", [6, 5, 4, 3, 2], index=0)
    st.session_state.entry_amount = st.number_input("Entry Amount ($)", 1.0, 100.0, 10.0)
    
    st.markdown("---")
    st.markdown(f"**Total Props:** {len(df):,}")
    
    # Show league distribution
    st.markdown("### 📊 League Distribution")
    if 'league_counts' in st.session_state:
        sorted_leagues = sorted(st.session_state.league_counts.items(), key=lambda x: x[1], reverse=True)
        for league_id, count in sorted_leagues:
            sport = LEAGUE_NAMES.get(league_id, f'League {league_id}')
            st.write(f"**{sport}** (ID: {league_id}): {count}")

# Main content
col_left, col_right = st.columns([1.3, 0.7])

with col_left:
    st.markdown('<p class="section-header">📋 Available Props</p>', unsafe_allow_html=True)
    
    # Filter by league
    all_leagues = sorted(df['league_id'].unique())
    league_options = {lid: f"{LEAGUE_NAMES.get(lid, f'League {lid}')} (ID: {lid})" for lid in all_leagues}
    selected_leagues = st.multiselect(
        "Select Leagues",
        options=list(league_options.keys()),
        format_func=lambda x: league_options[x],
        default=[]
    )
    
    # Apply filters
    filtered_df = df.copy()
    if selected_leagues:
        filtered_df = filtered_df[filtered_df['league_id'].isin(selected_leagues)]
    
    # Simple filter for players
    if st.session_state.show_players_only:
        # Filter out 3-letter all-caps team codes
        filtered_df = filtered_df[~filtered_df['player_name'].str.match(r'^[A-Z]{3}$', na=False)]
        # Filter out quarter indicators
        filtered_df = filtered_df[~filtered_df['player_name'].str.contains('1Q|2Q|3Q|4Q|1H|2H', na=False, regex=True)]
        # Filter out common team patterns
        filtered_df = filtered_df[~filtered_df['player_name'].str.contains('FC|United|City|Real|Team', na=False, regex=True)]
        st.markdown('<div class="filter-note">🔍 Hiding obvious team props</div>', unsafe_allow_html=True)
    
    st.caption(f"**Showing {len(filtered_df)} props**")
    
    # Auto-select button
    if len(st.session_state.picks) == 0 and len(filtered_df) >= num_legs:
        if st.button("🤖 Auto-select"):
            for _, row in filtered_df.head(num_legs).iterrows():
                st.session_state.picks.append({
                    'sport': row['sport'],
                    'player': row['player_name'],
                    'stat': row['stat_type'],
                    'line': row['line'],
                    'league_id': row['league_id'],
                })
            st.rerun()
    
    # Display props
    for idx, row in filtered_df.head(30).iterrows():
        # Simple heuristic for display
        is_likely_team = (re.match(r'^[A-Z]{3}$', row['player_name']) or 
                         '1Q' in row['player_name'] or 
                         'FC' in row['player_name'] or
                         'United' in row['player_name'])
        name_class = "team-name" if is_likely_team else "player-name"
        
        with st.container():
            st.markdown(f"""
            <div class='prop-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span class='{name_class}'>{row['player_name']}</span>
                        <span class='league-badge'>{row['sport']}</span>
                    </div>
                </div>
                <div class='stat-line'>{row['stat_type']}: {row['line']:.1f}</div>
            """, unsafe_allow_html=True)
            
            if st.button("➕ Add to Entry", key=f"add_{idx}"):
                if len(st.session_state.picks) < num_legs:
                    st.session_state.picks.append({
                        'sport': row['sport'],
                        'player': row['player_name'],
                        'stat': row['stat_type'],
                        'line': row['line'],
                        'league_id': row['league_id'],
                    })
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<p class="section-header">📝 Your Entry</p>', unsafe_allow_html=True)
    
    if st.session_state.picks:
        for i, pick in enumerate(st.session_state.picks):
            with st.container():
                st.markdown(f"""
                <div class='prop-card'>
                    <div><strong>{pick['player']}</strong> <span class='league-badge'>{pick['sport']}</span></div>
                    <div class='stat-line'>{pick['stat']}: {pick['line']:.1f}</div>
                """, unsafe_allow_html=True)
                
                if st.button("❌ Remove", key=f"remove_{i}"):
                    st.session_state.picks.pop(i)
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("🗑️ Clear All", type="primary"):
            st.session_state.picks = []
            st.rerun()
    else:
        st.info("👆 Add props from the left panel")

# Footer
st.markdown("---")
st.markdown(f"""
<div class='footer'>
    <p>🏀 {len(df):,} total props</p>
</div>
""", unsafe_allow_html=True)