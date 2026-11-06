# 🧠 Captcha Lab — Brainz Technology

A full-stack **Django-based CAPTCHA testing & verification lab** that lets you generate, solve, detect, and verify CAPTCHAs from multiple providers — all from a single dashboard.

---

## ✨ Features

- 🖼️ **Generate** — Creates custom text-image CAPTCHAs on the fly
- 🤖 **Solve** — Auto-solves CAPTCHAs using Tesseract OCR + OpenCV preprocessing
- 📊 **Batch Test** — Runs up to 200 solve attempts to benchmark OCR accuracy
- 🔍 **Detect** — Identifies which CAPTCHA provider a webpage uses (from raw HTML)
- ✅ **Verify** — Sends tokens to Google reCAPTCHA, hCaptcha & Cloudflare Turnstile APIs
- 📈 **Stats** — Tracks success rates, timing, and failure reasons in real time

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.1.3 |
| Image Generation | Pillow |
| Image Preprocessing | OpenCV (headless), NumPy |
| OCR Engine | Tesseract + pytesseract |
| HTTP Client | requests |
| Config Management | python-dotenv |
| Database | SQLite (default) |

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.11+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed on your system

### 1. Clone the repository

```bash
git clone https://github.com/ahm455/captcha.git
cd captcha
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

Edit `.env`:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe  # adjust for your OS

# Google reCAPTCHA
RECAPTCHA_SITEKEY=your-sitekey
RECAPTCHA_SECRET=your-secret

# hCaptcha
HCAPTCHA_SITEKEY=your-sitekey
HCAPTCHA_SECRET=your-secret

# Cloudflare Turnstile
TURNSTILE_SITEKEY=your-sitekey
TURNSTILE_SECRET_PASS=your-secret-pass
TURNSTILE_SECRET_FAIL=your-secret-fail
TURNSTILE_SECRET_SPENT=your-secret-spent
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start the server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000** in your browser.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Main dashboard |
| `POST` | `/api/generate` | Generate a new CAPTCHA image |
| `POST` | `/api/solve` | Solve a CAPTCHA (by ID or file upload) |
| `POST` | `/api/batch` | Batch solve test (accuracy benchmark) |
| `POST` | `/api/detect` | Detect CAPTCHA provider from HTML |
| `POST` | `/api/verify` | Verify a CAPTCHA token with provider |
| `GET` | `/api/stats/` | Get attempt stats & history |

---

## 📁 Project Structure

```
captcha/
├── captcha_app/
│   ├── services/
│   │   ├── generator.py   # Draws CAPTCHA images
│   │   ├── solver.py      # OCR solve pipeline
│   │   ├── detector.py    # Detects provider from HTML
│   │   ├── verifier.py    # Calls provider verify APIs
│   │   ├── stats.py       # Records attempt results
│   │   └── config.py      # API keys & endpoints
│   ├── models.py          # Challenge, AttemptLog, UsedToken
│   ├── views.py           # REST API views
│   ├── urls.py            # App URL routing
│   └── templates/         # Frontend HTML
├── config/                # Django settings & routing
├── .env.example           # Environment variable template
├── requirements.txt       # Python dependencies
└── manage.py
```

---

## 🔐 Security Notes

- Never commit your `.env` file — it's listed in `.gitignore`
- Use a strong random `SECRET_KEY` in production
- Set `DEBUG=False` and configure `ALLOWED_HOSTS` before deploying
- Token replay attacks are prevented via SHA-256 fingerprinting

---

## 📄 License

This project is for educational purposes.

---

