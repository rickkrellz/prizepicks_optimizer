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

# Clean CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #0D47A1;
        border-bottom: 2px solid #1E88E5;
        padding-bottom: 0.3rem;
        margin: 1rem 0;
    }
    .badge-nba { background-color: #17408B; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-nhl { background-color: #000000; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-mlb { background-color: #041E42; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-nfl { background-color: #013369; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-pga { background-color: #0A4C33; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-tennis { background-color: #FFC72C; color: black; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-soccer { background-color: #00A651; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-mma { background-color: #D22B2B; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-esports { background-color: #6A0DAD; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-nascar { background-color: #FFD700; color: black; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-other { background-color: #757575; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    
    .more-badge { background-color: #2E7D32; color: white; padding: 0.3rem 1rem; border-radius: 25px; font-weight: bold; font-size: 0.9rem; display: inline-block; min-width: 70px; text-align: center; }
    .less-badge { background-color: #C62828; color: white; padding: 0.3rem 1rem; border-radius: 25px; font-weight: bold; font-size: 0.9rem; display: inline-block; min-width: 70px; text-align: center; }
    
    .hit-high { color: #2E7D32; font-weight: bold; font-size: 1.1rem; background-color: #E8F5E9; padding: 0.2rem 0.5rem; border-radius: 8px; }
    .hit-low { color: #C62828; font-weight: bold; font-size: 1.1rem; background-color: #FFEBEE; padding: 0.2rem 0.5rem; border-radius: 8px; }
    
    .prop-card {
        background-color: #FFFFFF;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #E0E0E0;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .entry-card {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #1E88E5;
    }
    .summary-box {
        background-color: #E3F2FD;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .player-name {
        font-size: 1.2rem;
        font-weight: 700;
        color: #0D47A1;
    }
    .stat-line {
        background-color: #F5F5F5;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.95rem;
        display: inline-block;
    }
    .stButton button {
        width: 100%;
        border-radius: 20px;
        font-weight: 600;
    }
    .footer {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        padding: 1rem;
        background-color: #F5F5F5;
        border-radius: 10px;
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

# ===================================================
# THE-ODDS-API KEY
# ===================================================

ODDS_API_KEY = "047afdffc14ecda16cb02206a22070c4"

# ===================================================
# SPORT MAPPING
# ===================================================

SPORT_MAPPING = {
    '12': {'name': 'MMA', 'emoji': '🥊', 'badge': 'badge-mma'},
    '82': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    '265': {'name': 'CS2', 'emoji': '🎮', 'badge': 'badge-esports'},
    '121': {'name': 'LoL', 'emoji': '🎮', 'badge': 'badge-esports'},
    '174': {'name': 'CS2', 'emoji': '🎮', 'badge': 'badge-esports'},
    '159': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    '161': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    '145': {'name': 'RL', 'emoji': '🎮', 'badge': 'badge-esports'},
    '42': {'name': 'Boxing', 'emoji': '🥊', 'badge': 'badge-mma'},
    '20': {'name': 'CBB', 'emoji': '🏀', 'badge': 'badge-nba'},
    '290': {'name': 'CBB', 'emoji': '🏀', 'badge': 'badge-nba'},
    '149': {'name': 'NBA', 'emoji': '🏀', 'badge': 'badge-nba'},
    '192': {'name': 'NBA', 'emoji': '🏀', 'badge': 'badge-nba'},
    '286': {'name': 'Table Tennis', 'emoji': '🏓', 'badge': 'badge-other'},
    '131': {'name': 'Golf', 'emoji': '⛳', 'badge': 'badge-pga'},
    '1': {'name': 'PGA', 'emoji': '⛳', 'badge': 'badge-pga'},
    '5': {'name': 'Tennis', 'emoji': '🎾', 'badge': 'badge-tennis'},
    '277': {'name': 'Curling', 'emoji': '🥌', 'badge': 'badge-other'},
    '379': {'name': 'Olympic Hockey', 'emoji': '🏒', 'badge': 'badge-nhl'},
    '43': {'name': 'MLB', 'emoji': '⚾', 'badge': 'badge-mlb'},
    '7': {'name': 'NBA', 'emoji': '🏀', 'badge': 'badge-nba'},
    '284': {'name': 'Handball', 'emoji': '🤾', 'badge': 'badge-other'},
    '4': {'name': 'NASCAR', 'emoji': '🏎️', 'badge': 'badge-nascar'},
    '288': {'name': 'Unrivaled', 'emoji': '🏀', 'badge': 'badge-nba'},
    '8': {'name': 'NHL', 'emoji': '🏒', 'badge': 'badge-nhl'},
    '190': {'name': 'MLB', 'emoji': '⚾', 'badge': 'badge-mlb'},
    'default': {'name': 'Other', 'emoji': '🏆', 'badge': 'badge-other'}
}

# ===================================================
# PLAYER NAME VALIDATION - ONLY show real player names
# ===================================================

def is_real_player_name(name):
    """Check if this is a real player name (not a team code)"""
    if not name or len(name) < 5:  # Too short to be a real name
        return False
    
    # If it's all uppercase and 2-4 letters, it's a team code
    if name.isupper() and 2 <= len(name) <= 4:
        return False
    
    # Must have at least one space (first and last name)
    if ' ' not in name:
        return False
    
    # Must have at least 2 parts
    parts = name.split()
    if len(parts) < 2:
        return False
    
    # Each part should be at least 2 letters
    for part in parts:
        if len(part) < 2:
            return False
    
    # Common team names to filter out
    team_names = ['Team', 'United', 'FC', 'SC', 'CF', 'Club', 'City', 'Athletic']
    if any(team in name for team in team_names):
        return False
    
    return True

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
    
    random_factor = random.uniform(0.98, 1.02)
    
    hit_rate = base_rate * line_factor * injury_factor * random_factor
    hit_rate = min(hit_rate, 0.75)
    hit_rate = max(hit_rate, 0.25)
    
    return hit_rate

# ===================================================
# PRIZEPICKS API
# ===================================================

@st.cache_data(ttl=300)
def fetch_prizepicks_projections():
    url = "https://api.prizepicks.com/projections"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Accept': 'application/json',
        'Referer': 'https://app.prizepicks.com/',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
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
            
            # ONLY keep real player names
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
st.markdown('<p class="main-header">🏀 PrizePicks Player Props Only</p>', unsafe_allow_html=True)
st.markdown(f"**Last Updated:** {current_time.strftime('%I:%M:%S %p CT')}")

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
    st.error("No player props loaded. Using sample data.")
    df = pd.DataFrame([
        {'sport': 'NBA', 'sport_emoji': '🏀', 'badge_class': 'badge-nba', 'player_name': 'Dillon Brooks', 'line': 23.5, 'stat_type': 'Points'},
        {'sport': 'NBA', 'sport_emoji': '🏀', 'badge_class': 'badge-nba', 'player_name': 'Desmond Bane', 'line': 18.5, 'stat_type': 'Points'},
        {'sport': 'NBA', 'sport_emoji': '🏀', 'badge_class': 'badge-nba', 'player_name': 'Anthony Black', 'line': 16.5, 'stat_type': 'Points'},
        {'sport': 'NBA', 'sport_emoji': '🏀', 'badge_class': 'badge-nba', 'player_name': 'Cade Cunningham', 'line': 25.5, 'stat_type': 'Points'},
        {'sport': 'NBA', 'sport_emoji': '🏀', 'badge_class': 'badge-nba', 'player_name': 'Kevin Durant', 'line': 24.5, 'stat_type': 'Points'},
    ])

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
                    <div style='display: flex; justify-content: space-between;'>
                        <span class='player-name'>{pick['sport_emoji']} {pick['player']}</span>
                        <span class='{"more-badge" if pick["pick"]=="MORE" else "less-badge"}' style='padding:0.2rem 0.8rem; font-size:0.8rem;'>
                            {pick['pick']}
                        </span>
                    </div>
                    <div>{pick['stat']} {pick['line']:.1f}</div>
                    <div style='color: {"#2E7D32" if pick["hit_rate"] > 0.5415 else "#C62828"};'>
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
                    <p style='color: {"#2E7D32" if roi>0 else "#C62828"}; font-weight:bold; font-size:1.2rem;'>
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
    <p>🏀 {len(df):,} player props only | 
    <span style='color:#2E7D32;'>{len(df[df['recommendation']=='MORE']):,} MORE</span> / 
    <span style='color:#C62828;'>{len(df[df['recommendation']=='LESS']):,} LESS</span>
    </p>
    <p style='font-size:0.8rem;'>Central Time (CT) | {current_time.strftime('%B %d, %Y')}</p>
</div>
""", unsafe_allow_html=True)
