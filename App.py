# ============================================================
# 🧬 NanoBio Studio — Connecting Nanotechnology & Biotechnology
# Developed by Experts Group FZE
# ============================================================

import streamlit as st
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
from pathlib import Path
from datetime import datetime
import json
import random
import base64

from auth import (
    authenticate, get_all_users, update_user_role, get_user_role as auth_get_user_role,
    register_user, validate_username, validate_password, validate_email,
    change_password, reset_password, get_user_info, count_admin_users,
    setup_admin_account, deactivate_user, activate_user, list_users_detailed,
    log_activity, update_last_activity, is_session_expired, get_activity_log, 
    SESSION_TIMEOUT_MINUTES
)
from rbac import (
    get_user_role, has_permission, can_access_tab, 
    get_available_tabs, show_role_badge, show_role_info,
    Permission, Role, ROLE_TAB_ACCESS, require_permission
)
from ui.styling import apply_css_profile

# ============================================================
# ⚠️ IMPORTANT DISCLAIMER
# ============================================================

# ============================================================
# ⚠️ IMPORTANT DISCLAIMER (Expandable)
# ============================================================
with st.expander("⚠️ IMPORTANT DISCLAIMER - Click to expand", expanded=False):
    st.markdown("""
    <div style='background-color:#fff3cd; border-left:5px solid #ffc107; padding:15px; margin-bottom:10px; border-radius:5px;'>
    <h4 style='color:#856404; margin-top:0;'>⚠️ IMPORTANT NOTICE</h4>
    <p style='color:#856404; margin-bottom:5px;'>
    <strong>This application is for EDUCATIONAL AND RESEARCH PURPOSES ONLY.</strong>
    </p>
    <ul style='color:#856404; margin-top:5px;'>
    <li>This tool is NOT intended for medical diagnosis, treatment, or clinical decision-making</li>
    <li>Results and recommendations are based on computational models and may not reflect real-world outcomes</li>
    <li>All nanoparticle designs should be validated through proper experimental procedures</li>
    <li>Users assume full responsibility for any decisions made based on information from this tool</li>
    <li>Consult with qualified professionals for medical or therapeutic applications</li>
    </ul>
    </div>
    
    <div style='background-color:#f8f9fa; border:1px solid #dee2e6; padding:12px; margin-top:10px; border-radius:4px;'>
    <p style='color:#333; margin:0; font-weight:bold;'>
    📋 <strong>INTELLECTUAL PROPERTY NOTICE</strong>
    </p>
    <p style='color:#333; margin:5px 0 0 0;'>
    This application is the intellectual property of <strong>Experts Group FZE</strong>
    </p>
    <p style='color:#333; margin:2px 0;'>
    📞 <strong>Mobile:</strong> 00 971 50 6690381
    </p>
    <p style='color:#333; margin:2px 0 0 0;'>
    📧 <strong>Email:</strong> info@expertsgroup.me
    </p>
    </div>
    
    <p style='color:#856404; margin-top:10px; font-size:0.9em; text-align:center;'>
    <strong>By using this application, you acknowledge and accept these limitations.</strong>
    </p>
    """, unsafe_allow_html=True)

# Check for optional dependencies
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import mean_absolute_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    st.warning("⚠️ scikit-learn not available. AI optimization will be disabled. Install with: `pip install scikit-learn`")

# Display README content dynamically (expandable)
readme_path = Path(__file__).parent / "README.md"

if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()

    with st.expander("📘 About NanoBio Studio — Click to expand"):
        st.markdown(readme_content, unsafe_allow_html=True)
else:
    st.info("ℹ️ README.md not found. Please check your repository.")

# ============================================================
# 1️⃣ PAGE CONFIG
# ============================================================
st.set_page_config(page_title="NanoBio Studio", page_icon="🧬", layout="wide")

# ============================================================
# 🎨 AGGRESSIVE FONT SIZE OVERRIDE - Apply BEFORE anything else
# ============================================================
st.markdown("""<style>
/* Force font size changes across entire app */
html, body, * { font-size: inherit !important; }

/* Main text and body */
p, span, div, label { font-size: 13px !important; }
button, [data-testid="stButton"] button { font-size: 9px !important; }
h1 { font-size: 28px !important; }
h2 { font-size: 24px !important; }
h3 { font-size: 20px !important; }

/* Streamlit specific overrides */
[data-testid="stButton"] button { font-size: 12px !important; padding: 8px 12px !important; }
[data-testid="stSelectbox"] { font-size: 13px !important; }
[data-testid="stNumberInput"] { font-size: 13px !important; }
[data-testid="stTextInput"] { font-size: 13px !important; }
[data-testid="stSlider"] { font-size: 13px !important; }
[data-testid="stMetricLabel"] { font-size: 12px !important; }

/* Menu/navbar buttons - most important */
div.navbar button { font-size: 10px !important; }
button[key^="nav_"] { font-size: 10px !important; }
</style>""", unsafe_allow_html=True)

# ============================================================
# 🔐 LOGIN GATE (runs before the rest of the UI)
# ============================================================

def show_login_page():
    """Display login page with signup option"""
    # Initialize session state
    if "auth_tab" not in st.session_state:
        st.session_state.auth_tab = "Login"
    
    # Header
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title("🧬 NanoBio Studio")
        st.caption("Connecting Nanotechnology & Biotechnology")
    
    with col2:
        st.markdown("### © Experts Group FZE")
        st.caption("Confidential / Proprietary")
    
    st.divider()
    
    # Check if admin exists
    admin_count = count_admin_users()
    
    # Tabs for Login, Signup, Admin Setup
    if admin_count == 0:
        tab_options = ["Admin Setup", "Login", "Sign Up"]
    else:
        tab_options = ["Login", "Sign Up"]
    
    tab1, tab2, *extra_tabs = st.tabs(tab_options)
    
    # ============================================================
    # ADMIN SETUP TAB (only if no admin exists)
    # ============================================================
    if admin_count == 0 and len(extra_tabs) > 0:
        with tab1:
            st.info("⚠️ **No admin account exists yet.** Please create one to get started.")
            
            with st.form("admin_setup_form"):
                st.markdown("### Create Admin Account")
                
                admin_username = st.text_input(
                    "Admin Username",
                    help="Username for the system administrator"
                )
                admin_email = st.text_input(
                    "Admin Email (optional)",
                    help="Email address for the admin account"
                )
                admin_password = st.text_input(
                    "Admin Password",
                    type="password",
                    help="Must contain at least 6 characters, with letters and numbers"
                )
                admin_password_confirm = st.text_input(
                    "Confirm Password",
                    type="password",
                    help="Re-enter your password"
                )
                
                if st.form_submit_button("Create Admin Account", use_container_width=True):
                    if admin_password != admin_password_confirm:
                        st.error("❌ Passwords do not match")
                    else:
                        success, msg = setup_admin_account(admin_username, admin_password, admin_email)
                        if success:
                            st.success(f"✅ {msg}")
                            st.info("Admin account created! Please log in.")
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
        
        # Switch to login tab
        with tab2:
            login_tab_content()
        
        if len(extra_tabs) > 0:
            with extra_tabs[0]:
                signup_tab_content()
    else:
        # Standard login and signup tabs
        with tab1:
            login_tab_content()
        
        with tab2:
            signup_tab_content()
    
    st.stop()


def login_tab_content():
    """Login tab content"""
    st.markdown("### 🔐 Login to Your Account")
    
    with st.form("login_form"):
        username = st.text_input("Username", help="Your username")
        password = st.text_input("Password", type="password", help="Your password")
        
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("Login", use_container_width=True)
        with col2:
            st.form_submit_button("Clear", use_container_width=True)
        
        if login_button:
            if username and password:
                ok, role = authenticate(username, password)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.username = username.strip()
                    st.session_state.role = role
                    st.success(f"✅ Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")
            else:
                st.warning("⚠️ Please enter both username and password")
    
    # Password recovery section
    st.markdown("---")
    st.markdown("#### 🔑 Forgot Your Password?")
    st.info("If you forgot your password, please contact your administrator to reset it. Provide them with your username.")
    
    with st.expander("📝 Password Recovery Options"):
        st.markdown("""
        **If you forgot your password:**
        1. **Contact Your Administrator** - Provide them with your username
        2. **Check Your Email** - Password reset instructions may have been sent
        3. **Account Recovery** - Contact your institution's IT support
        
        **Security Note:** For your protection, only administrators can reset passwords. This prevents unauthorized access to accounts.
        """)


def signup_tab_content():
    """Signup tab content"""
    st.markdown("### 👤 Create New Account")
    
    with st.form("signup_form"):
        st.markdown("Fill in the form below to create a new account")
        
        new_username = st.text_input(
            "Username",
            help="3-30 characters, letters, numbers, underscore, and hyphen only"
        )
        new_email = st.text_input(
            "Email (optional)",
            help="Valid email address for account recovery"
        )
        new_password = st.text_input(
            "Password",
            type="password",
            help="At least 6 characters with letters and numbers"
        )
        new_password_confirm = st.text_input(
            "Confirm Password",
            type="password",
            help="Re-enter your password"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            signup_button = st.form_submit_button("Create Account", use_container_width=True)
        with col2:
            st.form_submit_button("Clear", use_container_width=True)
        
        if signup_button:
            # Validate passwords match
            if new_password != new_password_confirm:
                st.error("❌ Passwords do not match")
            else:
                # Register user
                success, msg = register_user(new_username, new_password, new_email, role="student")
                if success:
                    st.success(f"✅ {msg}")
                    st.info("Your account has been created! Please log in with your credentials.")
                else:
                    st.error(f"❌ {msg}")
    
    st.markdown("---")
    st.markdown("### Requirements:")
    st.markdown("""
    - **Username:** 3-30 characters (letters, numbers, underscore, hyphen)
    - **Password:** At least 6 characters (must include letters and numbers)
    - **Email:** Optional but recommended for account recovery
    """)


def require_login():
    """Check login status and show login page if needed"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None

    # Check for session timeout if user is logged in
    if st.session_state.logged_in and st.session_state.username:
        is_expired, time_remaining = is_session_expired(st.session_state.username, SESSION_TIMEOUT_MINUTES)
        
        if is_expired:
            # Session has expired
            log_activity(st.session_state.username, "SESSION_EXPIRED", "User session timeout due to inactivity")
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            st.error("⏱️ Your session has expired due to inactivity. Please log in again.")
            st.stop()
        else:
            # Update last activity
            update_last_activity(st.session_state.username)

    if st.session_state.logged_in:
        return

    show_login_page()

require_login()

# Optional: show logged-in info or login link in sidebar
with st.sidebar:
    if st.session_state.logged_in:
        st.markdown("### 👤 Session")
        st.write(f"User: **{st.session_state.username}**")
        
        # Show role badge with RBAC styling
        show_role_badge()
        
        # Show session timeout info
        if st.session_state.username:
            is_expired, time_remaining = is_session_expired(st.session_state.username, SESSION_TIMEOUT_MINUTES)
            if not is_expired and "m" in time_remaining:
                # Extract remaining minutes
                remaining_str = time_remaining.replace("m", "").replace("s", "").strip().split()
                try:
                    mins = int(remaining_str[0]) if remaining_str else SESSION_TIMEOUT_MINUTES
                    if mins <= 5:  # Show warning when less than 5 minutes remain
                        st.warning(f"⏱️ Session expires in {time_remaining}. Click to refresh:", icon="⏱️")
                        if st.button("🔄 Refresh Session", use_container_width=True):
                            update_last_activity(st.session_state.username)
                            st.rerun()
                except:
                    pass
        
        # Divider
        st.divider()
        
        # Show role permissions info (expandable)
        with st.expander("📋 View My Permissions"):
            show_role_info()
        
        # Logout button
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚙️ Admin Panel", use_container_width=True):
                st.session_state.current_tab = "⚙️ Admin"
                st.rerun()
        
        with col2:
            if st.button("🚪 Logout", use_container_width=True):
                # Log logout activity
                log_activity(st.session_state.username, "LOGOUT", "User logged out")
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.role = None
                st.success("Logged out successfully!")
                st.rerun()
    else:
        # Show login link when not logged in
        st.markdown("### 🔐 Authentication")
        st.info("Please log in to access the full application.", icon="ℹ️")
        if st.button("🔑 Go to Login Page", use_container_width=True):
            st.rerun()


# ============================================================
# PLACEHOLDER - ADMIN PANEL CODE REMOVED FROM SIDEBAR
# ============================================================
# The admin panel has been moved to a dedicated page
# Find it under "⚙️ Admin" tab when logged in as admin


# ============================================================
# 🧭 NAVIGATION BAR (Fixed - Properly Clickable, with RBAC)
# ============================================================

# Initialize session state for navigation
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "🏠 Home"

# Define all available tabs
all_tabs = [
    "🏠 Home", "🧱 Materials", "🎨 Design", "📈 Delivery",
    "☣️ Toxicity", "💰 Cost", "🧾 Protocol", "🎯 Quiz"
]

# Only add 3D View if Plotly is available
if PLOTLY_AVAILABLE:
    all_tabs.append("🔬 3D View")

# Add AI Optimization if scikit-learn is available
if SKLEARN_AVAILABLE:
    all_tabs.append("🤖 AI Optimize")

# Add Design History tab for logged-in users
if st.session_state.logged_in:
    all_tabs.append("📊 History")

# Add Admin tab if user is admin
if get_user_role() == Role.ADMIN:
    all_tabs.append("⚙️ Admin")

# Filter tabs based on user's role
available_tabs = get_available_tabs(all_tabs)

# If current tab is not accessible, switch to Home
if st.session_state.current_tab not in available_tabs and "🏠 Home" in available_tabs:
    st.session_state.current_tab = "🏠 Home"

# Create navigation buttons
st.markdown("""
<style>
div.navbar {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    background-color: #f8f9fa;
    border-bottom: 1px solid #ddd;
    padding: 8px 6px;
    border-radius: 8px;
    margin-bottom: 10px;
}
div.navbar button {
    flex: 1 1 auto;
    margin: 2px;
    padding: 8px 12px !important;
    border-radius: 8px;
    border: 1px solid #ccc;
    background-color: white;
    color: #333;
    font-weight: 600;
    font-size: 10px !important;
    line-height: 1.2 !important;
    transition: all 0.25s;
    cursor: pointer;
}
div.navbar button span {
    font-size: 10px !important;
}
div.navbar button:hover {
    background-color: #e3f2fd !important;
    border-color: #90caf9 !important;
    transform: translateY(-1px);
}
div.navbar button:active {
    transform: translateY(0px);
}
/* Highlight current tab */
div.navbar button.current-tab {
    background-color: #1976d2 !important;
    color: white !important;
    border-color: #1976d2 !important;
}
/* Override Streamlit's default button styles */
[data-testid="column"] div button {
    font-size: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# Create navigation bar
st.markdown('<div class="navbar">', unsafe_allow_html=True)
cols = st.columns(len(available_tabs))

for i, tab_name in enumerate(available_tabs):
    with cols[i]:
        # Determine if this is the current tab
        is_current = st.session_state.current_tab == tab_name
        button_label = tab_name
        
        if st.button(button_label, use_container_width=True, key=f"nav_{i}", 
                    type="primary" if is_current else "secondary"):
            st.session_state.current_tab = tab_name
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Set the current mode based on navigation
mode = st.session_state.current_tab

# ============================================================
# 2️⃣ SESSION STATE
# ============================================================

if "design" not in st.session_state:
    st.session_state.design = {
        # Basic properties (existing)
        "Material": "Lipid NP",
        "Size": 100,
        "Charge": -5,
        "Encapsulation": 70,
        "Target": "Liver Cells",
        "Ligand": "GalNAc",
        "Receptor": "ASGPR",
        
        # Advanced properties (new)
        "HydrodynamicSize": 120,
        "PDI": 0.15,
        "SurfaceArea": 250,
        "PoreSize": 2.5,
        "DegradationTime": 30,
        "Stability": 85
    }

# Add example designs
if "example_designs" not in st.session_state:
    st.session_state.example_designs = {
        "COVID-19 mRNA Vaccine": {"Size": 80, "Charge": -2, "Encapsulation": 95, "Material": "Lipid NP", "Target": "Immune Cells"},
        "Cancer Drug Delivery": {"Size": 120, "Charge": -8, "Encapsulation": 85, "Material": "PLGA", "Target": "Tumor Cells"},
        "Gene Therapy Vector": {"Size": 150, "Charge": 15, "Encapsulation": 70, "Material": "DNA Origami", "Target": "Neurons"},
        "Poor Design Example": {"Size": 300, "Charge": 45, "Encapsulation": 20, "Material": "Lipid NP", "Target": "Liver Cells"},
        "Optimal Design": {"Size": 100, "Charge": 5, "Encapsulation": 90, "Material": "Lipid NP", "Target": "Liver Cells"}
    }

# Add example descriptions
if "example_descriptions" not in st.session_state:
    st.session_state.example_descriptions = {
        "COVID-19 mRNA Vaccine": "Lipid nanoparticles optimized for mRNA delivery with high encapsulation and neutral charge for reduced toxicity. Based on COVID-19 vaccine technology.",
        "Cancer Drug Delivery": "PLGA nanoparticles designed for tumor targeting with moderate size for enhanced permeability and retention (EPR) effect. Commonly used in chemotherapy.",
        "Gene Therapy Vector": "DNA origami structures with positive charge for efficient binding with negatively charged cell membranes. Used in advanced gene delivery systems.",
        "Poor Design Example": "Demonstrates common pitfalls: too large for cellular uptake, highly charged causing toxicity, and poor encapsulation leading to drug waste.",
        "Optimal Design": "Well-balanced parameters showing ideal nanoparticle characteristics - optimal size, near-neutral charge, and high encapsulation efficiency."
    }

# Design history for tracking improvements
if "design_history" not in st.session_state:
    st.session_state.design_history = []

# AI Model storage
if "ai_model" not in st.session_state and SKLEARN_AVAILABLE:
    st.session_state.ai_model = None
    st.session_state.training_data = None

# ============================================================
# 3️⃣ HELPER FUNCTIONS
# ============================================================
def compute_impact(design):
    """Compute delivery, toxicity, and cost - UPDATED WITH ADVANCED PROPERTIES"""
    d = design
    
    # ---- Delivery Score (0-100) - UPDATED WITH ADVANCED PROPERTIES
    # Size: optimal is 80-120nm
    if 80 <= d["Size"] <= 120:
        size_score = 100
    elif d["Size"] < 80:
        size_score = (d["Size"] / 80.0) * 100
    else:
        size_score = max(0, 100 - ((d["Size"] - 120) / 2))
    
    # Charge: optimal is -10 to +10 mV  
    if abs(d["Charge"]) <= 10:
        charge_score = 100
    else:
        charge_score = max(0, 100 - ((abs(d["Charge"]) - 10) * 3))
    
    # Encapsulation: direct percentage
    encap_score = d["Encapsulation"]
    
    # NEW: Advanced properties affecting delivery
    # PDI (Polydispersity Index) - lower is better
    pdi_score = max(0, 100 - (d["PDI"] * 200))  # PDI=0.1 → 80, PDI=0.5 → 0
    
    # Hydrodynamic size vs core size ratio - closer to 1 is better
    size_ratio = d["HydrodynamicSize"] / d["Size"] if d["Size"] > 0 else 1
    if 1.0 <= size_ratio <= 1.3:
        hydrodynamic_score = 100
    else:
        hydrodynamic_score = max(0, 100 - (abs(size_ratio - 1.15) * 50))
    
    # Stability score
    stability_score = d["Stability"]
    
    # Weighted average for delivery - UPDATED WEIGHTS
    delivery = (
        size_score * 0.25 + 
        charge_score * 0.20 + 
        encap_score * 0.25 +
        pdi_score * 0.15 +
        hydrodynamic_score * 0.10 +
        stability_score * 0.05
    )
    
    # ---- Toxicity (0-10) - UPDATED WITH ADVANCED PROPERTIES
    base_toxicity = min(10, 
        (abs(d["Charge"]) / 10) +
        (max(0, abs(d["Size"] - 100)) / 50)
    )
    
    # NEW: Advanced properties affecting toxicity
    # High PDI increases toxicity (non-uniform particles)
    pdi_toxicity = d["PDI"] * 2
    
    # Very slow degradation can cause accumulation toxicity
    degradation_toxicity = max(0, (d["DegradationTime"] - 30) / 30)
    
    toxicity = min(10, base_toxicity + pdi_toxicity + degradation_toxicity)
    
    # ---- Cost (0-100) - UPDATED WITH ADVANCED PROPERTIES  
    base_cost = min(100, 
        (100 - d["Encapsulation"]) * 0.8 +
        (d["Size"] / 4)
    )
    
    # NEW: Advanced properties affecting cost
    # High surface area increases manufacturing cost
    surface_area_cost = d["SurfaceArea"] / 20
    
    # Very low PDI increases cost (requires better manufacturing)
    pdi_cost = (0.2 - min(d["PDI"], 0.2)) * 100
    
    # Long degradation time might require special materials
    degradation_cost = max(0, (d["DegradationTime"] - 60) / 10)
    
    cost = min(100, base_cost + surface_area_cost + pdi_cost + degradation_cost)
    
    return {"Delivery": delivery, "Toxicity": toxicity, "Cost": cost}

def get_recommendations(design):
    """Get design improvement recommendations"""
    recommendations = []
    
    if design["Size"] < 80:
        recommendations.append("🔴 **Increase size to 80-120nm** for better stability and circulation")
    elif design["Size"] > 150:
        recommendations.append("🔴 **Reduce size to 80-120nm** for better cellular uptake")
    
    if abs(design["Charge"]) > 15:
        recommendations.append("🟡 **Lower surface charge** to ±10mV for reduced toxicity")
    elif abs(design["Charge"]) > 10:
        recommendations.append("🟡 **Consider reducing charge** closer to neutral for optimal safety")
    
    if design["Encapsulation"] < 70:
        recommendations.append("🔴 **Improve encapsulation to >80%** for better drug delivery efficiency")
    elif design["Encapsulation"] < 85:
        recommendations.append("🟡 **Aim for >85% encapsulation** for optimal performance")
    
    if not recommendations:
        recommendations.append("✅ **Excellent design!** All parameters are within optimal ranges")
    
    return recommendations

def validate_parameter(param, value, optimal_range):
    """Color-coded parameter validation"""
    if value >= optimal_range[0] and value <= optimal_range[1]:
        return "✅"
    elif abs(value - optimal_range[0]) < 20 or abs(value - optimal_range[1]) < 20:
        return "🟡"
    else:
        return "🔴"

def show_circular_dial(value: float, label: str = "Overall Design Score", size: float = 3.0):
    """FIXED dial gauge - won't vanish anymore"""
    score = float(np.clip(value, 0, 100))
    
    fig, ax = plt.subplots(figsize=(size, size))
    
    # Clear background
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')
    
    # Draw colored background segments
    segments = [
        (180, 240, "#FF4E4E"),  # Red: 9 o'clock to 7 o'clock (0-33%)
        (240, 300, "#FFC200"),  # Yellow: 7 o'clock to 5 o'clock (33-66%)
        (300, 360, "#4CAF50"),  # Green: 5 o'clock to 3 o'clock (66-100%)
        (0, 60, "#4CAF50"),     # Green: 3 o'clock to 1 o'clock
        (60, 120, "#FFC200"),   # Yellow: 1 o'clock to 11 o'clock
        (120, 180, "#FF4E4E"),  # Red: 11 o'clock to 9 o'clock
    ]
    
    for start, end, color in segments:
        ax.add_patch(Wedge((0, 0), 1.0, start, end, width=0.3, color=color, alpha=0.3))

    # Draw outer ring
    outer_ring = Wedge((0, 0), 1.0, 0, 360, width=0.3, fill=False, edgecolor='#444', linewidth=2)
    ax.add_patch(outer_ring)
    
    # Angle calculation
    needle_angle = 180 + (score / 100.0) * 180
    angle_rad = np.radians(needle_angle)
    
    # Draw needle
    needle_length = 0.8
    x_end = needle_length * np.cos(angle_rad)
    y_end = needle_length * np.sin(angle_rad)
    
    ax.plot([0, x_end], [0, y_end], color='#333', linewidth=3)
    
    # Draw center dot
    ax.plot(0, 0, 'ko', markersize=6)
    
    # Add score text
    ax.text(0, 0, f"{score:.0f}%", ha='center', va='center', 
            fontsize=16, fontweight='bold', color='#333')
    
    # Add label
    ax.text(0, -1.2, label, ha='center', va='center', 
            fontsize=12, color='#555', fontweight='600')
    
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect('equal')
    ax.axis('off')
    
    st.pyplot(fig, use_container_width=False)

def characterization_techniques(design):
    """Suggest characterization methods based on design"""
    st.markdown("### 🔍 Recommended Characterization Techniques")
    
    techniques = []
    
    # Size-related characterization
    techniques.append("**Dynamic Light Scattering (DLS)** - Hydrodynamic size and PDI")
    
    if design["Size"] < 100:
        techniques.append("**Transmission Electron Microscopy (TEM)** - High resolution size and morphology")
    else:
        techniques.append("**Scanning Electron Microscopy (SEM)** - Surface morphology and size")
    
    # Surface characterization
    techniques.append("**Zeta Potential** - Surface charge and stability")
    
    # Structural characterization
    if design["SurfaceArea"] > 300:
        techniques.append("**BET Surface Area Analysis** - Specific surface area and porosity")
    
    if design["PoreSize"] > 2:
        techniques.append("**Gas Adsorption** - Pore size distribution")
    
    # Drug-related characterization
    if design["Encapsulation"] > 0:
        techniques.append("**High Performance Liquid Chromatography (HPLC)** - Encapsulation efficiency and drug loading")
        techniques.append("**UV-Vis Spectroscopy** - Drug content and release studies")
    
    # Stability and degradation
    techniques.append("**Stability Studies** - Size and charge stability over time")
    
    if design["DegradationTime"] < 60:
        techniques.append("**In vitro Degradation** - Mass loss and degradation products")
    
    # Display techniques
    for i, tech in enumerate(techniques, 1):
        st.write(f"{i}. {tech}")
    
    return techniques

def regulatory_checklist(design):
    """FDA/EMA compliance checklist"""
    st.markdown("### 📋 Regulatory Considerations")
    
    checklist = {
        "Size < 200nm": design["Size"] <= 200,
        "PDI < 0.3": design["PDI"] < 0.3,
        "Charge within ±30mV": abs(design["Charge"]) <= 30,
        "Encapsulation > 70%": design["Encapsulation"] >= 70,
        "Stability > 80%": design["Stability"] >= 80,
        "Material approved for medical use": design["Material"] in ["Lipid NP", "PLGA"],
        "Degradation products characterized": design["DegradationTime"] < 90,
        "Sterilization method defined": True
    }
    
    passed = 0
    total = len(checklist)
    
    for item, status in checklist.items():
        if status:
            st.success(f"✅ {item}")
            passed += 1
        else:
            st.error(f"❌ {item}")
    
    compliance_rate = (passed / total) * 100
    st.metric("Regulatory Compliance", f"{compliance_rate:.1f}%")
    
    return compliance_rate

# ============================================================
# 3D VISUALIZATION FUNCTIONS
# ============================================================

if PLOTLY_AVAILABLE:
    def create_3d_nanoparticle(design):
        """Create interactive 3D nanoparticle model"""
        
        # Core nanoparticle
        size = design['Size'] / 50  # Scale for visualization
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = size * np.outer(np.cos(u), np.sin(v))
        y = size * np.outer(np.sin(u), np.sin(v))
        z = size * np.outer(np.ones(np.size(u)), np.cos(v))
        
        # Surface charge representation
        charge_color = 'red' if design['Charge'] > 0 else 'blue' if design['Charge'] < 0 else 'gray'
        charge_intensity = min(1.0, abs(design['Charge']) / 30)
        
        # Ligands/targeting molecules
        ligand_positions = []
        num_ligands = max(3, int(design['Encapsulation'] / 20))
        
        for i in range(num_ligands):
            theta = 2 * np.pi * i / num_ligands
            phi = np.pi / 4
            ligand_x = size * 1.2 * np.sin(phi) * np.cos(theta)
            ligand_y = size * 1.2 * np.sin(phi) * np.sin(theta) 
            ligand_z = size * 1.2 * np.cos(phi)
            ligand_positions.append((ligand_x, ligand_y, ligand_z))
        
        fig = go.Figure()
        
        # Core nanoparticle
        fig.add_trace(go.Surface(
            x=x, y=y, z=z,
            colorscale=[[0, charge_color], [1, charge_color]],
            opacity=0.8,
            showscale=False,
            name=f"Core ({design['Size']}nm)"
        ))
        
        # Ligands
        if ligand_positions:
            lig_x, lig_y, lig_z = zip(*ligand_positions)
            fig.add_trace(go.Scatter3d(
                x=lig_x, y=lig_y, z=lig_z,
                mode='markers+lines',
                marker=dict(
                    size=6,
                    color='green',
                    symbol='circle'
                ),
                line=dict(
                    color='darkgreen',
                    width=3
                ),
                name=f"Ligands ({design['Ligand']})"
            ))
        
        # Drug molecules inside (if encapsulated)
        if design['Encapsulation'] > 0:
            drug_positions = []
            num_drugs = int(design['Encapsulation'] / 10)
            
            for i in range(num_drugs):
                r = np.random.random() * size * 0.8
                theta = np.random.random() * 2 * np.pi
                phi = np.random.random() * np.pi
                drug_x = r * np.sin(phi) * np.cos(theta)
                drug_y = r * np.sin(phi) * np.sin(theta)
                drug_z = r * np.cos(phi)
                drug_positions.append((drug_x, drug_y, drug_z))
            
            drug_x, drug_y, drug_z = zip(*drug_positions)
            fig.add_trace(go.Scatter3d(
                x=drug_x, y=drug_y, z=drug_z,
                mode='markers',
                marker=dict(
                    size=4,
                    color='purple',
                    symbol='diamond'
                ),
                name=f"Drug ({design['Encapsulation']}% encapsulated)"
            ))
        
        fig.update_layout(
            title=f"3D Nanoparticle Model: {design['Material']}",
            scene=dict(
                xaxis_title="X (nm)",
                yaxis_title="Y (nm)", 
                zaxis_title="Z (nm)",
                bgcolor='white',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
            ),
            width=800,
            height=600
        )
        
        return fig

    def create_multi_parameter_radar(design):
        """Create radar chart for multiple parameters"""
        
        categories = ['Size', 'Charge', 'Encapsulation', 'Stability', 'PDI', 'Targeting']
        
        # Normalize values for radar chart
        size_score = max(0, 100 - abs(design['Size'] - 100))
        charge_score = max(0, 100 - abs(design['Charge']) * 3)
        encap_score = design['Encapsulation']
        stability_score = design['Stability']
        pdi_score = max(0, 100 - (design['PDI'] * 200))
        targeting_score = 80  # Based on ligand-receptor match
        
        values = [size_score, charge_score, encap_score, stability_score, pdi_score, targeting_score]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Current Design',
            line=dict(color='blue', width=2),
            fillcolor='rgba(0, 0, 255, 0.3)'
        ))
        
        # Add optimal range
        optimal_values = [90, 90, 90, 90, 90, 90]
        fig.add_trace(go.Scatterpolar(
            r=optimal_values,
            theta=categories,
            fill='toself',
            name='Optimal Range',
            line=dict(color='green', width=1, dash='dash'),
            fillcolor='rgba(0, 255, 0, 0.1)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Design Parameter Radar Chart"
        )
        
        return fig

# ============================================================
# AI OPTIMIZATION FUNCTIONS
# ============================================================

if SKLEARN_AVAILABLE:
    def generate_training_data():
        """Generate synthetic training data for nanoparticle optimization"""
        np.random.seed(42)
        n_samples = 1000
        
        data = []
        for i in range(n_samples):
            # Generate realistic nanoparticle parameters
            size = np.random.uniform(10, 300)
            charge = np.random.uniform(-50, 50)
            encapsulation = np.random.uniform(10, 100)
            material_idx = np.random.choice([0, 1, 2, 3])  # Lipid NP, PLGA, DNA Origami, MOF-303
            pdi = np.random.uniform(0.01, 0.5)
            stability = np.random.uniform(50, 100)
            surface_area = np.random.uniform(50, 1000)
            degradation_time = np.random.uniform(1, 180)
            
            # Create design dictionary
            design = {
                "Size": size,
                "Charge": charge,
                "Encapsulation": encapsulation,
                "Material": material_idx,
                "PDI": pdi,
                "Stability": stability,
                "SurfaceArea": surface_area,
                "DegradationTime": degradation_time
            }
            
            # Calculate impact scores
            impact = compute_impact({
                "Size": size, "Charge": charge, "Encapsulation": encapsulation,
                "Material": "Lipid NP", "Target": "Liver Cells", "Ligand": "GalNAc", "Receptor": "ASGPR",
                "HydrodynamicSize": size * 1.2, "PDI": pdi, "SurfaceArea": surface_area,
                "PoreSize": 2.5, "DegradationTime": degradation_time, "Stability": stability
            })
            
            data.append({
                **design,
                "Delivery": impact["Delivery"],
                "Toxicity": impact["Toxicity"],
                "Cost": impact["Cost"],
                "Overall": max(0, min(100,
                    (impact["Delivery"] * 0.6) +
                    ((10 - impact["Toxicity"]) * 3) +
                    ((100 - impact["Cost"]) * 0.1)
                ))
            })
        
        return pd.DataFrame(data)
    
    def train_ai_model():
        """Train the AI optimization model"""
        if st.session_state.training_data is None:
            with st.spinner("🤖 Generating training data..."):
                st.session_state.training_data = generate_training_data()
        
        df = st.session_state.training_data
        
        # Prepare features and targets
        feature_columns = ['Size', 'Charge', 'Encapsulation', 'Material', 'PDI', 'Stability', 'SurfaceArea', 'DegradationTime']
        X = df[feature_columns]
        
        # Multiple target variables
        y_delivery = df['Delivery']
        y_toxicity = df['Toxicity']
        y_cost = df['Cost']
        y_overall = df['Overall']
        
        # Train models for each target
        models = {}
        for target_name, y in [('delivery', y_delivery), ('toxicity', y_toxicity), 
                              ('cost', y_cost), ('overall', y_overall)]:
            model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
            model.fit(X, y)
            models[target_name] = model
        
        st.session_state.ai_model = {
            'models': models,
            'feature_columns': feature_columns,
            'feature_means': X.mean().to_dict(),
            'feature_stds': X.std().to_dict()
        }
        
        return models
    
    def ai_design_suggestions(current_design, target_metric="delivery", improvement_target=10):
        """AI-powered design optimization suggestions"""
        if st.session_state.ai_model is None:
            train_ai_model()
        
        model_data = st.session_state.ai_model
        models = model_data['models']
        feature_columns = model_data['feature_columns']
        
        # Convert current design to feature vector
        material_mapping = {"Lipid NP": 0, "PLGA": 1, "DNA Origami": 2, "MOF-303": 3}
        current_features = np.array([[
            current_design['Size'],
            current_design['Charge'],
            current_design['Encapsulation'],
            material_mapping.get(current_design['Material'], 0),
            current_design['PDI'],
            current_design['Stability'],
            current_design['SurfaceArea'],
            current_design['DegradationTime']
        ]])
        
        # Get current score
        current_score = models[target_metric].predict(current_features)[0]
        target_score = min(100, current_score + improvement_target)
        
        # Generate optimization suggestions using gradient-free optimization
        suggestions = generate_optimization_suggestions(current_design, target_metric, target_score, models, feature_columns)
        
        return {
            "current_score": current_score,
            "target_score": target_score,
            "improvement_needed": improvement_target,
            "suggestions": suggestions,
            "confidence": np.random.uniform(0.7, 0.95)  # Simulated confidence score
        }
    
    def generate_optimization_suggestions(current_design, target_metric, target_score, models, feature_columns):
        """Generate specific parameter adjustment suggestions"""
        suggestions = []
        
        # Material-specific optimizations
        material_suggestions = {
            "Lipid NP": "Consider PEGylation for improved stability and reduced immunogenicity",
            "PLGA": "Optimize lactide:glycolide ratio for controlled release profile",
            "DNA Origami": "Increase structural stability with cross-linking strategies",
            "MOF-303": "Modulate pore size for better drug loading and release"
        }
        
        current_material = current_design['Material']
        if current_material in material_suggestions:
            suggestions.append(material_suggestions[current_material])
        
        # Parameter-specific optimizations based on target metric
        if target_metric == "delivery":
            if current_design['Size'] > 150:
                suggestions.append(f"Reduce size from {current_design['Size']}nm to 80-120nm for better cellular uptake")
            elif current_design['Size'] < 80:
                suggestions.append(f"Increase size from {current_design['Size']}nm to 80-120nm for improved circulation")
            
            if abs(current_design['Charge']) > 15:
                suggestions.append(f"Adjust charge from {current_design['Charge']}mV to ±10mV for better membrane interaction")
            
            if current_design['Encapsulation'] < 80:
                suggestions.append(f"Improve encapsulation from {current_design['Encapsulation']}% to >85% using double emulsion methods")
        
        elif target_metric == "toxicity":
            if abs(current_design['Charge']) > 10:
                suggestions.append(f"Reduce absolute charge from {abs(current_design['Charge'])}mV to <10mV for lower toxicity")
            
            if current_design['PDI'] > 0.2:
                suggestions.append(f"Improve uniformity (reduce PDI from {current_design['PDI']} to <0.15)")
            
            if current_design['DegradationTime'] > 60:
                suggestions.append(f"Consider faster-degrading materials (current: {current_design['DegradationTime']} days)")
        
        elif target_metric == "cost":
            if current_design['Encapsulation'] < 70:
                suggestions.append(f"Increase encapsulation from {current_design['Encapsulation']}% to reduce drug waste")
            
            if current_design['SurfaceArea'] > 500:
                suggestions.append("Consider materials with moderate surface area to reduce synthesis cost")
            
            if current_design['PDI'] < 0.1:
                suggestions.append("Slightly relax PDI requirement to reduce manufacturing complexity")
        
        # Advanced optimization strategies
        advanced_suggestions = [
            "Implement surface functionalization for targeted delivery",
            "Optimize core-shell structure for controlled release",
            "Consider hybrid materials for improved performance",
            "Use computational modeling to predict in vivo behavior"
        ]
        
        # Add 1-2 advanced suggestions
        suggestions.extend(np.random.choice(advanced_suggestions, size=min(2, len(advanced_suggestions)), replace=False))
        
        return suggestions
    
    def perform_parameter_sweep(current_design, target_metric):
        """Perform parameter sweep to find optimal values"""
        best_score = -1
        best_params = current_design.copy()
        
        # Test different parameter combinations
        n_iterations = 50
        improvements = []
        
        for i in range(n_iterations):
            # Generate random parameter variations
            test_design = current_design.copy()
            
            # Vary key parameters
            test_design['Size'] = np.clip(current_design['Size'] + np.random.normal(0, 20), 10, 300)
            test_design['Charge'] = np.clip(current_design['Charge'] + np.random.normal(0, 5), -50, 50)
            test_design['Encapsulation'] = np.clip(current_design['Encapsulation'] + np.random.normal(0, 10), 10, 100)
            test_design['PDI'] = np.clip(current_design['PDI'] + np.random.normal(0, 0.05), 0.01, 0.5)
            
            # Calculate score
            impact = compute_impact(test_design)
            if target_metric == "delivery":
                score = impact["Delivery"]
            elif target_metric == "toxicity":
                score = 10 - impact["Toxicity"]  # Lower toxicity is better
            elif target_metric == "cost":
                score = 100 - impact["Cost"]  # Lower cost is better
            else:  # overall
                score = max(0, min(100,
                    (impact["Delivery"] * 0.6) +
                    ((10 - impact["Toxicity"]) * 3) +
                    ((100 - impact["Cost"]) * 0.1)
                ))
            
            improvements.append({
                'iteration': i,
                'score': score,
                'size_change': test_design['Size'] - current_design['Size'],
                'charge_change': test_design['Charge'] - current_design['Charge'],
                'encapsulation_change': test_design['Encapsulation'] - current_design['Encapsulation']
            })
            
            if score > best_score:
                best_score = score
                best_params = test_design.copy()
        
        return best_params, best_score, improvements

# ============================================================
# 4️⃣ LAYOUT & MODULES
# ============================================================

# Sidebar: Live impact panel
with st.sidebar:
    st.markdown("## ⚡ Live Impact Overview")
    
    # Get current design
    d = st.session_state.design
    st.write("**Current Parameters:**")
    st.write(f"Size: {d['Size']}nm, Charge: {d['Charge']}mV, Encapsulation: {d['Encapsulation']}%")
    
    # Calculate impact
    impact = compute_impact(d)
    st.write("**Impact Scores:**")
    st.write(f"Delivery: {impact['Delivery']:.1f}%")
    st.write(f"Toxicity: {impact['Toxicity']:.2f}/10")
    st.write(f"Cost: {impact['Cost']:.1f}")
    
    # Calculate overall score - FIXED VERSION
    overall_score = max(0, min(100,
        (impact["Delivery"] * 0.6) +          # Delivery is most important (60%)
        ((10 - impact["Toxicity"]) * 3) +     # Low toxicity adds points (max +30)
        ((100 - impact["Cost"]) * 0.1)        # Low cost adds a little (max +10)
    ))
    
    st.write(f"**Overall Score: {overall_score:.1f}%**")
    
    # Display the dial gauge
    show_circular_dial(overall_score)
    
    # Add design recommendations to sidebar
    st.markdown("---")
    st.markdown("### 💡 Recommendations")
    recommendations = get_recommendations(st.session_state.design)
    for rec in recommendations:
        st.write(rec)
    
    # Add regulatory checklist to sidebar
    st.markdown("---")
    regulatory_checklist(st.session_state.design)

# ============================================================
# 🏠 HOME DASHBOARD
# ============================================================
if mode == "🏠 Home":
    # Logo and header
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://cdn.pixabay.com/photo/2017/01/31/23/42/animal-2028258_1280.png", 
                width=80)
    with col2:
        st.header("🏠 NanoBio Studio Dashboard")
    
    # Pre-set Examples Section
    st.markdown("### 🚀 Quick Start Examples")
    st.markdown("Load pre-configured nanoparticle designs to see how different parameters affect performance:")
    
    # Create columns for example buttons
    example_cols = st.columns(3)
    
    with example_cols[0]:
        if st.button("💉 mRNA Vaccine", use_container_width=True, help="COVID-19 mRNA Vaccine Example"):
            st.session_state.design.update(st.session_state.example_designs["COVID-19 mRNA Vaccine"])
            st.session_state.design_history.append({
                "timestamp": datetime.now(),
                "design": dict(st.session_state.design),
                "score": overall_score
            })
            st.success("Loaded mRNA Vaccine example!")
            st.rerun()
    
    with example_cols[1]:
        if st.button("🎯 Cancer Therapy", use_container_width=True, help="Cancer Drug Delivery Example"):
            st.session_state.design.update(st.session_state.example_designs["Cancer Drug Delivery"])
            st.session_state.design_history.append({
                "timestamp": datetime.now(),
                "design": dict(st.session_state.design),
                "score": overall_score
            })
            st.success("Loaded Cancer Therapy example!")
            st.rerun()
    
    with example_cols[2]:
        if st.button("🧬 Gene Therapy", use_container_width=True, help="Gene Therapy Vector Example"):
            st.session_state.design.update(st.session_state.example_designs["Gene Therapy Vector"])
            st.session_state.design_history.append({
                "timestamp": datetime.now(),
                "design": dict(st.session_state.design),
                "score": overall_score
            })
            st.success("Loaded Gene Therapy example!")
            st.rerun()
    
    # Second row of examples
    example_cols2 = st.columns(2)
    
    with example_cols2[0]:
        if st.button("⚠️ Poor Design", use_container_width=True, help="Poor Design Example"):
            st.session_state.design.update(st.session_state.example_designs["Poor Design Example"])
            st.session_state.design_history.append({
                "timestamp": datetime.now(),
                "design": dict(st.session_state.design),
                "score": overall_score
            })
            st.success("Loaded Poor Design example!")
            st.rerun()
    
    with example_cols2[1]:
        if st.button("⭐ Optimal Design", use_container_width=True, help="Optimal Design Example"):
            st.session_state.design.update(st.session_state.example_designs["Optimal Design"])
            st.session_state.design_history.append({
                "timestamp": datetime.now(),
                "design": dict(st.session_state.design),
                "score": overall_score
            })
            st.success("Loaded Optimal Design example!")
            st.rerun()

    # Example descriptions expander
    with st.expander("📚 Learn About Each Example Design"):
        st.markdown("""
        **Understanding the examples will help you design better nanoparticles:**
        """)
        
        for example_name, description in st.session_state.example_descriptions.items():
            params = st.session_state.example_designs[example_name]
            st.markdown(f"**{example_name}**")
            st.markdown(f"*{description}*")
            st.markdown(f"**Parameters:** Size={params['Size']}nm, Charge={params['Charge']}mV, Encapsulation={params['Encapsulation']}%")
            st.markdown("---")
    
    st.markdown("---")
    
    st.markdown("""
    Welcome to **NanoBio Studio**, your integrated environment linking **Nanotechnology** and **Biotechnology**.  
    This dashboard gives you an instant overview of your current design performance.
    """)

    # 3D Design Preview Section (Only if Plotly available)
    if PLOTLY_AVAILABLE:
        st.markdown("### 🔬 3D Design Preview")
        col1, col2 = st.columns(2)

        with col1:
            # Quick 3D preview
            st.markdown("**Interactive 3D Model**")
            simple_fig = create_3d_nanoparticle(st.session_state.design)
            st.plotly_chart(simple_fig, use_container_width=True)

        with col2:
            st.markdown("**Live Parameter Analysis**")
            radar_fig = create_multi_parameter_radar(st.session_state.design)
            st.plotly_chart(radar_fig, use_container_width=True)

    # --- Smaller font wrapper for Current Design Summary (HOME only) ---
    st.markdown("""
    <style>
    /* Only affects content inside this wrapper */
    #current-design-summary {
      font-size: 0.90rem;
      line-height: 1.25;
    }

    /* Streamlit caption text in this wrapper */
    #current-design-summary .stCaption {
      font-size: 0.80rem !important;
    }

    /* Streamlit metric label/value sizes */
    #current-design-summary [data-testid="stMetricLabel"] {
      font-size: 0.85rem !important;
    }
    #current-design-summary [data-testid="stMetricValue"] {
      font-size: 1.15rem !important;
    }

    /* Any markdown paragraphs inside wrapper */
    #current-design-summary p {
      font-size: 0.90rem !important;
    }
    </style>

    <div id="current-design-summary">
    """, unsafe_allow_html=True)
    st.markdown("### 📊 Current Design Summary")
    d = st.session_state.design
    
    # Parameter validation with color coding
    st.markdown("#### Parameter Analysis")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        size_status = validate_parameter("Size", d["Size"], [80, 120])
        st.metric("Particle Size", f"{d['Size']} nm")
        st.caption(f"{size_status} Optimal: 80-120nm")
    
    with col2:
        charge_status = validate_parameter("Charge", abs(d["Charge"]), [0, 10])
        st.metric("Surface Charge", f"{d['Charge']} mV")
        st.caption(f"{charge_status} Optimal: ±10mV")
    
    with col3:
        encap_status = validate_parameter("Encapsulation", d["Encapsulation"], [80, 100])
        st.metric("Encapsulation", f"{d['Encapsulation']}%")
        st.caption(f"{encap_status} Target: >80%")
    
    # Design details
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Material", d["Material"])
        st.metric("Target", d["Target"])
    with col2:
        st.metric("Ligand", d["Ligand"])
        st.metric("Receptor", d["Receptor"])
    
    impact = compute_impact(d)
    overall = np.clip(100 - (impact["Toxicity"] * 5) + (impact["Delivery"] / 2) - (impact["Cost"] / 10), 0, 100)

    # --- End smaller font wrapper ---
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("### ⚡ Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delivery_status = "🟢" if impact["Delivery"] > 70 else "🟡" if impact["Delivery"] > 50 else "🔴"
        st.metric("🚀 Delivery", f"{impact['Delivery']:.1f}%")
        st.caption(f"{delivery_status} {'Excellent' if impact['Delivery'] > 70 else 'Good' if impact['Delivery'] > 50 else 'Needs Improvement'}")
    
    with col2:
        toxicity_status = "🟢" if impact["Toxicity"] < 3 else "🟡" if impact["Toxicity"] < 6 else "🔴"
        st.metric("☣️ Toxicity", f"{impact['Toxicity']:.2f}/10")
        st.caption(f"{toxicity_status} {'Low' if impact['Toxicity'] < 3 else 'Moderate' if impact['Toxicity'] < 6 else 'High'} Risk")
    
    with col3:
        cost_status = "🟢" if impact["Cost"] < 30 else "🟡" if impact["Cost"] < 60 else "🔴"
        st.metric("💰 Cost", f"{impact['Cost']:.1f}")
        st.caption(f"{cost_status} {'Low' if impact['Cost'] < 30 else 'Moderate' if impact['Cost'] < 60 else 'High'} Cost")
    
    with col4:
        overall_status = "🟢" if overall > 70 else "🟡" if overall > 50 else "🔴"
        st.metric("🧠 Overall Score", f"{overall:.1f}%")
        st.caption(f"{overall_status} {'Excellent' if overall > 70 else 'Good' if overall > 50 else 'Needs Improvement'}")

    # Export functionality
    st.markdown("### 📤 Export Your Design")
    col1, col2 = st.columns(2)
    
    with col1:
        # Export as JSON
        design_json = json.dumps(st.session_state.design, indent=2)
        st.download_button(
            label="📥 Download Design as JSON",
            data=design_json,
            file_name=f"nanoparticle_design_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        # Generate and download report
        report = f"""
NanoBio Studio Design Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DESIGN PARAMETERS:
- Material: {d['Material']}
- Target: {d['Target']}
- Size: {d['Size']} nm
- Charge: {d['Charge']} mV
- Encapsulation: {d['Encapsulation']}%
- Ligand: {d['Ligand']}
- Receptor: {d['Receptor']}

PERFORMANCE METRICS:
- Delivery Efficiency: {impact['Delivery']:.1f}%
- Toxicity Index: {impact['Toxicity']:.2f}/10
- Cost Index: {impact['Cost']:.1f}
- Overall Score: {overall:.1f}%

DESIGN RECOMMENDATIONS:
"""
        for rec in get_recommendations(st.session_state.design):
            report += f"- {rec.replace('✅', '✓').replace('🔴', '✗').replace('🟡', '~')}\n"
        
        st.download_button(
            label="📄 Download Full Report",
            data=report,
            file_name=f"nanoparticle_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

    st.markdown("### 🎯 Quick Actions")
    action_cols = st.columns(4)
    if action_cols[0].button("🎨 Redesign Particle", use_container_width=True):
        st.session_state.current_tab = "🎨 Design"
        st.rerun()
    if action_cols[1].button("📈 Run Delivery Simulation", use_container_width=True):
        st.session_state.current_tab = "📈 Delivery"
        st.rerun()
    if action_cols[2].button("☣️ Check Toxicity", use_container_width=True):
        st.session_state.current_tab = "☣️ Toxicity"
        st.rerun()
    if action_cols[3].button("🧾 Generate Protocol", use_container_width=True):
        st.session_state.current_tab = "🧾 Protocol"
        st.rerun()

    # Educational insights with expandable sections
    st.markdown("---")
    st.markdown("### 🎓 Educational Insights")
    
    with st.expander("💡 Why Particle Size Matters"):
        st.markdown("""
        - **<80nm**: May be cleared quickly by kidneys
        - **80-120nm**: Optimal for most applications - balances circulation time and cellular uptake
        - **120-200nm**: Good for certain targeting applications but may have reduced penetration
        - **>200nm**: Risk of accumulation in organs and reduced cellular uptake
        """)
    
    with st.expander("💡 Surface Charge Considerations"):
        st.markdown("""
        - **Neutral (±10mV)**: Lower toxicity, better stability in circulation
        - **Positive charge**: Better cell membrane interaction but higher toxicity risk
        - **Negative charge**: Reduced toxicity but may have faster clearance
        - **Extreme charges (>±20mV)**: High toxicity and stability issues
        """)
    
    with st.expander("💡 Encapsulation Efficiency"):
        st.markdown("""
        - **<70%**: Poor - significant drug waste and reduced efficacy
        - **70-85%**: Acceptable - reasonable efficiency for many applications  
        - **85-95%**: Good - efficient drug delivery
        - **>95%**: Excellent - minimal waste, maximum therapeutic effect
        """)

# ============================================================
# 🧱 MATERIALS & TARGETS MODULE
# ============================================================
elif mode == "🧱 Materials":
    st.header("🧱 Materials & Targets Library")
    
    st.markdown("""
    ### 📚 Comprehensive Nanomaterial Database
    Explore different nanoparticle materials and their targeting strategies for optimal drug delivery.
    """)
    
    # Materials Database
    materials_db = {
        "Lipid NP": {
            "description": "Lipid-based nanoparticles for mRNA/drug delivery",
            "composition": "Ionizable lipids, DSPC, cholesterol, PEG-lipid",
            "advantages": ["High biocompatibility", "Easy scalability", "FDA approved components"],
            "limitations": ["Limited stability", "Rapid clearance", "Moderate loading capacity"],
            "applications": ["mRNA vaccines", "siRNA delivery", "Small molecule drugs"],
            "cost": "Low-Medium",
            "toxicity": "Low",
            "stability": "2-6 months",
            "manufacturing": "Microfluidics, Ethanol injection",
            "regulatory_status": "Well-established (COVID-19 vaccines)"
        },
        "PLGA": {
            "description": "Poly(lactic-co-glycolic acid) biodegradable polymer",
            "composition": "Lactic acid + Glycolic acid copolymer",
            "advantages": ["Biodegradable", "Tunable release", "FDA approved"],
            "limitations": ["Acidic degradation", "Burst release", "Hydrophobic"],
            "applications": ["Controlled release", "Cancer therapy", "Protein delivery"],
            "cost": "Medium",
            "toxicity": "Very Low",
            "stability": "6-12 months",
            "manufacturing": "Emulsion-solvent evaporation, Nanoprecipitation",
            "regulatory_status": "FDA approved for several products"
        },
        "Gold NP": {
            "description": "Gold nanoparticles for imaging and therapy",
            "composition": "Gold core with various surface modifications",
            "advantages": ["Excellent imaging", "Photothermal therapy", "Easy surface modification"],
            "limitations": ["Non-biodegradable", "Potential accumulation", "Higher cost"],
            "applications": ["Photothermal therapy", "Imaging contrast", "Radiosensitization"],
            "cost": "High",
            "toxicity": "Medium",
            "stability": "Long-term",
            "manufacturing": "Chemical reduction, Citrate method",
            "regulatory_status": "Clinical trials ongoing"
        },
        "Silica NP": {
            "description": "Mesoporous silica nanoparticles",
            "composition": "Silica framework with porous structure",
            "advantages": ["High surface area", "Tunable pores", "Good stability"],
            "limitations": ["Slow degradation", "Inflammatory potential", "Rigid structure"],
            "applications": ["High drug loading", "Combination therapy", "Imaging"],
            "cost": "Medium",
            "toxicity": "Low-Medium",
            "stability": "12+ months",
            "manufacturing": "Sol-gel process, Stöber method",
            "regulatory_status": "Preclinical development"
        },
        "DNA Origami": {
            "description": "Programmable DNA nanostructures",
            "composition": "DNA strands forming 3D structures",
            "advantages": ["Precise control", "Biodegradable", "Multi-functional"],
            "limitations": ["Complex synthesis", "Stability issues", "High cost"],
            "applications": ["Precision medicine", "Molecular robotics", "Diagnostics"],
            "cost": "Very High",
            "toxicity": "Low",
            "stability": "Weeks (enzymatic degradation)",
            "manufacturing": "DNA self-assembly",
            "regulatory_status": "Early research phase"
        },
        "MOF-303": {
            "description": "Metal-Organic Framework nanoparticles",
            "composition": "Aluminum + organic linkers",
            "advantages": ["Ultra-high surface area", "Tunable chemistry", "Biodegradable"],
            "limitations": ["Complex synthesis", "Limited stability", "Characterization challenges"],
            "applications": ["High-capacity loading", "Gas storage", "Catalysis"],
            "cost": "High",
            "toxicity": "Low (aluminum-based)",
            "stability": "1-3 months",
            "manufacturing": "Solvothermal synthesis",
            "regulatory_status": "Research phase"
        }
    }
    
    # Targeting Ligands Database
    ligands_db = {
        "GalNAc": {
            "target": "ASGPR",
            "cells": "Hepatocytes (Liver cells)",
            "affinity": "High (nM range)",
            "applications": ["Liver targeting", "siRNA delivery", "Gene therapy"],
            "advantages": ["High specificity", "Rapid internalization", "Clinical validation"],
            "limitations": ["Liver-specific only", "Competition with natural ligands"]
        },
        "Folate": {
            "target": "Folate receptor",
            "cells": "Cancer cells, Macrophages",
            "affinity": "Medium (μM range)",
            "applications": ["Cancer targeting", "Inflammation targeting"],
            "advantages": ["Broad applicability", "Low cost", "Good safety"],
            "limitations": ["Moderate specificity", "Competition with dietary folate"]
        },
        "RGD peptide": {
            "target": "Integrins (αvβ3, αvβ5)",
            "cells": "Endothelial cells, Cancer cells",
            "affinity": "Medium (μM range)",
            "applications": ["Angiogenesis targeting", "Cancer therapy"],
            "advantages": ["Broad tumor targeting", "Good penetration"],
            "limitations": ["Moderate specificity", "Inflammatory effects"]
        },
        "Transferrin": {
            "target": "Transferrin receptor",
            "cells": "Rapidly dividing cells, Blood-brain barrier",
            "affinity": "High (nM range)",
            "applications": ["Cancer targeting", "Brain delivery"],
            "advantages": ["Natural ligand", "High uptake", "BBB penetration"],
            "limitations": ["Competition with endogenous transferrin"]
        },
        "Anti-HER2 antibody": {
            "target": "HER2 receptor",
            "cells": "HER2+ cancer cells",
            "affinity": "Very High (pM range)",
            "applications": ["Breast cancer", "Gastric cancer"],
            "advantages": ["Extreme specificity", "Clinical validation"],
            "limitations": ["High cost", "Immunogenicity risk"]
        },
        "Aptamers": {
            "target": "Various (programmable)",
            "cells": "Target-specific cells",
            "affinity": "High (nM range)",
            "applications": ["Precision targeting", "Diagnostics"],
            "advantages": ["Programmable", "Low immunogenicity", "Good stability"],
            "limitations": ["Complex selection", "Nuclease sensitivity"]
        }
    }
    
    # Layout for Materials Selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🧪 Select Nanoparticle Material")
        
        # Material selection
        selected_material = st.selectbox(
            "Choose a material:",
            list(materials_db.keys()),
            index=0,
            help="Select the core material for your nanoparticle"
        )
        
        # Display material details
        material = materials_db[selected_material]
        
        st.markdown(f"#### {selected_material} Details")
        st.write(f"**Description:** {material['description']}")
        st.write(f"**Composition:** {material['composition']}")
        
        # Properties in columns
        prop_col1, prop_col2, prop_col3 = st.columns(3)
        with prop_col1:
            st.metric("Cost", material['cost'])
            st.metric("Toxicity", material['toxicity'])
        with prop_col2:
            st.metric("Stability", material['stability'])
            st.metric("Manufacturing", material['manufacturing'])
        with prop_col3:
            st.metric("Regulatory Status", material['regulatory_status'])
        
        # Advantages and Limitations
        adv_col, lim_col = st.columns(2)
        with adv_col:
            st.markdown("**✅ Advantages:**")
            for advantage in material['advantages']:
                st.write(f"• {advantage}")
        with lim_col:
            st.markdown("**⚠️ Limitations:**")
            for limitation in material['limitations']:
                st.write(f"• {limitation}")
        
        # Applications
        st.markdown("**🎯 Applications:**")
        for app in material['applications']:
            st.write(f"• {app}")
    
    with col2:
        st.markdown("### 🎯 Targeting Strategy")
        
        # Ligand selection
        selected_ligand = st.selectbox(
            "Choose targeting ligand:",
            list(ligands_db.keys()),
            index=0,
            help="Select targeting ligand for specific cell delivery"
        )
        
        # Display ligand details
        ligand = ligands_db[selected_ligand]
        
        st.markdown(f"#### {selected_ligand} Targeting")
        st.write(f"**Target Receptor:** {ligand['target']}")
        st.write(f"**Target Cells:** {ligand['cells']}")
        st.write(f"**Binding Affinity:** {ligand['affinity']}")
        
        # Applications
        st.markdown("**Applications:**")
        for app in ligand['applications']:
            st.write(f"• {app}")
        
        # Advantages and Limitations for ligand
        st.markdown("**Advantages:**")
        for adv in ligand['advantages']:
            st.write(f"✅ {adv}")
        
        st.markdown("**Limitations:**")
        for lim in ligand['limitations']:
            st.write(f"⚠️ {lim}")
        
        # Apply selections to current design
        st.markdown("---")
        if st.button("🔄 Apply to Current Design", use_container_width=True):
            st.session_state.design.update({
                "Material": selected_material,
                "Ligand": selected_ligand,
                "Receptor": ligand['target'],
                "Target": ligand['cells']
            })
            st.success(f"✅ Applied {selected_material} with {selected_ligand} targeting!")
            st.rerun()
    
    # Material Comparison Section
    st.markdown("---")
    st.markdown("### 📊 Material Comparison")
    
    # Select materials to compare
    compare_materials = st.multiselect(
        "Select materials to compare:",
        list(materials_db.keys()),
        default=["Lipid NP", "PLGA", "Gold NP"],
        max_selections=4
    )
    
    if compare_materials:
        # Create comparison table
        comparison_data = []
        for material_name in compare_materials:
            mat = materials_db[material_name]
            comparison_data.append({
                "Material": material_name,
                "Cost": mat['cost'],
                "Toxicity": mat['toxicity'],
                "Stability": mat['stability'],
                "Manufacturing": mat['manufacturing'],
                "Regulatory Status": mat['regulatory_status']
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)
        
        # Visual comparison
        col1, col2 = st.columns(2)
        
        with col1:
            # Cost comparison chart
            cost_values = {
                "Very High": 4, "High": 3, "Medium": 2, "Low-Medium": 1.5, "Low": 1
            }
            cost_data = {
                "Material": compare_materials,
                "Cost Score": [cost_values[materials_db[m]['cost']] for m in compare_materials]
            }
            cost_df = pd.DataFrame(cost_data)
            
            fig_cost = px.bar(
                cost_df, 
                x="Material", 
                y="Cost Score",
                title="📈 Cost Comparison",
                color="Cost Score",
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig_cost, use_container_width=True)
        
        with col2:
            # Toxicity comparison - FIXED VERSION
            tox_values = {"Very Low": 1, "Low": 2, "Low-Medium": 2.5, "Medium": 3, "High": 4}
            
            # Safe extraction of toxicity values
            tox_scores = []
            for material_name in compare_materials:
                toxicity_text = materials_db[material_name]['toxicity']
                # Extract just the main toxicity level (before any parentheses)
                base_toxicity = toxicity_text.split('(')[0].strip() if '(' in toxicity_text else toxicity_text
                tox_scores.append(tox_values.get(base_toxicity, 2))  # Default to 2 if not found
            
            tox_data = {
                "Material": compare_materials,
                "Toxicity Score": tox_scores
            }
            tox_df = pd.DataFrame(tox_data)
            
            fig_tox = px.bar(
                tox_df, 
                x="Material", 
                y="Toxicity Score",
                title="☣️ Toxicity Comparison",
                color="Toxicity Score",
                color_continuous_scale="RdYlGn_r"
            )
            st.plotly_chart(fig_tox, use_container_width=True)
    
    # Material Selection Guide
    st.markdown("---")
    st.markdown("### 🎓 Material Selection Guide")
    
    with st.expander("💡 How to Choose the Right Material"):
        st.markdown("""
        **Selection Criteria:**
        
        - **🚀 Application Requirements:**
          - *mRNA/siRNA delivery* → Lipid NP, Polymer NP
          - *Controlled release* → PLGA, Mesoporous silica
          - *Imaging + therapy* → Gold NP, Iron oxide NP
          - *High loading capacity* → MOF, Mesoporous silica
        
        - **💰 Cost Considerations:**
          - *Budget constraints* → Lipid NP, PLGA
          - *Research phase* → Can consider higher cost materials
          - *Scale-up planned* → Consider manufacturing complexity
        
        - **⚖️ Regulatory Pathway:**
          - *Fast to clinic* → Lipid NP, PLGA (established safety)
          - *Novel applications* → Can explore newer materials
        
        - **🧬 Biological Requirements:**
          - *Biodegradability needed* → PLGA, Lipid NP, DNA Origami
          - *Long circulation* → PEGylated materials
          - *Specific targeting* → Materials with easy surface modification
        """)
    
    with st.expander("🔬 Advanced Material Properties"):
        st.markdown("""
        **Material-Specific Recommendations:**
        
        | Material | Best For | Avoid When |
        |----------|----------|------------|
        | **Lipid NP** | mRNA vaccines, siRNA delivery | High temperature, Organic solvents |
        | **PLGA** | Controlled release, Proteins | Acid-sensitive drugs |
        | **Gold NP** | Photothermal therapy, Imaging | Budget constraints, Biodegradability required |
        | **Silica NP** | High drug loading, Stability | Inflammatory diseases |
        | **DNA Origami** | Precision medicine, Robotics | Nuclease-rich environments |
        | **MOF** | Gas storage, High capacity | Aqueous instability concerns |
        """)
    
    # Quick Material Selection Tool
    st.markdown("---")
    st.markdown("### ⚡ Quick Material Selector")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        application = st.selectbox(
            "Primary Application:",
            ["mRNA/siRNA Delivery", "Cancer Therapy", "Imaging", "Controlled Release", "Gene Therapy"]
        )
    
    with col2:
        budget = st.select_slider(
            "Budget Level:",
            options=["Low", "Medium", "High", "Very High"]
        )
    
    with col3:
        timeline = st.select_slider(
            "Development Timeline:",
            options=["Fast (1-2 years)", "Medium (2-4 years)", "Long (4+ years)"]
        )
    
    if st.button("🎯 Get Material Recommendations", use_container_width=True):
        # Simple recommendation logic
        recommendations = []
        
        if application == "mRNA/siRNA Delivery":
            recommendations.append("**Lipid NP** - Optimized for nucleic acid delivery")
            recommendations.append("**Polymer NP** - Good for controlled release")
        
        elif application == "Cancer Therapy":
            recommendations.append("**PLGA** - Biodegradable, controlled release")
            recommendations.append("**Gold NP** - Photothermal therapy capability")
        
        elif application == "Imaging":
            recommendations.append("**Gold NP** - Excellent contrast agent")
            recommendations.append("**Silica NP** - Good for functionalization")
        
        elif application == "Controlled Release":
            recommendations.append("**PLGA** - Tunable degradation rate")
            recommendations.append("**Mesoporous Silica** - High loading capacity")
        
        elif application == "Gene Therapy":
            recommendations.append("**Lipid NP** - High transfection efficiency")
            recommendations.append("**DNA Origami** - Precision delivery")
        
        # Budget considerations
        if budget in ["Low", "Medium"]:
            recommendations.append("💡 **Cost-effective option**: Lipid NP or PLGA")
        else:
            recommendations.append("💡 **Advanced option**: Gold NP or DNA Origami")
        
        # Display recommendations
        st.markdown("#### 🎯 Recommended Materials:")
        for rec in recommendations:
            st.write(rec)
    
    # Save current configuration
    st.markdown("---")
    st.markdown("### 💾 Save Material Configuration")
    
    config_name = st.text_input("Configuration Name:", "My_Material_Setup")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Configuration", use_container_width=True):
            config = {
                "material": selected_material,
                "ligand": selected_ligand,
                "receptor": ligands_db[selected_ligand]['target'],
                "target_cells": ligands_db[selected_ligand]['cells'],
                "timestamp": datetime.now().isoformat()
            }
            
            if "material_configs" not in st.session_state:
                st.session_state.material_configs = {}
            
            st.session_state.material_configs[config_name] = config
            st.success(f"✅ Configuration '{config_name}' saved!")
    
    with col2:
        if "material_configs" in st.session_state and st.session_state.material_configs:
            saved_config = st.selectbox(
                "Load saved configuration:",
                list(st.session_state.material_configs.keys())
            )
            
            if st.button("📂 Load Configuration", use_container_width=True):
                config = st.session_state.material_configs[saved_config]
                st.session_state.design.update({
                    "Material": config['material'],
                    "Ligand": config['ligand'],
                    "Receptor": config['receptor'],
                    "Target": config['target_cells']
                })
                st.success(f"✅ Loaded configuration '{saved_config}'!")
                st.rerun()

# ============================================================
# 🎨 DESIGN NANOPARTICLE MODULE
# ============================================================
elif mode == "🎨 Design":
    # Permission check
    if not has_permission(Permission.VIEW_DESIGN):
        st.error("❌ Access Denied: You do not have permission to access the Design module.")
        st.info(f"📋 Your role ({get_user_role()}) does not have access to this feature. Please contact an administrator.")
        st.stop()
    
    st.header("🎨 Design Your Nanoparticle")
    
    st.markdown("""
    ### 🎛️ Customize Nanoparticle Parameters
    Adjust the parameters below to optimize your nanoparticle design for specific applications.
    """)
    
    # Design parameters in expandable sections
    with st.expander("📏 Core Parameters", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.session_state.design["Size"] = st.slider(
                "Particle Size (nm)",
                min_value=10,
                max_value=300,
                value=st.session_state.design["Size"],
                help="Optimal range: 80-120nm for most applications"
            )
            
            st.session_state.design["Charge"] = st.slider(
                "Surface Charge (mV)",
                min_value=-50,
                max_value=50,
                value=st.session_state.design["Charge"],
                help="Optimal range: ±10mV for low toxicity"
            )
        
        with col2:
            st.session_state.design["Encapsulation"] = st.slider(
                "Encapsulation Efficiency (%)",
                min_value=10,
                max_value=100,
                value=st.session_state.design["Encapsulation"],
                help="Target >80% for good efficiency"
            )
            
            st.session_state.design["Stability"] = st.slider(
                "Stability (%)",
                min_value=50,
                max_value=100,
                value=st.session_state.design["Stability"],
                help="Stability over 4 weeks at 4°C"
            )
        
        with col3:
            st.session_state.design["Material"] = st.selectbox(
                "Core Material",
                ["Lipid NP", "PLGA", "Gold NP", "Silica NP", "DNA Origami", "MOF-303"],
                index=0
            )
            
            st.session_state.design["Target"] = st.selectbox(
                "Target Cells/Tissue",
                ["Liver Cells", "Tumor Cells", "Immune Cells", "Neurons", "Endothelial Cells", "Pancreatic Cells"],
                index=0
            )
    
    with st.expander("🔬 Advanced Parameters", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.design["HydrodynamicSize"] = st.slider(
                "Hydrodynamic Size (nm)",
                min_value=50,
                max_value=500,
                value=st.session_state.design["HydrodynamicSize"],
                help="Size in biological fluids (usually 1.1-1.3x core size)"
            )
            
            st.session_state.design["PDI"] = st.slider(
                "Polydispersity Index (PDI)",
                min_value=0.01,
                max_value=0.5,
                value=st.session_state.design["PDI"],
                step=0.01,
                help="Lower PDI = more uniform particles (target <0.2)"
            )
            
            st.session_state.design["SurfaceArea"] = st.slider(
                "Surface Area (m²/g)",
                min_value=50,
                max_value=1000,
                value=st.session_state.design["SurfaceArea"],
                help="Higher surface area = more drug loading capacity"
            )
        
        with col2:
            st.session_state.design["PoreSize"] = st.slider(
                "Pore Size (nm)",
                min_value=1.0,
                max_value=10.0,
                value=st.session_state.design["PoreSize"],
                step=0.1,
                help="For porous nanoparticles only"
            )
            
            st.session_state.design["DegradationTime"] = st.slider(
                "Degradation Time (days)",
                min_value=1,
                max_value=180,
                value=st.session_state.design["DegradationTime"],
                help="Time for 50% degradation in physiological conditions"
            )
            
            st.session_state.design["Ligand"] = st.selectbox(
                "Targeting Ligand",
                ["GalNAc", "Folate", "RGD peptide", "Transferrin", "Anti-HER2 antibody", "Aptamers", "None"],
                index=0
            )
            
            if st.session_state.design["Ligand"] != "None":
                st.session_state.design["Receptor"] = st.text_input(
                    "Target Receptor",
                    value=st.session_state.design["Receptor"],
                    help="Specific receptor for the targeting ligand"
                )
    
    # Real-time impact visualization
    st.markdown("---")
    st.markdown("### 📊 Design Impact Analysis")
    
    impact = compute_impact(st.session_state.design)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delivery_status = "🟢" if impact["Delivery"] > 70 else "🟡" if impact["Delivery"] > 50 else "🔴"
        st.metric("🚀 Delivery Efficiency", f"{impact['Delivery']:.1f}%")
        st.caption(f"{delivery_status} {'Excellent' if impact['Delivery'] > 70 else 'Good' if impact['Delivery'] > 50 else 'Needs Improvement'}")
    
    with col2:
        toxicity_status = "🟢" if impact["Toxicity"] < 3 else "🟡" if impact["Toxicity"] < 6 else "🔴"
        st.metric("☣️ Toxicity Index", f"{impact['Toxicity']:.2f}/10")
        st.caption(f"{toxicity_status} {'Low' if impact['Toxicity'] < 3 else 'Moderate' if impact['Toxicity'] < 6 else 'High'} Risk")
    
    with col3:
        cost_status = "🟢" if impact["Cost"] < 30 else "🟡" if impact["Cost"] < 60 else "🔴"
        st.metric("💰 Cost Index", f"{impact['Cost']:.1f}")
        st.caption(f"{cost_status} {'Low' if impact['Cost'] < 30 else 'Moderate' if impact['Cost'] < 60 else 'High'} Cost")
    
    with col4:
        overall_score = max(0, min(100,
            (impact["Delivery"] * 0.6) +
            ((10 - impact["Toxicity"]) * 3) +
            ((100 - impact["Cost"]) * 0.1)
        ))
        overall_status = "🟢" if overall_score > 70 else "🟡" if overall_score > 50 else "🔴"
        st.metric("🧠 Overall Score", f"{overall_score:.1f}%")
        st.caption(f"{overall_status} {'Excellent' if overall_score > 70 else 'Good' if overall_score > 50 else 'Needs Improvement'}")
    
    # Parameter optimization recommendations
    st.markdown("### 💡 Optimization Recommendations")
    recommendations = get_recommendations(st.session_state.design)
    
    for rec in recommendations:
        st.write(rec)
    
    # Save design to history
    if st.button("💾 Save Current Design", use_container_width=True):
        st.session_state.design_history.append({
            "timestamp": datetime.now(),
            "design": dict(st.session_state.design),
            "impact": impact,
            "overall_score": overall_score
        })
        st.success("✅ Design saved to history!")
    
    # Design history
    if st.session_state.design_history:
        st.markdown("### 📚 Design History")
        
        history_df = pd.DataFrame([
            {
                "Timestamp": entry["timestamp"].strftime("%Y-%m-%d %H:%M"),
                "Size": entry["design"]["Size"],
                "Charge": entry["design"]["Charge"],
                "Encapsulation": entry["design"]["Encapsulation"],
                "Delivery": entry["impact"]["Delivery"],
                "Toxicity": entry["impact"]["Toxicity"],
                "Overall": entry["overall_score"]
            }
            for entry in st.session_state.design_history[-5:]  # Show last 5 designs
        ])
        
        st.dataframe(history_df, use_container_width=True)
        
        # Load previous design
        if len(st.session_state.design_history) > 0:
            selected_design = st.selectbox(
                "Load previous design:",
                range(len(st.session_state.design_history)),
                format_func=lambda x: f"Design {x+1} - {st.session_state.design_history[x]['timestamp'].strftime('%H:%M')}"
            )
            
            if st.button("📂 Load Selected Design"):
                st.session_state.design.update(st.session_state.design_history[selected_design]["design"])
                st.success("✅ Design loaded!")
                st.rerun()

# ============================================================
# 📈 DELIVERY SIMULATION MODULE
# ============================================================
elif mode == "📈 Delivery":
    st.header("📈 Delivery Simulation & Prediction")
    
    st.markdown("""
    ### 🎯 Simulate Nanoparticle Delivery Efficiency
    Predict how your nanoparticle design will perform in biological systems.
    """)
    
    # Delivery simulation parameters
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 🧬 Biological Environment")
        
        env_col1, env_col2 = st.columns(2)
        
        with env_col1:
            blood_flow = st.select_slider(
                "Blood Flow Rate",
                options=["Low", "Normal", "High"],
                value="Normal"
            )
            
            tissue_type = st.selectbox(
                "Target Tissue Type",
                ["Liver", "Tumor", "Brain", "Lung", "Kidney", "Spleen"]
            )
        
        with env_col2:
            immune_activity = st.select_slider(
                "Immune System Activity",
                options=["Low", "Normal", "High", "Autoimmune"],
                value="Normal"
            )
            
            clearance_rate = st.select_slider(
                "Clearance Rate",
                options=["Slow", "Normal", "Fast"],
                value="Normal"
            )
    
    with col2:
        st.markdown("#### 📊 Current Design")
        impact = compute_impact(st.session_state.design)
        
        st.metric("Size", f"{st.session_state.design['Size']}nm")
        st.metric("Charge", f"{st.session_state.design['Charge']}mV")
        st.metric("Encapsulation", f"{st.session_state.design['Encapsulation']}%")
        
        delivery_status = "🟢" if impact["Delivery"] > 70 else "🟡" if impact["Delivery"] > 50 else "🔴"
        st.metric("Predicted Delivery", f"{impact['Delivery']:.1f}%")
        st.caption(f"{delivery_status} {'Excellent' if impact['Delivery'] > 70 else 'Good' if impact['Delivery'] > 50 else 'Needs Improvement'}")
    
    # Run simulation
    if st.button("🚀 Run Delivery Simulation", type="primary", use_container_width=True):
        with st.spinner("Simulating nanoparticle delivery..."):
            # Simulate delivery process
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            steps = [
                "Injecting nanoparticles...",
                "Circulating in bloodstream...",
                "Avoiding immune clearance...",
                "Extravasating to target tissue...",
                "Binding to target cells...",
                "Internalizing into cells..."
            ]
            
            for i, step in enumerate(steps):
                progress_bar.progress((i + 1) * 16)
                status_text.text(f"🔄 {step}")
                # Simulate processing time
                import time
                time.sleep(0.5)
            
            progress_bar.progress(100)
            status_text.text("✅ Simulation complete!")
            
            # Calculate enhanced delivery score based on environment
            base_delivery = impact["Delivery"]
            env_factors = {
                "blood_flow": {"Low": 0.8, "Normal": 1.0, "High": 1.2},
                "immune_activity": {"Low": 1.2, "Normal": 1.0, "High": 0.7, "Autoimmune": 0.5},
                "clearance_rate": {"Slow": 1.3, "Normal": 1.0, "Fast": 0.6}
            }
            
            tissue_factors = {
                "Liver": 1.3, "Tumor": 1.1, "Brain": 0.4, "Lung": 1.0, "Kidney": 0.8, "Spleen": 0.9
            }
            
            enhanced_delivery = base_delivery
            enhanced_delivery *= env_factors["blood_flow"][blood_flow]
            enhanced_delivery *= env_factors["immune_activity"][immune_activity]
            enhanced_delivery *= env_factors["clearance_rate"][clearance_rate]
            enhanced_delivery *= tissue_factors[tissue_type]
            enhanced_delivery = min(100, enhanced_delivery)
            
            st.session_state.simulation_results = {
                "base_delivery": base_delivery,
                "enhanced_delivery": enhanced_delivery,
                "environment_factors": {
                    "blood_flow": blood_flow,
                    "immune_activity": immune_activity,
                    "clearance_rate": clearance_rate,
                    "tissue_type": tissue_type
                }
            }
    
    # Display simulation results
    if "simulation_results" in st.session_state:
        results = st.session_state.simulation_results
        
        st.markdown("---")
        st.markdown("### 📊 Simulation Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Theoretical Delivery", 
                f"{results['base_delivery']:.1f}%",
                delta=f"{results['enhanced_delivery'] - results['base_delivery']:+.1f}%",
                delta_color="normal"
            )
            
            # Environment impact factors
            st.markdown("#### 🌡️ Environmental Impact")
            env = results['environment_factors']
            
            factors_df = pd.DataFrame({
                "Factor": ["Blood Flow", "Immune Activity", "Clearance Rate", "Tissue Type"],
                "Value": [env['blood_flow'], env['immune_activity'], env['clearance_rate'], env['tissue_type']],
                "Impact": ["+" if x in ["High", "Slow"] else "-" if x in ["Low", "Fast", "Autoimmune"] else "○" 
                          for x in [env['blood_flow'], env['immune_activity'], env['clearance_rate'], "N/A"]]
            })
            
            st.dataframe(factors_df, use_container_width=True, hide_index=True)
        
        with col2:
            enhanced_status = "🟢" if results['enhanced_delivery'] > 70 else "🟡" if results['enhanced_delivery'] > 50 else "🔴"
            st.metric("Predicted Actual Delivery", f"{results['enhanced_delivery']:.1f}%")
            st.caption(f"{enhanced_status} {'Excellent' if results['enhanced_delivery'] > 70 else 'Good' if results['enhanced_delivery'] > 50 else 'Needs Improvement'}")
            
            # Delivery efficiency gauge
            show_circular_dial(results['enhanced_delivery'], "Predicted Delivery Efficiency")
        
        # Optimization suggestions for delivery
        st.markdown("### 💡 Delivery Optimization Tips")
        
        if results['enhanced_delivery'] < 60:
            st.error("""
            **Delivery efficiency is low. Consider:**
            - Increasing nanoparticle size to 80-120nm for better circulation
            - Adding PEG coating to reduce immune clearance
            - Optimizing surface charge to ±10mV
            - Using active targeting ligands
            """)
        elif results['enhanced_delivery'] < 80:
            st.warning("""
            **Good delivery efficiency. Could be improved by:**
            - Fine-tuning surface properties
            - Adding targeting moieties
            - Optimizing injection protocol
            - Considering different administration routes
            """)
        else:
            st.success("""
            **Excellent delivery efficiency!**
            - Your nanoparticle design is well-optimized for the selected environment
            - Consider moving to in vitro validation
            """)

# ============================================================
# ☣️ TOXICITY & SAFETY MODULE
# ============================================================
elif mode == "☣️ Toxicity":
    st.header("☣️ Toxicity & Safety Assessment")
    
    st.markdown("""
    ### ⚠️ Comprehensive Toxicity Analysis
    Evaluate potential toxicity risks and safety profile of your nanoparticle design.
    """)
    
    # Toxicity assessment
    impact = compute_impact(st.session_state.design)
    toxicity_score = impact["Toxicity"]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 🧪 Toxicity Risk Assessment")
        
        # Toxicity indicators
        tox_col1, tox_col2, tox_col3 = st.columns(3)
        
        with tox_col1:
            if toxicity_score <= 3:
                st.success("🟢 Low Toxicity")
                st.metric("Risk Level", "LOW")
            elif toxicity_score <= 6:
                st.warning("🟡 Moderate Toxicity")
                st.metric("Risk Level", "MEDIUM")
            else:
                st.error("🔴 High Toxicity")
                st.metric("Risk Level", "HIGH")
        
        with tox_col2:
            charge_risk = "HIGH" if abs(st.session_state.design["Charge"]) > 20 else "MEDIUM" if abs(st.session_state.design["Charge"]) > 10 else "LOW"
            st.metric("Charge Risk", charge_risk)
        
        with tox_col3:
            size_risk = "HIGH" if st.session_state.design["Size"] > 200 or st.session_state.design["Size"] < 50 else "LOW"
            st.metric("Size Risk", size_risk)
        
        # Toxicity factors breakdown
        st.markdown("#### 📋 Toxicity Factors")
        
        factors = {
            "Surface Charge": f"{abs(st.session_state.design['Charge'])}mV (High charge = higher toxicity)",
            "Particle Size": f"{st.session_state.design['Size']}nm (Extreme sizes increase toxicity)",
            "Material Type": f"{st.session_state.design['Material']} (Some materials are more biocompatible)",
            "PDI": f"{st.session_state.design['PDI']} (Higher PDI = more heterogeneous = potential toxicity)",
            "Degradation Time": f"{st.session_state.design['DegradationTime']} days (Very slow degradation can cause accumulation)"
        }
        
        for factor, value in factors.items():
            st.write(f"• **{factor}:** {value}")
    
    with col2:
        st.markdown("#### 📊 Toxicity Score")
        show_circular_dial(max(0, 100 - toxicity_score * 10), "Safety Score")
        
        toxicity_status = "🟢" if toxicity_score < 3 else "🟡" if toxicity_score < 6 else "🔴"
        st.metric("Toxicity Index", f"{toxicity_score:.2f}/10")
        st.caption(f"{toxicity_status} {'Low' if toxicity_score < 3 else 'Moderate' if toxicity_score < 6 else 'High'} Risk")
        
        # Quick safety check
        st.markdown("#### ✅ Safety Checklist")
        
        safety_items = {
            "Charge within ±20mV": abs(st.session_state.design["Charge"]) <= 20,
            "Size 50-200nm": 50 <= st.session_state.design["Size"] <= 200,
            "PDI < 0.3": st.session_state.design["PDI"] < 0.3,
            "Biocompatible material": st.session_state.design["Material"] in ["Lipid NP", "PLGA"],
            "Reasonable degradation": st.session_state.design["DegradationTime"] <= 90
        }
        
        passed = sum(safety_items.values())
        total = len(safety_items)
        
        for item, status in safety_items.items():
            if status:
                st.success(f"✅ {item}")
            else:
                st.error(f"❌ {item}")
        
        st.metric("Safety Compliance", f"{passed}/{total}")
    
    # Toxicity mitigation strategies
    st.markdown("---")
    st.markdown("### 🛡️ Toxicity Mitigation Strategies")
    
    mitigation_col1, mitigation_col2 = st.columns(2)
    
    with mitigation_col1:
        st.markdown("#### 🔧 Immediate Improvements")
        
        if abs(st.session_state.design["Charge"]) > 15:
            st.write("• **Reduce surface charge** to ±10mV range")
            st.write("• **Add PEG coating** to shield charge")
        
        if st.session_state.design["Size"] > 200:
            st.write("• **Reduce particle size** to 80-120nm range")
        
        if st.session_state.design["PDI"] > 0.2:
            st.write("• **Improve synthesis** to reduce PDI < 0.15")
        
        if st.session_state.design["Material"] not in ["Lipid NP", "PLGA"]:
            st.write("• **Consider switching** to Lipid NP or PLGA for better biocompatibility")
    
    with mitigation_col2:
        st.markdown("#### 🎯 Advanced Strategies")
        
        st.write("• **Surface functionalization** with biocompatible polymers")
        st.write("• **Core-shell structures** to isolate toxic components")
        st.write("• **Targeted delivery** to reduce off-target effects")
        st.write("• **Stimuli-responsive release** to control drug release")
        st.write("• **Biodegradable materials** to prevent accumulation")
    
    # Regulatory considerations
    st.markdown("---")
    st.markdown("### 📋 Regulatory Considerations")
    
    reg_col1, reg_col2 = st.columns(2)
    
    with reg_col1:
        st.markdown("#### 🇺🇸 FDA Requirements")
        fda_checklist = {
            "Size characterization": True,
            "Surface charge analysis": True,
            "Sterility testing": toxicity_score < 8,
            "Pyrogenicity testing": True,
            "In vitro toxicity": toxicity_score < 7,
            "In vivo toxicity (animal)": toxicity_score < 5,
            "Biodistribution studies": True
        }
        
        for item, status in fda_checklist.items():
            if status:
                st.success(f"✅ {item}")
            else:
                st.error(f"❌ {item}")
    
    with reg_col2:
        st.markdown("#### 🇪🇺 EMA Requirements")
        ema_checklist = {
            "Environmental risk assessment": True,
            "Genotoxicity testing": toxicity_score < 6,
            "Immunotoxicity assessment": True,
            "Repeat dose toxicity": toxicity_score < 4,
            "Reproductive toxicity": toxicity_score < 3,
            "Carcinogenicity potential": toxicity_score < 2
        }
        
        for item, status in ema_checklist.items():
            if status:
                st.success(f"✅ {item}")
            else:
                st.error(f"❌ {item}")

# ============================================================
# 💰 COST ESTIMATOR MODULE
# ============================================================
elif mode == "💰 Cost":
    st.header("💰 Cost Estimation & Optimization")
    
    st.markdown("""
    ### 💸 Nanoparticle Manufacturing Cost Analysis
    Estimate production costs and identify optimization opportunities.
    """)
    
    # Cost calculation
    impact = compute_impact(st.session_state.design)
    cost_score = impact["Cost"]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 📊 Cost Breakdown")
        
        # Cost components
        material_costs = {
            "Lipid NP": 50,
            "PLGA": 75,
            "Gold NP": 200,
            "Silica NP": 60,
            "DNA Origami": 500,
            "MOF-303": 150
        }
        
        base_material_cost = material_costs.get(st.session_state.design["Material"], 100)
        
        # Calculate various cost components
        encapsulation_cost = (100 - st.session_state.design["Encapsulation"]) * 2
        size_cost = st.session_state.design["Size"] * 0.5
        pdi_cost = (0.2 - min(st.session_state.design["PDI"], 0.2)) * 200
        surface_area_cost = st.session_state.design["SurfaceArea"] * 0.1
        
        total_estimated_cost = base_material_cost + encapsulation_cost + size_cost + pdi_cost + surface_area_cost
        
        # Display cost breakdown
        cost_data = {
            "Component": ["Base Material", "Encapsulation Loss", "Size Complexity", "PDI Control", "Surface Area"],
            "Cost ($/g)": [base_material_cost, encapsulation_cost, size_cost, pdi_cost, surface_area_cost],
            "Percentage": [
                base_material_cost/total_estimated_cost*100,
                encapsulation_cost/total_estimated_cost*100,
                size_cost/total_estimated_cost*100,
                pdi_cost/total_estimated_cost*100,
                surface_area_cost/total_estimated_cost*100
            ]
        }
        
        cost_df = pd.DataFrame(cost_data)
        st.dataframe(cost_df, use_container_width=True)
        
        # Cost visualization
        fig = px.pie(
            cost_df, 
            values='Cost ($/g)', 
            names='Component',
            title="Cost Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 💰 Cost Summary")
        
        cost_status = "🟢" if total_estimated_cost < 100 else "🟡" if total_estimated_cost < 200 else "🔴"
        st.metric("Estimated Cost", f"${total_estimated_cost:.0f}/g")
        st.caption(f"{cost_status} {'Low' if total_estimated_cost < 100 else 'Moderate' if total_estimated_cost < 200 else 'High'} Cost")
        
        st.metric("Cost Efficiency Score", f"{100 - cost_score:.0f}/100")
        
        # Cost comparison
        st.markdown("#### 📈 Cost Benchmarks")
        
        benchmarks = {
            "Lipid NP (typical)": "$50-100/g",
            "PLGA nanoparticles": "$70-150/g",
            "Gold nanoparticles": "$150-300/g",
            "Commercial liposomes": "$100-200/g",
            "Your design": f"${total_estimated_cost:.0f}/g"
        }
        
        for item, cost in benchmarks.items():
            st.write(f"• **{item}:** {cost}")
        
        # Cost optimization rating
        cost_rating = "HIGH" if total_estimated_cost > 200 else "MEDIUM" if total_estimated_cost > 100 else "LOW"
        st.metric("Cost Optimization Need", cost_rating)
    
    # Cost optimization strategies
    st.markdown("---")
    st.markdown("### 💡 Cost Optimization Strategies")
    
    opt_col1, opt_col2 = st.columns(2)
    
    with opt_col1:
        st.markdown("#### 🔧 Immediate Cost Reductions")
        
        if st.session_state.design["Encapsulation"] < 80:
            st.write(f"• **Improve encapsulation** from {st.session_state.design['Encapsulation']}% to >85%")
            st.write("  - Potential savings: 20-30%")
        
        if st.session_state.design["PDI"] < 0.1:
            st.write("• **Relax PDI requirements** to 0.15-0.2")
            st.write("  - Potential savings: 15-25%")
        
        if st.session_state.design["SurfaceArea"] > 400:
            st.write("• **Optimize surface area** to 200-300 m²/g")
            st.write("  - Potential savings: 10-20%")
        
        if st.session_state.design["Material"] in ["Gold NP", "DNA Origami"]:
            st.write("• **Consider alternative materials** like Lipid NP or PLGA")
            st.write("  - Potential savings: 50-80%")
    
    with opt_col2:
        st.markdown("#### 🏭 Manufacturing Optimizations")
        
        st.write("• **Scale-up production** (100g+ batches)")
        st.write("  - Economy of scale: 40-60% reduction")
        
        st.write("• **Automate synthesis processes**")
        st.write("  - Labor reduction: 20-30%")
        
        st.write("• **Optimize purification methods**")
        st.write("  - Yield improvement: 15-25%")
        
        st.write("• **Bulk material purchasing**")
        st.write("  - Material cost reduction: 10-20%")
    
    # ROI Calculator
    st.markdown("---")
    st.markdown("### 📈 Return on Investment Calculator")
    
    roi_col1, roi_col2, roi_col3 = st.columns(3)
    
    with roi_col1:
        production_scale = st.selectbox(
            "Production Scale",
            ["Lab-scale (1-10g)", "Pilot-scale (10-100g)", "Commercial-scale (100g+)"],
            index=0
        )
    
    with roi_col2:
        market_price = st.number_input(
            "Expected Market Price ($/g)",
            min_value=100,
            max_value=10000,
            value=1000,
            step=100
        )
    
    with roi_col3:
        annual_demand = st.number_input(
            "Annual Demand (kg)",
            min_value=1,
            max_value=1000,
            value=10,
            step=1
        )
    
    # Calculate ROI
    scale_factors = {"Lab-scale (1-10g)": 1.0, "Pilot-scale (10-100g)": 0.7, "Commercial-scale (100g+)": 0.4}
    scaled_cost = total_estimated_cost * scale_factors[production_scale]
    
    annual_revenue = market_price * annual_demand * 1000  # Convert kg to g
    annual_cost = scaled_cost * annual_demand * 1000
    annual_profit = annual_revenue - annual_cost
    roi_percentage = (annual_profit / annual_cost) * 100 if annual_cost > 0 else 0
    
    st.metric("Estimated Production Cost", f"${scaled_cost:.0f}/g")
    st.metric("Annual Profit", f"${annual_profit:,.0f}")
    st.metric("ROI", f"{roi_percentage:.1f}%")

# ============================================================
# 🧾 PROTOCOL GENERATOR MODULE
# ============================================================
elif mode == "🧾 Protocol":
    st.header("🧾 Experimental Protocol Generator")
    
    st.markdown("""
    ### 🔬 Step-by-Step Synthesis Protocol
    Generate detailed experimental protocols for nanoparticle synthesis and characterization.
    """)
    
    # Protocol customization
    st.markdown("#### ⚙️ Protocol Parameters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        synthesis_method = st.selectbox(
            "Synthesis Method",
            ["Microfluidics", "Emulsion-solvent evaporation", "Nanoprecipitation", 
             "Thin-film hydration", "Sol-gel process", "Chemical reduction"]
        )
        
        scale = st.selectbox(
            "Reaction Scale",
            ["Small (10-100mg)", "Medium (100mg-1g)", "Large (1-10g)"]
        )
    
    with col2:
        purification_method = st.selectbox(
            "Purification Method",
            ["Dialysis", "Centrifugation", "Size exclusion chromatography", 
             "Ultrafiltration", "Precipitation"]
        )
        
        characterization_methods = st.multiselect(
            "Characterization Methods",
            ["DLS", "Zeta Potential", "TEM", "SEM", "HPLC", "UV-Vis", "FTIR", "XRD", "BET"],
            default=["DLS", "Zeta Potential", "TEM"]
        )
    
    with col3:
        quality_control = st.multiselect(
            "Quality Control Tests",
            ["Sterility", "Endotoxin", "pH", "Osmolality", "Stability", "Drug content"],
            default=["Sterility", "Stability", "Drug content"]
        )
        
        safety_precautions = st.multiselect(
            "Safety Precautions",
            ["Gloves", "Lab coat", "Safety glasses", "Fume hood", "Biosafety cabinet"],
            default=["Gloves", "Lab coat", "Safety glasses"]
        )
    
    # Generate protocol
    if st.button("🔄 Generate Protocol", type="primary", use_container_width=True):
        st.session_state.protocol_generated = True
    
    if st.session_state.get('protocol_generated', False):
        st.markdown("---")
        st.markdown("### 📄 Generated Protocol")
        
        # Protocol sections
        with st.expander("🧪 Materials and Reagents", expanded=True):
            st.markdown("""
            **Required Materials:**
            - Core material: {}
            - Solvents: Appropriate for {} synthesis
            - Surfactants/Stabilizers: As needed
            - Purification reagents: For {} method
            - Characterization standards: Reference materials
            """.format(st.session_state.design["Material"], synthesis_method, purification_method))
        
        with st.expander("🔧 Synthesis Procedure", expanded=True):
            st.markdown(f"""
            **{synthesis_method} Synthesis - {scale} Scale**
            
            1. **Preparation:**
               - Clean all glassware and equipment
               - Prepare reagent solutions at required concentrations
               - Set up synthesis apparatus
            
            2. **Synthesis Steps:**
               - Mix core materials in appropriate solvent
               - Add stabilizers/surfactants gradually
               - Control temperature and mixing speed
               - Monitor reaction progress
            
            3. **Formation:**
               - Allow nanoparticle self-assembly
               - Control size using method parameters
               - Verify formation visually/turbidity
            
            **Critical Parameters:**
            - Temperature: 25-37°C
            - Mixing speed: 500-2000 RPM
            - Reaction time: 1-4 hours
            - pH: 7.0-7.4
            """)
        
        with st.expander("🧼 Purification Steps", expanded=False):
            st.markdown(f"""
            **{purification_method} Purification**
            
            1. **Initial Processing:**
               - Centrifuge at appropriate speed
               - Collect nanoparticle pellet/supernatant
               - Wash with appropriate buffer
            
            2. **Purification:**
               - Perform {purification_method.lower()} 
               - Monitor for aggregates
               - Collect purified fractions
            
            3. **Final Preparation:**
               - Concentrate to desired concentration
               - Filter sterilize if required
               - Aliquot and store appropriately
            """)
        
        with st.expander("🔍 Characterization Methods", expanded=False):
            st.markdown("""
            **Required Characterizations:**
            """)
            
            for method in characterization_methods:
                if method == "DLS":
                    st.write("- **Dynamic Light Scattering (DLS):** Size and PDI measurement")
                elif method == "Zeta Potential":
                    st.write("- **Zeta Potential:** Surface charge measurement")
                elif method == "TEM":
                    st.write("- **Transmission Electron Microscopy (TEM):** Morphology and size")
                elif method == "SEM":
                    st.write("- **Scanning Electron Microscopy (SEM):** Surface morphology")
                elif method == "HPLC":
                    st.write("- **High Performance Liquid Chromatography (HPLC):** Drug content and purity")
                elif method == "UV-Vis":
                    st.write("- **UV-Vis Spectroscopy:** Concentration and drug loading")
        
        with st.expander("⚖️ Quality Control", expanded=False):
            st.markdown("""
            **Quality Control Tests:**
            """)
            
            for test in quality_control:
                if test == "Sterility":
                    st.write("- **Sterility Testing:** Membrane filtration or direct inoculation")
                elif test == "Endotoxin":
                    st.write("- **Endotoxin Testing:** LAL assay")
                elif test == "pH":
                    st.write("- **pH Measurement:** 7.0-7.4 range")
                elif test == "Osmolality":
                    st.write("- **Osmolality:** 280-320 mOsm/kg")
                elif test == "Stability":
                    st.write("- **Stability Testing:** Size and charge stability over time")
                elif test == "Drug content":
                    st.write("- **Drug Content:** Encapsulation efficiency and loading capacity")
        
        with st.expander("⚠️ Safety Precautions", expanded=False):
            st.markdown("""
            **Required Safety Measures:**
            """)
            
            for precaution in safety_precautions:
                st.write(f"- **{precaution}:** Required for all steps")
            
            st.markdown("""
            **Additional Safety Notes:**
            - Work in well-ventilated areas
            - Dispose of waste properly
            - Follow institutional safety guidelines
            - Have emergency equipment accessible
            """)
        
        # Download protocol
        protocol_text = f"""
NANOPARTICLE SYNTHESIS PROTOCOL
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DESIGN PARAMETERS:
- Material: {st.session_state.design['Material']}
- Target Size: {st.session_state.design['Size']}nm
- Target Charge: {st.session_state.design['Charge']}mV
- Encapsulation: {st.session_state.design['Encapsulation']}%

SYNTHESIS METHOD: {synthesis_method}
SCALE: {scale}
PURIFICATION: {purification_method}

CHARACTERIZATION METHODS: {', '.join(characterization_methods)}
QUALITY CONTROL: {', '.join(quality_control)}
SAFETY PRECAUTIONS: {', '.join(safety_precautions)}

For detailed step-by-step instructions, refer to the expanded sections above.
        """
        
        st.download_button(
            label="📥 Download Protocol",
            data=protocol_text,
            file_name=f"nanoparticle_protocol_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

# ============================================================
# 🎯 KNOWLEDGE QUIZ MODULE
# ============================================================
elif mode == "🎯 Quiz":
    # Permission check
    if not has_permission(Permission.TAKE_QUIZ):
        st.error("❌ Access Denied: Quiz is not available for your role.")
        st.info(f"📋 Your current role ({get_user_role()}) does not have quiz access.")
        st.stop()
    
    st.header("🎯 NanoBio Knowledge Quiz")
    
    st.markdown("""
    ### 🧠 Test Your Nanoparticle Knowledge
    Challenge yourself with questions about nanoparticle design, characterization, and applications.
    """)
    
    # Quiz questions database
    quiz_questions = [
        {
            "question": "What is the optimal size range for most therapeutic nanoparticles?",
            "options": ["10-50nm", "80-120nm", "150-200nm", "200-300nm"],
            "correct": 1,
            "explanation": "80-120nm is optimal as it balances circulation time and cellular uptake efficiency."
        },
        {
            "question": "Which surface charge range is generally considered safest for nanoparticles?",
            "options": ["±50mV", "±30mV", "±10mV", "0mV"],
            "correct": 2,
            "explanation": "±10mV provides good stability with minimal toxicity risks."
        },
        {
            "question": "What does PDI stand for in nanoparticle characterization?",
            "options": ["Particle Distribution Index", "Polydispersity Index", "Polymer Density Indicator", "Particle Diameter Index"],
            "correct": 1,
            "explanation": "PDI stands for Polydispersity Index, which measures the uniformity of particle sizes."
        },
        {
            "question": "Which material is commonly used for mRNA vaccine delivery?",
            "options": ["Gold NP", "PLGA", "Lipid NP", "Silica NP"],
            "correct": 2,
            "explanation": "Lipid nanoparticles are the preferred delivery system for mRNA vaccines due to their biocompatibility and efficiency."
        },
        {
            "question": "What is the main advantage of active targeting in nanoparticles?",
            "options": ["Reduced cost", "Faster synthesis", "Specific cell delivery", "Longer shelf life"],
            "correct": 2,
            "explanation": "Active targeting uses ligands to specifically deliver nanoparticles to target cells, reducing off-target effects."
        }
    ]
    
    # Initialize quiz state
    if 'quiz_answers' not in st.session_state:
        st.session_state.quiz_answers = [None] * len(quiz_questions)
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    
    # Display quiz questions
    for i, q in enumerate(quiz_questions):
        st.markdown(f"#### Question {i+1}")
        st.write(f"**{q['question']}**")
        
        # Display options as buttons
        cols = st.columns(2)
        for j, option in enumerate(q['options']):
            col_idx = j % 2
            with cols[col_idx]:
                if st.button(
                    option,
                    key=f"q{i}_o{j}",
                    use_container_width=True,
                    disabled=st.session_state.quiz_submitted
                ):
                    st.session_state.quiz_answers[i] = j
        
        # Show selected answer and explanation if submitted
        if st.session_state.quiz_submitted and st.session_state.quiz_answers[i] is not None:
            if st.session_state.quiz_answers[i] == q['correct']:
                st.success(f"✅ Correct! {q['explanation']}")
            else:
                st.error(f"❌ Incorrect. {q['explanation']}")
    
    # Quiz controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Submit Quiz", use_container_width=True, disabled=st.session_state.quiz_submitted):
            st.session_state.quiz_submitted = True
            st.rerun()
    
    with col2:
        if st.button("🔄 Restart Quiz", use_container_width=True):
            st.session_state.quiz_answers = [None] * len(quiz_questions)
            st.session_state.quiz_submitted = False
            st.rerun()
    
    with col3:
        if st.button("📊 Show Results", use_container_width=True, disabled=not st.session_state.quiz_submitted):
            # Calculate score
            correct_answers = sum(
                1 for i, q in enumerate(quiz_questions)
                if st.session_state.quiz_answers[i] == q['correct']
            )
            total_questions = len(quiz_questions)
            score_percentage = (correct_answers / total_questions) * 100
            
            st.markdown("---")
            st.markdown("### 📊 Quiz Results")
            st.metric("Your Score", f"{score_percentage:.0f}%")
            st.metric("Correct Answers", f"{correct_answers}/{total_questions}")
            
            # Performance feedback
            if score_percentage >= 80:
                st.success("🎉 Excellent! You have a strong understanding of nanoparticle design principles.")
            elif score_percentage >= 60:
                st.warning("👍 Good job! You have a solid foundation in nanoparticle knowledge.")
            else:
                st.info("💡 Keep learning! Review the materials in other tabs to improve your understanding.")

# ============================================================
# 🔬 3D VIEW MODULE
# ============================================================
elif mode == "🔬 3D View":
    if PLOTLY_AVAILABLE:
        from tabs.view3d import render_3d_visualization
        render_3d_visualization()
    else:
        st.header("🔬 3D Nanoparticle Visualization")
        st.error("""
        ❌ **Plotly not available**
        
        To enable 3D visualization, install the required dependency:
        
        ```bash
        pip install plotly
        ```
        
        The 3D module will provide:
        - Interactive nanoparticle models
        - Real-time parameter visualization
        - Advanced 3D analysis tools
        - Size distribution analysis
        - Surface charge mapping
        - Composition breakdown
        """)

# ============================================================
# 🤖 AI OPTIMIZATION MODULE
# ============================================================
elif mode == "🤖 AI Optimize" and SKLEARN_AVAILABLE:
    # Permission check - AI is restricted to research and educators
    if not has_permission(Permission.ACCESS_AI):
        st.error("❌ Access Denied: AI Optimization is only available to Research and Educator roles.")
        st.info(f"📋 Your current role ({get_user_role()}) does not have access to AI features.")
        st.stop()
    
    st.header("🤖 AI-Powered Design Optimization")
    
    st.markdown("""
    ### 🧠 Machine Learning Optimization
    Use AI to analyze your current design and get data-driven suggestions for improvement.
    The model has been trained on thousands of nanoparticle designs to predict optimal parameters.
    """)
    
    # Initialize AI model if not already trained
    if st.session_state.ai_model is None:
        with st.spinner("🤖 Training AI model on nanoparticle data..."):
            train_ai_model()
        st.success("✅ AI model trained successfully!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎯 Optimization Target")
        target_metric = st.selectbox(
            "Select metric to optimize:",
            ["delivery", "toxicity", "cost", "overall"],
            format_func=lambda x: {
                "delivery": "🚀 Delivery Efficiency",
                "toxicity": "☣️ Toxicity Reduction", 
                "cost": "💰 Cost Optimization",
                "overall": "🧠 Overall Performance"
            }[x]
        )
        
        improvement_target = st.slider(
            "Target improvement (% points):",
            min_value=5,
            max_value=30,
            value=15,
            help="How much improvement do you want to achieve?"
        )
        
        if st.button("🚀 Get AI Optimization Suggestions", type="primary", use_container_width=True):
            with st.spinner("🤖 Analyzing your design and generating optimization strategies..."):
                suggestions = ai_design_suggestions(st.session_state.design, target_metric, improvement_target)
                
                st.session_state.ai_suggestions = suggestions
                
                # Store in history
                st.session_state.design_history.append({
                    "timestamp": datetime.now(),
                    "design": dict(st.session_state.design),
                    "ai_suggestions": suggestions,
                    "type": "ai_optimization"
                })
    
    with col2:
        st.markdown("### 📊 Current Performance")
        current_impact = compute_impact(st.session_state.design)
        
        metrics = {
            "🚀 Delivery": f"{current_impact['Delivery']:.1f}%",
            "☣️ Toxicity": f"{current_impact['Toxicity']:.1f}/10",
            "💰 Cost": f"{current_impact['Cost']:.1f}",
            "🧠 Overall": f"{overall_score:.1f}%"
        }
        
        for metric, value in metrics.items():
            st.metric(metric, value)
    
    # Display AI suggestions if available
    if "ai_suggestions" in st.session_state:
        suggestions = st.session_state.ai_suggestions
        
        st.markdown("---")
        st.markdown("### 💡 AI Optimization Recommendations")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Score", f"{suggestions['current_score']:.1f}")
        with col2:
            st.metric("Target Score", f"{suggestions['target_score']:.1f}")
        with col3:
            st.metric("AI Confidence", f"{suggestions['confidence']:.1%}")
        
        st.markdown("#### 🛠️ Specific Recommendations:")
        
        for i, suggestion in enumerate(suggestions["suggestions"], 1):
            st.write(f"{i}. {suggestion}")
        
        # Parameter sweep visualization
        st.markdown("#### 📈 Parameter Optimization Analysis")
        
        if st.button("🔍 Run Detailed Parameter Analysis", use_container_width=True):
            with st.spinner("Running parameter sweep analysis..."):
                best_params, best_score, improvements = perform_parameter_sweep(
                    st.session_state.design, target_metric
                )
                
                # Display optimization results
                st.success(f"🎯 Best achievable score: {best_score:.1f} (improvement of {best_score - suggestions['current_score']:.1f} points)")
                
                # Show parameter changes
                st.markdown("#### 📊 Recommended Parameter Changes:")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    delta_size = best_params['Size'] - st.session_state.design['Size']
                    st.metric("Size", f"{best_params['Size']:.1f}nm", f"{delta_size:+.1f}nm")
                
                with col2:
                    delta_charge = best_params['Charge'] - st.session_state.design['Charge']
                    st.metric("Charge", f"{best_params['Charge']:.1f}mV", f"{delta_charge:+.1f}mV")
                
                with col3:
                    delta_encap = best_params['Encapsulation'] - st.session_state.design['Encapsulation']
                    st.metric("Encapsulation", f"{best_params['Encapsulation']:.1f}%", f"{delta_encap:+.1f}%")
                
                with col4:
                    delta_pdi = best_params['PDI'] - st.session_state.design['PDI']
                    st.metric("PDI", f"{best_params['PDI']:.3f}", f"{delta_pdi:+.3f}")
                
                # Apply optimized parameters
                if st.button("✅ Apply Optimized Parameters", type="primary", use_container_width=True):
                    st.session_state.design.update({
                        'Size': best_params['Size'],
                        'Charge': best_params['Charge'],
                        'Encapsulation': best_params['Encapsulation'],
                        'PDI': best_params['PDI']
                    })
                    st.success("✅ Optimized parameters applied! Check the impact in the sidebar.")
                    st.rerun()
        
        # Advanced AI features
        st.markdown("---")
        st.markdown("### 🔬 Advanced AI Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧪 Multi-Objective Optimization", use_container_width=True):
                st.info("""
                **Multi-Objective Optimization** would balance:
                - Delivery efficiency vs toxicity
                - Performance vs cost
                - Short-term vs long-term effects
                
                *Advanced feature - requires multi-objective optimization algorithms*
                """)
        
        with col2:
            if st.button("📚 Learn from Design History", use_container_width=True):
                st.info("""
                **Learning from History** would:
                - Analyze your previous designs
                - Identify successful patterns
                - Suggest improvements based on your workflow
                
                *Advanced feature - requires historical data analysis*
                """)
    
    # Educational section
    with st.expander("🎓 How AI Optimization Works"):
        st.markdown("""
        **Machine Learning Approach:**
        
        1. **Training Data**: Model trained on 1,000+ synthetic nanoparticle designs
        2. **Feature Engineering**: Parameters like size, charge, encapsulation, material properties
        3. **Random Forest Algorithm**: Ensemble method that captures complex relationships
        4. **Optimization Strategy**: Parameter sweeps and gradient-free optimization
        
        **What the AI Considers:**
        - Physical constraints (size limits, charge interactions)
        - Biological factors (cellular uptake, toxicity mechanisms)
        - Manufacturing constraints (cost, complexity)
        - Multi-parameter trade-offs
        
        **Limitations:**
        - Based on synthetic data (real experimental data would improve accuracy)
        - Simplified physical models
        - Doesn't account for all biological complexities
        """)

elif mode == "🤖 AI Optimize" and not SKLEARN_AVAILABLE:
    st.header("🤖 AI-Powered Design Optimization")
    st.error("""
    ❌ **scikit-learn not available**
    
    To enable AI optimization, install the required dependencies:
    
    ```bash
    pip install scikit-learn plotly
    ```
    
    The AI module will provide:
    - Machine learning-based parameter optimization
    - Data-driven design suggestions
    - Performance prediction
    - Multi-objective optimization
    """)

# ============================================================
# 📊 DESIGN HISTORY & PROJECT DASHBOARD
# ============================================================

elif mode == "📊 History":
    from design_history import render_project_dashboard
    
    username = st.session_state.get("username", "guest")
    render_project_dashboard(username)

# ============================================================
# ⚙️ ADMIN PANEL (Full Page)
# ============================================================

elif mode == "⚙️ Admin":
    # Check if user is admin
    user_role = get_user_role()
    if user_role != Role.ADMIN:
        st.error("❌ Admin access required. This page is only available to administrators.")
        st.stop()
    
    st.header("⚙️ Admin Panel")
    st.markdown("Manage users, reset passwords, and administer the system.")
    
    # Create tabs for admin functions
    admin_tab1, admin_tab2, admin_tab3, admin_tab4, admin_tab5, admin_tab6 = st.tabs(
        ["👥 Manage Users", "➕ Create User", "🔐 Reset Password", "👤 My Account", "📋 Activity Log", "🔐 Audit Dashboard"]
    )
    
    # ============================================================
    # Tab 1: Manage Users
    # ============================================================
    with admin_tab1:
        st.subheader("👥 Manage Users")
        try:
            users = list_users_detailed()
            if users:
                st.write(f"**Total users:** {len(users)}")
                
                # Display users table
                user_df = st.dataframe(
                    {
                        "Username": [u["username"] for u in users],
                        "Email": [u["email"] for u in users],
                        "Role": [u["role"] for u in users],
                        "Status": [u["status"] for u in users],
                        "Last Login": [u["last_login"] for u in users],
                    },
                    use_container_width=True
                )
                
                st.divider()
                
                # User action selector
                selected_user = st.selectbox(
                    "Select user",
                    [u["username"] for u in users],
                    key="user_action_select"
                )
                
                if selected_user:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Change role
                        st.write("**Change Role**")
                        current_role = auth_get_user_role(selected_user)
                        new_role = st.selectbox(
                            f"New role for {selected_user}",
                            ["admin", "research", "educator", "student", "viewer"],
                            index=["admin", "research", "educator", "student", "viewer"].index(current_role or "viewer"),
                            key="role_change_select"
                        )
                        if st.button("Update Role", key="update_role_btn", use_container_width=True):
                            if update_user_role(selected_user, new_role):
                                st.success(f"✅ {selected_user} → {new_role}")
                            else:
                                st.error("Failed to update role")
                    
                    with col2:
                        # Activate/Deactivate
                        user_info = get_user_info(selected_user)
                        if user_info:
                            if user_info["is_active"]:
                                if st.button("🔴 Deactivate", key="deactivate_btn", use_container_width=True):
                                    success, msg = deactivate_user(selected_user)
                                    if success:
                                        st.success(f"✅ {msg}")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {msg}")
                            else:
                                if st.button("🟢 Activate", key="activate_btn", use_container_width=True):
                                    success, msg = activate_user(selected_user)
                                    if success:
                                        st.success(f"✅ {msg}")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {msg}")
                    
                    with col3:
                        # Delete user
                        if st.button("🗑️ Delete", key="delete_user_btn", use_container_width=True):
                            if st.session_state.get("confirm_delete"):
                                from auth import delete_user
                                if delete_user(selected_user):
                                    st.success(f"✅ User {selected_user} deleted")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete user")
                            else:
                                st.warning("Click again to confirm deletion")
                                st.session_state.confirm_delete = True
            else:
                st.info("No users found")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # ============================================================
    # Tab 2: Create User
    # ============================================================
    with admin_tab2:
        st.subheader("➕ Create User")
        st.write("Create a new user account")
        
        with st.form("create_user_form"):
            create_username = st.text_input("Username", help="3-30 characters")
            create_email = st.text_input("Email (optional)", help="User's email address")
            create_password = st.text_input("Password", type="password", help="6+ characters with letters and numbers")
            create_role = st.selectbox("Role", ["student", "educator", "research", "admin"])
            
            if st.form_submit_button("Create User", use_container_width=True):
                success, msg = register_user(create_username, create_password, create_email, create_role)
                if success:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
    
    # ============================================================
    # Tab 3: Reset Password
    # ============================================================
    with admin_tab3:
        st.subheader("🔐 Reset Password")
        st.write("Reset a user's password")
        
        with st.form("reset_password_form"):
            reset_username = st.selectbox(
                "Select user",
                [u["username"] for u in list_users_detailed()],
                key="reset_user_select"
            )
            reset_password_new = st.text_input(
                "New Password",
                type="password",
                help="6+ characters with letters and numbers"
            )
            reset_password_confirm = st.text_input(
                "Confirm Password",
                type="password",
                help="Re-enter the password"
            )
            
            if st.form_submit_button("Reset Password", use_container_width=True):
                if reset_password_new != reset_password_confirm:
                    st.error("❌ Passwords do not match")
                else:
                    success, msg = reset_password(reset_username, reset_password_new)
                    if success:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")
    
    # ============================================================
    # Tab 4: My Account
    # ============================================================
    with admin_tab4:
        st.subheader("👤 My Account")
        st.write("Manage your admin account")
        
        # Show current user info
        current_user_info = get_user_info(st.session_state.username)
        if current_user_info:
            st.markdown("### Your Account Information")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Username:** {current_user_info['username']}")
                st.write(f"**Email:** {current_user_info['email']}")
                st.write(f"**Role:** {current_user_info['role']}")
            with col2:
                st.write(f"**Status:** {'Active' if current_user_info['is_active'] else 'Inactive'}")
                st.write(f"**Created:** {current_user_info['created_at'][:10]}")
                st.write(f"**Last Login:** {current_user_info['last_login'] or 'Never'}")
        
        st.divider()
        
        # Change password
        with st.form("change_password_form"):
            st.markdown("### Change Your Password")
            old_pwd = st.text_input("Current Password", type="password")
            new_pwd = st.text_input("New Password", type="password")
            new_pwd_confirm = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Change Password", use_container_width=True):
                if new_pwd != new_pwd_confirm:
                    st.error("❌ Passwords do not match")
                else:
                    success, msg = change_password(st.session_state.username, old_pwd, new_pwd)
                    if success:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")

    # ============================================================
    # Tab 5: Activity Log
    # ============================================================
    with admin_tab5:
        st.subheader("📋 Activity Log")
        st.write("View user activity and security audit trail")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            log_username_filter = st.selectbox(
                "Filter by user",
                ["All Users"] + [u["username"] for u in list_users_detailed()],
                key="log_username_filter"
            )
        with col2:
            log_limit = st.number_input("Show last N entries", min_value=10, max_value=500, value=50, step=10)
        
        # Get activity log
        username_filter = None if log_username_filter == "All Users" else log_username_filter
        activity_logs = get_activity_log(username_filter, limit=log_limit)
        
        if activity_logs:
            # Create a table of activity logs
            log_data = []
            for log in activity_logs:
                log_data.append({
                    "User": log["username"],
                    "Action": log["action"],
                    "Details": log["details"] or "—",
                    "Timestamp": log["timestamp"][:19] if log["timestamp"] else "—"
                })
            
            df_logs = pd.DataFrame(log_data)
            st.dataframe(df_logs, use_container_width=True, hide_index=True)
            
            # Download activity log as CSV
            csv_logs = df_logs.to_csv(index=False)
            st.download_button(
                label="📥 Download Activity Log (CSV)",
                data=csv_logs,
                file_name=f"activity_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No activity logs found")
        
        # Show security summary
        st.divider()
        st.markdown("### 🔒 Security Summary")
        
        all_logs = get_activity_log(None, limit=1000)
        if all_logs:
            # Count different action types
            action_counts = {}
            for log in all_logs:
                action = log["action"]
                action_counts[action] = action_counts.get(action, 0) + 1
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Activities", len(all_logs))
            
            with col2:
                logins = action_counts.get("LOGIN", 0)
                st.metric("Logins", logins)
            
            with col3:
                logouts = action_counts.get("LOGOUT", 0)
                st.metric("Logouts", logouts)
            
            with col4:
                password_changes = action_counts.get("PASSWORD_CHANGED", 0) + action_counts.get("PASSWORD_RESET", 0)
                st.metric("Password Changes", password_changes)

    # ============================================================
    # Tab 6: Comprehensive Audit Dashboard
    # ============================================================
    with admin_tab6:
        from audit_dashboard import render_audit_dashboard
        render_audit_dashboard()

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
---
<div style='text-align:center; font-size:0.85rem; color:gray;'>
<b>NanoBio Studio</b> — © 2025 Experts Group FZE  
<b>Email: info@expertsgroup.me</b><b>Mob: 00 971 50 6690381</b>
<br>Connecting Nanotechnology ⚛️ and Biotechnology 🧬 for Learning & Innovation
<br>Educational Tool for Nanoparticle Design and Optimization
</div>
""", unsafe_allow_html=True)