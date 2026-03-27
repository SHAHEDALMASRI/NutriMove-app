import streamlit as st
import matplotlib.pyplot as plt
import csv
import io
import json

# -----------------------------
# 🎨 UI & Background
# -----------------------------
st.set_page_config(page_title="NutriMove", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)),
    url("https://images.unsplash.com/photo-1554284126-aa88f22d8b74");
    background-size: cover;
    background-position: center;
}

h1, h2, h3, h4, p, label {
    color: white !important;
}

.stButton>button {
    background-color: #ff4b4b;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
}

.stTextInput>div>div>input,
.stNumberInput input {
    background-color: rgba(255,255,255,0.8);
}
</style>
""", unsafe_allow_html=True)

st.title("🏃‍♀️ NutriMove")
st.markdown("### 🚀 Welcome to NutriMove – Your Smart Fitness Companion")
st.write("Track your fitness & nutrition journey 💪")

# -----------------------------
# Session State
# -----------------------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# -----------------------------
# Load / Save
# -----------------------------
def load_users():
    try:
        with open("users_data.json", "r") as f:
            st.session_state.users = json.load(f)
    except:
        st.session_state.users = {}

def save_users():
    with open("users_data.json", "w") as f:
        json.dump(st.session_state.users, f)

# -----------------------------
# User Login
# -----------------------------
def create_user():
    st.subheader("Create / Login User")
    username = st.text_input("Enter username")

    if st.button("Login"):
        if username not in st.session_state.users:
            st.session_state.users[username] = {
                "weight": 60,
                "height": 160,
                "goal": "Stay Fit",
                "entries": []
            }

        st.session_state.current_user = username
        save_users()
        st.success(f"Welcome {username}! 🎉")

# -----------------------------
# Profile
# -----------------------------
def edit_profile():
    user = st.session_state.users[st.session_state.current_user]

    st.subheader("Edit Profile")

    weight = st.number_input("Weight (kg)", value=int(user["weight"]))
    height = st.number_input("Height (cm)", value=int(user["height"]))
    goal = st.text_input("Goal", value=user["goal"])

    if st.button("Save Profile"):
        user["weight"] = weight
        user["height"] = height
        user["goal"] = goal
        save_users()
        st.success("Profile updated ✅")

# -----------------------------
# Add Entry
# -----------------------------
def add_entry():
    st.subheader("Add Entry")

    entry_type = st.selectbox("Type", ["Workout", "Meal"])
    category = st.text_input("Category")
    duration = st.text_input("Duration / Quantity")
    calories = st.number_input("Calories", min_value=0)
    date = st.date_input("Date")

    if st.button("Add Entry"):
        entry = {
            "type": entry_type,
            "category": category,
            "duration": duration,
            "calories": calories,
            "date": str(date)
        }

        st.session_state.users[st.session_state.current_user]["entries"].append(entry)
        save_users()
        st.success("Entry added 🎯")

# -----------------------------
# CSV Upload
# -----------------------------
def load_csv():
    st.subheader("Upload CSV")

    file = st.file_uploader("Choose CSV file", type=["csv"])

    if file:
        reader = csv.DictReader(io.StringIO(file.getvalue().decode("utf-8")))
        for row in reader:
            row["calories"] = int(row["calories"])
            st.session_state.users[st.session_state.current_user]["entries"].append(row)

        save_users()
        st.success("CSV Uploaded ✅")

# -----------------------------
# Graphs
# -----------------------------
def plot_calories():
    st.subheader("Calories Overview")

    entries = st.session_state.users[st.session_state.current_user]["entries"]

    consumed = sum(int(e["calories"]) for e in entries if e["type"].lower() == "meal")
    burned = sum(int(e["calories"]) for e in entries if e["type"].lower() == "workout")

    fig, ax = plt.subplots()
    ax.bar(["Consumed", "Burned"], [consumed, burned])
    st.pyplot(fig)

def plot_meal_pie():
    st.subheader("Meal Distribution")

    entries = st.session_state.users[st.session_state.current_user]["entries"]

    meals = {}
    for e in entries:
        if e["type"].lower() == "meal":
            meals[e["category"]] = meals.get(e["category"], 0) + int(e["calories"])

    if meals:
        fig, ax = plt.subplots()
        ax.pie(meals.values(), labels=meals.keys(), autopct='%1.1f%%')
        st.pyplot(fig)
    else:
        st.info("No meal data")

# -----------------------------
# Insight
# -----------------------------
def health_insight():
    st.subheader("Health Insight")

    entries = st.session_state.users[st.session_state.current_user]["entries"]

    consumed = sum(int(e["calories"]) for e in entries if e["type"].lower() == "meal")
    burned = sum(int(e["calories"]) for e in entries if e["type"].lower() == "workout")

    if consumed > burned:
        st.warning("⚠️ You consume more than you burn")
    else:
        st.success("✅ Great balance!")

# -----------------------------
# Run App
# -----------------------------
load_users()

create_user()

if st.session_state.current_user:

    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Profile",
        "➕ Add Entry",
        "📊 Graphs",
        "💡 Insight"
    ])

    with tab1:
        edit_profile()

    with tab2:
        add_entry()
        load_csv()

    with tab3:
        plot_calories()
        plot_meal_pie()

    with tab4:
        health_insight()
