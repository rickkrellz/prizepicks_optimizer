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
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better colors and visibility
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #0D47A1;
        margin-top: 1rem;
    }
    /* Better color scheme */
    .more-badge {
        background-color: #2E7D32;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 2rem;
        font-size: 0.9rem;
        font-weight: bold;
        display: inline-block;
        text-align: center;
        min-width: 60px;
    }
    .less-badge {
        background-color: #C62828;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 2rem;
        font-size: 0.9rem;
        font-weight: bold;
        display: inline-block;
        text-align: center;
        min-width: 60px;
    }
    .hit-rate-high {
        color: #2E7D32;
        font-weight: 700;
        font-size: 1rem;
    }
    .hit-rate-low {
        color: #C62828;
        font-weight: 700;
        font-size: 1rem;
    }
    .sport-badge {
        background-color: #E1F5FE;
        color: #01579B;
        padding: 0.2rem 0.6rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    .injury-badge {
        background-color: #FF9800;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }
    .stButton button {
        width: 100%;
        font-size: 0.9rem;
        padding: 0.3rem;
        border-radius: 0.5rem;
    }
    .pick-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.8rem;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .player-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }
    .player-info {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        flex-wrap: wrap;
    }
    .player-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #0D47A1;
    }
    .player-stats {
        display: flex;
        align-items: center;
        gap: 1rem;
        flex-wrap: wrap;
    }
    .stat-line {
        font-size: 1rem;
        font-weight: 500;
        color: #424242;
    }
    .entry-card {
        background-color: #F5F5F5;
        padding: 0.8rem;
        border-radius: 0.8rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1E88E5;
    }
    .summary-box {
        background-color: #E3F2FD;
        padding: 1.2rem;
        border-radius: 0.8rem;
        border-left: 4px solid #1E88E5;
        margin: 1rem 0;
    }
    .positive-ev {
        color: #2E7D32;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .negative-ev {
        color: #C62828;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .footer {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        margin-top: 2rem;
        padding: 1rem;
        background-color: #F5F5F5;
        border-radius: 0.5rem;
    }
    @media (max-width: 768px) {
        .player-row {
            flex-direction: column;
            align-items: flex-start;
        }
        .player-stats {
            width: 100%;
            justify-content: space-between;
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
    st.session_state.show_recommended = False
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

# ===================================================
# THE-ODDS-API KEY
# ===================================================

ODDS_API_KEY = "047afdffc14ecda16cb02206a22070c4"

# ===================================================
# SPORT MAPPING
# ===================================================

SPORT_MAPPING = {
    '4': {'name': 'NBA', 'emoji': '🏀'},
    '1': {'name': 'MLB', 'emoji': '⚾'},
    '2': {'name': 'NFL', 'emoji': '🏈'},
    '3': {'name': 'NHL', 'emoji': '🏒'},
    '5': {'name': 'Soccer', 'emoji': '⚽'},
    '7': {'name': 'MMA', 'emoji': '🥊'},
    '8': {'name': 'Tennis', 'emoji': '🎾'},
    '6': {'name': 'Golf', 'emoji': '🏌️'},
    '10': {'name': 'Esports', 'emoji': '🎮'},
    'default': {'name': 'Other', 'emoji': '🏆'}
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
        'LeBron James': {'status': 'Active'},
        'Stephen Curry': {'status': 'Active'},
        'Luka Doncic': {'status': 'Active'},
    }
    return injuries

def get_player_injury_status(player_name, injuries_dict):
    for name, info in injuries_dict.items():
        if name.lower() in player_name.lower():
            return info
    return {'status': 'Active'}

# ===================================================
# AUTO-PICK ENGINE
# ===================================================

def calculate_projected_hit_rate(line, sport, injury_status):
    base_rates = {
        'NBA': 0.48,
        'NFL': 0.51,
        'MLB': 0.53,
        'NHL': 0.51,
        'Soccer': 0.50,
        'Esports': 0.52,
        'MMA': 0.49,
        'Tennis': 0.50,
        'Golf': 0.48,
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
            
            projections.append({
                'sport': sport_info['name'],
                'sport_emoji': sport_info['emoji'],
                'player_name': player_name,
                'line': float(line_score),
                'stat_type': stat_type,
            })
        except:
            continue
    
    return pd.DataFrame(projections)

# ===================================================
# MAIN APP
# ===================================================

st.markdown('<p class="main-header">🏀 PrizePicks Optimizer</p>', unsafe_allow_html=True)
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
    
    st.session_state.debug_mode = st.checkbox("🔧 Debug Mode", value=False)
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Load data
with st.spinner("Loading props from PrizePicks..."):
    df = get_all_sports_projections()
    injuries_dict = fetch_injury_report()

if df.empty:
    st.error("No props loaded. Using sample data.")
    df = pd.DataFrame([
        {'sport': 'NBA', 'sport_emoji': '🏀', 'player_name': 'Dillon Brooks', 'line': 23.5, 'stat_type': 'Points'},
        {'sport': 'NBA', 'sport_emoji': '🏀', 'player_name': 'Desmond Bane', 'line': 18.5, 'stat_type': 'Points'},
        {'sport': 'NBA', 'sport_emoji': '🏀', 'player_name': 'Anthony Black', 'line': 16.5, 'stat_type': 'Points'},
        {'sport': 'NBA', 'sport_emoji': '🏀', 'player_name': 'Cade Cunningham', 'line': 25.5, 'stat_type': 'Points'},
    ])

# Add injury status and hit rates
df['injury_status'] = df['player_name'].apply(lambda x: get_player_injury_status(x, injuries_dict))
df['hit_rate'] = df.apply(lambda row: calculate_projected_hit_rate(row['line'], row['sport'], row['injury_status']), axis=1)
df['recommendation'] = df['hit_rate'].apply(lambda x: 'MORE' if x > 0.5415 else 'LESS')
df = df.sort_values('hit_rate', ascending=False)

# Sidebar stats
st.sidebar.markdown(f"**Loaded:** {len(df):,} props")
st.sidebar.markdown(f"**MORE:** {len(df[df['recommendation']=='MORE']):,}")
st.sidebar.markdown(f"**LESS:** {len(df[df['recommendation']=='LESS']):,}")

# Debug view
if st.session_state.debug_mode:
    with st.sidebar.expander("📊 Sport Breakdown"):
        for sport, count in df['sport'].value_counts().items():
            more = len(df[(df['sport']==sport) & (df['recommendation']=='MORE')])
            st.write(f"{sport}: {count} ({more} MORE)")

# Main content
col_left, col_right = st.columns([1.3, 0.7])

with col_left:
    st.markdown('<p class="sub-header">📋 Available Props</p>', unsafe_allow_html=True)
    
    # Sport filter
    sports_list = sorted(df['sport'].unique())
    default_sports = ['NBA'] if 'NBA' in sports_list else []
    selected_sports = st.multiselect("Select Sports", sports_list, default=default_sports)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_sports:
        filtered_df = filtered_df[filtered_df['sport'].isin(selected_sports)]
    
    if st.session_state.show_recommended and not filtered_df.empty:
        filtered_df = filtered_df[filtered_df['hit_rate'] > 0.5415]
    
    st.caption(f"**Showing {len(filtered_df):,} of {len(df):,} total props**")
    
    # Auto-select
    if st.session_state.auto_select and len(st.session_state.picks) == 0 and len(filtered_df) >= num_legs:
        for _, row in filtered_df.head(num_legs).iterrows():
            st.session_state.picks.append({
                'sport_emoji': row['sport_emoji'],
                'sport': row['sport'],
                'player': row['player_name'],
                'stat': row['stat_type'],
                'line': row['line'],
                'pick': row['recommendation'],
                'hit_rate': row['hit_rate'],
            })
        st.rerun()
    
    # Display props - CLEAN VERSION WITH PROPER INFO
    for idx, row in filtered_df.head(20).iterrows():
        # Create the prop card with all information visible
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{row['sport_emoji']} {row['player_name']}**")
                st.markdown(f"<span class='sport-badge'>{row['sport']}</span>", unsafe_allow_html=True)
                if row['injury_status']['status'] != 'Active':
                    st.markdown(f"<span class='injury-badge'>{row['injury_status']['status']}</span>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{row['stat_type']}**")
                st.markdown(f"{row['line']:.1f}")
            
            with col3:
                # Hit rate with color
                hit_color = "hit-rate-high" if row['hit_rate'] > 0.5415 else "hit-rate-low"
                st.markdown(f"<span class='{hit_color}'>{row['hit_rate']*100:.1f}%</span>", unsafe_allow_html=True)
                
                # Recommendation badge
                if row['recommendation'] == 'MORE':
                    st.markdown("<span class='more-badge'>MORE</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='less-badge'>LESS</span>", unsafe_allow_html=True)
            
            # Add button
            if st.button("➕ Add to Entry", key=f"add_{idx}", use_container_width=True):
                if len(st.session_state.picks) < num_legs:
                    st.session_state.picks.append({
                        'sport_emoji': row['sport_emoji'],
                        'sport': row['sport'],
                        'player': row['player_name'],
                        'stat': row['stat_type'],
                        'line': row['line'],
                        'pick': row['recommendation'],
                        'hit_rate': row['hit_rate'],
                    })
                    st.rerun()
            
            st.markdown("---")

with col_right:
    st.markdown('<p class="sub-header">📝 Your Entry</p>', unsafe_allow_html=True)
    
    if st.session_state.picks:
        for i, pick in enumerate(st.session_state.picks):
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{pick['sport_emoji']} {pick['player']}**")
                    st.markdown(f"{pick['stat']} {pick['line']:.1f}")
                    st.markdown(f"Hit rate: {pick['hit_rate']*100:.1f}%")
                
                with col2:
                    if pick['pick'] == 'MORE':
                        st.markdown("<span class='more-badge'>MORE</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span class='less-badge'>LESS</span>", unsafe_allow_html=True)
                    
                    if st.button("❌", key=f"remove_{i}"):
                        st.session_state.picks.pop(i)
                        st.rerun()
                
                st.markdown("---")
        
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
                    <h4 style='margin:0;'>🎯 Entry Summary</h4>
                    <p><strong>Avg Hit Rate:</strong> {avg_hit*100:.1f}%</p>
                    <p><strong>Expected Return:</strong> ${ev:.2f}</p>
                    <p><strong>ROI:</strong> {roi:.1f}%</p>
                    <p class='{"positive-ev" if roi>0 else "negative-ev"}'><strong>{'✅ +EV' if roi>0 else '⚠️ -EV'}</strong></p>
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
    <p>🏀 {len(df):,} live props loaded | {len(df[df['recommendation']=='MORE']):,} MORE / {len(df[df['recommendation']=='LESS']):,} LESS recommendations</p>
</div>
""", unsafe_allow_html=True)