# Add this to a separate page or at the end of your main app for testing

import streamlit as st
from full_screen import start_tab_monitor, stop_tab_monitor, test_tab_monitor

st.title("🔍 Tab Monitor Debug Page")

st.markdown("""
## Quick Test Instructions:
1. Click "Start Monitor" 
2. Look for the green indicator
3. Open browser console (F12) to see debug logs
4. Try switching to another tab
5. You should see warning popup + console logs
""")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🟢 Start Monitor", key="start_debug"):
        start_tab_monitor()

with col2:
    if st.button("🧪 Test Warning", key="test_debug"):
        test_tab_monitor()

with col3:
    if st.button("🔴 Stop Monitor", key="stop_debug"):
        stop_tab_monitor()

st.markdown("""
---
## Debug Checklist:

### ✅ Things to Check:
1. **Browser Console** - Press F12, look for messages starting with 🔍, ✅, or ❌
2. **Green Indicator** - Should appear when monitor starts
3. **Test Button** - Should show red warning popup
4. **Tab Switch** - Try switching tabs after starting monitor

### 🐛 If Still Not Working:
1. **Try different browser** (Chrome works best)
2. **Check browser permissions** - Allow popups/sound
3. **Refresh the page** completely
4. **Look for JavaScript errors** in browser console

### 📊 Console Logs You Should See:
- `🔍 DEBUG: Script is loading...`
- `✅ Starting fresh monitor`  
- `🔗 Adding visibility change listener`
- `⏰ Test 1: Document hidden=false, hasFocus=true`
- When you switch tabs: `👁️ Visibility changed. Hidden: true`
- `🚨 SHOWING WARNING: You switched tabs...`
""")

# Add some debugging info
if st.checkbox("Show Session State Debug"):
    st.json(dict(st.session_state))