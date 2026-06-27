import streamlit as st
from google import genai
from dotenv import load_dotenv
from datetime import datetime, date
import plotly.express as px
import json
import os

# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="AI Deadline Hero",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# LOAD CSS
# -----------------------------

if os.path.exists("style.css"):
    with open("style.css") as css:
        st.markdown(
            f"<style>{css.read()}</style>",
            unsafe_allow_html=True
        )

# -----------------------------
# ENV
# -----------------------------

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# -----------------------------
# JSON DATABASE
# -----------------------------

FILE = "tasks.json"


def load_tasks():

    if os.path.exists(FILE):

        with open(FILE, "r") as f:
            return json.load(f)

    return []


def save_tasks():

    with open(FILE, "w") as f:
        json.dump(st.session_state.tasks, f, indent=4)


# -----------------------------
# SESSION
# -----------------------------

if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.title("🚀 AI Deadline Hero")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "➕ Add Task",
        "🤖 AI Planner",
        "📊 Analytics",
        "⚙️ Settings"
    ]
)

st.sidebar.markdown("---")
st.sidebar.success("Version 4.0")

# -----------------------------
# HEADER
# -----------------------------

st.markdown("""
<div class='title'>
🚀 AI Deadline Hero
</div>

<div class='subtitle'>
Never Miss A Deadline Again
</div>
""", unsafe_allow_html=True)

# -----------------------------
# DASHBOARD
# -----------------------------

if page == "🏠 Dashboard":

    total = len(st.session_state.tasks)

    completed = len(
        [
            t for t in st.session_state.tasks
            if t["status"] == "Completed"
        ]
    )

    pending = total - completed

    score = 0

    if total > 0:
        score = int((completed / total) * 100)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("📋 Total", total)

    with c2:
        st.metric("✅ Completed", completed)

    with c3:
        st.metric("⏳ Pending", pending)

    with c4:
        st.metric("🔥 Productivity", f"{score}%")

    st.divider()

    search = st.text_input("🔍 Search Task")

    tasks = []

    for task in st.session_state.tasks:

        if search.lower() in task["task"].lower():
            tasks.append(task)

    if len(tasks) == 0:

        st.info("No Task Found.")

    else:

        st.subheader("📋 Your Tasks")
        # -----------------------------
# SHOW TASKS
# -----------------------------

        for i, task in enumerate(tasks):

            col1, col2, col3 = st.columns([5, 2, 2])

            with col1:

                st.markdown(f"""
### 📌 {task['task']}

📂 **{task['category']}**

📝 {task['notes']}
""")

            with col2:

                deadline = date.fromisoformat(task["deadline"])

                days = (deadline - date.today()).days

                if days < 0:
                    st.error("🔴 Overdue")

                elif days == 0:
                    st.warning("🟠 Due Today")

                else:
                    st.success(f"🟢 {days} Days Left")

                st.write("Priority:", task["priority"])

            with col3:

                if task["status"] == "Pending":

                    if st.button("✅ Complete", key=f"done{i}"):

                        task["status"] = "Completed"

                        save_tasks()

                        st.rerun()

                else:

                    st.success("Completed")

                if st.button("🗑 Delete", key=f"del{i}"):

                    st.session_state.tasks.remove(task)

                    save_tasks()

                    st.rerun()

# -----------------------------
# ADD TASK
# -----------------------------

elif page == "➕ Add Task":

    st.subheader("➕ Add New Task")

    with st.form("task_form", clear_on_submit=True):

        task = st.text_input("📌 Task Name")

        category = st.selectbox(
            "📂 Category",
            [
                "Assignment",
                "Exam",
                "Project",
                "Interview",
                "Meeting",
                "Personal"
            ]
        )

        priority = st.selectbox(
            "🔥 Priority",
            [
                "High",
                "Medium",
                "Low"
            ]
        )

        deadline = st.date_input("📅 Deadline")

        hours = st.slider(
            "⏰ Estimated Hours",
            1,
            30,
            5
        )

        notes = st.text_area("📝 Notes")

        submit = st.form_submit_button("💾 Save Task")

        if submit:

            if task.strip() == "":

                st.warning("Task name required!")

            else:

                st.session_state.tasks.append({

                    "task": task,

                    "category": category,

                    "priority": priority,

                    "deadline": str(deadline),

                    "hours": hours,

                    "notes": notes,

                    "status": "Pending"

                })

                save_tasks()

                st.success("✅ Task Saved Successfully!")

                st.rerun()
                # -----------------------------
# AI PLANNER
# -----------------------------

elif page == "🤖 AI Planner":

    st.subheader("🤖 AI Productivity Planner")

    task = st.text_input("📌 Task Name")

    deadline = st.date_input("📅 Deadline")

    hours = st.slider(
        "⏰ Estimated Hours",
        1,
        30,
        5
    )

    if st.button("🚀 Generate AI Plan"):

        if task.strip() == "":

            st.warning("Please enter a task.")

        else:

            prompt = f"""
You are an expert productivity coach.

Task:
{task}

Deadline:
{deadline}

Estimated Hours:
{hours}

Generate a beautiful markdown report.

Include:

# Priority

# Daily Study Schedule

# Step-by-Step Task Breakdown

# Risk Analysis

# Productivity Tips

# Motivation Quote

Keep it practical and easy to follow.
"""

            with st.spinner("🤖 AI is generating your plan..."):

                try:

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )

                    st.success("✅ AI Plan Generated Successfully!")

                    st.markdown(response.text)

                except Exception as e:

                    st.error(f"Error: {e}")

    st.divider()

    st.subheader("⚡ Quick Productivity Tips")

    tips = [
        "🎯 Start with the highest priority task.",
        "⏰ Use the Pomodoro Technique (25 min focus + 5 min break).",
        "📵 Turn off social media notifications while studying.",
        "💧 Stay hydrated throughout your work session.",
        "🛌 Get at least 7–8 hours of sleep.",
        "📚 Review completed work before ending the day."
    ]

    for tip in tips:
        st.info(tip)
        # -----------------------------
# ANALYTICS
# -----------------------------

elif page == "📊 Analytics":

    st.subheader("📊 Analytics Dashboard")

    if len(st.session_state.tasks) == 0:

        st.info("No tasks available.")

    else:

        total = len(st.session_state.tasks)

        completed = len([
            t for t in st.session_state.tasks
            if t["status"] == "Completed"
        ])

        pending = total - completed

        score = int((completed / total) * 100) if total > 0 else 0

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("📋 Total Tasks", total)

        with c2:
            st.metric("✅ Completed", completed)

        with c3:
            st.metric("⏳ Pending", pending)

        st.divider()

        pie_data = {
            "Status": ["Completed", "Pending"],
            "Count": [completed, pending]
        }

        fig = px.pie(
            pie_data,
            names="Status",
            values="Count",
            hole=0.45,
            title="Task Completion"
        )

        st.plotly_chart(fig, use_container_width=True)

        category_count = {}

        for task in st.session_state.tasks:

            cat = task["category"]

            category_count[cat] = category_count.get(cat, 0) + 1

        bar = px.bar(
            x=list(category_count.keys()),
            y=list(category_count.values()),
            labels={
                "x": "Category",
                "y": "Tasks"
            },
            title="Tasks by Category"
        )

        st.plotly_chart(bar, use_container_width=True)

        st.subheader("🏆 Productivity Score")

        st.progress(score / 100)

        if score >= 80:
            st.success(f"Excellent! Productivity Score: {score}%")

        elif score >= 50:
            st.warning(f"Good Progress! Productivity Score: {score}%")

        else:
            st.error(f"Need Improvement! Productivity Score: {score}%")

            # -----------------------------
# SETTINGS
# -----------------------------

elif page == "⚙️ Settings":

    st.subheader("⚙️ Settings")

    st.info("AI Deadline Hero Version 4.0")

    st.write("Current Time")

    st.code(datetime.now())

    st.divider()

    if st.button("🗑 Clear All Tasks"):

        st.session_state.tasks = []

        save_tasks()

        st.success("All Tasks Deleted!")

        st.rerun()