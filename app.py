import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time
import pytz

# Page config
st.set_page_config(
    page_title="PrizePicks Viewer",
    page_icon="📊",
    layout="wide"
)

# Set timezone
central_tz = pytz.timezone('US/Central')
utc_tz = pytz.UTC

def get_central_time():
    utc_now = datetime.now(utc_tz)
    central_now = utc_now.astimezone(central_tz)
    return central_now

# Ultra simple CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .prop-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #1E88E5;
    }
    .badge {
        background-color: #0D47A1;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        display: inline-block;
    }
    .stat-line {
        font-weight: bold;
        color: #0D47A1;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">📊 PrizePicks Raw Data Viewer</p>', unsafe_allow_html=True)
st.markdown(f"**Last Updated:** {get_central_time().strftime('%I:%M:%S %p CT')}")

# Simple API call
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
        return None
    except:
        return None

if st.button("🔄 Refresh"):
    st.cache_data.clear()

data = fetch_data()

if data:
    items = data.get('data', [])
    st.success(f"✅ Got {len(items)} items")
    
    # Show league ID distribution
    league_counts = {}
    for item in items:
        league_rel = item.get('relationships', {}).get('league', {}).get('data', {})
        league_id = league_rel.get('id', 'unknown')
        league_counts[league_id] = league_counts.get(league_id, 0) + 1
    
    st.subheader("📊 League IDs in Data")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**League ID**")
    with col2:
        st.write("**Count**")
    
    for lid, count in sorted(league_counts.items(), key=lambda x: x[1], reverse=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write(lid)
        with col2:
            st.write(count)
    
    # Show sample data
    st.subheader("🔍 Sample Items")
    for item in items[:20]:
        attrs = item.get('attributes', {})
        name = attrs.get('name') or attrs.get('description', 'Unknown')
        stat = attrs.get('stat_type', 'Unknown')
        line = attrs.get('line_score', 0)
        league_rel = item.get('relationships', {}).get('league', {}).get('data', {})
        league_id = league_rel.get('id', 'unknown')
        
        st.markdown(f"""
        <div class='prop-card'>
            <div><strong>{name}</strong> <span class='badge'>League {league_id}</span></div>
            <div class='stat-line'>{stat}: {line}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("No data loaded")