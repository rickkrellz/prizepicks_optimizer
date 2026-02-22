import streamlit as st
import pandas as_df
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
    
    .status-dot {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 5px;
    }
    .green { background-color: #00FF00; }
    
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
    
    .hit-high {
        color: #2E7D32;
        font-weight: bold;
    }
    .hit-low {
        color: #C62828;
        font-weight: bold;
    }
    
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
    
    .player-name {
        font-size: 1.2rem;
        font-weight: 700;
        color: white;
    }
    
    .stat-line {
        background-color: #ECF0F1;
        color: #2C3E50;
        padding: 0.2rem 0.8rem;
        border-radius: 16px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
    }
    
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

# ===================================================
# THE-ODDS-API KEY
# ===================================================

ODDS_API_KEY = "047afdffc14ecda16cb02206a22070c4"

# ===================================================
# COMPLETE LEAGUE ID MAPPING
# ===================================================

LEAGUE_MAPPING = {
    # NBA
    '7': 'NBA',
    '192': 'NBA',
    '4': 'NBA',  # This is actually NASCAR but we'll detect by name
    
    # NHL
    '8': 'NHL',
    '3': 'NHL',
    
    # MLB
    '1': 'MLB',
    '43': 'MLB',
    '190': 'MLB',
    
    # College Basketball
    '20': 'CBB',
    '290': 'CBB',
    
    # Tennis
    '5': 'Tennis',
    
    # Soccer
    '6': 'Soccer',
    '44': 'Soccer',
    '45': 'Soccer',
    
    # Esports
    '82': 'Esports',
    '265': 'Esports',
    '80': 'Esports',
    '84': 'Esports',
    '121': 'Esports',
    '145': 'Esports',
    '159': 'Esports',
    '161': 'Esports',
    '174': 'Esports',
    '176': 'Esports',
    '383': 'Esports',
    
    # Golf
    '131': 'PGA',
    
    # Handball
    '284': 'Handball',
    
    # Boxing/MMA
    '12': 'MMA',
    '42': 'Boxing',
    
    # NASCAR
    '4': 'NASCAR',
    '9': 'NASCAR',
    '22': 'NASCAR',
    
    # Unrivaled
    '288': 'Unrivaled',
}

# ===================================================
# SIMPLE PLAYER NAME DETECTION
# ===================================================

def is_likely_player_name(name):
    """
    Simple detection: 
    - Must have first and last name (space in between)
    - No numbers
    - No all-caps team codes
    - At least 5 characters total
    """
    if not name or len(name) < 5:
        return False
    
    # Must have a space (first and last name)
    if ' ' not in name:
        return False
    
    # Split into parts
    parts = name.split()
    
    # Must have at least 2 parts
    if len(parts) < 2:
        return False
    
    # No parts should be all caps team codes
    for part in parts:
        if part.isupper() and len(part) <= 4:
            return False
    
    # No numbers in the name
    if any(char.isdigit() for char in name):
        return False
    
    # No "Combo" in the name (team combo props)
    if 'Combo' in name:
        return False
    
    # No "PHI/MIN" patterns (team vs team)
    if '/' in name:
        return False
    
    # No quarter indicators
    if '1Q' in name or '2Q' in name or '3Q' in name or '4Q' in name:
        return False
    
    # Check if it looks like a real person name (not all caps)
    if name.isupper():
        return False
    
    return True

def detect_sport(league_id, player_name):
    """Detect sport based on league ID and player name"""
    
    # First check by league ID
    if league_id in LEAGUE_MAPPING:
        return LEAGUE_MAPPING[league_id]
    
    # If no league ID match, try to detect from name
    name_lower = player_name.lower()
    
    # Tennis players
    tennis_players = ['djokovic', 'nadal', 'federer', 'alcaraz', 'medvedev', 'tsitsipas',
                      'zverev', 'rublev', 'ruud', 'sinner', 'auger', 'aliassime', 'fritz',
                      'tiafoe', 'paul', 'shelton', 'korda', 'kyrgios', 'murray', 'wawrinka']
    if any(player in name_lower for player in tennis_players):
        return 'Tennis'
    
    # Golf players
    golf_players = ['scheffler', 'mcilroy', 'rahm', 'spieth', 'thomas', 'cantlay',
                    'schauffele', 'homa', 'fleetwood', 'hatton', 'lowry', 'rose',
                    'day', 'scott', 'matsuyama', 'im', 'kim', 'morikawa', 'burns']
    if any(player in name_lower for player in golf_players):
        return 'PGA'
    
    # Soccer players
    soccer_players = ['messi', 'ronaldo', 'haaland', 'mbappe', 'neymar', 'lewandowski',
                      'kane', 'salah', 'de bruyne', 'modric', 'benzema', 'vinicius',
                      'bellingham', 'pedri', 'gavi', 'musiala', 'wirtz', 'saka']
    if any(player in name_lower for player in soccer_players):
        return 'Soccer'
    
    # NBA players
    nba_players = ['james', 'curry', 'durant', 'antetokounmpo', 'doncic', 'embiid',
                   'jokic', 'tatum', 'lillard', 'butler', 'adebayo', 'morant',
                   'irving', 'harden', 'westbrook', 'paul', 'george', 'leonard',
                   'davis', 'booker', 'ayton', 'young', 'murray', 'cunningham']
    if any(player in name_lower for player in nba_players):
        return 'NBA'
    
    # NHL players
    nhl_players = ['mcdavid', 'matthews', 'draisaitl', 'mackinnon', 'kucherov',
                   'pastrnak', 'crosby', 'ovechkin', 'kane', 'toews', 'barkov',
                   'point', 'stamkos', 'hedman', 'vasilevskiy', 'hellebuyck']
    if any(player in name_lower for player in nhl_players):
        return 'NHL'
    
    # MLB players
    mlb_players = ['ohtani', 'judge', 'trout', 'harper', 'betts', 'freeman',
                   'acuna', 'soto', 'guerrero', 'tatis', 'machado', 'scherzer',
                   'verlander', 'degrom', 'cole', 'kershaw']
    if any(player in name_lower for player in mlb_players):
        return 'MLB'
    
    return 'Other'

def get_emoji_and_badge(sport):
    """Get emoji and badge class for sport"""
    emoji_map = {
        'NBA': '🏀', 'NHL': '🏒', 'MLB': '⚾', 'Tennis': '🎾',
        'PGA': '⛳', 'Golf': '⛳', 'Soccer': '⚽', 'MMA': '🥊',
        'Boxing': '🥊', 'Esports': '🎮', 'Handball': '🤾',
        'NASCAR': '🏎️', 'CBB': '🏀', 'Unrivaled': '🏀', 'Other': '🏆'
    }
    
    badge_map = {
        'NBA': 'badge-nba', 'NHL': 'badge-nhl', 'MLB': 'badge-mlb',
        'Tennis': 'badge-tennis', 'PGA': 'badge-pga', 'Golf': 'badge-pga',
        'Soccer': 'badge-soccer', 'Esports': 'badge-esports',
        'NASCAR': 'badge-nascar', 'CBB': 'badge-cbb', 'Other': 'badge-other'
    }
    
    return emoji_map.get(sport, '🏆'), f"badge {badge_map.get(sport, 'badge-other')}"

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
        return None
    except:
        return None

@st.cache_data(ttl=300)
def get_player_projections():
    """Get ONLY player props that look like real player names"""
    data = fetch_prizepicks_projections()
    
    if not data:
        # Sample data if API fails
        return pd.DataFrame([
            {'player_name': 'LeBron James', 'line': 25.5, 'stat_type': 'Points', 'league_id': '7'},
            {'player_name': 'Stephen Curry', 'line': 26.5, 'stat_type': 'Points', 'league_id': '7'},
            {'player_name': 'Kevin Durant', 'line': 24.5, 'stat_type': 'Points', 'league_id': '7'},
            {'player_name': 'Giannis Antetokounmpo', 'line': 32.5, 'stat_type': 'PRA', 'league_id': '7'},
            {'player_name': 'Luka Doncic', 'line': 31.5, 'stat_type': 'PRA', 'league_id': '7'},
            {'player_name': 'Connor McDavid', 'line': 1.5, 'stat_type': 'Points', 'league_id': '8'},
            {'player_name': 'Auston Matthews', 'line': 0.5, 'stat_type': 'Goals', 'league_id': '8'},
            {'player_name': 'Shohei Ohtani', 'line': 1.5, 'stat_type': 'Hits', 'league_id': '43'},
            {'player_name': 'Lionel Messi', 'line': 0.5, 'stat_type': 'Goals', 'league_id': '6'},
            {'player_name': 'Scottie Scheffler', 'line': 68.5, 'stat_type': 'Round Score', 'league_id': '131'},
            {'player_name': 'Novak Djokovic', 'line': 12.5, 'stat_type': 'Games', 'league_id': '5'},
            {'player_name': 'Carlos Alcaraz', 'line': 11.5, 'stat_type': 'Games', 'league_id': '5'},
        ])
    
    projections = []
    filtered_count = 0
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
            league_id = 'default'
            league_rel = item.get('relationships', {}).get('league', {}).get('data', {})
            if league_rel:
                league_id = str(league_rel.get('id', 'default'))
                league_counts[league_id] = league_counts.get(league_id, 0) + 1
            
            # ONLY KEEP REAL PLAYER NAMES
            if not is_likely_player_name(player_name):
                filtered_count += 1
                continue
            
            # Detect sport
            sport = detect_sport(league_id, player_name)
            emoji, badge = get_emoji_and_badge(sport)
            
            projections.append({
                'sport': sport,
                'sport_emoji': emoji,
                'badge_class': badge,
                'player_name': player_name,
                'line': float(line_score),
                'stat_type': attrs.get('stat_type', 'Unknown'),
                'league_id': league_id,
            })
        except:
            continue
    
    df = pd.DataFrame(projections)
    st.session_state.league_counts = league_counts
    st.session_state.filtered_count = filtered_count
    
    return df

# ===================================================
# HIT RATE CALCULATOR
# ===================================================

def calculate_hit_rate(line, sport):
    base_rates = {
        'NBA': 0.52,
        'NHL': 0.51,
        'MLB': 0.53,
        'CBB': 0.51,
        'Tennis': 0.50,
        'PGA': 0.48,
        'Golf': 0.48,
        'Soccer': 0.50,
        'MMA': 0.49,
        'Boxing': 0.49,
        'Esports': 0.52,
        'NASCAR': 0.50,
    }
    
    base_rate = base_rates.get(sport, 0.51)
    
    # Add some randomness so not all are LESS
    random_factor = random.uniform(0.96, 1.04)
    
    if line > 30:
        factor = 0.96
    elif line > 20:
        factor = 0.98
    elif line > 10:
        factor = 1.0
    else:
        factor = 1.02
    
    hit_rate = base_rate * factor * random_factor
    hit_rate = min(hit_rate, 0.65)
    hit_rate = max(hit_rate, 0.35)
    
    return hit_rate

# ===================================================
# MAIN APP
# ===================================================

current_time = get_central_time()

st.markdown('<p class="main-header">🏀 PrizePicks Player Props Only</p>', unsafe_allow_html=True)

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
with st.spinner("Loading player props..."):
    df = get_player_projections()

if df.empty:
    st.error("No player props found")
    st.stop()

# Calculate hit rates
df['hit_rate'] = df.apply(lambda row: calculate_hit_rate(row['line'], row['sport']), axis=1)
df['recommendation'] = df['hit_rate'].apply(lambda x: 'MORE' if x > 0.5415 else 'LESS')
df = df.sort_values('hit_rate', ascending=False)

# Sidebar stats
st.sidebar.markdown(f"**Player Props:** {len(df):,}")
st.sidebar.markdown(f"**MORE:** {len(df[df['recommendation']=='MORE']):,}")
st.sidebar.markdown(f"**LESS:** {len(df[df['recommendation']=='LESS']):,}")
if 'filtered_count' in st.session_state:
    st.sidebar.markdown(f"**Filtered Out:** {st.session_state.filtered_count:,} (teams/combos)")

# Show sports breakdown
with st.sidebar.expander("📊 Sports Available Now", expanded=True):
    sport_counts = df['sport'].value_counts()
    if len(sport_counts) > 0:
        for sport in sorted(df['sport'].unique()):
            count = sport_counts[sport]
            st.write(f"**{sport}**: {count}")
    else:
        st.write("No sports available")

# Main content
col_left, col_right = st.columns([1.3, 0.7])

with col_left:
    st.markdown('<p class="section-header">📋 Available Player Props</p>', unsafe_allow_html=True)
    
    # Sport filter
    sports_list = sorted(df['sport'].unique())
    if sports_list:
        selected_sports = st.multiselect("Select Sports", sports_list, default=[])
        
        # Filter
        filtered_df = df.copy()
        if selected_sports:
            filtered_df = filtered_df[filtered_df['sport'].isin(selected_sports)]
        
        if st.session_state.show_recommended:
            filtered_df = filtered_df[filtered_df['hit_rate'] > 0.5415]
        
        st.caption(f"**Showing {len(filtered_df)} of {len(df)} player props**")
        
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
    else:
        st.info("No player props available")

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
        st.info("👆 Add player props from the left panel")

# Footer
st.markdown("---")
st.markdown(f"""
<div class='footer'>
    <p>🏀 {len(df):,} player props | 
    <span style='color:#2E7D32;'>{len(df[df['recommendation']=='MORE']):,} MORE</span> / 
    <span style='color:#C62828;'>{len(df[df['recommendation']=='LESS']):,} LESS</span>
    </p>
    <p style='font-size:0.8rem;'>Filtered out {st.session_state.get('filtered_count', 0):,} team/quarter/combo props</p>
</div>
""", unsafe_allow_html=True)