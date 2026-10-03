<div align="center">

  <h1>🔍 Campus Lost & Found Portal</h1>

  <p><b>A full-stack Web Application for campus lost item reporting, matching, and automated email notifications</b></p>

  <br/>

  <a href="https://lost-found-portal-51t9.onrender.com/" target="_blank">
    <img src="https://img.shields.io/badge/Live_Demo-Render-46E3B7?style=for-the-badge&logo=render&logoColor=black" alt="Live Demo on Render" />
  </a>
  &nbsp;
  <a href="https://github.com/thahirahamed33-tech/lost-found-portal" target="_blank">
    <img src="https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Repo" />
  </a>

  <br/><br/>

  <img src="https://img.shields.io/badge/Status-Deployed_--_Active-brightgreen?style=flat-square" alt="Status" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white" alt="HTML5" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white" alt="CSS3" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black" alt="JavaScript" />

</div>

<br/>

---

## 📌 Executive Summary

The **Campus Lost & Found Portal** is an end-to-end web system tailored for educational institutions, college campuses, and community centers. It solves the real-world friction of locating lost items by providing a centralized database, search interface, claim management, and automated email notifications.

Users can quickly post details of items they have lost or found. When a matching item is identified in the system, automated notification services instantly inform the item owner to initiate recovery.

<br/>

## 🌐 Live Access

| Platform | URL |
| :--- | :--- |
| **Render Web Service** | [https://lost-found-portal-51t9.onrender.com/](https://lost-found-portal-51t9.onrender.com/) |
| **GitHub Repository** | [https://github.com/thahirahamed33-tech/lost-found-portal](https://github.com/thahirahamed33-tech/lost-found-portal) |

<br/>

## ✨ Key Features & Capabilities

### 1. 📝 Item Submission & Categorization
- **Lost Item Reporting**: Submit details including item name, category (Electronics, ID Cards, Bags, Accessories, Books, etc.), description, location lost, and date.
- **Found Item Logging**: Good Samaritans or campus security staff can record found items with precise pickup location and contact details.

### 2. 🔍 Real-Time Search & Filtering
- Dynamic search functionality allowing users to filter reported items by category, location, status, or date range.
- Lightweight and fast querying powered by SQLite database indexes.

### 3. 📧 Automated Email Notification Engine
- Integrated Python email dispatcher module (`test_email.py`).
- Triggered automatically when potential matches or claim requests are lodged, ensuring users are informed immediately.

### 4. 📊 Campus Competencies & Claims Management
- Dedicated competency view (`competencies.html`) detailing campus guidelines, claim verification workflows, and security protocols.
- Structured claim submission to verify item ownership before handoff.

<br/>

## 🛠️ Technology Stack

| Layer | Technology | Function |
| :--- | :--- | :--- |
| **Backend Framework** | **Python 3 / Flask** | Server routes, request processing, business logic |
| **Database** | **SQLite (`campus_lost_found.db`)** | Persistent storage for item entries, user claims, and match logs |
| **Email Service** | **Python SMTP / Mailer** | Automated notification dispatching (`test_email.py`) |
| **Frontend Layout** | **HTML5 & CSS3 (`styles.css`)** | Custom responsive UI designed for mobile and desktop screens |
| **Client Scripting** | **JavaScript** | Dynamic form validation and interactive item filtering |
| **Cloud Hosting** | **Render Platform** | WSGI application deployment and production hosting |

<br/>

## 📂 Project Architecture & File Breakdown

```text
lost-found-portal/
├── campus_lost_found.db   # Relational SQLite database storing lost/found logs & user claims
├── competencies.html      # Campus guidelines & system competency dashboard UI
├── index.html             # Main user portal dashboard for submitting & viewing items
├── requirements.txt       # Python package dependencies (Flask, Gunicorn, Jinja2, etc.)
├── styles.css             # Responsive styling rules, color variables & layout grid
├── test_email.py          # Email service dispatcher for match notifications & alert testing
└── test_route.py          # Flask route definitions, backend logic & unit test handlers
```

### Module Responsibilities:
- `test_route.py`: Handles HTTP routes, database connection pool, API payloads, and response rendering.
- `campus_lost_found.db`: Stores structured tables for items (`item_id`, `type`, `title`, `description`, `location`, `status`, `date_posted`, `contact_email`).
- `test_email.py`: Configures SMTP server parameters and formats HTML match notifications.

<br/>

## 💻 Local Installation & Setup Guide

Follow these steps to run the application locally on your machine:

### Prerequisites
- Python 3.8 or higher installed
- Git installed

### Step-by-step Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/thahirahamed33-tech/lost-found-portal.git
   cd lost-found-portal
   ```

2. **Create & activate a virtual environment (optional but recommended):**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the application:**
   ```bash
   python test_route.py
   ```

5. **Access the portal:**
   Open your browser and navigate to `http://127.0.0.1:5000` or open `index.html`.

<br/>

## 🚀 Cloud Deployment Details (Render)

This project is configured for seamless deployment on **Render**:

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn test_route:app` (or `python test_route.py`)
- **Environment**: Python 3.x WSGI Environment
- **Live URL**: [https://lost-found-portal-51t9.onrender.com/](https://lost-found-portal-51t9.onrender.com/)

<br/>

## 📈 Future Roadmap & Enhancements

- [ ] Image Uploads for reported lost/found items using cloud storage.
- [ ] User Authentication & Campus SSO (Single Sign-On) Integration.
- [ ] Admin Analytics Dashboard for tracking recovery metrics and lost item statistics.
- [ ] Location Mapping with interactive campus pin drops.

<br/>

---

<div align="center">
  <p><b>Developed by Thahir Ahamed K</b></p>
  <p><i>Building practical full-stack solutions for campus communities 🚀</i></p>
</div>
