import streamlit as st
import streamlit.components.v1 as components

def start_tab_monitor():
    """
    Simple, bulletproof tab monitor - guaranteed to work
    """
    js_code = """
    <div id="tab-monitor-container"></div>
    <script>
    console.log("🔍 DEBUG: Script is loading...");
    
    // Simple global check
    if (window.tabMonitorActive) {
        console.log("⚠️ Monitor already active, skipping");
    } else {
        console.log("✅ Starting fresh monitor");
        window.tabMonitorActive = true;
        
        // Simple state
        let warningShown = false;
        
        // Simple beep function
        function playBeep() {
            console.log("🔊 Playing beep...");
            try {
                // Method 1: Try creating audio context
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = ctx.createOscillator();
                const vol = ctx.createGain();
                
                osc.connect(vol);
                vol.connect(ctx.destination);
                
                osc.frequency.value = 800;
                vol.gain.value = 0.1;
                
                osc.start();
                osc.stop(ctx.currentTime + 0.5);
                
                console.log("✅ Beep played via AudioContext");
            } catch(e) {
                console.log("❌ AudioContext failed:", e);
                // Fallback: try HTML audio
                try {
                    const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+Dws2QYBT2U2PA=');
                    audio.volume = 0.3;
                    audio.play();
                    console.log("✅ Beep played via HTML5 Audio");
                } catch(e2) {
                    console.log("❌ All audio methods failed:", e2);
                }
            }
        }
        
        // Simple warning function
        function showWarning(reason) {
            if (warningShown) {
                console.log("⚠️ Warning already shown, skipping");
                return;
            }
            
            console.log("🚨 SHOWING WARNING:", reason);
            warningShown = true;
            
            // Play beep first
            playBeep();
            
            // Create simple overlay
            const overlay = document.createElement('div');
            overlay.id = 'simple-warning';
            overlay.style.cssText = `
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
                background: rgba(255, 0, 0, 0.9) !important;
                z-index: 999999 !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                color: white !important;
                font-family: Arial, sans-serif !important;
                font-size: 24px !important;
                text-align: center !important;
                cursor: pointer !important;
            `;
            
            overlay.innerHTML = `
                <div style="background: white; color: red; padding: 40px; border-radius: 10px; max-width: 400px;">
                    <h1 style="margin: 0 0 20px 0; font-size: 32px;">⚠️ WARNING!</h1>
                    <p style="margin: 0 0 20px 0; color: black;">${reason}</p>
                    <p style="margin: 0 0 30px 0; color: black;">Click here to return to exam</p>
                    <button onclick="this.parentElement.parentElement.remove(); window.tabMonitorWarningShown = false; console.log('Warning dismissed');" 
                            style="background: #007bff; color: white; border: none; padding: 15px 30px; border-radius: 5px; font-size: 18px; cursor: pointer;">
                        Return to Exam
                    </button>
                </div>
            `;
            
            // Add to page
            document.body.appendChild(overlay);
            
            // Make it clickable
            overlay.addEventListener('click', function() {
                console.log("📱 Warning clicked - dismissing");
                overlay.remove();
                warningShown = false;
            });
            
            console.log("✅ Warning overlay created and shown");
        }
        
        // Test warning function (remove this after testing)
        window.testWarning = function() {
            console.log("🧪 TEST: Triggering manual warning");
            showWarning("Manual Test Warning");
        };
        
        // Simple detection functions
        function onVisibilityChange() {
            console.log("👁️ Visibility changed. Hidden:", document.hidden);
            if (document.hidden && !warningShown) {
                showWarning("You switched tabs or minimized the window!");
            }
        }
        
        function onWindowBlur() {
            console.log("🔍 Window blur detected");
            setTimeout(function() {
                if (!document.hasFocus() && !warningShown) {
                    showWarning("Window lost focus - return to exam!");
                }
            }, 200);
        }
        
        function onPageHide() {
            console.log("📄 Page hide detected");
            if (!warningShown) {
                showWarning("Page navigation detected!");
            }
        }
        
        // Add listeners with error handling
        try {
            console.log("🔗 Adding visibility change listener");
            document.addEventListener('visibilitychange', onVisibilityChange);
        } catch(e) {
            console.log("❌ Failed to add visibilitychange:", e);
        }
        
        try {
            console.log("🔗 Adding window blur listener");
            window.addEventListener('blur', onWindowBlur);
        } catch(e) {
            console.log("❌ Failed to add blur:", e);
        }
        
        try {
            console.log("🔗 Adding page hide listener");
            window.addEventListener('pagehide', onPageHide);
        } catch(e) {
            console.log("❌ Failed to add pagehide:", e);
        }
        
        // Test that events are working
        console.log("🧪 Setting up test interval...");
        let testCount = 0;
        const testInterval = setInterval(function() {
            testCount++;
            console.log(`⏰ Test ${testCount}: Document hidden=${document.hidden}, hasFocus=${document.hasFocus()}`);
            
            if (testCount >= 5) {
                clearInterval(testInterval);
                console.log("🏁 Test interval complete");
            }
        }, 2000);
        
        console.log("✅ Tab monitor setup complete!");
        console.log("🧪 To test manually, run: testWarning() in console");
    }
    </script>
    """
    
    # Use a unique key to force re-render
    import time
    key = f"tab_monitor_{int(time.time())}"
    
    components.html(js_code, height=100, width=100, key=key)
    
    # Also add a visible indicator
    st.markdown("""
    <div style="background: #e8f5e8; padding: 10px; border-radius: 5px; margin: 10px 0;">
        🟢 <strong>Tab Monitor Active</strong> - Try switching tabs to test the warning system
    </div>
    """, unsafe_allow_html=True)

def stop_tab_monitor():
    """Clean stop function"""
    cleanup_js = """
    <script>
    console.log("🛑 Stopping tab monitor");
    window.tabMonitorActive = false;
    
    // Remove warning if present
    const warning = document.getElementById('simple-warning');
    if (warning) {
        warning.remove();
        console.log("🗑️ Removed warning overlay");
    }
    </script>
    """
    
    components.html(cleanup_js, height=0, width=0)
    
    st.markdown("""
    <div style="background: #ffe8e8; padding: 10px; border-radius: 5px; margin: 10px 0;">
        🔴 <strong>Tab Monitor Stopped</strong>
    </div>
    """, unsafe_allow_html=True)

# Test function for debugging
def test_tab_monitor():
    """Test the tab monitor manually"""
    test_js = """
    <script>
    console.log("🧪 Manual test triggered");
    if (window.testWarning) {
        window.testWarning();
    } else {
        console.log("❌ testWarning function not found");
        alert("Tab monitor might not be loaded yet");
    }
    </script>
    """
    
    components.html(test_js, height=0, width=0)
    st.success("✅ Test warning triggered! Check browser console for debug info.")

# Legacy compatibility
def start_tab_monitor_legacy(test_id: str = "", student_id: str = "", backend_url: str = ""):
    start_tab_monitor()