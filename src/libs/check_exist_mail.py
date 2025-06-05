import re
import smtplib
from verify_email import verify_email
import requests
import dns.resolver
import os
from dotenv import load_dotenv
load_dotenv()


# def is_valid_email(email):
#     pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
#     return re.match(pattern, email) is not None


def is_valid_email(email):
    url = f'https://apps.emaillistverify.com/api/verifyEmail?secret={os.getenv("API_EMAIL_KEY")}&email={email}'
    response = requests.get(url)

    if response.status_code == 200:
        result = response.text.strip()

        valid_statuses = ["ok", "catch_all"]

        return result in valid_statuses
    else:
        return False