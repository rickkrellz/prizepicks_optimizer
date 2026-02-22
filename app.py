import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time
import pytz

# Page config
st.set_page_config(
    page_title="PrizePicks Debug",
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

# Simple CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        color: #1E88E5;
        text-align: center;
    }
    .debug-box {
        background-color: #1E1E1E;
        color: #00FF00;
        padding: 1rem;
        border-radius: 5px;
        font-family: monospace;
        white-space: pre-wrap;
    }
    .success { color: #00FF00; }
    .error { color: #FF0000; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🔍 PrizePicks API Debug Tool</p>', unsafe_allow_html=True)
st.markdown(f"**Current Time:** {get_central_time().strftime('%I:%M:%S %p CT')}")

# Function to test API with different headers
def test_api(headers_version=1):
    url = "https://api.prizepicks.com/projections"
    
    headers_options = {
        1: {
            'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Accept': 'application/json',
        },
        2: {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        3: {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://app.prizepicks.com/',
        },
        4: {
            'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://app.prizepicks.com/',
            'Origin': 'https://app.prizepicks.com',
            'Connection': 'keep-alive',
        }
    }
    
    headers = headers_options.get(headers_version, headers_options[1])
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'content_length': len(response.content) if response.content else 0,
            'success': response.status_code == 200
        }
    except Exception as e:
        return {
            'error': str(e),
            'success': False
        }

# Test buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Test Headers v1"):
        result = test_api(1)
        st.session_state.last_test = result
        st.session_state.headers_used = 1

with col2:
    if st.button("Test Headers v2"):
        result = test_api(2)
        st.session_state.last_test = result
        st.session_state.headers_used = 2

with col3:
    if st.button("Test Headers v3"):
        result = test_api(3)
        st.session_state.last_test = result
        st.session_state.headers_used = 3

with col4:
    if st.button("Test Headers v4"):
        result = test_api(4)
        st.session_state.last_test = result
        st.session_state.headers_used = 4

# Display results
if 'last_test' in st.session_state:
    st.markdown("---")
    st.subheader(f"Test Results (Headers v{st.session_state.headers_used})")
    
    result = st.session_state.last_test
    
    if result.get('success'):
        st.markdown(f"<p class='success'>✅ SUCCESS! Status Code: {result['status_code']}</p>", unsafe_allow_html=True)
        st.markdown(f"Content Length: {result['content_length']} bytes")
    else:
        st.markdown(f"<p class='error'>❌ FAILED</p>", unsafe_allow_html=True)
        if 'status_code' in result:
            st.markdown(f"Status Code: {result['status_code']}")
        if 'error' in result:
            st.markdown(f"Error: {result['error']}")
    
    with st.expander("View Response Headers"):
        st.json(result.get('headers', {}))

# Try to fetch and display sample data if successful
if 'last_test' in st.session_state and st.session_state.last_test.get('success'):
    st.markdown("---")
    st.subheader("Attempting to fetch data...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://app.prizepicks.com/',
        'Origin': 'https://app.prizepicks.com',
    }
    
    try:
        response = requests.get("https://api.prizepicks.com/projections", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            st.success(f"✅ Successfully fetched data! Found {len(data.get('data', []))} items")
            
            # Show sample
            if data.get('data'):
                st.markdown("### First Item Sample:")
                st.json(data['data'][0])
                
                # Extract unique league IDs
                league_ids = set()
                for item in data['data'][:100]:  # Check first 100
                    try:
                        league_rel = item.get('relationships', {}).get('league', {}).get('data', {})
                        if league_rel:
                            league_ids.add(league_rel.get('id'))
                    except:
                        pass
                
                if league_ids:
                    st.markdown("### League IDs Found:")
                    st.write(sorted(league_ids))
        else:
            st.error(f"Failed to fetch data: {response.status_code}")
    except Exception as e:
        st.error(f"Error: {e}")

# Instructions
st.markdown("---")
st.markdown("""
### 📝 Instructions:
1. Click each header version button to test different combinations
2. Look for a **200 status code** (success)
3. Once successful, the app will show sample data and league IDs
4. Note which header version works - we'll use that in the main app
""")