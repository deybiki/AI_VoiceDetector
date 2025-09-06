# # import os, json
# # import streamlit as st
# # import streamlit.components.v1 as components
# # from datetime import datetime

# # def _inject_js(save_dir: str):
# #     """
# #     Injects JavaScript for fullscreen + tab monitoring.
# #     Logs violations into Streamlit session_state + candidate_dir/violations.json.
# #     """
# #     if "violations" not in st.session_state:
# #         st.session_state.violations = []

# #     os.makedirs(save_dir, exist_ok=True)
# #     log_file = os.path.join(save_dir, "violations.json")

# #     if not os.path.exists(log_file):
# #         with open(log_file, "w") as f:
# #             json.dump([], f)

# #     # JavaScript to detect violations
# #     js_code = """
# #     <script>
# #     function logViolation(reason) {
# #         const payload = {
# #             reason: reason,
# #             ts: new Date().toISOString()
# #         };
# #         window.parent.postMessage(
# #             { type: "streamlit:setComponentValue", value: payload },
# #             "*"
# #         );
# #         alert("⚠️ " + reason + ". Please stay in fullscreen!");
# #         enableFullscreen();
# #     }

# #     function enableFullscreen() {
# #         let elem = document.documentElement;
# #         if (elem.requestFullscreen) {
# #             elem.requestFullscreen();
# #         } else if (elem.mozRequestFullScreen) {
# #             elem.mozRequestFullScreen();
# #         } else if (elem.webkitRequestFullscreen) {
# #             elem.webkitRequestFullscreen();
# #         } else if (elem.msRequestFullscreen) {
# #             elem.msRequestFullscreen();
# #         }
# #     }

# #     document.addEventListener("visibilitychange", () => {
# #         if (document.hidden) {
# #             logViolation("Tab switch / minimized detected");
# #         }
# #     });

# #     window.addEventListener("blur", () => {
# #         logViolation("Window lost focus");
# #     });

# #     document.addEventListener("fullscreenchange", () => {
# #         if (!document.fullscreenElement) {
# #             logViolation("Exited fullscreen");
# #         }
# #     });

# #     enableFullscreen();
# #     </script>
# #     """

# #     # Render hidden component that passes violations back
# #     payload = components.html(js_code, height=0, width=0)

# #     # If JS sent back a violation, save it
# #     if payload is not None:
# #         st.session_state.violations.append(payload)
# #         with open(log_file, "r") as f:
# #             logs = json.load(f)
# #         logs.append(payload)
# #         with open(log_file, "w") as f:
# #             json.dump(logs, f, indent=2)


# # def init_fullscreen_monitor(candidate_dir: str):
# #     """Start fullscreen + tab monitoring."""
# #     _inject_js(candidate_dir)


# # def stop_fullscreen_monitor():
# #     """Stop fullscreen monitor cleanly."""
# #     st.markdown(
# #         """
# #         <script>
# #         if (document.exitFullscreen) {
# #             document.exitFullscreen();
# #         }
# #         </script>
# #         """,
# #         unsafe_allow_html=True,
# #     )
# #     st.session_state.violations = []














import streamlit as st
import streamlit.components.v1 as components

def start_tab_monitor(test_id: str, student_id: str, backend_url: str):
    js_code = f"""
    <script>
    (function() {{
        if (window._tabMonitorInstalled) return;
        window._tabMonitorInstalled = true;

        const LOG_URL = "{backend_url}/log-violation";
        const meta = {{ testId: "{test_id}", studentId: "{student_id}" }};

        function logViolation(reason) {{
            const payload = {{ ...meta, reason, ts: new Date().toISOString() }};
            console.log("Sending violation:", payload);

            fetch(LOG_URL, {{
                method: "POST",
                headers: {{ "Content-Type": "application/json" }},
                body: JSON.stringify(payload)
            }}).then(r => console.log("Server response", r.status))
              .catch(err => console.error("Fetch error", err));

            let bar = document.getElementById("violation-banner");
            if (!bar) {{
                bar = document.createElement("div");
                bar.id = "violation-banner";
                bar.style.position = "fixed";
                bar.style.top = "0";
                bar.style.left = "0";
                bar.style.width = "100%";
                bar.style.padding = "12px";
                bar.style.background = "red";
                bar.style.color = "white";
                bar.style.fontWeight = "bold";
                bar.style.textAlign = "center";
                bar.style.zIndex = "999999";
                document.body.appendChild(bar);
            }}
            bar.innerText = "⚠️ " + reason + " — logged!";
            setTimeout(() => {{ if (bar) bar.remove(); }}, 4000);
        }}

        // Save refs so we can remove them later
        window._tabVisibilityHandler = () => {{
            if (document.hidden) logViolation("Tab switch / minimized");
        }};
        window._tabBlurHandler = () => logViolation("Window lost focus");

        document.addEventListener("visibilitychange", window._tabVisibilityHandler);
        window.addEventListener("blur", window._tabBlurHandler);

        console.log("✅ Tab monitor active");
    }})();
    </script>
    """
    components.html(js_code, height=0, width=0)

def stop_tab_monitor():
    components.html(
        """
        <script>
        try {
            if (window._tabMonitorInstalled) {
                document.removeEventListener("visibilitychange", window._tabVisibilityHandler);
                window.removeEventListener("blur", window._tabBlurHandler);
                window._tabMonitorInstalled = false;
                console.log("🛑 Tab monitor stopped");
            }
        } catch(e) { console.error("Stop error", e); }
        </script>
        """,
        height=0,
        width=0,
    )




