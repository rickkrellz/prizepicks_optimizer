import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time
import pytz

# Page config
st.set_page_config(
    page_title="PrizePicks Data Viewer",
    page_icon="🔍",
    layout="wide"
)

# Set timezone
central_tz = pytz.timezone('US/Central')
utc_tz = pytz.UTC

def get_central_time():
    utc_now = datetime.now(utc_tz)
    central_now = utc_now.astimezone(central_tz)
    return central_now

st.title("🔍 PrizePicks Raw Data Viewer")
st.markdown(f"**Last Updated:** {get_central_time().strftime('%I:%M:%S %p CT')}")

# API call
@st.cache_data(ttl=60)
def fetch_data():
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
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

data = fetch_data()

if data:
    st.success(f"✅ Connected! Got {len(data.get('data', []))} items")
    
    # Extract data
    rows = []
    for item in data.get('data', [])[:500]:  # First 500 items
        try:
            attrs = item.get('attributes', {})
            league_rel = item.get('relationships', {}).get('league', {}).get('data', {})
            league_id = league_rel.get('id') if league_rel else 'unknown'
            
            rows.append({
                'league_id': league_id,
                'name': attrs.get('name') or attrs.get('description', 'Unknown'),
                'stat': attrs.get('stat_type', 'Unknown'),
                'line': attrs.get('line_score', 0),
                'game': attrs.get('game_id', 'Unknown'),
            })
        except:
            continue
    
    df = pd.DataFrame(rows)
    
    if not df.empty:
        # Show league ID distribution
        st.subheader("📊 League ID Distribution")
        league_counts = df['league_id'].value_counts().reset_index()
        league_counts.columns = ['League ID', 'Count']
        st.dataframe(league_counts, use_container_width=True)
        
        # Let user select a league to explore
        st.subheader("🔍 Explore League")
        selected_league = st.selectbox("Select League ID", sorted(df['league_id'].unique()))
        
        if selected_league:
            league_data = df[df['league_id'] == selected_league]
            st.write(f"**{len(league_data)} items in League {selected_league}**")
            
            # Show sample
            st.dataframe(league_data.head(20), use_container_width=True)
            
            # Let user search within this league
            search = st.text_input(f"Search in League {selected_league}")
            if search:
                results = league_data[league_data['name'].str.contains(search, case=False, na=False)]
                st.write(f"Found {len(results)} results")
                st.dataframe(results, use_container_width=True)
        
        # Overall search
        st.subheader("🔍 Search All")
        search_all = st.text_input("Search all (e.g., 'James', 'McDavid', '400', 'CLE')")
        if search_all:
            results = df[df['name'].str.contains(search_all, case=False, na=False)]
            st.write(f"Found {len(results)} results")
            
            # Show league breakdown for search results
            if len(results) > 0:
                st.write("League breakdown:")
                st.write(results['league_id'].value_counts())
            
            st.dataframe(results, use_container_width=True)
    else:
        st.warning("No data extracted")
else:
    st.warning("No data loaded")