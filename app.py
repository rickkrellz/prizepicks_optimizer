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
    .badge-team { background-color: #FFA500; }  /* Orange for team props */
    
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
    
    .team-tag {
        background-color: #FFA500;
        color: black;
        padding: 0.1rem 0.4rem;
        border-radius: 8px;
        font-size: 0.7rem;
        font-weight: bold;
        margin-left: 5px;
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
    
    .team-note {
        background-color: #FFA500;
        color: black;
        padding: 0.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-weight: bold;
        text-align: center;
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
if 'show_team_props' not in st.session_state:
    st.session_state.show_team_props = True

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

# ===================================================
# TEAM MAPPINGS FOR ALL MAJOR SPORTS
# ===================================================

NBA_TEAMS = {
    'ATL': 'Hawks', 'BOS': 'Celtics', 'BKN': 'Nets', 'CHA': 'Hornets', 'CHI': 'Bulls',
    'CLE': 'Cavaliers', 'DAL': 'Mavericks', 'DEN': 'Nuggets', 'DET': 'Pistons', 'GSW': 'Warriors',
    'HOU': 'Rockets', 'IND': 'Pacers', 'LAC': 'Clippers', 'LAL': 'Lakers', 'MEM': 'Grizzlies',
    'MIA': 'Heat', 'MIL': 'Bucks', 'MIN': 'Timberwolves', 'NOP': 'Pelicans', 'NYK': 'Knicks',
    'OKC': 'Thunder', 'ORL': 'Magic', 'PHI': '76ers', 'PHX': 'Suns', 'POR': 'Trail Blazers',
    'SAC': 'Kings', 'SAS': 'Spurs', 'TOR': 'Raptors', 'UTA': 'Jazz', 'WAS': 'Wizards'
}

NHL_TEAMS = {
    'ANA': 'Ducks', 'ARI': 'Coyotes', 'BOS': 'Bruins', 'BUF': 'Sabres', 'CGY': 'Flames',
    'CAR': 'Hurricanes', 'CHI': 'Blackhawks', 'COL': 'Avalanche', 'CBJ': 'Blue Jackets',
    'DAL': 'Stars', 'DET': 'Red Wings', 'EDM': 'Oilers', 'FLA': 'Panthers', 'LAK': 'Kings',
    'MIN': 'Wild', 'MTL': 'Canadiens', 'NSH': 'Predators', 'NJD': 'Devils', 'NYI': 'Islanders',
    'NYR': 'Rangers', 'OTT': 'Senators', 'PHI': 'Flyers', 'PIT': 'Penguins', 'SJS': 'Sharks',
    'SEA': 'Kraken', 'STL': 'Blues', 'TBL': 'Lightning', 'TOR': 'Maple Leafs', 'VAN': 'Canucks',
    'VGK': 'Golden Knights', 'WSH': 'Capitals', 'WPG': 'Jets'
}

MLB_TEAMS = {
    'ARI': 'Diamondbacks', 'ATL': 'Braves', 'BAL': 'Orioles', 'BOS': 'Red Sox',
    'CHC': 'Cubs', 'CIN': 'Reds', 'CLE': 'Guardians', 'COL': 'Rockies', 'CWS': 'White Sox',
    'DET': 'Tigers', 'HOU': 'Astros', 'KC': 'Royals', 'LAA': 'Angels', 'LAD': 'Dodgers',
    'MIA': 'Marlins', 'MIL': 'Brewers', 'MIN': 'Twins', 'NYM': 'Mets', 'NYY': 'Yankees',
    'OAK': 'Athletics', 'PHI': 'Phillies', 'PIT': 'Pirates', 'SD': 'Padres', 'SF': 'Giants',
    'SEA': 'Mariners', 'STL': 'Cardinals', 'TB': 'Rays', 'TEX': 'Rangers', 'TOR': 'Blue Jays',
    'WSH': 'Nationals'
}

NFL_TEAMS = {
    'ARI': 'Cardinals', 'ATL': 'Falcons', 'BAL': 'Ravens', 'BUF': 'Bills', 'CAR': 'Panthers',
    'CHI': 'Bears', 'CIN': 'Bengals', 'CLE': 'Browns', 'DAL': 'Cowboys', 'DEN': 'Broncos',
    'DET': 'Lions', 'GB': 'Packers', 'HOU': 'Texans', 'IND': 'Colts', 'JAX': 'Jaguars',
    'KC': 'Chiefs', 'LV': 'Raiders', 'LAC': 'Chargers', 'LAR': 'Rams', 'MIA': 'Dolphins',
    'MIN': 'Vikings', 'NE': 'Patriots', 'NO': 'Saints', 'NYG': 'Giants', 'NYJ': 'Jets',
    'PHI': 'Eagles', 'PIT': 'Steelers', 'SF': '49ers', 'SEA': 'Seahawks', 'TB': 'Buccaneers',
    'TEN': 'Titans', 'WAS': 'Commanders'
}

# Known player names for detection (from your working list)
KNOWN_PLAYERS = [
    # NBA
    'LeBron James', 'Stephen Curry', 'Kevin Durant', 'Giannis Antetokounmpo', 'Luka Doncic',
    'Joel Embiid', 'Nikola Jokic', 'Jayson Tatum', 'Shai Gilgeous-Alexander', 'Anthony Davis',
    'Devin Booker', 'Donovan Mitchell', 'Trae Young', 'Zion Williamson', 'Ja Morant',
    'Kyrie Irving', 'James Harden', 'Chris Paul', 'Kawhi Leonard', 'Paul George',
    'Jimmy Butler', 'Bam Adebayo', 'Tyrese Haliburton', 'LaMelo Ball', 'Cade Cunningham',
    'Victor Wembanyama', 'Chet Holmgren', 'Jalen Williams', 'Scottie Barnes', 'Evan Mobley',
    'Paolo Banchero', 'Franz Wagner', 'Jalen Green', 'Alperen Sengun', 'Jaren Jackson Jr.',
    'Desmond Bane', 'Dillon Brooks',
    
    # NHL
    'Connor McDavid', 'Auston Matthews', 'Leon Draisaitl', 'Nathan MacKinnon', 'Nikita Kucherov',
    'David Pastrnak', 'Sidney Crosby', 'Alex Ovechkin', 'Patrick Kane', 'Jonathan Toews',
    'Aleksander Barkov', 'Brayden Point', 'Steven Stamkos', 'Victor Hedman', 'Andrei Vasilevskiy',
    
    # MLB
    'Shohei Ohtani', 'Aaron Judge', 'Mike Trout', 'Bryce Harper', 'Mookie Betts',
    'Freddie Freeman', 'Ronald Acuña Jr.', 'Juan Soto', 'Vladimir Guerrero Jr.', 'Fernando Tatis Jr.',
    'Manny Machado', 'Max Scherzer', 'Justin Verlander', 'Jacob deGrom', 'Gerrit Cole',
    'Clayton Kershaw',
    
    # Tennis
    'Novak Djokovic', 'Carlos Alcaraz', 'Jannik Sinner', 'Daniil Medvedev', 'Alexander Zverev',
    'Andrey Rublev', 'Casper Ruud', 'Stefanos Tsitsipas', 'Holger Rune', 'Taylor Fritz',
    'Frances Tiafoe', 'Tommy Paul', 'Ben Shelton', 'Sebastian Korda', 'Nick Kyrgios',
    'Andy Murray', 'Stan Wawrinka',
    
    # Golf
    'Scottie Scheffler', 'Rory McIlroy', 'Jon Rahm', 'Xander Schauffele', 'Patrick Cantlay',
    'Viktor Hovland', 'Ludvig Aberg', 'Max Homa', 'Tony Finau', 'Collin Morikawa',
    'Jordan Spieth', 'Justin Thomas', 'Brooks Koepka', 'Bryson DeChambeau', 'Dustin Johnson',
    'Cameron Smith', 'Hideki Matsuyama', 'Sungjae Im', 'Tom Kim', 'Sam Burns',
    
    # Soccer
    'Lionel Messi', 'Cristiano Ronaldo', 'Erling Haaland', 'Kylian Mbappé', 'Neymar Jr',
    'Robert Lewandowski', 'Harry Kane', 'Mohamed Salah', 'Kevin De Bruyne', 'Luka Modric',
    'Karim Benzema', 'Vinícius Jr', 'Jude Bellingham', 'Pedri', 'Gavi', 'Jamal Musiala',
    'Florian Wirtz', 'Bukayo Saka', 'Phil Foden'
]

def get_team_info(name, sport):
    """Extract team information and format display name"""
    if not name:
        return name, None, False
    
    # Check if it's a quarter/half prop
    if re.search(r'[0-9][QH]', name):
        return f"{name} (Quarter Team Prop)", name, True
    
    # Check if it's a 3-letter team code
    if len(name) == 3 and name.isupper():
        if sport == 'NBA' and name in NBA_TEAMS:
            return f"{name} {NBA_TEAMS[name]}", name, True
        elif sport == 'NHL' and name in NHL_TEAMS:
            return f"{name} {NHL_TEAMS[name]}", name, True
        elif sport == 'MLB' and name in MLB_TEAMS:
            return f"{name} {MLB_TEAMS[name]}", name, True
        elif sport == 'NFL' and name in NFL_TEAMS:
            return f"{name} {NFL_TEAMS[name]}", name, True
        else:
            return f"{name} Team", name, True
    
    # Check if it's in known players list
    name_lower = name.lower()
    for player in KNOWN_PLAYERS:
        if player.lower() in name_lower:
            return name, None, False
    
    # Check if it has a space (likely a player name)
    if ' ' in name:
        return name, None, False
    
    # Default: treat as team prop
    return f"{name} (Team)", name, True

def get_badge_class(sport, is_team):
    """Get badge class based on sport and whether it's a team prop"""
    if is_team:
        return "badge-team"
    
    badge_map = {
        'NBA': 'badge-nba', 'NHL': 'badge-nhl', 'MLB': 'badge-mlb',
        'Tennis': 'badge-tennis', 'Soccer': 'badge-soccer', 'Golf': 'badge-pga',
        'Esports': 'badge-esports', 'CBB': 'badge-cbb', 'NASCAR': 'badge-nascar',
        'Other': 'badge-other'
    }
    return badge_map.get(sport, 'badge-other')

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
            
            # Get team info and formatted name
            display_name, team_code, is_team = get_team_info(player_name, sport)
            
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
                'is_team': is_team,
                'line': float(line_score),
                'stat_type': attrs.get('stat_type', 'Unknown'),
            })
        except:
            continue
    
    st.session_state.league_counts = league_counts
    return pd.DataFrame(projections)

# Hit rate calculator
def calculate_hit_rate(line, sport):
    base_rates = {
        'NBA': 0.52, 'NHL': 0.51, 'MLB': 0.53, 'Tennis': 0.50,
        'Soccer': 0.50, 'Golf': 0.48, 'Esports': 0.52, 'CBB': 0.51,
        'NASCAR': 0.50, 'MMA': 0.49, 'Boxing': 0.49
    }
    base_rate = base_rates.get(sport, 0.51)
    
    # More randomness for variety
    random_factor = random.uniform(0.92, 1.08)
    
    if line > 30:
        factor = 0.96
    elif line > 20:
        factor = 0.98
    elif line > 10:
        factor = 1.0
    else:
        factor = 1.02
    
    hit_rate = base_rate * factor * random_factor
    return min(max(hit_rate, 0.35), 0.68)

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
    st.session_state.show_team_props = st.checkbox("Show Team Props", value=True)
    
    st.markdown("---")
    
    # Stats
    player_count = len(df[df['is_team'] == False])
    team_count = len(df[df['is_team'] == True])
    
    st.markdown(f"**Total Props:** {len(df):,}")
    st.markdown(f"**Player Props:** {player_count:,}")
    st.markdown(f"**Team Props:** {team_count:,}")
    st.markdown(f"**MORE:** {len(df[df['recommendation']=='MORE']):,}")
    st.markdown(f"**LESS:** {len(df[df['recommendation']=='LESS']):,}")
    
    # League distribution
    st.markdown("### 📊 League Distribution")
    if 'league_counts' in st.session_state:
        sorted_leagues = sorted(st.session_state.league_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        for league_id, count in sorted_leagues:
            sport = LEAGUE_MAPPING.get(league_id, f'League {league_id}')
            league_player_count = len(df[(df['league_id'] == league_id) & (df['is_team'] == False)])
            st.write(f"**{sport}** (ID: {league_id}): {count} total ({league_player_count} players)")

# Main content
col_left, col_right = st.columns([1.3, 0.7])

with col_left:
    st.markdown('<p class="section-header">📋 Available Props</p>', unsafe_allow_html=True)
    
    # Note about team props
    st.markdown('<div class="team-note">🏷️ Orange badges = Team Props | Blue badges = Player Props</div>', unsafe_allow_html=True)
    
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
    
    if not st.session_state.show_team_props:
        filtered_df = filtered_df[filtered_df['is_team'] == False]
    
    if st.session_state.show_recommended:
        filtered_df = filtered_df[filtered_df['hit_rate'] > 0.5415]
    
    st.caption(f"**Showing {len(filtered_df)} props ({len(filtered_df[filtered_df['is_team']==False])} players, {len(filtered_df[filtered_df['is_team']==True])} teams)**")
    
    # Auto-select
    if st.session_state.auto_select and len(st.session_state.picks) == 0 and len(filtered_df) >= num_legs:
        if st.button("🤖 Auto-select best picks"):
            for _, row in filtered_df.head(num_legs).iterrows():
                st.session_state.picks.append({
                    'emoji': row['emoji'],
                    'sport': row['sport'],
                    'player': row['player_name'],
                    'display_name': row['display_name'],
                    'is_team': row['is_team'],
                    'stat': row['stat_type'],
                    'line': row['line'],
                    'pick': row['recommendation'],
                    'hit_rate': row['hit_rate'],
                })
            st.rerun()
    
    # Display props
    for idx, row in filtered_df.head(30).iterrows():
        with st.container():
            badge_class = get_badge_class(row['sport'], row['is_team'])
            
            st.markdown(f"""
            <div class='prop-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span style='font-size:1.2rem;'>{row['emoji']}</span>
                        <span style='font-weight:bold; font-size:1.1rem;'>{row['display_name']}</span>
                        <span class='{badge_class}'>{row['sport']}{' TEAM' if row['is_team'] else ''}</span>
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
                        'display_name': row['display_name'],
                        'is_team': row['is_team'],
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
                badge_class = get_badge_class(pick['sport'], pick['is_team'])
                
                st.markdown(f"""
                <div class='prop-card'>
                    <div style='display:flex; justify-content:space-between;'>
                        <div>
                            <span>{pick['emoji']}</span>
                            <strong>{pick['display_name']}</strong>
                            <span class='{badge_class}' style='margin-left:5px;'>{pick['sport']}</span>
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
    <p style='font-size:0.8rem;'>🟠 Orange badges = Team props | 🔵 Colored badges = Player props</p>
</div>
""", unsafe_allow_html=True)