import os
from dotenv import load_dotenv

load_dotenv()

RESEND_API_BASE_URL = "https://api.resend.com"
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
DELAY_SECONDS = 1 # resend api has a rate limit of max 2 requests per second.

# Email Configuration
FROM_EMAIL = "YOUR_FROM_EMAIL" # TODO: change to your email, note you can directly define alias in this string like "Zihao from Klavis AI <xxx@klavis.ai>"
EMAIL_RECIPIENTS = [     # TODO: Add recipient email addresses here
    "TO_EMAIL_1",
    "TO_EMAIL_2",
    "TO_EMAIL_3",
]
SUBJECT = "YOUR_SUBJECT" # TODO: change to your subject
REPLY_TO = None # optional

ATTACHMENT_PATH = "templates/example_attachment.pdf" # TODO: change to your attachment path, default is the example attachment in the templates folder
ATTACHMENT_NAME = "example_attachment.pdf" # TODO: change to your attachment name
