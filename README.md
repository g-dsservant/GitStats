# 🚀 GitStats — GitHub Analytics Dashboard

GitStats is a professional GitHub analytics dashboard built with Streamlit. It allows you to visualize individual and team-level performance using metrics like commits, pull requests, code churn, contributors, deployment status, and recent activity — all with theme toggling and responsive charts.

![Screenshot Placeholder](https://via.placeholder.com/800x400?text=GitStats+Dashboard+Screenshot)

---

## 🛠️ Features

- 📊 Total commits, pull requests, deployments
- 🔁 Code churn analysis (additions/deletions over time)
- 👥 Contributor performance
- 📦 Deployment status (latest deployments)
- 📆 Recent activity feed (commit + PR timeline)

---

## 🔐 GitHub Token Permissions

### ✅ Fine-Grained Token (Recommended)

Enable **read access** to the following:

- `Contents`
- `Metadata`
- `Pull requests`
- `Actions`
- `Deployments`
- `Issues`
- `Commit statuses`

And **allow access to the repositories** you want to analyze.

---

### 🔓 Classic Token (Legacy)

Minimum scopes required:

- `repo` – Full access to repo contents and commits
- `read:org` – To get contributor info in orgs
- `read:user` – To read profile of contributors
- `user:email` – (For email mapping, optional)
- `admin:repo_hook` – (Optional, if analyzing webhooks)

For public repositories only: `public_repo` is sufficient.

---

## 💻 How to Run the App Locally

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/gitstats.git
cd gitstats
```

### 2. Install Dependencies

```bash
pip install requests pandas streamlit plotly
```

### 3. Launch The Dashboard

```bash
streamlit run app.py
```

Enter the following when prompted:

    Your GitHub Personal Access Token (PAT)

    The owner (username or org)

    The repository name
