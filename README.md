# 🏥 Patient Management System (Flask + MySQL)

A web-based Patient Management System built using Flask and MySQL that allows an admin to:
- Register with email verification
- Login securely
- Add and manage patient records
- Record check-in/check-out times
- Assign doctors
- Track test results
- Reset forgotten passwords via secure email tokens

---

## 🚀 Features

- 🔐 Email confirmation and password reset via token links
- 📋 Patient registration, check-in/out with timestamps
- 👩‍⚕️ Doctor assignment for patients
- 📊 Patient test tracking
- 🧠 Built using Flask, MySQL, Jinja2, and Python 3

---

## 🧾 Project Structure

```bash
.
├── bali.py               # Main Flask app
├── key.py                # App secrets and salts
├── sdmail.py             # Email sender script using SMTP
├── tokenreset.py         # Token generation for password reset
├── requirements.txt      # Python dependencies
└── templates/            # HTML templates (not included in repo upload)



