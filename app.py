import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import time
import random
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

# CSS
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
    
    .badge {
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        color: white;
        display: inline-block;
        margin-left: 8px;
    }
    .badge-nba { background-color: #17408B; }
    .badge-nhl { background-color: #000000; }
    .badge-mlb { background-color: #041E42; }
    .badge-tennis { background-color: #CC5500; }
    .badge-soccer { background-color: #006400; }
    .badge-pga { background-color: #0A4C33; }
    .badge-esports { background-color: #4B0082; }
    .badge-nascar { background-color: #8B4513; }
    .badge-cbb { background-color: #FF4500; }
    .badge-other { background-color: #555555; }
    
    .more-badge {
        background-color: #2E7D32;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 16px;
        font-weight: bold;
        font-size: 0.9rem;
        display: inline-block;
        min-width: 60px;
        text-align: center;
    }
    .less-badge {
        background-color: #C62828;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 16px;
        font-weight: bold;
        font-size: 0.9rem;
        display: inline-block;
        min-width: 60px;
        text-align: center;
    }
    
    .team-name {
        font-size: 0.9rem;
        color: #FFD700;
        margin-left: 5px;
    }
    
    .player-name {
        font-size: 1.2rem;
        font-weight: 700;
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

# League mapping
LEAGUE_MAPPING = {
    '7': 'NBA', '192': 'NBA',
    '8': 'NHL', '3': 'NHL',
    '1': 'MLB', '43': 'MLB', '190': 'MLB',
    '5': 'Tennis',
    '6': 'Soccer', '44': 'Soccer', '45': 'Soccer',
    '82': 'Esports', '265': 'Esports', '80': 'Esports', '84': 'Esports',
    '121': 'Esports', '145': 'Esports', '159': 'Esports', '161': 'Esports',
    '174': 'Esports', '176': 'Esports', '383': 'Esports',
    '131': 'Golf',
    '20': 'CBB', '290': 'CBB',
    '4': 'NASCAR', '9': 'NASCAR', '22': 'NASCAR',
    '12': 'MMA', '42': 'Boxing',
    '284': 'Handball',
    '288': 'Unrivaled',
    '277': 'Curling',
    '379': 'Olympic Hockey',
}

# NBA team mapping for better display
NBA_TEAMS = {
    'ATL': 'Hawks', 'BOS': 'Celtics', 'BKN': 'Nets', 'CHA': 'Hornets', 'CHI': 'Bulls',
    'CLE': 'Cavaliers', 'DAL': 'Mavericks', 'DEN': 'Nuggets', 'DET': 'Pistons', 'GSW': 'Warriors',
    'HOU': 'Rockets', 'IND': 'Pacers', 'LAC': 'Clippers', 'LAL': 'Lakers', 'MEM': 'Grizzlies',
    'MIA': 'Heat', 'MIL': 'Bucks', 'MIN': 'Timberwolves', 'NOP': 'Pelicans', 'NYK': 'Knicks',
    'OKC': 'Thunder', 'ORL': 'Magic', 'PHI': '76ers', 'PHX': 'Suns', 'POR': 'Trail Blazers',
    'SAC': 'Kings', 'SAS': 'Spurs', 'TOR': 'Raptors', 'UTA': 'Jazz', 'WAS': 'Wizards'
}

def extract_team_info(player_name, sport):
    """Extract team information from player name"""
    # Check if it's a team code
    if len(player_name) == 3 and player_name.isupper():
        if sport == 'NBA' and player_name in NBA_TEAMS:
            return f"{player_name} {NBA_TEAMS[player_name]}", player_name
        return f"{player_name} Team", player_name
    return player_name, None

def calculate_hit_rate(line, sport):
    """Calculate hit rate with more variation"""
    base_rates = {
        'NBA': 0.52, 'NHL': 0.51, 'MLB': 0.53, 'Tennis': 0.50,
        'Soccer': 0.50, 'Golf': 0.48, 'Esports': 0.52, 'CBB': 0.51,
        'NASCAR': 0.50, 'MMA': 0.49, 'Boxing': 0.49
    }
    base_rate = base_rates.get(sport, 0.51)
    
    # More randomness to get both MORE and LESS
    random_factor = random.uniform(0.92, 1.08)
    
    # Line adjustment
    if line > 30:
        line_factor = 0.96
    elif line > 20:
        line_factor = 0.98
    elif line > 10:
        line_factor = 1.0
    else:
        line_factor = 1.02
    
    hit_rate = base_rate * line_factor * random_factor
    return min(max(hit_rate, 0.35), 0.68)

# API call
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
            
            league_id = 'unknown'
            league_rel = item.get('relationships', {}).get('league', {}).get('data', {})
            if league_rel:
                league_id = str(league_rel.get('id', 'unknown'))
                league_counts[league_id] = league_counts.get(league_id, 0) + 1
            
            sport = LEAGUE_MAPPING.get(league_id, 'Other')
            
            # Get team info
            display_name, team_code = extract_team_info(player_name, sport)
            
            # Emoji mapping
            emoji = {
                'NBA': '🏀', 'NHL': '🏒', 'MLB': '⚾', 'Tennis': '🎾',
                'Soccer': '⚽', 'Golf': '⛳', 'Esports': '🎮', 'CBB': '🏀',
                'NASCAR': '🏎️', 'MMA': '🥊', 'Boxing': '🥊', 'Other': '🏆'
            }.get(sport, '🏆')
            
            projections.append({
                'league_id': league_id,
                'sport': sport,
                'emoji': emoji,
                'player_name': player_name,
                'display_name': display_name,
                'team_code': team_code,
                'line': float(line_score),
                'stat_type': attrs.get('stat_type', 'Unknown'),
            })
        except:
            continue
    
    st.session_state.league_counts = league_counts
    return pd.DataFrame(projections)

# Main app
current_time = get_central_time()

st.markdown('<p class="main-header">🏀 PrizePicks Player Props</p>', unsafe_allow_html=True)

# Status
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"**Last Updated:** {current_time.strftime('%I:%M:%S %p CT')}")
with col2:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# Load data
with st.spinner("Loading props..."):
    df = get_all_projections()

if df.empty:
    st.error("No data loaded")
    st.stop()

# Calculate hit rates
df['hit_rate'] = df.apply(lambda row: calculate_hit_rate(row['line'], row['sport']), axis=1)
df['recommendation'] = df['hit_rate'].apply(lambda x: 'MORE' if x > 0.5415 else 'LESS')
df = df.sort_values('hit_rate', ascending=False)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    num_legs = st.selectbox("Number of Legs", [6, 5, 4, 3, 2], index=0)
    st.session_state.entry_amount = st.number_input("Entry Amount ($)", 1.0, 100.0, 10.0)
    
    st.markdown("---")
    st.markdown("### 🤖 Auto Features")
    st.session_state.auto_select = st.checkbox("Auto-select best picks", value=True)
    st.session_state.show_recommended = st.checkbox("Show only recommended (>54.15%)", value=False)
    
    st.markdown("---")
    st.markdown(f"**Total Props:** {len(df):,}")
    st.markdown(f"**MORE:** {len(df[df['recommendation']=='MORE']):,}")
    st.markdown(f"**LESS:** {len(df[df['recommendation']=='LESS']):,}")
    
    # League distribution
    st.markdown("### 📊 League Distribution")
    if 'league_counts' in st.session_state:
        sorted_leagues = sorted(st.session_state.league_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        for league_id, count in sorted_leagues:
            sport = LEAGUE_MAPPING.get(league_id, f'League {league_id}')
            st.write(f"**{sport}** (ID: {league_id}): {count}")

# Main content
col_left, col_right = st.columns([1.3, 0.7])

with col_left:
    st.markdown('<p class="section-header">📋 Available Props</p>', unsafe_allow_html=True)
    
    # League filter
    all_leagues = sorted(df['league_id'].unique())
    league_options = {lid: f"{LEAGUE_MAPPING.get(lid, f'League {lid}')} (ID: {lid})" for lid in all_leagues}
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
    
    if st.session_state.show_recommended:
        filtered_df = filtered_df[filtered_df['hit_rate'] > 0.5415]
    
    st.caption(f"**Showing {len(filtered_df)} of {len(df)} props**")
    
    # Auto-select
    if st.session_state.auto_select and len(st.session_state.picks) == 0 and len(filtered_df) >= num_legs:
        if st.button("🤖 Auto-select best picks"):
            for _, row in filtered_df.head(num_legs).iterrows():
                st.session_state.picks.append({
                    'emoji': row['emoji'],
                    'sport': row['sport'],
                    'player': row['player_name'],
                    'display_name': row['display_name'],
                    'team_code': row['team_code'],
                    'stat': row['stat_type'],
                    'line': row['line'],
                    'pick': row['recommendation'],
                    'hit_rate': row['hit_rate'],
                })
            st.rerun()
    
    # Display props
    for idx, row in filtered_df.head(30).iterrows():
        with st.container():
            # Build display string
            if row['team_code']:
                display_text = f"{row['display_name']}"
            else:
                display_text = row['player_name']
            
            st.markdown(f"""
            <div class='prop-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span style='font-size:1.2rem;'>{row['emoji']}</span>
                        <span class='player-name'>{display_text}</span>
                        <span class='badge badge-other'>{row['sport']}</span>
                    </div>
                    <span style='font-weight:bold; color:{"#2E7D32" if row["hit_rate"]>0.5415 else "#C62828"};'>
                        {row['hit_rate']*100:.1f}%
                    </span>
                </div>
                <div class='stat-line'>{row['stat_type']}: {row['line']:.1f}</div>
                <div style='display:flex; gap:10px; align-items:center; margin-top:8px;'>
                    <span class='{"more-badge" if row["recommendation"]=="MORE" else "less-badge"}'>
                        {row['recommendation']}
                    </span>
            """, unsafe_allow_html=True)
            
            if st.button("➕ Add", key=f"add_{idx}"):
                if len(st.session_state.picks) < num_legs:
                    st.session_state.picks.append({
                        'emoji': row['emoji'],
                        'sport': row['sport'],
                        'player': row['player_name'],
                        'display_name': display_text,
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
                <div class='prop-card'>
                    <div style='display:flex; justify-content:space-between;'>
                        <div>
                            <span>{pick['emoji']}</span>
                            <strong>{pick['display_name']}</strong>
                        </div>
                        <span class='{"more-badge" if pick["pick"]=="MORE" else "less-badge"}' style='padding:0.2rem 0.5rem; font-size:0.8rem;'>
                            {pick['pick']}
                        </span>
                    </div>
                    <div>{pick['stat']} {pick['line']:.1f}</div>
                    <div style='color:{"#2E7D32" if pick["hit_rate"]>0.5415 else "#C62828"}; margin-top:5px;'>
                        Hit rate: {pick['hit_rate']*100:.1f}%
                    </div>
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
    <p>🏀 {len(df):,} total props | 
    <span style='color:#2E7D32;'>{len(df[df['recommendation']=='MORE']):,} MORE</span> / 
    <span style='color:#C62828;'>{len(df[df['recommendation']=='LESS']):,} LESS</span>
    </p>
</div>
""", unsafe_allow_html=True)