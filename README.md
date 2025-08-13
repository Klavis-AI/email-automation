# Email Automation

A Python script for automated email sending using Resend API.

## Setup

1. Create and activate a Python 3 virtual environment, then install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create your environment file:
```bash
cp .env.example .env
```

3. Get your Resend API key from the [Resend dashboard](https://resend.com/api-keys) and put it in `.env`:
```env
RESEND_API_KEY=your_resend_api_key
```

4. Open `constants.py` and set your email configuration values:
- `FROM_EMAIL`
- `EMAIL_RECIPIENTS`
- `SUBJECT`
- `REPLY_TO` (optional)
- `ATTACHMENT_PATH` and `ATTACHMENT_NAME` (optional)

## Run it!

```bash
python main.py
```