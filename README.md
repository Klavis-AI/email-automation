# Email Automation

A Python script for automated email sending using Resend API.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Resend API key in `constants.py`

3. Update email lists in `email_lists.py`

## Usage

```bash
python main.py
```

## Features

- Batch email sending with templates
- Multiple HTML email templates support
- Attachment support
- Rate limiting between sends
- Detailed logging
