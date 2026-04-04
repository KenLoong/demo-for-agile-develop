# 🎓 UWA Skill-Swap
### *Connect. Exchange. Excel.*

**UWA Skill-Swap** is a web-based platform designed specifically for University of Western Australia students to exchange knowledge and skills. Whether you are a coding pro looking to learn guitar, or a linguist wanting to understand data science, this platform facilitates peer-to-peer learning through a persistent, user-friendly client-server application.

---

## 📖 Project Overview

### Purpose
In a university environment, students possess diverse talents beyond their primary degree. This application aims to:
*   **Bridge the knowledge gap** between different faculties.
*   **Promote community engagement** within the UWA campus.
*   **Provide a practical utility** for students to find tutors or hobbyist partners without financial barriers.

### Design & Features
*   **User Authentication:** Secure login/logout with Flask-Login; registration enforces `@student.uwa.edu.au` email and password hashing.
*   **Skill Management (CRUD):** Users can post skills, edit or delete their own listings.
*   **Dynamic Discovery:** Homepage with **jQuery AJAX** category filtering against `/api/filter`, plus keyword search (title and description).
*   **Interaction:** Comments on posts; **Express interest** with dashboard views for received and sent requests (including contact email).
*   **UI:** Responsive layouts with **Bootstrap 5**.

---

## 🛠 Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Python / Flask |
| **Database** | SQLite + SQLAlchemy (ORM) |
| **Frontend** | HTML5, Jinja2, Bootstrap 5, JavaScript |
| **Interactivity** | jQuery + AJAX |
| **Version Control** | Git / GitHub |

---

## 👥 Team Members

| UWA ID | Name | GitHub Account |
| :--- | :--- | :--- |
| `[24702822]` | Warson | [Warson Long](https://github.com/WarsonLong) |
| `[24319908]` | Dylan | [Yuxuan Xi](https://github.com/dylayXi) |
| `[24902808]` | Shawn | [Shawn Wang](https://github.com/Lipo021) |
| `[24684008]` | Nuwanga | [Nuwanga Niroshan](https://github.com/NuwangaNiroshan) |

---

## 🚀 How to run locally

### Prerequisites
* **Python 3.10+** (3.11+ recommended)
* `pip` (use a **virtual environment**; on macOS/Homebrew Python you may see an “externally managed” error if you skip the venv step)

### 1. Clone and enter the project
```bash
git clone <your-repository-url>
cd demo-for-agile-develop
```
*(Replace the folder name if your clone path differs.)*

### 2. Create and activate a virtual environment
```bash
python3 -m venv .venv
```
**macOS / Linux:**
```bash
source .venv/bin/activate
```
**Windows (cmd):**
```bat
.venv\Scripts\activate.bat
```
**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Database (choose one)

**Option A — Sample data (recommended for demos)**  
Resets the DB and inserts test users/posts/interests (see `seed.py` for emails and passwords):
```bash
python seed.py
```
Test logins (after seeding):
* `a@student.uwa.edu.au` / `password123`
* `b@student.uwa.edu.au` / `password123`

**Option B — Empty database**  
Create tables only (no sample rows):
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 5. Start the development server

**Recommended (creates tables automatically if you use `app.py` as entry point):**
```bash
python app.py
```
Then open **http://127.0.0.1:5000/** in your browser.

**Alternative — Flask CLI**  
If you use `flask run`, ensure tables exist first (run the `db.create_all()` one-liner in Option B once), then:
```bash
export FLASK_APP=app.py
# Optional: export FLASK_DEBUG=1
flask run
```
On Windows, use `set FLASK_APP=app.py` instead of `export`.

### Notes
* The SQLite file is **`database.db`** in the project root (ignored by Git per `.gitignore`). Each developer keeps their own local file.
* For production, move `SECRET_KEY` out of source code into an environment variable.

---

## 🧪 Tests

Automated tests are **not included** in this repository yet. If you add a `tests/` package, you can run them with:
```bash
python -m unittest discover tests
```

---

## 📜 Unit Learning Outcomes (CITS5505)
This project demonstrates:
*   Implementation of **Client-Server Architecture**.
*   Proficiency in **Server-side (Flask)** and **Client-side (JS/AJAX)** technologies.
*   Application of **Agile Methodologies** through iterative Git commits.
*   Secure handling of **Data Persistence** and user sessions.
