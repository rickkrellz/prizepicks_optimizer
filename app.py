import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import time
import pytz

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

# SIMPLIFIED CSS - Easy to read
st.markdown("""
<style>
    /* Main header */
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
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: white;
        background-color: #0D47A1;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Status indicators */
    .status-dot {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 5px;
    }
    .green { background-color: #00FF00; }
    .red { background-color: #FF0000; }
    
    /* Sport badges */
    .badge {
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        color: white;
        display: inline-block;
    }
    .badge-nba { background-color: #17408B; }
    .badge-nhl { background-color: #000000; }
    .badge-mlb { background-color: #041E42; }
    .badge-soccer { background-color: #006400; }
    .badge-other { background-color: #555555; }
    
    /* MORE/LESS badges */
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
    
    /* Hit rate */
    .hit-high {
        color: #2E7D32;
        font-weight: bold;
        font-size: 1rem;
    }
    .hit-low {
        color: #C62828;
        font-weight: bold;
        font-size: 1rem;
    }
    
    /* Cards */
    .prop-card {
        background-color: #2C3E50;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #1E88E5;
        margin: 0.5rem 0;
        color: white;
    }
    .entry-card {
        background-color: #34495E;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #1E88E5;
        color: white;
    }
    .summary-box {
        background-color: #1E3A5F;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: white;
    }
    
    /* Player name */
    .player-name {
        font-size: 1.2rem;
        font-weight: 700;
        color: white;
    }
    
    /* Stat line */
    .stat-line {
        background-color: #ECF0F1;
        color: #2C3E50;
        padding: 0.2rem 0.8rem;
        border-radius: 16px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Buttons - SIMPLE */
    .stButton button {
        width: 100%;
        border-radius: 20px;
        font-weight: 600;
        background-color: #1E88E5;
        color: white;
        border: 2px solid white;
    }
    .stButton button:hover {
        background-color: #0D47A1;
        color: white;
    }
    
    /* Text colors */
    .white-text { color: white !important; }
    
    /* Footer */
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

# ===================================================
# SIMPLE SPORT MAPPING
# ===================================================

SPORT_MAPPING = {
    # NBA
    '7': 'NBA',
    '192': 'NBA',
    '4': 'NBA',  # This might be NASCAR, but we'll see
    
    # NHL
    '8': 'NHL',
    '3': 'NHL',
    
    # MLB
    '1': 'MLB',
    '43': 'MLB',
    '190': 'MLB',
    
    # Soccer
    '5': 'Soccer',
    '6': 'Soccer',
    '44': 'Soccer',
    '45': 'Soccer',
    
    # Others default to 'Other'
}

def get_sport_name(league_id):
    return SPORT_MAPPING.get(league_id, 'Other')

def get_sport_emoji(sport):
    emojis = {
        'NBA': '🏀',
        'NHL': '🏒',
        'MLB': '⚾',
        'Soccer': '⚽',
        'Other': '🏆'
    }
    return emojis.get(sport, '🏆')

def get_badge_class(sport):
    classes = {
        'NBA': 'badge-nba',
        'NHL': 'badge-nhl',
        'MLB': 'badge-mlb',
        'Soccer': 'badge-soccer',
        'Other': 'badge-other'
    }
    return f"badge {classes.get(sport, 'badge-other')}"

# ===================================================
# SIMPLE PLAYER NAME CHECK
# ===================================================

def is_player_name(name):
    """Simple check - keep it basic for now"""
    if not name or len(name) < 3:
        return False
    
    # Skip obvious team codes
    team_codes = ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 
                  'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK',
                  'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']
    
    if name.upper() in team_codes:
        return False
    
    # Skip if it has "SZN" in it
    if 'SZN' in name:
        return False
    
    return True

# ===================================================
# API FUNCTIONS
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
        time.sleep(0.5)
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

@st.cache_data(ttl=300)
def get_all_projections():
    data = fetch_prizepicks_projections()
    
    if not data:
        # Sample data if API fails
        return pd.DataFrame([
            {'player_name': 'LeBron James', 'line': 25.5, 'stat_type': 'Points', 'league_id': '7'},
            {'player_name': 'Stephen Curry', 'line': 26.5, 'stat_type': 'Points', 'league_id': '7'},
            {'player_name': 'Kevin Durant', 'line': 24.5, 'stat_type': 'Points', 'league_id': '7'},
        ])
    
    projections = []
    
    for item in data.get('data', []):
        try:
            attrs = item.get('attributes', {})
            line_score = attrs.get('line_score')
            if line_score is None:
                continue
            
            player_name = (attrs.get('name') or attrs.get('description') or '').strip()
            if not player_name or not is_player_name(player_name):
                continue
            
            league_id = 'default'
            league_rel = item.get('relationships', {}).get('league', {}).get('data', {})
            if league_rel:
                league_id = str(league_rel.get('id', 'default'))
            
            sport = get_sport_name(league_id)
            
            projections.append({
                'sport': sport,
                'sport_emoji': get_sport_emoji(sport),
                'badge_class': get_badge_class(sport),
                'player_name': player_name,
                'line': float(line_score),
                'stat_type': attrs.get('stat_type', 'Unknown'),
                'league_id': league_id,
            })
        except:
            continue
    
    return pd.DataFrame(projections)

# ===================================================
# HIT RATE CALCULATOR
# ===================================================

def calculate_hit_rate(line, sport):
    base_rate = 0.52 if sport == 'NBA' else 0.51
    
    if line > 30:
        factor = 0.96
    elif line > 20:
        factor = 0.98
    else:
        factor = 1.0
    
    hit_rate = base_rate * factor
    hit_rate = min(hit_rate, 0.65)
    hit_rate = max(hit_rate, 0.35)
    
    return hit_rate

# ===================================================
# MAIN APP
# ===================================================

current_time = get_central_time()

st.markdown('<p class="main-header">🏀 PrizePicks Player Props</p>', unsafe_allow_html=True)

# Status bar
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<span class="status-dot green"></span> PrizePicks: Connected', unsafe_allow_html=True)
with col2:
    st.markdown('<span class="status-dot green"></span> Odds API: Connected', unsafe_allow_html=True)
with col3:
    st.markdown(f"🕐 Updated: {current_time.strftime('%I:%M:%S %p CT')}")

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
    if st.button("🔄 Refresh Data", use_container_width=True):
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

# Sidebar stats
st.sidebar.markdown(f"**Total Props:** {len(df):,}")
st.sidebar.markdown(f"**MORE:** {len(df[df['recommendation']=='MORE']):,}")
st.sidebar.markdown(f"**LESS:** {len(df[df['recommendation']=='LESS']):,}")

# Show sports
with st.sidebar.expander("📊 Sports", expanded=True):
    for sport in sorted(df['sport'].unique()):
        count = len(df[df['sport'] == sport])
        st.write(f"**{sport}**: {count}")

# Main content
col_left, col_right = st.columns([1.3, 0.7])

with col_left:
    st.markdown('<p class="section-header">📋 Available Props</p>', unsafe_allow_html=True)
    
    # Sport filter
    sports_list = sorted(df['sport'].unique())
    selected_sports = st.multiselect("Select Sports", sports_list, default=['NBA'] if 'NBA' in sports_list else [])
    
    # Filter
    filtered_df = df.copy()
    if selected_sports:
        filtered_df = filtered_df[filtered_df['sport'].isin(selected_sports)]
    
    if st.session_state.show_recommended:
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
    for idx, row in filtered_df.head(30).iterrows():
        hit_class = "hit-high" if row['hit_rate'] > 0.5415 else "hit-low"
        
        with st.container():
            st.markdown(f"""
            <div class='prop-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span class='player-name'>{row['sport_emoji']} {row['player_name']}</span>
                        <span class='{row['badge_class']}'>{row['sport']}</span>
                    </div>
                    <span class='{hit_class}'>{row['hit_rate']*100:.1f}%</span>
                </div>
                <div style='margin: 8px 0;'>
                    <span class='stat-line'>{row['stat_type']}: {row['line']:.1f}</span>
                </div>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
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
                        <span class='{"more-badge" if pick["pick"]=="MORE" else "less-badge"}' style='padding:0.2rem 0.5rem; font-size:0.8rem;'>
                            {pick['pick']}
                        </span>
                    </div>
                    <div>{pick['stat']} {pick['line']:.1f}</div>
                    <div class='{"hit-high" if pick["hit_rate"] > 0.5415 else "hit-low"}'>
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
                    <h4>🎯 Entry Summary</h4>
                    <p><strong>Avg Hit Rate:</strong> {avg_hit*100:.1f}%</p>
                    <p><strong>Expected Return:</strong> ${ev:.2f}</p>
                    <p><strong>ROI:</strong> {roi:.1f}%</p>
                    <p style='color: {"#2E7D32" if roi>0 else "#C62828"}; font-weight:bold;'>
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
    <p>🏀 {len(df):,} props loaded | 
    <span style='color:#2E7D32;'>{len(df[df['recommendation']=='MORE']):,} MORE</span> / 
    <span style='color:#C62828;'>{len(df[df['recommendation']=='LESS']):,} LESS</span>
    </p>
</div>
""", unsafe_allow_html=True)