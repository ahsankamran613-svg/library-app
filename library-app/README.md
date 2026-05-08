# LibraryMS — Flask Library Book Manager

A simple Library Management System built with Flask + SQLite, designed for a Selenium/Jenkins CI assignment.

## Features
- User Registration & Login
- Add / Edit / Delete Books
- Search books by title or author
- Borrow & Return books

---

## Local Setup (Without Docker)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install flask flask-sqlalchemy werkzeug

# 3. Run the app
python app.py
# Visit http://localhost:5000
```

---

## Running with Docker

```bash
# Build and run
docker build -t library-app .
docker run -d -p 5000:5000 --name library-app library-app

# Visit http://localhost:5000
```

---

## Running Selenium Tests Locally

```bash
# Make sure app is running on port 5000, then:
pip install selenium pytest pytest-html

# Run tests
pytest tests/test_library.py -v --html=report.html --self-contained-html

# Or with custom URL:
APP_URL=http://your-server:5000 pytest tests/test_library.py -v
```

---

## Jenkins Pipeline

The `Jenkinsfile` defines a 5-stage pipeline:
1. **Checkout** — Pulls code from GitHub
2. **Build App Image** — Builds Flask app Docker image
3. **Deploy App** — Starts app container on port 5000
4. **Build Test Image** — Builds Selenium test Docker image
5. **Run Tests** — Executes all 16 test cases, publishes HTML report

After tests, an email is sent to the person who triggered the push.

### Prerequisites on Jenkins/EC2:
- Docker installed
- Jenkins plugins: Pipeline, HTML Publisher, Email Extension, JUnit
- Configure SMTP in Jenkins → Manage Jenkins → Configure System

---

## Test Cases Summary

| # | Test | Description |
|---|------|-------------|
| TC-01 | Home page load | App loads and redirects correctly |
| TC-02 | Register page loads | Registration form renders |
| TC-03 | Register new user | Successful registration |
| TC-04 | Duplicate username | Error on duplicate register |
| TC-05 | Login page loads | Login form renders |
| TC-06 | Invalid login | Error on wrong credentials |
| TC-07 | Valid login | Redirects to /books |
| TC-08 | Auth protection | /books redirects to login when not authenticated |
| TC-09 | Add book page | Add form renders |
| TC-10 | Add book validation | Missing fields shows error |
| TC-11 | Add book success | Book added and redirected |
| TC-12 | Book in list | Added book visible in table |
| TC-13 | Search book | Search filters by title |
| TC-14 | Edit book | Book title can be updated |
| TC-15 | Edited book visible | Updated title in list |
| TC-16 | Borrow book | Status changes on borrow |
| TC-17 | Return button appears | Return button visible after borrow |
| TC-18 | Return book | Book returned successfully |
| TC-19 | Delete book | Book removed from list |
| TC-20 | Logout | Session cleared, redirect to login |
