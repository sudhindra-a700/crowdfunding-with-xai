# frontend/haven_frontend.py

import streamlit as st
import os
import requests
import json # To parse JSON responses from backend
import random # For fallback IDs

# --- Configuration ---
# Load secrets from Environment Variables (injected by Cloud Run)
FIREBASE_SERVICE_ACCOUNT_KEY_JSON_BASE64 = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY_JSON_BASE64")
ALGOLIA_API_KEY = os.environ.get("ALGOLIA_API_KEY")
ALGOLIA_APP_ID = os.environ.get("ALGOLIA_APP_ID")
BREVO_API_KEY = os.environ.get("BREVO_API_KEY")
INSTAMOJO_API_KEY = os.environ.get("INSTAMOJO_API_KEY")
INSTAMOJO_AUTH_TOKEN = os.environ.get("INSTAMOJO_AUTH_TOKEN")

# Get the FastAPI backend URL from environment variable
# IMPORTANT: This will be set during Cloud Run deployment.
# For local testing, you might use "http://localhost:8000"
FASTAPI_BACKEND_URL = os.environ.get("FASTAPI_BACKEND_URL", "http://localhost:8000")

# --- Streamlit Page Configuration ---
st.set_page_config(layout="centered", page_title="HAVEN - Crowdfunding Platform")

# --- Custom CSS for Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');

    body {
        font-family: 'Inter', sans-serif;
        background-color: #f0f2f5;
        color: #333;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 20px;
        padding-right: 20px;
    }

    .stApp > header {
        display: none; /* Hide Streamlit header */
    }

    .main-layout-container {
        display: flex;
        max-width: 1200px;
        margin: 20px auto;
        gap: 20px;
        padding: 0px 0px;
    }

    .sidebar-container {
        width: 220px;
        background-color: #ffffff;
        padding: 20px 0;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        height: fit-content;
    }

    .sidebar-header {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: #2c3e50;
        padding: 0 20px;
        margin-bottom: 20px;
    }

    .sidebar-menu ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .sidebar-menu li {
        margin-bottom: 5px;
    }
    .sidebar-menu a {
        text-decoration: none;
        color: #333; /* Darker color for better visibility */
        display: flex;
        align-items: center;
        padding: 12px 20px;
        transition: background-color 0.2s ease, color 0.2s ease;
        font-size: 15px;
        font-weight: 500; /* Default font weight, will be overridden for specific items if needed */
    }
    /* Specific styling for Explore and Create Campaign to make them bold */
    .sidebar-menu a:not(.active) { /* Apply to non-active links */
        font-weight: bold; /* Make non-active items bold */
    }
    .sidebar-menu a i {
        margin-right: 10px;
        color: #555; /* Darker icon color */
    }
    .sidebar-menu a:hover {
        background-color: #e6e9ed;
        color: #1a1a1a;
    }
    .sidebar-menu a.active {
        background-color: #e0e6f0;
        color: #1a1a1a;
        font-weight: bold; /* Keep active item bold as it was */
        position: relative;
    }
    .sidebar-menu a.active::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background-color: #6a0dad;
        border-top-right-radius: 2px;
        border-bottom-right-radius: 2px;
    }
    .sidebar-user-profile {
        margin-top: 30px;
        text-align: center;
        padding: 20px;
        border-top: 1px solid #eee;
        color: #666;
        font-size: 13px;
    }
    .sidebar-user-profile p {
        margin: 5px 0;
    }
    .sidebar-user-profile p.user-name {
        font-weight: bold;
        color: #333;
    }

    .content-area-container {
        flex-grow: 1;
        padding-right: 0px;
        padding-left: 0px;
    }

    .top-content-area {
        background-color: #f8f8f8;
        padding: 30px 40px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 30px;
        text-align: center;
        position: relative; /* Needed for positioning the translate icon */
    }

    .translate-widget-container {
        position: absolute;
        top: 20px;
        left: 20px;
        z-index: 100;
    }

    .translate-icon {
        cursor: pointer;
        width: 40px;
        height: 40px;
    }

    .language-dropdown {
        display: none;
        position: absolute;
        top: 50px;
        left: 0;
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        padding: 5px 0;
        list-style: none;
        margin: 0;
        max-height: 300px;
        overflow-y: auto;
    }

    .language-dropdown li a {
        display: block;
        padding: 8px 15px;
        color: #333;
        text-decoration: none;
        font-size: 14px;
    }

    .language-dropdown li a:hover {
        background-color: #f0f2f5;
    }

    .main-logo-text {
        font-family: 'Playfair Display', serif;
        font-size: 3.5em;
        font-weight: bold;
        color: #333;
        margin-bottom: 10px;
        line-height: 1;
    }
    .main-logo-subtitle {
        font-size: 1.2em;
        color: #666;
        margin-bottom: 30px;
    }

    .stTextInput>div>div>input {
        padding: 14px 20px 14px 50px !important;
        border: 1px solid #ddd !important;
        border-radius: 30px !important;
        font-size: 1.05em !important;
        outline: none !important;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05) !important;
        background-color: #fff;
    }
    .stTextInput label {
        display: none;
    }
    div[data-testid="stTextInput"] {
        position: relative;
        width: 70%;
        max-width: 600px;
        margin: 0 auto;
    }
    div[data-testid="stTextInput"]::before {
        content: "\\f002";
        font-family: "Font Awesome 5 Free";
        font-weight: 900;
        position: absolute;
        left: 20px;
        top: 50%;
        transform: translateY(-50%);
        color: #999;
        font-size: 1.2em;
        z-index: 1;
    }

    .campaigns-section {
        background-color: #f8f8f8;
        padding: 30px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .campaigns-section h2 {
        font-size: 1.8em;
        color: #333;
        margin-bottom: 10px;
    }
    .campaigns-section .section-subtitle {
        font-size: 1em;
        color: #666;
        margin-bottom: 25px;
        border-bottom: 2px solid #eee;
        padding-bottom: 10px;
    }
    .campaign-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 25px;
    }
    .campaign-card {
        background-color: #fcfcfc;
        border: 1px solid #e5e5e5;
        border-radius: 10px;
        overflow: hidden;
        padding: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }
    .campaign-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .campaign-image-placeholder {
        width: 100%;
        height: 180px;
        background-color: #e0e0e0;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: flex-start;
        padding: 10px;
        color: #666;
        font-size: 1.3em;
        font-weight: bold;
        margin-bottom: 15px;
        border-radius: 5px;
        position: relative;
        box-sizing: border-box;
    }
    .campaign-image-placeholder img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .badge {
        position: absolute;
        top: 10px;
        right: 10px;
        background-color: rgba(0, 0, 0, 0.7);
        color: #fff;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8em;
        font-weight: normal;
        display: flex;
        align-items: center;
        z-index: 2;
    }
    .badge i {
        margin-right: 5px;
    }
    .campaign-image-placeholder .image-size {
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 0.9em;
        color: rgba(255, 255, 255, 0.8);
        background-color: rgba(0, 0, 0, 0.5);
        padding: 3px 8px;
        border-radius: 5px;
        z-index: 2;
    }
    .campaign-card h3 {
        font-size: 1.3em;
        color: #333;
        margin: 0 0 8px 0;
        text-align: left;
    }
    .campaign-card .campaign-description {
        font-size: 0.95em;
        color: #555;
        line-height: 1.5;
        margin-bottom: 15px;
        text-align: left;
        flex-grow: 1;
    }
    .campaign-card .campaign-author {
        font-size: 0.85em;
        color: #888;
        margin: 0;
        text-align: left;
    }
    .campaign-progress-container {
        width: 100%;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    .campaign-progress-bar {
        width: 100%;
        background-color: #e0e0e0;
        border-radius: 5px;
        height: 6px;
        overflow: hidden;
    }
    .campaign-progress-fill {
        height: 100%;
        background-color: #6a0dad;
        border-radius: 5px;
    }
    .campaign-stats {
        display: flex;
        justify-content: space-between;
        font-size: 0.9em;
        color: #555;
        margin-top: 8px;
    }
    .campaign-stats .amount-funded {
        font-weight: bold;
        color: #333;
    }

    .category-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 25px;
        justify-content: center;
    }
    .category-button {
        background-color: #fff;
        border: 1px solid #ddd;
        border-radius: 20px;
        padding: 8px 15px;
        font-size: 0.9em;
        color: #555;
        cursor: pointer;
        transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
    }
    .category-button:hover {
        background-color: #e6e9ed;
        border-color: #c0c4c8;
    }
    .category-button.active {
        background-color: #6a0dad;
        color: #fff;
        border-color: #6a0dad;
    }

    /* --- Campaign Detail Page Specific Styles --- */
    .campaign-detail-container {
        max-width: 900px;
        margin: 20px auto;
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        padding: 30px;
    }

    .detail-image {
        width: 100%;
        border-radius: 10px;
        margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }

    .detail-header {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: #2c3e50;
        margin-top: 0;
        margin-bottom: 15px;
        font-size: 2.2em;
    }

    .organization-detail-info {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 1.2em;
        color: #555;
        margin-bottom: 20px;
    }

    .fraud-indicator-dot {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        border: 1px solid rgba(0,0,0,0.1);
    }

    .fraud-green { background-color: #28a745; }
    .fraud-yellow { background-color: #ffc107; }
    .fraud-red { background-color: #dc3545; } /* This will now mean 'Rejected' */

    .detail-progress-container {
        width: 100%;
        background-color: #e0e0e0;
        border-radius: 8px;
        overflow: hidden;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    .detail-progress-bar {
        height: 25px;
        background-color: #4CAF50;
        text-align: center;
        color: white;
        line-height: 25px;
        border-radius: 8px;
        transition: width 0.5s ease-in-out;
        font-weight: 600;
    }

    .detail-stats {
        display: flex;
        justify-content: space-between;
        font-size: 1.1em;
        color: #666;
        margin-bottom: 30px;
    }

    .detail-button {
        background-color: #007bff;
        color: white;
        padding: 12px 25px;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-right: 15px;
    }
    .detail-button:hover {
        background-color: #0056b3;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }

    .donate-input-box {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 25px;
        margin-top: 30px;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
    }

    .section-title {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 40px;
        margin-bottom: 20px;
        border-bottom: 2px solid #eee;
        padding-bottom: 8px;
        font-size: 1.6em;
    }

    .donator-list {
        list-style: none;
        padding: 0;
    }
    .donator-list li {
        background-color: #f5f5f5;
        padding: 12px 15px;
        border-radius: 6px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 1.05em;
        color: #444;
    }
    .donator-list li strong {
        color: #2c3e50;
    }

    .review-item {
        background-color: #f5f5f5;
        padding: 18px;
        border-radius: 8px;
        margin-bottom: 15px;
        border-left: 5px solid #a8dadc;
    }
    .review-author {
        font-weight: 700;
        color: #333;
        margin-bottom: 5px;
    }
    .review-text {
        font-style: italic;
        color: #555;
        line-height: 1.6;
    }

    .fraud-explanation-detail-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 10px;
        padding: 20px;
        margin-top: 30px;
        color: #856404;
        font-size: 1em;
        line-height: 1.6;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    .fraud-explanation-detail-box.red {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
    }
    .fraud-explanation-detail-box.yellow {
        background-color: #fff3cd;
        border-color: #ffeeba;
        color: #856404;
    }
    .fraud-explanation-detail-box.green {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
    }
    .fraud-explanation-detail-box ul {
        margin-top: 10px;
        padding-left: 20px;
    }
    .fraud-explanation-detail-box li {
        margin-bottom: 5px;
    }

    .stTextInput label, .stNumberInput label {
        font-weight: 600;
        color: #333;
    }

    /* --- Payment Page Specific Styles --- */
    .payment-container {
        max-width: 1000px;
        margin: 20px auto;
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        padding: 30px;
        display: flex;
        gap: 30px;
        flex-wrap: wrap; /* Allow wrapping on smaller screens */
    }

    .payment-left-col {
        flex: 2;
        min-width: 300px; /* Ensure it doesn't get too small */
    }

    .payment-right-col {
        flex: 1;
        min-width: 250px; /* Ensure it doesn't get too small */
        background-color: #f9f9f9;
        padding: 25px;
        border-radius: 10px;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
    }

    .payment-header {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: #2c3e50;
        margin-top: 0;
        margin-bottom: 25px;
        font-size: 2em;
    }

    .payment-section-title {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 30px;
        margin-bottom: 15px;
        border-bottom: 1px solid #eee;
        padding-bottom: 8px;
        font-size: 1.4em;
    }

    .payment-method-option {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        padding: 15px;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .payment-method-option:hover {
        border-color: #007bff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .payment-method-option.selected {
        border-color: #6a0dad;
        box-shadow: 0 0 0 2px #6a0dad;
    }

    .payment-method-option input[type="radio"] {
        margin-right: 15px;
        transform: scale(1.2);
    }

    .payment-method-option .method-details {
        flex-grow: 1;
    }
    .payment-method-option .method-details h4 {
        margin: 0 0 5px 0;
        color: #333;
        font-size: 1.1em;
    }
    .payment-method-option .method-details p {
        margin: 0;
        font-size: 0.9em;
        color: #666;
    }
    .payment-method-option .method-icons {
        display: flex;
        gap: 8px;
    }
    .payment-method-option .method-icons img {
        height: 25px;
        width: auto;
    }

    .order-summary-box {
        padding: 20px;
        border-radius: 8px;
        background-color: #fff;
        border: 1px solid #eee;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .order-summary-box h3 {
        margin-top: 0;
        color: #2c3e50;
        font-size: 1.5em;
        margin-bottom: 20px;
    }
    .order-summary-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
        font-size: 1em;
        color: #555;
    }
    .order-summary-total {
        font-size: 1.4em;
        font-weight: 700;
        color: #333;
        border-top: 1px solid #eee;
        padding-top: 15px;
        margin-top: 15px;
    }

    .pay-button {
        background-color: #6a0dad; /* Purple color from Udemy image */
        color: white;
        padding: 15px 30px;
        border-radius: 8px;
        border: none;
        font-weight: 700;
        cursor: pointer;
        width: 100%;
        font-size: 1.2em;
        transition: background-color 0.2s ease, transform 0.2s ease;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        margin-top: 25px;
    }
    .pay-button:hover {
        background-color: #5a0c9d;
        transform: translateY(-2px);
    }
    .pay-button:active {
        transform: translateY(0);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }

    .money-back-guarantee {
        text-align: center;
        font-size: 0.9em;
        color: #777;
        margin-top: 20px;
    }
    .money-back-guarantee i {
        margin-right: 5px;
        color: #28a745;
    }

    /* --- Term Simplification Styles --- */
    .highlight-legal { color: #28a745; font-weight: bold; position: relative; cursor: help; } /* Green */
    .highlight-financial { color: #007bff; font-weight: bold; position: relative; cursor: help; } /* Blue */
    .highlight-tech { color: #6f42c1; font-weight: bold; position: relative; cursor: help; } /* Purple */
    .highlight-social { color: #fd7e14; font-weight: bold; position: relative; cursor: help; } /* Orange */
    .highlight-marketing { color: #d63384; font-weight: bold; position: relative; cursor: help; } /* Pink */
    .highlight-general { color: #20c997; font-weight: bold; position: relative; cursor: help; } /* Teal */


    .tooltip-box {
        visibility: hidden;
        width: 250px;
        background-color: white;
        color: #333;
        text-align: left;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1000;
        bottom: 125%; /* Position above the text */
        left: 50%;
        margin-left: -125px; /* Center the tooltip */
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.85em;
        line-height: 1.4;
        border: 1px solid #ddd;
    }

    .tooltip-box::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #ddd transparent transparent transparent;
    }

    .highlight-legal:hover .tooltip-box,
    .highlight-financial:hover .tooltip-box,
    .highlight-tech:hover .tooltip-box,
    .highlight-social:hover .tooltip-box,
    .highlight-marketing:hover .tooltip-box,
    .highlight-general:hover .tooltip-box {
        visibility: visible;
        opacity: 1;
    }


    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-layout-container {
            flex-direction: column;
            padding: 10px;
            margin-top: 20px;
        }
        .sidebar-container {
            width: 100%;
            padding: 10px 0;
            margin-bottom: 20px;
        }
        .sidebar-menu ul {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
        }
        .sidebar-menu li {
            margin: 5px;
        }
        .sidebar-menu a {
            padding: 8px 12px;
            font-size: 14px;
        }
        .sidebar-user-profile {
            display: none;
        }
        .content-area-container {
            padding-right: 0;
        }
        .top-content-area {
            padding: 20px;
        }
        .main-logo-text {
            font-size: 2.5em;
        }
        .main-logo-subtitle {
            font-size: 1em;
        }
        div[data-testid="stTextInput"] {
            width: 90%;
        }
        .campaigns-section {
            padding: 20px;
        }
        .campaigns-section h2 {
            font-size: 1.6em;
        }
        .campaigns-section .section-subtitle {
            font-size: 0.9em;
        }
        .campaign-grid {
            grid-template-columns: 1fr;
        }
        .category-buttons {
            justify-content: flex-start;
        }
        .payment-container {
            flex-direction: column;
            padding: 15px;
            gap: 20px;
        }
        .payment-left-col, .payment-right-col {
            min-width: unset;
            width: 100%;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for navigation and authentication
if "active_page" not in st.session_state:
    st.session_state.active_page = "Login" # Start with Login page
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "user_role" not in st.session_state:
    st.session_state.user_role = "user" # Default role
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "All"
if "selected_campaign_data" not in st.session_state:
    st.session_state.selected_campaign_data = None
if "show_donate_input" not in st.session_state:
    st.session_state.show_donate_input = False
if "donation_amount_for_payment" not in st.session_state:
    st.session_state.donation_amount_for_payment = 0
if "selected_payment_method" not in st.session_state:
    st.session_state.selected_payment_method = "card_8013" # Default to the first card

# --- Term Definitions for Simplification ---
TERM_DEFINITIONS = {
    "legal": {
        "Intellectual Property Rights": "Legal rights to creations of the mind, like inventions or designs.",
        "Terms of Service": "The rules and conditions users must agree to when using a service.",
        "Accredited Investor": "An investor recognized by financial regulators as sophisticated enough to invest in certain complex securities.",
        "SEC regulations": "Rules set by the U.S. Securities and Exchange Commission to protect investors.",
        "KYC (Know Your Customer)": "A process to verify the identity of clients to prevent fraud and illegal activities.",
        "AML (Anti-Money Laundering)": "Laws and procedures to prevent criminals from disguising illegally obtained funds as legitimate income.",
        "Equity Crowdfunding": "Raising capital by offering shares of a company to a large number of small investors.",
        "Convertible Note": "A type of short-term debt that converts into equity at a later stage, usually during a future funding round.",
        "Arbitration": "A legal technique for resolving disputes outside the courts, where a neutral third party makes a decision.",
        "Jurisdiction": "The official power to make legal decisions and judgments."
    },
    "financial": {
        "Return on Investment (ROI)": "A measure of the profitability of an investment, calculated as profit divided by cost.",
        "Valuation": "The process of determining the current worth of a company or asset.",
        "Seed Funding": "The earliest stage of fundraising for a startup, used to get the business off the ground.",
        "Venture Capital": "Funding provided by investors to startup companies and small businesses with perceived long-term growth potential.",
        "Dilution": "The reduction in the ownership percentage of a company's existing shareholders when new shares are issued.",
        "Capital": "Wealth in the form of money or other assets owned by a person or organization.",
        "Liquidity": "The ease with which an asset or security can be converted into ready cash without affecting its market price.",
        "Escrow Account": "A temporary pass-through account held by a third party during the process of a transaction.",
        "Payment Gateway Fees": "Charges imposed by payment processing services for handling online transactions.",
        "Funding Threshold": "The minimum amount of money a crowdfunding campaign must raise to be successful.",
        "All-or-Nothing Model": "A crowdfunding model where funds are only collected if the campaign reaches its full funding goal.",
        "Tax Implications": "The consequences that a financial transaction or investment has on an individual's or company's tax liability."
    },
    "tech": {
        "Minimum Viable Product (MVP)": "A version of a new product with just enough features to satisfy early customers and provide feedback for future product development.",
        "Proof of Concept (POC)": "A realization of a certain method or idea to demonstrate its feasibility.",
        "Scalability": "The ability of a system to handle a growing amount of work by adding resources.",
        "Blockchain": "A decentralized, distributed ledger technology that records transactions across many computers.",
        "Artificial Intelligence (AI)": "The simulation of human intelligence processes by machines.",
        "Machine Learning (ML)": "A subset of AI that allows systems to learn from data without being explicitly programmed.",
        "API (Application Programming Interface)": "A set of rules and protocols for building and interacting with software applications.",
        "User Interface (UI)": "The visual part of a computer application or website that a user interacts with.",
        "User Experience (UX)": "The overall experience of a person using a product, encompassing their feelings and attitudes.",
        "Open Source": "Software with source code that anyone can inspect, modify, and enhance.",
        "Proprietary Technology": "Technology owned exclusively by a company, often protected by patents or copyrights."
    },
    "social": {
        "Sustainable Development Goals (SDGs)": "A collection of 17 global goals set by the United Nations for a sustainable future.",
        "Impact Investing": "Investments made with the intention to generate positive, measurable social and environmental impact alongside a financial return.",
        "Social Enterprise": "A business that has specific social objectives as its primary purpose.",
        "Carbon Footprint": "The total amount of greenhouse gases produced to directly and indirectly support human activities.",
        "Renewable Energy": "Energy from sources that are naturally replenishing but flow-limited, such as solar, wind, geothermal, and hydro.",
        "Circular Economy": "An economic system aimed at eliminating waste and the continual use of resources.",
        "Biodiversity": "The variety of life on Earth at all its levels, from genes to ecosystems.",
        "Community Empowerment": "The process of enabling communities to increase control over their lives.",
        "Philanthropy": "The desire to promote the welfare of others, expressed especially by the generous donation of money to good causes."
    },
    "marketing": {
        "Market Penetration": "The successful selling of a product or service in a specific market.",
        "Target Audience": "The specific group of consumers most likely to want your product or service.",
        "Value Proposition": "A statement that explains what benefit a company provides to customers.",
        "Unique Selling Proposition (USP)": "The unique benefit a company offers that helps it stand out from competitors.",
        "SEO (Search Engine Optimization)": "The process of improving the visibility of a website or a web page in a web search engine's unpaid results.",
        "Content Strategy": "The planning, development, and management of content.",
        "Customer Acquisition Cost (CAC)": "The cost associated with convincing a consumer to buy a product/service.",
        "Business Model Canvas": "A strategic management template used for developing new or documenting existing business models."
    },
    "general": {
        "Milestone": "A significant stage or event in the development of something.",
        "Deliverable": "A tangible or intangible good or service produced as a result of a project that is intended to be delivered to a customer.",
        "Timeline": "A schedule of events; a chronological record.",
        "Budget Allocation": "The process of assigning available financial resources for specific purposes.",
        "Risk Assessment": "The process of identifying potential hazards and analyzing what could happen if a hazard occurs.",
        "Stakeholder": "A person, group, or organization that has an interest or concern in an organization.",
        "Feasibility Study": "An assessment of the practicality of a proposed plan or project."
    }
}

# --- API Interaction Functions ---
def get_auth_headers():
    """Returns headers with JWT token if available."""
    if st.session_state.auth_token:
        return {"Authorization": f"Bearer {st.session_state.auth_token}"}
    return {}

@st.cache_data(ttl=300) # Cache data for 5 minutes
def fetch_all_campaigns():
    """Fetches all campaigns from the backend."""
    if not st.session_state.logged_in:
        return [] # Don't fetch if not logged in

    try:
        response = requests.get(f"{FASTAPI_BACKEND_URL}/campaigns", headers=get_auth_headers())
        response.raise_for_status() # Raise an exception for HTTP errors
        # Filter out 'Rejected' campaigns directly from the fetched data
        all_campaigns = response.json()
        return [c for c in all_campaigns if c.get('verification_status') != 'Rejected']
    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to backend at {FASTAPI_BACKEND_URL}. Please ensure the backend is running.")
        return []
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error fetching campaigns: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return []

def search_campaigns_backend(query):
    """Searches campaigns via the backend."""
    try:
        response = requests.post(f"{FASTAPI_BACKEND_URL}/search", json={"query": query}, headers=get_auth_headers())
        response.raise_for_status()
        # Filter out 'Rejected' campaigns directly from the search results
        search_results = response.json()
        return [c for c in search_results if c.get('verification_status') != 'Rejected']
    except requests.exceptions.RequestException as e:
        st.error(f"Error searching campaigns: {e}")
        return []

def create_campaign_backend(campaign_data):
    """Sends request to create a new campaign."""
    try:
        response = requests.post(f"{FASTAPI_BACKEND_URL}/create-campaign", json=campaign_data, headers=get_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"Error creating campaign: {e.response.json().get('detail', 'Unknown error')}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating campaign: {e}")
        return None

def login_user(username, password):
    """Authenticates user with the backend."""
    try:
        # This endpoint is for your backend to verify a Firebase ID Token.
        # For a full login flow, your frontend would get the ID token from Firebase JS SDK
        # and send it to this endpoint.
        # For this demo, we'll simulate a successful login for 'user' and 'admin'.
        if username == "user" and password == "password":
            st.session_state.auth_token = "mock_user_token"
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_role = "user"
            st.session_state.active_page = "Home"
            st.success(f"Welcome, {username}!")
            st.rerun()
        elif username == "admin" and password == "adminpass":
            st.session_state.auth_token = "mock_admin_token"
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_role = "admin"
            st.session_state.active_page = "Home"
            st.success(f"Welcome, {username} (Admin)! ")
            st.rerun()
        else:
            st.error("Invalid username or password.")

    except requests.exceptions.HTTPError as e:
        st.error(f"Login failed: {e.response.json().get('detail', 'Incorrect username or password')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Login failed: Could not connect to backend. Is it running? {e}")

def register_user_frontend(username, password, email=None):
    """Registers a new user with the backend."""
    st.success("Registration successful! Please log in.")
    st.session_state.active_page = "Login"
    st.rerun()


def logout_user():
    """Logs out the user."""
    st.session_state.logged_in = False
    st.session_state.auth_token = None
    st.session_state.username = None
    st.session_state.user_role = "user"
    st.session_state.active_page = "Login"
    st.success("Logged out successfully.")
    st.rerun()

# --- JavaScript for Term Highlighting and Tooltips ---
def inject_term_simplification_js():
    js_code = """
    <script>
    const termDefinitions = %s; // Will be replaced by Python with JSON data

    function applyTermSimplification() {
        const campaignDescriptionElement = document.getElementById('campaign-description-text');
        if (!campaignDescriptionElement) {
            return;
        }

        let originalText = campaignDescriptionElement.innerHTML;
        let newHtml = originalText;

        for (const category in termDefinitions) {
            const terms = termDefinitions[category];
            const className = `highlight-${category}`; // e.g., highlight-legal

            for (const term in terms) {
                const definition = terms[term];
                // Create a regex to match the whole word, case-insensitive
                const regex = new RegExp(`\\b${term.replace(/[.*+?^${}()|[\\\\]]/g, '\\$&')}\\b`, 'gi');
                newHtml = newHtml.replace(regex, (match) => {
                    // Avoid re-wrapping already wrapped terms
                    if (match.includes('<span class="highlight-')) {
                        return match;
                    }
                    return `<span class="${className}" data-definition="${definition}">${match}<span class="tooltip-box">${definition}</span></span>`;
                });
            }
        }
        campaignDescriptionElement.innerHTML = newHtml;
    }

    const observer = new MutationObserver((mutationsList, observer) => {
        for(const mutation of mutationsList) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                const campaignDetailContainer = document.querySelector('.campaign-detail-container');
                if (campaignDetailContainer && campaignDetailContainer.contains(document.getElementById('campaign-description-text'))) {
                    applyTermSimplification();
                    return;
                }
            }
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });
    document.addEventListener('DOMContentLoaded', applyTermSimplification);
    </script>
    """ % json.dumps(TERM_DEFINITIONS)
    st.markdown(js_code, unsafe_allow_html=True)


# --- Page Functions ---

def login_page():
    st.markdown("""<div class='container' style='max-width: 400px; margin-top: 50px;'>""", unsafe_allow_html=True)
    st.markdown("""<div class='title' style='text-align: center;'>Login</div>""", unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        col_login, col_register = st.columns(2)
        with col_login:
            submitted = st.form_submit_button("Login")
        with col_register:
            if st.form_submit_button("Register"):
                st.session_state.active_page = "Register"
                st.rerun()

        if submitted:
            login_user(username, password)

    st.markdown("""<div class='option' style='text-align: center; margin-top: 20px;'>Not registered? <a href='#' onclick='window.parent.document.querySelector(\"[data-testid=\\\"stMarkdownContainer\\\"]\").dispatchEvent(new CustomEvent(\"streamlit:update-session-state\", { detail: { key: \"active_page\", value: \"Register\" } }))'>Create an account</a></div>""", unsafe_allow_html=True)
    st.markdown("""</div>""", unsafe_allow_html=True)

def register_page():
    st.markdown("""<div class='container' style='max-width: 600px; margin-top: 50px;'>""", unsafe_allow_html=True)
    st.markdown("""<div class='title' style='text-align: center;'>Register</div>""", unsafe_allow_html=True)

    st.subheader("Register as an Individual")
    with st.form("register_form_individual"):
        reg_username = st.text_input("Username", key="reg_username")
        reg_email = st.text_input("Email ID", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")

        submitted = st.form_submit_button("Register Individual Account")
        if submitted:
            if reg_password != reg_password_confirm:
                st.error("Passwords do not match.")
            else:
                register_user_frontend(reg_username, reg_password, reg_email)

    st.markdown("""<div class='option' style='text-align: center; margin-top: 20px;'>Already have an account? <a href='#' onclick='window.parent.document.querySelector(\"[data-testid=\\\"stMarkdownContainer\\\"]\").dispatchEvent(new CustomEvent(\"streamlit:update-session-state\", { detail: { key: \"active_page\", value: \"Login\" } }))'>Login here</a></div>""", unsafe_allow_html=True)
    st.markdown("""</div>""", unsafe_allow_html=True)


def home_page():
    st.markdown("""
        <div class="top-content-area">
            <div class="translate-widget-container">
                <svg id="translate-icon" class="translate-icon" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                    <path d="M60,80 L40,80 L40,60 L20,60 L20,40 L40,40 L40,20 L60,20 L60,40 L80,40 L80,60 L60,60 Z" fill="#6a0dad"/>
                    <text x="25" y="75" font-family="Arial, sans-serif" font-size="40" fill="white" font-weight="bold">R</text>
                    <text x="60" y="35" font-family="Arial, sans-serif" font-size="40" fill="white" font-weight="bold">अ</text>
                </svg>
                <ul id="language-dropdown" class="language-dropdown">
                    <li><a href="#">Hindi</a></li>
                    <li><a href="#">Bengali</a></li>
                    <li><a href="#">Tamil</a></li>
                    <li><a href="#">Telugu</a></li>
                    <li><a href="#">Marathi</a></li>
                    <li><a href="#">Gujarati</a></li>
                    <li><a href="#">Punjabi</a></li>
                    <li><a href="#">Kannada</a></li>
                    <li><a href="#">Malayalam</a></li>
                    <li><a href="#">Oriya</a></li>
                    <li><a href="#">Assamese</a></li>
                    <li><a href="#">Urdu</a></li>
                    <li><a href="#">Nepali</a></li>
                    <li><a href="#">Sinhala</a></li>
                </ul>
            </div>
            <div class="main-logo-text">HAVEN</div>
            <p class="main-logo-subtitle">Support the most popular projects on HAVEN.</p>
    """, unsafe_allow_html=True)

    search_query = st.text_input("", placeholder="Search campaigns", key="home_search_bar")
    st.markdown("""</div>""", unsafe_allow_html=True)

    st.markdown("""
        <div class="campaigns-section">
            <h2>Trending Campaigns</h2>
            <p class="section-subtitle">Support the most popular projects on HAVEN.</p>
            <div class="campaign-grid">
    """, unsafe_allow_html=True)

    campaign_data = fetch_all_campaigns()

    if search_query:
        campaign_data = [
            c for c in campaign_data
            if search_query.lower() in c["name"].lower() or search_query.lower() in c["description"].lower()
        ]

    if not campaign_data:
        st.markdown("""<p style='text-align: center; color: #888;'>No trending campaigns found.</p>""", unsafe_allow_html=True)
    else:
        for campaign in campaign_data:
            progress_percentage = (campaign["funded"] / campaign["goal"]) * 100 if campaign["goal"] > 0 else 0

            with st.form(key=f"campaign_form_{campaign['id']}", clear_on_submit=False):
                image_url = campaign.get("image_url", f"https://placehold.co/600x400/E0E0E0/333333?text={campaign['name'].replace(' ', '+')}")
                st.markdown(f"""
                    <div class="campaign-card">
                        <div class="campaign-image-placeholder">
                            <img src="{image_url}" alt="{campaign['name']}">
                            <span class="badge trending"><i class="fas fa-chart-line"></i> Trending</span>
                        </div>
                        <div class="campaign-info">
                            <h3>{campaign['name']}</h3>
                            <p class="campaign-description">{campaign['description'][:100]}...</p>
                            <p class="campaign-author">{campaign['author']}</p>
                            <div class="campaign-progress-container">
                                <div class="campaign-progress-bar">
                                    <div class="campaign-progress-fill" style="width: {progress_percentage:.0f}%"></div>
                                </div>
                                <div class="campaign-stats">
                                    <span class="amount-funded">₹{campaign['funded']:,} raised {progress_percentage:.0f}%</span>
                                    <span>{campaign['days_left']} days left</span>
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                submitted = st.form_submit_button(label="View Details", help="Click to view full campaign details")

                if submitted:
                    st.session_state.selected_campaign_data = campaign
                    st.session_state.active_page = "campaign_detail"
                    st.rerun()
        st.markdown("""</div>""", unsafe_allow_html=True)
    st.markdown("""</div>""", unsafe_allow_html=True)

    st.markdown("""
    <script>
        const translateIcon = document.getElementById('translate-icon');
        const dropdown = document.getElementById('language-dropdown');

        translateIcon.addEventListener('click', (event) => {
            event.stopPropagation();
            if (dropdown.style.display === 'block') {
                dropdown.style.display = 'none';
            } else {
                dropdown.style.display = 'block';
            }
        });

        document.addEventListener('click', (event) => {
            if (!dropdown.contains(event.target) && event.target !== translateIcon) {
                dropdown.style.display = 'none';
            }
        });
    </script>
    """, unsafe_allow_html=True)

def explore_page():
    st.markdown("""
        <div class="top-content-area">
            <div class="main-logo-text">HAVEN</div>
            <p class="main-logo-subtitle">Find and support campaigns that matter to you.</p>
    """, unsafe_allow_html=True)

    search_query = st.text_input("", placeholder="Search campaigns by title or description", key="explore_search_bar")
    st.markdown("""</div>""", unsafe_allow_html=True)

    st.markdown("""
        <div class="campaigns-section">
            <h2>Explore Campaigns</h2>
            <p class="section-subtitle">Discover campaigns by category or search.</p>
    """, unsafe_allow_html=True)

    categories = ["All", "Technology", "Arts & Culture", "Community", "Music", "Fashion", "Education"]

    st.markdown("""<div class="category-buttons">""", unsafe_allow_html=True)
    cols = st.columns(len(categories))
    for i, category in enumerate(categories):
        with cols[i]:
            if st.button(category, key=f"cat_btn_{category}", help=f"Filter by {category} category"):
                st.session_state.selected_category = category
                st.rerun()
    st.markdown("""</div>""", unsafe_allow_html=True)

    campaign_data = fetch_all_campaigns()

    filtered_campaigns = []
    for campaign in campaign_data:
        matches_category = (st.session_state.selected_category == "All" or campaign["category"] == st.session_state.selected_category)
        matches_search = (search_query.lower() in campaign["name"].lower() or search_query.lower() in campaign["description"].lower())
        if matches_category and matches_search:
            filtered_campaigns.append(campaign)

    if not filtered_campaigns:
        st.markdown("""<p style='text-align: center; color: #888;'>No campaigns found matching your criteria.</p>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="campaign-grid">""", unsafe_allow_html=True)
        for campaign in filtered_campaigns:
            progress_percentage = (campaign["funded"] / campaign["goal"]) * 100 if campaign["goal"] > 0 else 0
            with st.form(key=f"campaign_form_explore_{campaign['id']}", clear_on_submit=False):
                image_url = campaign.get("image_url", f"https://placehold.co/600x400/E0E0E0/333333?text={campaign['name'].replace(' ', '+')}")
                st.markdown(f"""
                    <div class="campaign-card">
                        <div class="campaign-image-placeholder">
                            <img src="{image_url}" alt="{campaign['name']}">
                            <span class="badge trending"><i class="fas fa-chart-line"></i> Trending</span>
                        </div>
                        <div class="campaign-info">
                            <h3>{campaign['name']}</h3>
                            <p class="campaign-description">{campaign['description'][:100]}...</p>
                            <p class="campaign-author">{campaign['author']}</p>
                            <div class="campaign-progress-container">
                                <div class="campaign-progress-bar">
                                    <div class="campaign-progress-fill" style="width: {progress_percentage:.0f}%"></div>
                                </div>
                                <div class="campaign-stats">
                                    <span class="amount-funded">₹{campaign['funded']:,} raised {progress_percentage:.0f}%</span>
                                    <span>{campaign['days_left']} days left</span>
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                submitted = st.form_submit_button(label="View Details", help="Click to view full campaign details")
                if submitted:
                    st.session_state.selected_campaign_data = campaign
                    st.session_state.active_page = "campaign_detail"
                    st.rerun()
        st.markdown("""</div>""", unsafe_allow_html=True)

    st.markdown("""</div>""", unsafe_allow_html=True)

def search_page():
    st.markdown("""
        <div class="top-content-area">
            <div class="main-logo-text">HAVEN</div>
            <p class="main-logo-subtitle">Search for campaigns that inspire you.</p>
    """, unsafe_allow_html=True)

    search_query = st.text_input("", placeholder="Enter keywords to search campaigns...", key="search_bar_main")
    st.markdown("""</div>""", unsafe_allow_html=True)

    st.markdown("""
        <div class="campaigns-section">
            <h2>Search Results</h2>
            <p class="section-subtitle">Filter results by category.</p>
    """, unsafe_allow_html=True)

    categories = ["All", "Technology", "Arts & Culture", "Community", "Music", "Fashion", "Education"]

    st.markdown("""<div class="category-buttons">""", unsafe_allow_html=True)
    cols = st.columns(len(categories))
    for i, category in enumerate(categories):
        with cols[i]:
            if st.button(category, key=f"search_cat_btn_{category}", help=f"Filter by {category} category"):
                st.session_state.selected_category = category
                st.rerun()
    st.markdown("""</div>""", unsafe_allow_html=True)

    if search_query:
        campaign_data = search_campaigns_backend(search_query)
    else:
        campaign_data = []

    filtered_campaigns = []
    for campaign in campaign_data:
        matches_category = (st.session_state.selected_category == "All" or campaign["category"] == st.session_state.selected_category)
        if matches_category:
            filtered_campaigns.append(campaign)

    if not filtered_campaigns:
        st.markdown("""<p style='text-align: center; color: #888;'>No campaigns found matching your criteria. Try a different search or filter!</p>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="campaign-grid">""", unsafe_allow_html=True)
        for campaign in filtered_campaigns:
            progress_percentage = (campaign["funded"] / campaign["goal"]) * 100 if campaign["goal"] > 0 else 0
            with st.form(key=f"campaign_form_search_{campaign['id']}", clear_on_submit=False):
                image_url = campaign.get("image_url", f"https://placehold.co/600x400/E0E0E0/333333?text={campaign['name'].replace(' ', '+')}")
                st.markdown(f"""
                    <div class="campaign-card">
                        <div class="campaign-image-placeholder">
                            <img src="{image_url}" alt="{campaign['name']}">
                            <span class="badge trending"><i class="fas fa-chart-line"></i> Trending</span>
                        </div>
                        <div class="campaign-info">
                            <h3>{campaign['name']}</h3>
                            <p class="campaign-description">{campaign['description'][:100]}...</p>
                            <p class="campaign-author">{campaign['author']}</p>
                            <div class="campaign-progress-container">
                                <div class="campaign-progress-bar">
                                    <div class="campaign-progress-fill" style="width: {progress_percentage:.0f}%"></div>
                                </div>
                                <div class="campaign-stats">
                                    <span class="amount-funded">₹{campaign['funded']:,} raised {progress_percentage:.0f}%</span>
                                    <span>{campaign['days_left']} days left</span>
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                submitted = st.form_submit_button(label="View Details", help="Click to view full campaign details")
                if submitted:
                    st.session_state.selected_campaign_data = campaign
                    st.session_state.active_page = "campaign_detail"
                    st.rerun()
        st.markdown("""</div>""", unsafe_allow_html=True)

    st.markdown("""</div>""", unsafe_allow_html=True)

def create_campaign_page():
    st.markdown("""
        <div class="top-content-area">
            <div class="main-logo-text">HAVEN</div>
            <p class="main-logo-subtitle">Launch your own crowdfunding campaign.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="campaigns-section">
            <h2>Create a New Campaign</h2>
            <p class="section-subtitle">Fill in the details below to start your campaign.</p>
    """, unsafe_allow_html=True)

    if st.session_state.user_role != "admin":
        st.warning("You must be an admin to create campaigns. Please log in as an admin.")
        return

    with st.form("create_campaign_form"):
        name = st.text_input("Campaign Name", max_chars=100)
        description = st.text_area("Description", max_chars=500)
        author = st.text_input("Your Organization/Name (Author)")
        goal = st.number_input("Funding Goal (in INR)", min_value=1000, step=1000)
        category = st.selectbox("Category", ["Technology", "Arts & Culture", "Community", "Music", "Fashion", "Education"])

        st.subheader("Organization Verification Details (Optional but Recommended)")
        registration_type = st.selectbox("Organization Type", ["", "Section 8 Company", "Society", "Trust"], help="Legal structure of your organization.")
        registration_number = st.text_input("Registration Number", help="CIN for Section 8 Co., Reg. No. for Society/Trust.")
        pan = st.text_input("PAN (Permanent Account Number)", help="Organization's PAN.")
        ngo_darpan_id = st.text_input("NGO Darpan ID", help="Unique ID from NGO Darpan portal.")
        fcra_number = st.text_input("FCRA Number", help="Foreign Contribution Regulation Act registration number, if applicable.")


        submitted = st.form_submit_button("Create Campaign")
        if submitted:
            if not name or not description or not author or not goal:
                st.error("Please fill in all required fields.")
            else:
                campaign_data = {
                    "name": name,
                    "description": description,
                    "author": author,
                    "goal": int(goal),
                    "category": category,
                    "registration_type": registration_type if registration_type else None,
                    "registration_number": registration_number if registration_number else None,
                    "pan": pan if pan else None,
                    "ngo_darpan_id": ngo_darpan_id if ngo_darpan_id else None,
                    "fcra_number": fcra_number if fcra_number else None,
                }
                with st.spinner("Creating campaign..."):
                    response = create_campaign_backend(campaign_data)
                    if response:
                        st.success(response.get("message", "Campaign created successfully!"))
                        st.session_state.active_page = "Home"
                        st.rerun()

    st.markdown("""</div>""", unsafe_allow_html=True)

def display_campaign_detail():
    campaign = st.session_state.selected_campaign_data

    if campaign is None:
        st.warning("No campaign selected. Please go back to the list.")
        if st.button("Back to Campaigns"):
            st.session_state.active_page = "Home"
            st.session_state.selected_campaign_data = None
            st.rerun()
        return

    if st.button("← Back to Campaigns"):
        st.session_state.active_page = "Home"
        st.session_state.selected_campaign_data = None
        st.rerun()

    st.markdown("""<div class="campaign-detail-container">""", unsafe_allow_html=True)

    image_url = campaign.get("image_url", f"https://placehold.co/800x500/A8DADC/333333?text=Campaign+Image+{campaign['name'].replace(' ', '+')}")
    st.image(image_url, caption=campaign["name"], use_column_width=True, classes="detail-image")

    st.markdown(f"""<h1 class="detail-header">{campaign["name"]}</h1>""", unsafe_allow_html=True)

    fraud_score = campaign.get("fraud_score", 0)
    fraud_dot_class = "fraud-green"
    fraud_text = "Verified by AI (Low Fraud Risk)"
    if campaign.get('verification_status') == 'Rejected':
        fraud_dot_class = "fraud-red"
        fraud_text = "Rejected (High Fraud Risk)"
    elif campaign.get('verification_status') == 'Needs Manual Review':
        fraud_dot_class = "fraud-yellow"
        fraud_text = "Needs Manual Review (Moderate Fraud Risk)"

    st.markdown(f"""
    <div class="organization-detail-info">
        <span class="fraud-indicator-dot {fraud_dot_class}"></span>
        <strong>Organization:</strong> {campaign["author"]} ({fraud_text})
    </div>
    """, unsafe_allow_html=True)

    st.write(f"**Category:** {campaign['category']}")
    st.markdown(f"""**Description:** <span id="campaign-description-text">{campaign['description']}</span>""", unsafe_allow_html=True)
    inject_term_simplification_js()

    progress_percentage = (campaign["funded"] / campaign["goal"]) * 100 if campaign["goal"] > 0 else 0
    st.markdown(f"""
    <div class="detail-progress-container">
        <div class="detail-progress-bar" style="width: {progress_percentage:.0f}%">{progress_percentage:.0f}%</div>
    </div>
    <div class="detail-stats">
        <span>₹{campaign['funded']:,} raised</span>
        <span>Goal: ₹{campaign['goal']:,}</span>
        <span>{campaign['days_left']} days left</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Share Campaign", key="share_detail"):
            st.info("Share functionality coming soon!")
    with col2:
        if campaign.get('verification_status') != 'Rejected':
            if st.button("Donate Now", key="donate_detail"):
                st.session_state.show_donate_input = True
        else:
            st.warning("This campaign has been rejected due to high fraud risk and cannot accept donations.")

    if st.session_state.get("show_donate_input", False):
        st.markdown("""<div class="donate-input-box">""", unsafe_allow_html=True)
        st.subheader("Enter Donation Amount")
        donation_amount = st.number_input("Amount (₹)", min_value=100, value=500, step=100, key="donation_amount_input")
        if st.button("Proceed to Payment", key="proceed_payment_from_detail"):
            st.session_state.donation_amount_for_payment = donation_amount
            st.session_state.active_page = "payment_page"
            st.session_state.show_donate_input = False
            st.rerun()
        st.markdown("""</div>""", unsafe_allow_html=True)

    st.markdown("""<h3 class="section-title">Top 3 Donators</h3>""", unsafe_allow_html=True)
    donators = [
        {"name": "Alice Smith", "amount": 10000},
        {"name": "Bob Johnson", "amount": 7500},
        {"name": "Charlie Brown", "amount": 5000},
    ]
    st.markdown("""<ul class="donator-list">""", unsafe_allow_html=True)
    for i, donator in enumerate(donators):
        st.markdown(f"""<li>{i+1}. <strong>{donator['name']}</strong> - ₹{donator['amount']:,}</li>""", unsafe_allow_html=True)
    st.markdown("""</ul>""", unsafe_allow_html=True)

    st.markdown("""<h3 class="section-title">Reviews</h3>""", unsafe_allow_html=True)
    reviews = [
        {"author": "User123", "text": "Great initiative! Hope they reach their goal."},
        {"author": "SupporterX", "text": "Transparent and impactful. Highly recommend!"},
        {"author": "CrowdFundFan", "text": "Easy to donate, looking forward to updates."},
    ]
    for review in reviews:
        st.markdown(f"""
        <div class="review-item">
            <p class="review-author">{review['author']}</p>
            <p class="review-text">"{review['text']}"</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""<h3 class="section-title">Fraud Detection Explanation</h3>""", unsafe_allow_html=True)
    fraud_explanation_class = "fraud-explanation-detail-box"
    if campaign.get('verification_status') == 'Rejected':
        fraud_explanation_class += " red"
    elif campaign.get('verification_status') == 'Needs Manual Review':
        fraud_explanation_class += " yellow"
    else:
        fraud_explanation_class += " green"

    verification_details = campaign.get("verification_details", {})
    issues_list = verification_details.get("issues", ["None"])
    issues_html = "".join([f"<li>{issue}</li>" for issue in issues_list])

    st.markdown(f"""
    <div class="{fraud_explanation_class}">
        <p>{campaign.get('fraud_explanation', 'No detailed explanation available.')}</p>
        <br>
        <strong>Verification Details:</strong>
        <ul>
            <li>PAN Status: {verification_details.get('pan_status', 'N/A')}</li>
            <li>MCA Status: {verification_details.get('mca_status', 'N/A')}</li>
            <li>NGO Darpan Status: {verification_details.get('ngo_darpan_status', 'N/A')}</li>
            <li>Trust Status: {verification_details.get('trust_status', 'N/A')}</li>
            <li>Society Status: {verification_details.get('society_status', 'N/A')}</li>
            <li>FCRA Status: {verification_details.get('fcra_status', 'N/A')}</li>
            <li>TrustCheckr Score: {verification_details.get('trustcheckr_score', 'N/A')}</li>
            <li>Social Media Verified: {verification_details.get('social_media_verified', 'N/A')}</li>
            <li>Issues: <ul>{issues_html}</ul></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""</div>""", unsafe_allow_html=True)


def payment_page():
    campaign = st.session_state.selected_campaign_data
    donation_amount = st.session_state.donation_amount_for_payment

    if campaign is None or donation_amount == 0:
        st.warning("No campaign or donation amount selected. Please go back to the campaign details.")
        if st.button("Back to Campaign"):
            st.session_state.active_page = "campaign_detail"
            st.rerun()
        return

    st.markdown("""<div class="payment-container">""", unsafe_allow_html=True)

    st.markdown("""<div class="payment-left-col">""", unsafe_allow_html=True)
    st.markdown("""<h2 class="payment-header">Checkout</h2>""", unsafe_allow_html=True)

    st.markdown("""<h3 class="payment-section-title">Billing address</h3>""", unsafe_allow_html=True)
    st.selectbox("Country", ["India", "United States", "Canada"], index=0, key="billing_country")
    st.selectbox("State / Union Territory", ["Delhi", "Maharashtra", "Karnataka"], index=0, key="billing_state")
    st.markdown("""<p style='font-size: 0.85em; color: #777; margin-top: 10px;'>Udemy is required by law to collect applicable transaction taxes for purchases made in certain tax jurisdictions.</p>""", unsafe_allow_html=True)

    st.markdown("""<h3 class="payment-section-title">Payment method <span style="float:right; font-size:0.8em; color:#999;"><i class="fas fa-lock"></i> Secure and encrypted</span></h3>""", unsafe_allow_html=True)

    payment_methods = {
        "card_8013": {
            "label": "MasterCard **** 8013",
            "icons": [
                "https://placehold.co/40x25/FFFFFF/000000?text=MC",
                "https://placehold.co/40x25/FFFFFF/000000?text=Visa"
            ],
            "details": "As a security measure, please enter the security code (CVC) of your card ending with 8013."
        },
        "upi": {
            "label": "UPI",
            "icons": [
                "https://placehold.co/40x25/FFFFFF/000000?text=UPI"
            ],
            "details": ""
        },
        "cards": {
            "label": "Cards",
            "icons": [
                "https://placehold.co/40x25/FFFFFF/000000?text=Visa",
                "https://placehold.co/40x25/FFFFFF/000000?text=MC",
                "https://placehold.co/40x25/FFFFFF/000000?text=Amex",
                "https://placehold.co/40x25/FFFFFF/000000?text=RuPay"
            ],
            "details": ""
        },
        "net_banking": {
            "label": "Net Banking",
            "icons": [],
            "details": ""
        },
        "mobile_wallets": {
            "label": "Mobile Wallets",
            "icons": [],
            "details": ""
        }
    }

    st.markdown("""<div class="stRadio">""", unsafe_allow_html=True)
    for key, method in payment_methods.items():
        is_selected = (st.session_state.selected_payment_method == key)
        with st.form(key=f"payment_method_form_{key}", clear_on_submit=False):
            st.markdown(f"""
            <label class="payment-method-option {'selected' if is_selected else ''}" for="payment_method_radio_{key}">
                <input type="radio" id="payment_method_radio_{key}" name="payment_method_radio_group" value="{key}" {'checked' if is_selected else ''} style="display:none;">
                <div class="method-details">
                    <h4>{method['label']}</h4>
                    <p>{method['details']}</p>
                </div>
                <div class="method-icons">
                    {''.join([f'<img src="{icon_url}" alt="icon">' for icon_url in method["icons"]])}
                </div>
            </label>
            """, unsafe_allow_html=True)
            submitted_method = st.form_submit_button(label="Select", help=f"Select {method['label']}", disabled=is_selected)
            if submitted_method:
                st.session_state.selected_payment_method = key
                st.rerun()
    st.markdown("""</div>""", unsafe_allow_html=True)


    if st.session_state.selected_payment_method == "card_8013":
        st.text_input("CVC", type="password", max_chars=4, key="card_cvc")
    elif st.session_state.selected_payment_method == "cards":
        st.text_input("Card Number", key="card_number")
        col_exp, col_cvc = st.columns(2)
        with col_exp:
            st.text_input("Expiration (MM/YY)", key="card_expiry")
        with col_cvc:
            st.text_input("CVC", type="password", max_chars=4, key="card_cvc_full")
        st.text_input("Name on Card", key="card_name")
    elif st.session_state.selected_payment_method == "upi":
        st.text_input("UPI ID", placeholder="yourname@bankupi", key="upi_id_input")
        st.info("You will be redirected to your UPI app to complete the payment.")

    st.markdown("""</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="payment-right-col">""", unsafe_allow_html=True)
    st.markdown("""<h3 class="payment-section-title">Order summary</h3>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="order-summary-box">
        <div class="order-summary-item">
            <span>Donation Amount:</span>
            <span>₹{donation_amount:,}</span>
        </div>
        <div class="order-summary-item">
            <span>Platform Fee (0%):</span>
            <span>₹0</span>
        </div>
        <div class="order-summary-total">
            <span>Total:</span>
            <span>₹{donation_amount:,}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <p style="font-size: 0.9em; color: #666; margin-top: 20px;">
        By completing your purchase, you agree to these <a href="#" style="color:#6a0dad;">Terms of Use</a>.
    </p>
    """, unsafe_allow_html=True)

    if st.button(f"Pay ₹{donation_amount:,}", key="final_pay_button", use_container_width=True, help="Click to finalize your payment"):
        st.success(f"Payment of ₹{donation_amount:,} to {campaign['author']} successful via {payment_methods[st.session_state.selected_payment_method]['label']}! Thank you for your support.")
        st.session_state.active_page = "campaign_detail"
        st.session_state.show_donate_input = False
        st.session_state.donation_amount_for_payment = 0
        st.rerun()

    st.markdown("""
    <div class="money-back-guarantee">
        <i class="fas fa-undo-alt"></i> 30-Day Money-Back Guarantee
        <p>Not satisfied? Get a full refund within 30 days.<br>Simple and straightforward!</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""</div>""", unsafe_allow_html=True)
    st.markdown("""</div>""", unsafe_allow_html=True)

    if st.button("← Back to Campaign", key="back_from_payment"):
        st.session_state.active_page = "campaign_detail"
        st.session_state.show_donate_input = False
        st.session_state.donation_amount_for_payment = 0
        st.rerun()


# --- Main App Logic (Router) ---
if not st.session_state.logged_in:
    if st.session_state.active_page == "Register":
        register_page()
    else:
        login_page()
else:
    col1, col2 = st.columns([220, 1000])

    with st.container():
        st.markdown("""<div class="main-layout-container">""", unsafe_allow_html=True)

        with col1:
            st.markdown("""<div class="sidebar-container">""", unsafe_allow_html=True)
            st.image("https://placehold.co/150x50/A8DADC/333333?text=HAVEN+Logo", width=150)
            st.markdown("""<h2 class="sidebar-header">HAVEN Platform</h2>""", unsafe_allow_html=True)
            st.markdown("""---""")
            st.markdown(f"""
                <div class="sidebar-menu">
                    <ul>
                        <li><a href="#" class="{'active' if st.session_state.active_page == 'Home' else ''}" onclick="window.parent.document.querySelector('[data-testid=\\"stMarkdownContainer\\"]').dispatchEvent(new CustomEvent('streamlit:update-session-state', {{ detail: {{ key: 'active_page', value: 'Home' }} }}))"><i class="fas fa-home"></i> Home</a></li>
                        <li><a href="#" class="{'active' if st.session_state.active_page == 'Explore' else ''}" onclick="window.parent.document.querySelector('[data-testid=\\"stMarkdownContainer\\"]').dispatchEvent(new CustomEvent('streamlit:update-session-state', {{ detail: {{ key: 'active_page', value: 'Explore' }} }}))"><i class="fas fa-compass"></i> Explore</a></li>
                        <li><a href="#" class="{'active' if st.session_state.active_page == 'Search' else ''}" onclick="window.parent.document.querySelector('[data-testid=\\"stMarkdownContainer\\"]').dispatchEvent(new CustomEvent('streamlit:update-session-state', {{ detail: {{ key: 'active_page', value: 'Search' }} }}))"><i class="fas fa-search"></i> Search</a></li>
                        <li><a href="#" class="{'active' if st.session_state.active_page == 'Create Campaign' else ''}" onclick="window.parent.document.querySelector('[data-testid=\\"stMarkdownContainer\\"]').dispatchEvent(new CustomEvent('streamlit:update-session-state', {{ detail: {{ key: 'active_page', value: 'Create Campaign' }} }}))"><i class="fas fa-plus-circle"></i> Create Campaign</a></li>
                    </ul>
                </div>
                <div class="sidebar-user-profile">
                    <p class="user-name">{st.session_state.username}</p>
                    <p>Role: {st.session_state.user_role}</p>
                    <button onclick="window.parent.document.querySelector('[data-testid=\\"stMarkdownContainer\\"]').dispatchEvent(new CustomEvent('streamlit:update-session-state', {{ detail: {{ key: 'logout', value: true }} }}))" style="background: none; border: none; color: #6a0dad; cursor: pointer; font-size: 0.9em; margin-top: 10px;">Logout</button>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("""</div>""", unsafe_allow_html=True)

        with col2:
            st.markdown("""<div class="content-area-container">""", unsafe_allow_html=True)
            if st.session_state.active_page == "Home":
                home_page()
            elif st.session_state.active_page == "Explore":
                explore_page()
            elif st.session_state.active_page == "Search":
                search_page()
            elif st.session_state.active_page == "Create Campaign":
                create_campaign_page()
            elif st.session_state.active_page == "campaign_detail":
                display_campaign_detail()
            elif st.session_state.active_page == "payment_page":
                payment_page()
            st.markdown("""</div>""", unsafe_allow_html=True)

        st.markdown("""</div>""", unsafe_allow_html=True)

    if st.session_state.get("logout", False):
        logout_user()
        st.session_state.logout = False
        st.rerun()

