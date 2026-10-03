🔍 Campus Lost & Found Portal

<div align="center">

  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:0ea5e9,100:2563eb&height=180&section=header&text=Campus%20Lost%20%26%20Found%20Portal&fontSize=30&fontColor=ffffff&fontAlignY=36&animation=twinkle" width="100%" alt="Header Banner" />

  <br/>

  <a href="https://lost-found-portal-51t9.onrender.com/" target="_blank">
    <img src="https://img.shields.io/badge/🚀_Live_Demo-Render-46E3B7?style=for-the-badge&logo=render&logoColor=black" alt="Live Demo on Render" />
  </a>
  <a href="https://github.com/thahirahamed33-tech/lost-found-portal">
    <img src="https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Repo" />
  </a>

  <br/><br/>

  <img src="https://img.shields.io/badge/Status-Live_%26_Deployed-brightgreen?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />

</div>

<br/>

---

## 📌 About The Project

The **Campus Lost & Found Portal** is a web-based management platform designed for educational institutions and campus communities. It provides a centralized, user-friendly hub to report lost belongings, log found items, track claim statuses, and automatically notify users when a matching item is identified.

<br/>

## ✨ Key Features

- 📝 **Report Lost & Found Items**: Easily report missing or discovered items with category, description, and location metadata.
- 🔍 **Real-Time Item Search & Filter**: Instantly query campus database records by category, status, and campus location tags.
- 📧 **Automated Email Notifications**: Built-in Python SMTP email dispatcher (`test_email.py`) sending instant notification alerts when potential matches are discovered.
- 🗄️ **SQLite Data Storage**: Embedded relational database (`campus_lost_found.db`) ensuring persistent item tracking and claim verification logs.
- 🌐 **Production Cloud Hosting**: Deployed live on **Render** web services for fast, continuous availability.

<br/>

## 🛠️ Tech Stack & Architecture

| Component | Technology Used |
| :--- | :--- |
| **Backend & API** | Python 3, Flask Web Framework |
| **Database** | SQLite (`campus_lost_found.db`) |
| **Email Service** | Python SMTP / Custom Mailer (`test_email.py`) |
| **Frontend UI** | HTML5, Modern CSS3 (`styles.css`), JavaScript |
| **Deployment** | Cloud Web Service on Render |

<br/>

## 📂 Repository Structure

```text
lost-found-portal/
├── campus_lost_found.db   # SQLite relational database store
├── competencies.html      # Guidelines & portal overview interface
├── index.html             # Main dashboard & item reporting UI
├── requirements.txt       # Python environment dependencies
├── styles.css             # Custom campus portal UI stylesheet
├── test_email.py          # Email alert dispatcher & match verification script
└── test_route.py          # Server route handler & endpoint unit tests
```

<br/>

## 🚀 Live Demo & Access

Access the deployed application live in your browser:
👉 **[Launch Campus Lost & Found Portal](https://lost-found-portal-51t9.onrender.com/)**

<br/>

## 💻 Local Setup Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/thahirahamed33-tech/lost-found-portal.git
   cd lost-found-portal
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Backend Server:**
   ```bash
   python test_route.py
   ```

4. **Open in Browser:**
   Open `http://localhost:5000` or navigate to `index.html`.

<br/>

---

<div align="center">
  <sub>Developed by <b>Thahir Ahamed K</b> • Built with Python & Flask 🚀</sub>
</div>

https://lost-found-portal-51t9.onrender.com/
