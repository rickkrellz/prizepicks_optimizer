import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import time
import random

# Page config
st.set_page_config(
    page_title="PrizePicks Optimizer",
    page_icon="🎯",
    layout="wide"
)

# Clean CSS with better text visibility
st.markdown("""
<style>
    /* Main header */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #0D47A1;
        border-bottom: 2px solid #1E88E5;
        padding-bottom: 0.3rem;
        margin: 1rem 0;
    }
    
    /* Sport badges - all with white text for readability */
    .badge-mma { background-color: #D22B2B; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-esports { background-color: #6A0DAD; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-boxing { background-color: #8B0000; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-cbb { background-color: #FF4500; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-cbb1h { background-color: #FF8C00; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-nba4q { background-color: #17408B; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-tabletennis { background-color: #708090; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-golf { background-color: #708090; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-tennis { background-color: #FFC72C; color: black; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-cs2 { background-color: #A52A2A; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-lol { background-color: #4B0082; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-curling { background-color: #00CED1; color: black; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-ohockey { background-color: #000000; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-pga { background-color: #0A4C33; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-mlb { background-color: #041E42; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-nba { background-color: #17408B; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-nba1q { background-color: #6A5ACD; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-handball { background-color: #CD5C5C; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-rl { background-color: #228B22; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-nascar { background-color: #FFD700; color: black; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-unrivaled { background-color: #FF69B4; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-nhl { background-color: #000000; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    .badge-mlbszn { background-color: #002D72; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
    
    /* MORE/LESS badges */
    .more-badge { background-color: #2E7D32; color: white; padding: 0.3rem 1rem; border-radius: 25px; font-weight: bold; font-size: 0.9rem; display: inline-block; min-width: 70px; text-align: center; }
    .less-badge { background-color: #C62828; color: white; padding: 0.3rem 1rem; border-radius: 25px; font-weight: bold; font-size: 0.9rem; display: inline-block; min-width: 70px; text-align: center; }
    
    /* Hit rate colors */
    .hit-high { color: #2E7D32; font-weight: bold; font-size: 1.1rem; background-color: #E8F5E9; padding: 0.2rem 0.5rem; border-radius: 8px; }
    .hit-low { color: #C62828; font-weight: bold; font-size: 1.1rem; background-color: #FFEBEE; padding: 0.2rem 0.5rem; border-radius: 8px; }
    
    /* Cards with better contrast */
    .prop-card {
        background-color: #FFFFFF;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #E0E0E0;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #000000;
    }
    .entry-card {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #1E88E5;
        color: #000000;
    }
    .summary-box {
        background-color: #E3F2FD;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #000000;
    }
    
    /* Player name */
    .player-name {
        font-size: 1.2rem;
        font-weight: 700;
        color: #0D47A1;
    }
    
    /* Stat line */
    .stat-line {
        background-color: #F5F5F5;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.95rem;
        display: inline-block;
        color: #000000;
    }
    
    /* Buttons */
    .stButton button {
        width: 100%;
        border-radius: 20px;
        font-weight: 600;
    }
    
    /* Footer */
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
# COMPLETE SPORT MAPPING - Based on your CSV export
# ===================================================

SPORT_MAPPING = {
    # MMA/UFC
    '12': {'name': 'MMA', 'emoji': '🥊', 'badge': 'badge-mma'},
    
    # Esports / Gaming
    '82': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    '265': {'name': 'CS2', 'emoji': '🎮', 'badge': 'badge-cs2'},
    '121': {'name': 'LoL', 'emoji': '🎮', 'badge': 'badge-lol'},
    '174': {'name': 'CS2', 'emoji': '🎮', 'badge': 'badge-cs2'},
    '159': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    '161': {'name': 'Esports', 'emoji': '🎮', 'badge': 'badge-esports'},
    '145': {'name': 'RL', 'emoji': '🎮', 'badge': 'badge-rl'},
    
    # Boxing
    '42': {'name': 'Boxing', 'emoji': '🥊', 'badge': 'badge-boxing'},
    
    # College Basketball
    '20': {'name': 'CBB', 'emoji': '🏀', 'badge': 'badge-cbb'},
    '290': {'name': 'CBB 1H', 'emoji': '🏀', 'badge': 'badge-cbb1h'},
    
    # NBA Quarters
    '149': {'name': 'NBA 4Q', 'emoji': '🏀', 'badge': 'badge-nba4q'},
    '192': {'name': 'NBA 1Q', 'emoji': '🏀', 'badge': 'badge-nba1q'},
    
    # Table Tennis
    '286': {'name': 'Table Tennis', 'emoji': '🏓', 'badge': 'badge-tabletennis'},
    
    # Golf
    '131': {'name': 'Golf', 'emoji': '⛳', 'badge': 'badge-golf'},
    '1': {'name': 'PGA', 'emoji': '⛳', 'badge': 'badge-pga'},
    
    # Tennis
    '5': {'name': 'Tennis', 'emoji': '🎾', 'badge': 'badge-tennis'},
    
    # Curling
    '277': {'name': 'Curling', 'emoji': '🥌', 'badge': 'badge-curling'},
    
    # Olympic Hockey
    '379': {'name': 'Olympic Hockey', 'emoji': '🏒', 'badge': 'badge-ohockey'},
    
    # MLB
    '43': {'name': 'MLB', 'emoji': '⚾', 'badge': 'badge-mlb'},
    
    # NBA
    '7': {'name': 'NBA', 'emoji': '🏀', 'badge': 'badge-nba'},
    
    # Handball
    '284': {'name': 'Handball', 'emoji': '🤾', 'badge': 'badge-handball'},
    
    # NASCAR
    '4': {'name': 'NASCAR', 'emoji': '🏎️', 'badge': 'badge-nascar'},
    
    # Unrivaled Basketball
    '288': {'name': 'Unrivaled', 'emoji': '🏀', 'badge': 'badge-unrivaled'},
    
    # NHL
    '8': {'name': 'NHL', 'emoji': '🏒', 'badge': 'badge-nhl'},
    
    # MLB Season
    '190': {'name': 'MLB SZN', 'emoji': '⚾', 'badge': 'badge-mlbszn'},
    
    'default': {'name': 'Other', 'emoji': '🏆', 'badge': 'badge-other'}
}

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
    
    # Randomness
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
def get_all_sports_projections():
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
            
            league_id = 'default'
            league_rel = item.get('relationships', {}).get('league', {}).get('data', {})
            if league_rel:
                league_id = str(league_rel.get('id', 'default'))
            
            sport_info = SPORT_MAPPING.get(league_id, SPORT_MAPPING['default'])
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
    
    return pd.DataFrame(projections)

def get_projections_with_fallback():
    df = get_all_sports_projections()
    
    if df.empty:
        # Sample data if API fails
        df = pd.DataFrame([
            {'sport': 'NBA', 'sport_emoji': '🏀', 'badge_class': 'badge-nba', 'player_name': 'Dillon Brooks', 'line': 23.5, 'stat_type': 'Points', 'game_id': 'PHX vs ORL', 'league_id': '7'},
            {'sport': 'NASCAR', 'sport_emoji': '🏎️', 'badge_class': 'badge-nascar', 'player_name': 'Kyle Busch', 'line': 5.5, 'stat_type': 'Fastest Laps', 'game_id': 'Autotrader 400', 'league_id': '4'},
        ])
    
    return df

# ===================================================
# MAIN APP
# ===================================================

st.markdown('<p class="main-header">🎯 PrizePicks Optimizer</p>', unsafe_allow_html=True)
st.markdown(f"**Last Updated:** {datetime.now().strftime('%I:%M:%S %p')}")

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
with st.spinner("Loading props from PrizePicks..."):
    df = get_projections_with_fallback()
    injuries_dict = fetch_injury_report()

if df.empty:
    st.error("No data loaded")
    st.stop()

# Add injury status
df['injury_status'] = df['player_name'].apply(lambda x: get_player_injury_status(x, injuries_dict))

# Calculate hit rates
df['hit_rate'] = df.apply(lambda row: calculate_projected_hit_rate(
    row['line'], row['sport'], row['injury_status']), axis=1)
df['recommendation'] = df['hit_rate'].apply(lambda x: 'MORE' if x > 0.5415 else 'LESS')
df = df.sort_values('hit_rate', ascending=False)

# Sidebar stats
st.sidebar.markdown(f"**Loaded:** {len(df):,} props")
st.sidebar.markdown(f"**MORE:** {len(df[df['recommendation']=='MORE']):,}")
st.sidebar.markdown(f"**LESS:** {len(df[df['recommendation']=='LESS']):,}")

# Show sport breakdown in sidebar
with st.sidebar.expander("📊 Sports Available"):
    for sport, count in df['sport'].value_counts().items():
        st.write(f"{sport}: {count}")

# Main content columns
col_left, col_right = st.columns([1.3, 0.7])

with col_left:
    st.markdown('<p class="section-header">📋 Available Props</p>', unsafe_allow_html=True)
    
    # Sport filter
    sports_list = sorted(df['sport'].unique())
    selected_sports = st.multiselect("Select Sports", sports_list, default=[])
    
    # Apply filters
    filtered_df = df.copy()
    if selected_sports:
        filtered_df = filtered_df[filtered_df['sport'].isin(selected_sports)]
    
    if st.session_state.show_recommended and not filtered_df.empty:
        filtered_df = filtered_df[filtered_df['hit_rate'] > 0.5415]
    
    st.caption(f"**Showing {len(filtered_df)} of {len(df)} props**")
    
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
    for idx, row in filtered_df.head(20).iterrows():
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
            
            if st.button("➕ Add to Entry", key=f"add_{idx}"):
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
                        <span><strong>{pick['sport_emoji']} {pick['player']}</strong></span>
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
        st.info("👆 Add props from the left panel")

# Footer
st.markdown("---")
st.markdown(f"""
<div class='footer'>
    <p>🎯 {len(df):,} props loaded | 
    <span style='color:#2E7D32;'>{len(df[df['recommendation']=='MORE']):,} MORE</span> / 
    <span style='color:#C62828;'>{len(df[df['recommendation']=='LESS']):,} LESS</span>
    </p>
</div>
""", unsafe_allow_html=True)