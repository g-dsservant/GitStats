import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import requests

# Set page config and enforce dark theme
st.set_page_config(page_title="GitStats", layout="wide")

# Dark theme styling
st.markdown("""
    <style>
        body {
            background-color: #0e1117;
            color: white;
        }
        .stMetric {
            background-color: white !important;
            color: black !important;
            padding: 1em;
            border-radius: 10px;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown p {
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar Inputs
st.sidebar.title("🔐 GitHub Access")
pat = st.sidebar.text_input("Personal Access Token", type="password")
owner = st.sidebar.text_input("GitHub Owner (user/org)")
repo = st.sidebar.text_input("Repository Name")

# GitHub API call
def run_query(query):
    headers = {"Authorization": f"Bearer {pat}"}
    response = requests.post("https://api.github.com/graphql", json={"query": query}, headers=headers)
    return response.json() if response.status_code == 200 else {}

# Help section before PAT
if not pat:
    st.title(":bar_chart: GitStats")
    st.markdown("""
    ### 🚀 What is GitStats?
    GitStats is a GitHub analytics dashboard that visualizes activity, contributions, and pull requests from a repository.

    ### 🔑 How to Get Started
    1. **Generate a GitHub Personal Access Token (PAT)**
    2. Enter the GitHub **owner (username/org)** and **repository name**.

    ### 🛡️ Required Token Permissions

    #### 🔐 Fine-Grained Token (Recommended)
    Set these **Read Access**:
    - Contents
    - Metadata
    - Pull requests
    - Actions
    - Deployments
    - Issues
    - Commit statuses

    Also: choose specific repository access.

    #### 🔹 Classic Token
    - `repo` scope (Full control of private repositories)
    - `read:org`
    - `read:user`
    - `user:email`
    - `admin:repo_hook`
    - For public-only: `public_repo` is sufficient.
    """)
    st.stop()

# Run if inputs are filled
if pat and owner and repo:
    st.title(":bar_chart: GitStats — GitHub Analytics Dashboard")
    status = st.empty()
    status.info("⏳ Fetching data...")

    # Commits Query
    commit_query = f"""
    {{
      repository(owner: \"{owner}\", name: \"{repo}\") {{
        defaultBranchRef {{
          target {{
            ... on Commit {{
              history(first: 100) {{
                edges {{
                  node {{
                    committedDate
                    additions
                    deletions
                    author {{ user {{ login }} }}
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    """
    commits_data = run_query(commit_query)
    history = commits_data.get('data', {}).get('repository', {}).get('defaultBranchRef', {}).get('target', {}).get('history', {}).get('edges', [])

    if not history:
        st.warning("No commit data found.")
        st.stop()

    commit_df = pd.DataFrame([
        {
            "date": c['node']['committedDate'][:10],
            "user": c['node']['author']['user']['login'] if c['node']['author']['user'] else "Unknown",
            "additions": c['node']['additions'],
            "deletions": c['node']['deletions']
        } for c in history
    ])
    commit_df['date'] = pd.to_datetime(commit_df['date'])

    # Time ranges
    today = pd.to_datetime("today").normalize()
    last_week = today - timedelta(days=7)
    prev_week = today - timedelta(days=14)

    commits_recent = commit_df[(commit_df['date'] > last_week) & (commit_df['date'] <= today)]
    commits_prev = commit_df[(commit_df['date'] > prev_week) & (commit_df['date'] <= last_week)]

    def delta_percent(curr, prev):
        if prev == 0:
            return "N/A"
        change = ((curr - prev) / prev) * 100
        color = "green" if change >= 0 else "red"
        symbol = "+" if change >= 0 else ""
        return f"<span style='color:{color}'>{symbol}{change:.1f}% from last week</span>"

    # Pull Requests
    pr_query = f"""
    {{
      repository(owner: \"{owner}\", name: \"{repo}\") {{
        pullRequests(first: 50, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
          nodes {{
            title
            createdAt
            mergedAt
            additions
            deletions
            author {{ login }}
          }}
        }}
      }}
    }}
    """
    pr_data = run_query(pr_query)
    prs = pr_data.get("data", {}).get("repository", {}).get("pullRequests", {}).get("nodes", [])

    pr_df = pd.DataFrame()
    if prs:
        pr_df = pd.DataFrame([
            {
                "title": pr['title'],
                "author": pr['author']['login'] if pr['author'] else "Unknown",
                "created": pr['createdAt'][:10],
                "merged_at": pr['mergedAt'][:10] if pr['mergedAt'] else None,
                "additions": pr['additions'],
                "deletions": pr['deletions'],
                "review_time": (
                    (datetime.fromisoformat(pr['mergedAt'][:-1]) - datetime.fromisoformat(pr['createdAt'][:-1])).days
                    if pr['mergedAt'] else None
                )
            } for pr in prs
        ])

    # Summary Metrics
    st.subheader(":bar_chart: Performance Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='stMetric'><strong>Commits (7d)</strong><br>{len(commits_recent)}<br>{delta_percent(len(commits_recent), len(commits_prev))}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='stMetric'><strong>Total Contributors</strong><br>{commit_df['user'].nunique()}</div>", unsafe_allow_html=True)
    with col3:
        total_lines = int(commit_df[['additions', 'deletions']].sum().sum())
        st.markdown(f"<div class='stMetric'><strong>Total Lines Changed</strong><br>{total_lines}</div>", unsafe_allow_html=True)
    with col4:
        avg_review_time = pr_df['review_time'].dropna().mean() if not pr_df.empty else None
        art = f"{avg_review_time:.2f}" if avg_review_time else "N/A"
        st.markdown(f"<div class='stMetric'><strong>Avg Review Time (days)</strong><br>{art}</div>", unsafe_allow_html=True)

    # --- Charts ---
    c1, c2 = st.columns(2)
    with c1:
        commits_per_day = commit_df.groupby("date").size().reset_index(name="commits")
        fig1 = px.line(commits_per_day, x="date", y="commits", title="Commits Over Time", template="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        churn = commit_df.groupby("date")[['additions', 'deletions']].sum().reset_index()
        fig2 = px.area(churn, x="date", y=["additions", "deletions"], 
                       title="Additions vs Deletions", template="plotly_dark",
                       color_discrete_map={"additions": "green", "deletions": "red"})
        st.plotly_chart(fig2, use_container_width=True)

    # --- Pull Requests Table ---
    st.subheader(":inbox_tray: Recent Pull Requests")
    if not pr_df.empty:
        st.dataframe(pr_df[['title', 'author', 'created', 'merged_at', 'review_time']])

    # --- Recent Activity ---
    st.subheader(":hourglass: Recent Commit Activity")
    st.dataframe(commit_df.sort_values(by="date", ascending=False).head(10))

    status.empty()
