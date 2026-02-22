import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time
import pytz
import json

# Page config
st.set_page_config(
    page_title="PrizePicks API Debug",
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
        margin-bottom: 2rem;
    }
    .debug-box {
        background-color: #1E1E1E;
        color: #00FF00;
        padding: 1rem;
        border-radius: 5px;
        font-family: monospace;
        white-space: pre-wrap;
        max-height: 400px;
        overflow: auto;
    }
    .success { color: #00FF00; font-weight: bold; }
    .error { color: #FF0000; font-weight: bold; }
    .warning { color: #FFA500; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🔍 PrizePicks API Debug Tool - Advanced</p>', unsafe_allow_html=True)
st.markdown(f"**Current Time:** {get_central_time().strftime('%I:%M:%S %p CT')}")

# Instructions
st.info("""
📱 **On your iPad:**
1. Open Safari and go to: https://api.prizepicks.com/projections
2. When the page loads, tap the 'Share' button (box with arrow)
3. Scroll down and tap 'Copy'
4. Come back here and paste below
""")

# Text area for pasting headers
pasted_content = st.text_area("Paste copied content here:", height=200)

if pasted_content:
    st.markdown("### 📋 Pasted Content Preview:")
    st.markdown(f'<div class="debug-box">{pasted_content[:500]}</div>', unsafe_allow_html=True)
    
    # Try to extract any useful information
    st.markdown("### 🔍 Analysis:")
    
    # Check if it looks like JSON
    try:
        json_data = json.loads(pasted_content)
        st.success("✅ This appears to be JSON data!")
        st.json(json_data)
    except:
        st.warning("⚠️ This doesn't appear to be JSON data")
        
        # Look for potential headers
        lines = pasted_content.split('\n')
        for line in lines[:20]:
            if ':' in line and any(key in line.lower() for key in ['user-agent', 'accept', 'cookie', 'referer']):
                st.write(f"Found header-like line: {line}")

# Manual header tester
st.markdown("---")
st.markdown("### 🧪 Manual Header Tester")

col1, col2 = st.columns(2)

with col1:
    custom_ua = st.text_input("User-Agent", value="Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1")
    custom_accept = st.text_input("Accept", value="application/json")
    custom_referer = st.text_input("Referer", value="https://app.prizepicks.com/")

with col2:
    custom_origin = st.text_input("Origin", value="https://app.prizepicks.com")
    custom_accept_lang = st.text_input("Accept-Language", value="en-US,en;q=0.9")
    custom_connection = st.text_input("Connection", value="keep-alive")

# Additional headers as checkboxes
st.markdown("#### Additional Headers:")
col3, col4, col5 = st.columns(3)
with col3:
    add_sec_fetch = st.checkbox("Add Sec-Fetch headers", value=True)
with col4:
    add_cache = st.checkbox("Add Cache-Control", value=False)
with col5:
    add_cookie = st.checkbox("Add Cookie (if you have one)", value=False)

if add_cookie and add_cookie:
    cookie_value = st.text_input("Cookie value:", type="password")

# Build headers
headers = {
    'User-Agent': custom_ua,
    'Accept': custom_accept,
}

if custom_referer:
    headers['Referer'] = custom_referer
if custom_origin:
    headers['Origin'] = custom_origin
if custom_accept_lang:
    headers['Accept-Language'] = custom_accept_lang
if custom_connection:
    headers['Connection'] = custom_connection
if add_sec_fetch:
    headers['Sec-Fetch-Dest'] = 'empty'
    headers['Sec-Fetch-Mode'] = 'cors'
    headers['Sec-Fetch-Site'] = 'same-site'
if add_cache:
    headers['Cache-Control'] = 'no-cache'
if add_cookie and add_cookie and 'cookie_value' in locals():
    headers['Cookie'] = cookie_value

# Show headers being used
with st.expander("📤 Headers being sent:", expanded=True):
    st.json(headers)

# Test button
if st.button("🚀 Test with these headers", type="primary"):
    with st.spinner("Testing API connection..."):
        try:
            # Add small delay
            time.sleep(1)
            
            # Make request
            response = requests.get(
                "https://api.prizepicks.com/projections", 
                headers=headers, 
                timeout=15
            )
            
            # Show results
            st.markdown("---")
            st.markdown("### 📊 Test Results")
            
            col_status, col_size = st.columns(2)
            with col_status:
                if response.status_code == 200:
                    st.markdown(f"<p class='success'>✅ Status: {response.status_code}</p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p class='error'>❌ Status: {response.status_code}</p>", unsafe_allow_html=True)
            
            with col_size:
                st.markdown(f"**Response Size:** {len(response.content):,} bytes")
            
            # Show response headers
            with st.expander("📥 Response Headers"):
                st.json(dict(response.headers))
            
            # Try to parse response
            if response.status_code == 200:
                try:
                    data = response.json()
                    st.success(f"✅ Successfully parsed JSON! Found {len(data.get('data', []))} items")
                    
                    # Show sample
                    if data.get('data'):
                        st.markdown("#### First Item Sample:")
                        st.json(data['data'][0])
                        
                        # Extract league IDs
                        league_ids = set()
                        for item in data['data'][:50]:
                            try:
                                league_rel = item.get('relationships', {}).get('league', {}).get('data', {})
                                if league_rel:
                                    league_ids.add(league_rel.get('id'))
                            except:
                                pass
                        
                        if league_ids:
                            st.markdown("#### League IDs Found:")
                            st.write(sorted(league_ids))
                            
                except Exception as e:
                    st.error(f"Error parsing JSON: {e}")
                    st.text(response.text[:500])
            else:
                st.error(f"Response content: {response.text[:500]}")
                
        except Exception as e:
            st.error(f"Request failed: {e}")

# Save working configuration
if 'working_headers' in st.session_state:
    st.markdown("---")
    st.markdown("### ✅ Working Configuration Found!")
    st.markdown("Copy these headers into your main app:")
    st.code(f"""
headers = {{
    'User-Agent': '{st.session_state.working_headers.get("User-Agent", "")}',
    'Accept': '{st.session_state.working_headers.get("Accept", "")}',
    'Referer': '{st.session_state.working_headers.get("Referer", "")}',
    'Origin': '{st.session_state.working_headers.get("Origin", "")}',
    'Accept-Language': '{st.session_state.working_headers.get("Accept-Language", "")}',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
}}
    """)

# Instructions
st.markdown("---")
st.markdown("""
### 📝 How to use this tool:

1. **Open Safari on your iPad** and go to: `https://api.prizepicks.com/projections`
2. **When the JSON loads**, tap the share button and select "Copy"
3. **Paste the content** in the text area above - this will show us what the API returns when accessed directly
4. **Use the manual tester** to try different header combinations
5. **When you find headers that work** (status 200), the configuration will be saved

If you get a 403 error, try:
- Adding/removing different headers
- Matching exactly what your iPad sends
- Adding cookies if you're logged into PrizePicks on your iPad
""")