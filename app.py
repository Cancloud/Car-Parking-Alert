import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import datetime
import pandas as pd

# --- Configuration ---
admin_list = ['ADMIN-1', 'ADMIN-2', 'ADMIN-3', 'ADMIN-4', 'ADMIN-5']
DEFAULT_ADMIN_PASS = 'admin888'

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            plate TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Insert test user if not exists
    c.execute("SELECT * FROM users WHERE plate='TEST-123'")
    if not c.fetchone():
        c.execute("INSERT INTO users (plate, password) VALUES ('TEST-123', 'admin888')")
        
    # Insert predefined admins if they do not exist
    for admin_plate in admin_list:
        c.execute("SELECT * FROM users WHERE plate=?", (admin_plate,))
        if not c.fetchone():
            c.execute("INSERT INTO users (plate, password) VALUES (?, ?)", (admin_plate, DEFAULT_ADMIN_PASS))
        
    conn.commit()
    conn.close()

# --- DB Helper Functions ---
def check_login(plate, password):
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE plate=? AND password=?", (plate, password))
    user = c.fetchone()
    conn.close()
    return user is not None

def register_user(plate, password):
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (plate, password) VALUES (?, ?)", (plate, password))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False # Plate already exists
    conn.close()
    return success

def add_report(plate):
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO reports (plate, timestamp) VALUES (?, ?)", (plate, timestamp))
    conn.commit()
    conn.close()

def get_reports():
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()
    c.execute("SELECT * FROM reports ORDER BY timestamp DESC")
    reports = c.fetchall()
    conn.close()
    return reports

def get_users():
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()
    c.execute("SELECT plate FROM users")
    users = c.fetchall()
    conn.close()
    return users

def delete_user(plate):
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE plate=?", (plate,))
    conn.commit()
    conn.close()

def delete_all_reports():
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()
    c.execute("DELETE FROM reports")
    conn.commit()
    conn.close()

# --- Main App ---
def main():
    # Page config for better mobile display
    st.set_page_config(page_title="Car Parking Notification", page_icon="🚗", layout="centered")
    
    init_db()
    
    # --- Auto-Refresh Logic (30 seconds) & Cache Bypassing ---
    components.html(
        """
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <script>
        setTimeout(function() {
            window.parent.location.reload(true);
        }, 30000);
        </script>
        """,
        height=0
    )
    
    # --- Public Alert Banner (No Login Required) ---
    recent_reports = get_reports()
    if recent_reports:
        # Check if the latest report is within 60 minutes
        latest_report = recent_reports[0]
        latest_time = datetime.datetime.strptime(latest_report[2], "%Y-%m-%d %H:%M:%S")
        if (datetime.datetime.now() - latest_time).total_seconds() <= 3600:
            st.markdown(f"""
                <div style="background-color: #ff1a1a; color: white; padding: 25px 15px; border-radius: 12px; text-align: center; border: 4px solid darkred; animation: blinker 1.5s linear infinite; margin-bottom: 25px; box-shadow: 0px 6px 15px rgba(255,0,0,0.6); width: 100%; box-sizing: border-box;">
                    <h2 style="margin:0; color:white; font-weight:900; font-size: 1.8rem; line-height: 1.3;">🚨 ALERT:<br>PARKING WARDEN SPOTTED AT<br>{latest_report[2]}!</h2>
                </div>
                <style>
                @keyframes blinker {{
                    50% {{ opacity: 0.6; }}
                }}
                </style>
            """, unsafe_allow_html=True)
    
    # Initialize session state for login
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'plate' not in st.session_state:
        st.session_state.plate = ""
        
    # --- Login / Sign Up Screen ---
    if not st.session_state.logged_in:
        st.title("🚗 Parking Alert")
        st.write("Please log in or sign up to report or view notifications.")
        
        # Style the tabs to be more mobile-friendly
        st.markdown("""
            <style>
            button[data-baseweb="tab"] {
                font-size: 1.2rem;
                padding-top: 15px;
                padding-bottom: 15px;
            }
            </style>
        """, unsafe_allow_html=True)
        
        auth_tab1, auth_tab2 = st.tabs(["Login", "Sign Up"])
        
        with auth_tab1:
            with st.form("login_form"):
                plate_input = st.text_input("License Plate", placeholder="e.g. TEST-123", key="login_plate")
                password_input = st.text_input("Password", type="password", key="login_pass")
                submit_button = st.form_submit_button("Login")
                
                if submit_button:
                    if check_login(plate_input, password_input):
                        st.session_state.logged_in = True
                        st.session_state.plate = plate_input
                        st.rerun()
                    else:
                        st.error("Invalid License Plate or Password")
                        
        with auth_tab2:
            with st.form("signup_form"):
                new_plate = st.text_input("License Plate", placeholder="e.g. ABC-9999", key="signup_plate")
                new_password = st.text_input("Password", type="password", key="signup_pass")
                signup_button = st.form_submit_button("Sign Up")
                
                if signup_button:
                    if not new_plate or not new_password:
                        st.error("Please fill in both fields.")
                    else:
                        if register_user(new_plate.upper(), new_password):
                            st.success("Successfully registered! You can now log in.")
                        else:
                            st.error("User with this License Plate already exists.")
    
    # --- Main App Screen ---
    else:
        st.title("🚗 Parking Alert")
        st.write(f"Logged in as: **{st.session_state.plate}**")
        
        # --- Admin Sidebar ---
        if st.session_state.plate in admin_list:
            with st.sidebar:
                st.header("🛠️ Admin Tools")
                
                st.subheader("User Management (Admins Only)")
                users = get_users()
                if users:
                    # Creating a custom layout for each user
                    st.markdown("---")
                    for user_tuple in users:
                        u_plate = user_tuple[0]
                        col1, col2 = st.columns([3, 1])
                        
                        # Display the plate name
                        col1.markdown(f"**🚗 {u_plate}**")
                        
                        # Add a delete button for non-admins
                        if u_plate not in admin_list:
                            if col2.button("❌ 刪除", key=f"del_user_{u_plate}"):
                                delete_user(u_plate)
                                st.rerun()
                        else:
                            col2.markdown("*Admin*")
                        st.markdown("---")
                else:
                    st.info("No users found.")
                
                st.markdown("---")
                st.subheader("Full History")
                reports = get_reports()
                if reports:
                    df_reports = pd.DataFrame(reports, columns=["ID", "Plate", "Timestamp"])
                    st.dataframe(df_reports, hide_index=True, use_container_width=True)
                    
                    csv = df_reports.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name='alerts_history.csv',
                        mime='text/csv',
                        use_container_width=True
                    )
                    
                    if st.button("🗑️ Clear All Logs", use_container_width=True):
                        delete_all_reports()
                        st.success("Logs cleared!")
                        st.rerun()
                else:
                    st.info("No reports.")

        # --- Regular User View ---
        st.markdown("### See a parking warden?")
        st.write("Quickly tap the button below to alert others!")
        
        # Custom CSS to make the main report button large and touch-friendly for mobile
        # Tagged under main section to prevent styling bleed to sidebar buttons
        st.markdown("""
            <style>
            section[data-testid="stMain"] div.stButton > button:first-child {
                background-color: #ff4b4b;
                color: white;
                height: 120px;
                width: 100%;
                font-size: 24px;
                font-weight: bold;
                border-radius: 12px;
                border: none;
                box-shadow: 0 4px 6px rgba(0,0,0,0.2);
                transition: all 0.2s ease-in-out;
            }
            section[data-testid="stMain"] div.stButton > button:first-child:hover {
                background-color: #ff3333;
                box-shadow: 0 6px 8px rgba(0,0,0,0.3);
                transform: translateY(-2px);
            }
            section[data-testid="stMain"] div.stButton > button:first-child:active {
                transform: translateY(2px);
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            </style>
        """, unsafe_allow_html=True)
        
        if st.button("🚨 REPORT WARDEN (通報開單)"):
            add_report(st.session_state.plate)
            st.success("Report submitted successfully!")
            
        st.markdown("---")
        st.subheader("Recent Alerts (Last 10)")
        reports = get_reports()
        if reports:
            # Limit to latest 10
            recent_10 = reports[:10]
            df_recent = pd.DataFrame(recent_10, columns=["ID", "Plate", "Timestamp"])
            st.dataframe(df_recent[["Plate", "Timestamp"]], hide_index=True, use_container_width=True)
        else:
            st.info("No reports yet.")
                
        # Logout
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.plate = ""
            st.rerun()

if __name__ == "__main__":
    main()
