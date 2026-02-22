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

# ===================================================
# THE-ODDS-API KEY
# ===================================================

ODDS_API_KEY = "047afdffc14ecda16cb02206a22070c4"

# ===================================================
# COMPLETE SPORT MAPPING - Based on actual API League IDs
# ===================================================

SPORT_MAPPING = {
    # Major Sports
    '4': {'name': 'NBA Basketball', 'emoji': '🏀'},
    '1': {'name': 'MLB Baseball', 'emoji': '⚾'},
    '2': {'name': 'NFL Football', 'emoji': '🏈'},
    '3': {'name': 'NHL Hockey', 'emoji': '🏒'},
    '5': {'name': 'Soccer', 'emoji': '⚽'},
    '7': {'name': 'MMA/UFC', 'emoji': '🥊'},
    '8': {'name': 'Tennis', 'emoji': '🎾'},
    '6': {'name': 'Golf', 'emoji': '🏌️'},
    
    # Esports / Gaming (all the IDs you found)
    '10': {'name': 'Esports', 'emoji': '🎮'},
    '12': {'name': 'Esports', 'emoji': '🎮'},
    '20': {'name': 'Esports', 'emoji': '🎮'},
    '42': {'name': 'Esports', 'emoji': '🎮'},
    '43': {'name': 'Esports', 'emoji': '🎮'},
    '80': {'name': 'Esports', 'emoji': '🎮'},
    '82': {'name': 'Esports', 'emoji': '🎮'},
    '84': {'name': 'Esports', 'emoji': '🎮'},
    '121': {'name': 'Esports', 'emoji': '🎮'},
    '131': {'name': 'Esports', 'emoji': '🎮'},
    '145': {'name': 'Esports', 'emoji': '🎮'},
    '159': {'name': 'Esports', 'emoji': '🎮'},
    '161': {'name': 'Esports', 'emoji': '🎮'},
    '174': {'name': 'Esports', 'emoji': '🎮'},
    '176': {'name': 'Esports', 'emoji': '🎮'},
    '190': {'name': 'Esports', 'emoji': '🎮'},
    '192': {'name': 'Esports', 'emoji': '🎮'},
    '265': {'name': 'Esports', 'emoji': '🎮'},
    '277': {'name': 'Esports', 'emoji': '🎮'},
    '284': {'name': 'Esports', 'emoji': '🎮'},
    '288': {'name': 'Esports', 'emoji': '🎮'},
    '290': {'name': 'Esports', 'emoji': '🎮'},
    '379': {'name': 'Esports', 'emoji': '🎮'},
    '383': {'name': 'Esports', 'emoji': '🎮'},
    
    'default': {'name': 'Other Sports', 'emoji': '🏆'}
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
# AUTO-PICK ENGINE
# ===================================================

def calculate_projected_hit_rate(line, sport, injury_status):
    base_rates = {
        'NBA Basketball': 0.52,
        'NFL Football': 0.51,
        'MLB Baseball': 0.53,
        'NHL Hockey': 0.51,
        'Soccer': 0.50,
        'Esports': 0.52,
    }
    
    base_rate = base_rates.get(sport, 0.51)
    
    # Line adjustment
    if line > 50:
        line_factor = 0.95
    elif line > 20:
        line_factor = 0.98
    else:
        line_factor = 1.0
    
    # Injury adjustment
    injury_factor = 1.0
    if injury_status['status'] == 'OUT':
        injury_factor = 0.3
    elif injury_status['status'] == 'Questionable':
        injury_factor = 0.8
    
    hit_rate = base_rate * line_factor * injury_factor
    hit_rate = min(hit_rate, 0.75)
    
    recommendation = "MORE" if hit_rate > 0.5415 else "LESS"
    
    return hit_rate, recommendation

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
            
            # Get player name
            player_name = (attrs.get('name') or attrs.get('description') or '').strip()
            if not player_name:
                continue
            
            # Get league ID
            league_id = 'default'
            league_rel = item.get('relationships', {}).get('league', {}).get('data', {})
            if league_rel:
                league_id = str(league_rel.get('id', 'default'))
            
            # Get sport info
            sport_info = SPORT_MAPPING.get(league_id, SPORT_MAPPING['default'])
            
            # Get stat type
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

st.markdown('<p class="main-header">🏆 PrizePicks Optimizer</p>', unsafe_allow_html=True)
st.markdown(f"**Last Updated:** {datetime.now().strftime('%I:%M:%S %p')}")

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    num_legs = st.selectbox("Number of Legs", [6, 5, 4, 3, 2], index=0)
    st.session_state.entry_amount = st.number_input("Entry Amount ($)", 1.0, 100.0, 10.0)
    
    st.markdown("---")
    st.markdown("### 🤖 Auto Features")
    st.session_state.auto_select = st.checkbox("Auto-select best picks", value=True)
    st.session_state.show_recommended = st.checkbox("Show only recommended picks", value=True)
    
    st.markdown("---")
    st.markdown("### 📊 6-Leg Flex")
    st.markdown("**Break-even:** 54.15% per pick")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Main content
col_left, col_right = st.columns([1.3, 0.7])

with col_left:
    st.markdown('<p class="sub-header">📋 Available Props</p>', unsafe_allow_html=True)
    
    with st.spinner("Loading 17,000+ props from PrizePicks..."):
        df = get_all_sports_projections()
        injuries_dict = fetch_injury_report()
    
    if df.empty:
        st.error("No props loaded. Using sample data.")
        df = pd.DataFrame([
            {'sport': 'NBA Basketball', 'sport_emoji': '🏀', 'player_name': 'Dillon Brooks', 'line': 23.5, 'stat_type': 'Points'},
            {'sport': 'NBA Basketball', 'sport_emoji': '🏀', 'player_name': 'Desmond Bane', 'line': 18.5, 'stat_type': 'Points'},
        ])
    
    # Add injury status and hit rates
    df['injury_status'] = df['player_name'].apply(lambda x: get_player_injury_status(x, injuries_dict))
    
    hit_results = df.apply(lambda row: calculate_projected_hit_rate(
        row['line'], row['sport'], row['injury_status']), axis=1)
    
    df['hit_rate'] = [hr[0] for hr in hit_results]
    df['recommendation'] = [hr[1] for hr in hit_results]
    
    # Sort by hit rate
    df = df.sort_values('hit_rate', ascending=False)
    
    # Show total count
    st.sidebar.success(f"✅ Loaded {len(df):,} props from PrizePicks")
    
    # Sport filter
    sports_list = sorted(df['sport'].unique())
    default_sports = ['NBA Basketball'] if 'NBA Basketball' in sports_list else []
    selected_sports = st.multiselect("Select Sports", sports_list, default=default_sports)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_sports:
        filtered_df = filtered_df[filtered_df['sport'].isin(selected_sports)]
    
    if st.session_state.show_recommended and not filtered_df.empty:
        filtered_df = filtered_df[filtered_df['hit_rate'] > 0.5415]
    
    st.caption(f"**Showing {len(filtered_df):,} of {len(df):,} total props**")
    
    # Auto-select if enabled
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
                'injury': row['injury_status']['status'],
            })
        st.rerun()
    
    # Display props
    for idx, row in filtered_df.head(20).iterrows():
        hit_color = "value-positive" if row['hit_rate'] > 0.5415 else "value-negative"
        badge_color = "#4CAF50" if row['hit_rate'] > 0.5415 else "#f44336"
        
        injury_badge = f"<span class='injury-badge'>{row['injury_status']['status']}</span>" if row['injury_status']['status'] != 'Active' else ""
        
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
                    <span style='background-color: {badge_color}; color: white; padding: 0.2rem 0.5rem; border-radius: 1rem; font-size: 0.8rem; font-weight: bold; min-width: 45px; text-align: center;'>
                        {row['recommendation']}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            pick = st.selectbox("Pick", ["MORE", "LESS"], 
                               index=0 if row['recommendation'] == "MORE" else 1,
                               key=f"pick_{idx}", label_visibility="collapsed")
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
                    })
                    st.rerun()

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

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; font-size: 0.8rem;'>
    <p>🏆 {len(df):,} live props loaded from PrizePicks | Auto picks enabled | 54.15% break-even</p>
</div>
""", unsafe_allow_html=True)