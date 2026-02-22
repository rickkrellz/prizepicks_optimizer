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

# ===================================================
# THE-ODDS-API KEY
# ===================================================

# 🔑 Your API key is set
ODDS_API_KEY = "047afdffc14ecda16cb02206a22070c4"

# ===================================================
# COMPLETE SPORT MAPPING
# ===================================================

SPORT_MAPPING = {
    '4': {'name': 'NBA Basketball', 'emoji': '🏀', 'api_sport': 'basketball_nba'},
    '2': {'name': 'NFL Football', 'emoji': '🏈', 'api_sport': 'americanfootball_nfl'},
    '1': {'name': 'MLB Baseball', 'emoji': '⚾', 'api_sport': 'baseball_mlb'},
    '3': {'name': 'NHL Hockey', 'emoji': '🏒', 'api_sport': 'icehockey_nhl'},
    '5': {'name': 'Soccer', 'emoji': '⚽', 'api_sport': 'soccer_uefa_champs_league'},
    '6': {'name': 'Golf', 'emoji': '🏌️', 'api_sport': 'golf_pga'},
    '7': {'name': 'MMA/UFC', 'emoji': '🥊', 'api_sport': 'mma_mixed_martial_arts'},
    '8': {'name': 'Tennis', 'emoji': '🎾', 'api_sport': 'tennis_atp'},
    '10': {'name': 'Esports', 'emoji': '🎮', 'api_sport': None},
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
            st.sidebar.info(f"📊 Using default odds - API limit may be reached")
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
# DATA SOURCE - USING SAMPLE DATA (PrizePicks API is protected)
# ===================================================

def get_projections():
    """Get player projections using sample data"""
    
    # Show data source notice
    st.sidebar.info("📊 Using sample data - PrizePicks API requires authentication")
    
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
        # NFL
        {'sport': 'NFL Football', 'sport_emoji': '🏈', 'player_name': 'Patrick Mahomes', 'line': 275.5, 'stat_type': 'Passing Yards', 'team': 'KC'},
        {'sport': 'NFL Football', 'sport_emoji': '🏈', 'player_name': 'Travis Kelce', 'line': 75.5, 'stat_type': 'Receiving Yards', 'team': 'KC'},
        {'sport': 'NFL Football', 'sport_emoji': '🏈', 'player_name': 'Christian McCaffrey', 'line': 110.5, 'stat_type': 'Rush+Yds', 'team': 'SF'},
        # MLB
        {'sport': 'MLB Baseball', 'sport_emoji': '⚾', 'player_name': 'Shohei Ohtani', 'line': 1.5, 'stat_type': 'Hits', 'team': 'LAD'},
        {'sport': 'MLB Baseball', 'sport_emoji': '⚾', 'player_name': 'Aaron Judge', 'line': 0.5, 'stat_type': 'Home Runs', 'team': 'NYY'},
        # NHL
        {'sport': 'NHL Hockey', 'sport_emoji': '🏒', 'player_name': 'Connor McDavid', 'line': 1.5, 'stat_type': 'Points', 'team': 'EDM'},
        {'sport': 'NHL Hockey', 'sport_emoji': '🏒', 'player_name': 'Auston Matthews', 'line': 0.5, 'stat_type': 'Goals', 'team': 'TOR'},
        # Soccer
        {'sport': 'Soccer', 'sport_emoji': '⚽', 'player_name': 'Lionel Messi', 'line': 0.5, 'stat_type': 'Goals', 'team': 'MIA'},
        {'sport': 'Soccer', 'sport_emoji': '⚽', 'player_name': 'Erling Haaland', 'line': 1.5, 'stat_type': 'Shots', 'team': 'MCI'},
        # Golf
        {'sport': 'Golf', 'sport_emoji': '🏌️', 'player_name': 'Scottie Scheffler', 'line': 68.5, 'stat_type': 'Round Score', 'team': 'USA'},
        {'sport': 'Golf', 'sport_emoji': '🏌️', 'player_name': 'Rory McIlroy', 'line': 69.5, 'stat_type': 'Round Score', 'team': 'NIR'},
        # MMA
        {'sport': 'MMA/UFC', 'sport_emoji': '🥊', 'player_name': 'Jon Jones', 'line': 45.5, 'stat_type': 'Significant Strikes', 'team': 'USA'},
        {'sport': 'MMA/UFC', 'sport_emoji': '🥊', 'player_name': 'Israel Adesanya', 'line': 2.5, 'stat_type': 'Takedowns', 'team': 'NZL'},
        # Esports
        {'sport': 'Esports', 'sport_emoji': '🎮', 'player_name': 'Faker', 'line': 5.5, 'stat_type': 'Kills', 'team': 'T1'},
        {'sport': 'Esports', 'sport_emoji': '🎮', 'player_name': 'Doublelift', 'line': 4.5, 'stat_type': 'Assists', 'team': '100T'},
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
        value=True,
        help="Automatically fill entry with top props"
    )
    
    st.session_state.show_recommended = st.checkbox(
        "Show only recommended picks",
        value=True,
        help="Only show props with hit rate > 54.15%"
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
    
    if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Main content
col_left, col_right = st.columns([1.3, 0.7])

with col_left:
    st.markdown('<p class="sub-header">📋 Available Props</p>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading projections..."):
        df = get_projections()
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
        default=['NBA Basketball']
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_sports:
        filtered_df = filtered_df[filtered_df['sport'].isin(selected_sports)]
    else:
        # If no sports selected, show NBA as default
        filtered_df = filtered_df[filtered_df['sport'] == 'NBA Basketball']
        st.info("👆 Select a sport above or viewing NBA by default")
    
    if st.session_state.show_recommended:
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
    
    # Display props - FIXED VERSION with proper badge rendering
    for idx, row in filtered_df.head(15).iterrows():
        # Determine colors
        hit_color = "value-positive" if row['hit_rate'] > 0.5415 else "value-negative"
        badge_color = "#4CAF50" if row['hit_rate'] > 0.5415 else "#f44336"
        
        # Build injury badge if needed
        injury_badge = ""
        if row['injury_status']['status'] != 'Active':
            injury_badge = f"<span class='injury-badge'>{row['injury_status']['status']}</span>"
        
        # Create prop card with proper badge rendering
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
    <p>🏆 Using sample data - PrizePicks API requires authentication | Auto picks enabled | Injuries included | 54.15% break-even threshold</p>
</div>
""", unsafe_allow_html=True)