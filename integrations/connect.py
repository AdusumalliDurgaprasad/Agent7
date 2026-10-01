import os
import requests
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv


load_dotenv()


class Integrations:

    LINKEDIN_POST_URL = (
        "https://api.linkedin.com/rest/posts"
    )

    LINKEDIN_USERINFO_URL = (
        "https://api.linkedin.com/v2/userinfo"
    )

    LINKEDIN_VERSION = os.getenv(
        "LINKEDIN_VERSION",
        "202603"
    )

    GMAIL_ADDRESS = os.getenv(
        "GMAIL_ADDRESS"
    )

    GMAIL_APP_PASSWORD = os.getenv(
        "GMAIL_APP_PASSWORD"
    )

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465

    def __init__(self):

        self.linkedin_access_token = os.getenv(
            "LINKEDIN_ACCESS_TOKEN"
        )

        if not self.linkedin_access_token:
            raise ValueError(
                "LINKEDIN_ACCESS_TOKEN is missing from .env"
            )

        self.session = requests.Session()

        self.session.headers.update({
            "Authorization":
                f"Bearer {self.linkedin_access_token}",

            "Accept":
                "application/json"
        })

    def get_userinfo(self):

        response = self.session.get(
            self.LINKEDIN_USERINFO_URL,
            timeout=15
        )

        print(
            "LinkedIn userinfo status:",
            response.status_code
        )

        print(
            "LinkedIn userinfo response:",
            response.text
        )

        response.raise_for_status()

        return response.json()

    def get_author_urn(self):

        profile = self.get_userinfo()

        sub = profile.get("sub")

        if not sub:
            raise ValueError(
                "LinkedIn userinfo did not return a member ID."
            )

        return f"urn:li:person:{sub}"

    def create_text_post(
        self,
        text,
        publish=True
    ):

        if not text or not text.strip():

            return {
                "success": False,
                "status_code": None,
                "error": "Post content is empty."
            }

        author_urn = self.get_author_urn()

        payload = {

            "author":
                author_urn,

            "commentary":
                text.strip(),

            "visibility":
                "PUBLIC",

            "distribution": {

                "feedDistribution":
                    "MAIN_FEED",

                "targetEntities":
                    [],

                "thirdPartyDistributionChannels":
                    []

            },

            "lifecycleState":
                "PUBLISHED",

            "isReshareDisabledByAuthor":
                False
        }

        if not publish:

            return {
                "success": True,
                "dry_run": True,
                "payload": payload
            }

        headers = {

            "Authorization":
                f"Bearer {self.linkedin_access_token}",

            "Accept":
                "application/json",

            "Content-Type":
                "application/json",

            "Linkedin-Version":
                self.LINKEDIN_VERSION,

            "X-Restli-Protocol-Version":
                "2.0.0"
        }

        print(
            "\n======================================"
        )

        print(
            "      PUBLISHING TO LINKEDIN"
        )

        print(
            "======================================"
        )

        print(
            "Author:",
            author_urn
        )

        print(
            "\nPost:"
        )

        print(text)

        try:

            response = requests.post(

                self.LINKEDIN_POST_URL,

                headers=headers,

                json=payload,

                timeout=30
            )

        except requests.exceptions.RequestException as e:

            print(
                "LinkedIn request error:",
                e
            )

            return {

                "success":
                    False,

                "status_code":
                    None,

                "error":
                    str(e)
            }

        print(
            "\nLinkedIn HTTP status:",
            response.status_code
        )

        print(
            "LinkedIn response:",
            response.text
        )

        if response.status_code == 201:

            post_id = response.headers.get(
                "x-restli-id"
            )

            print(
                "\nLINKEDIN POST PUBLISHED"
            )

            print(
                "Post ID:",
                post_id
            )

            return {

                "success":
                    True,

                "status_code":
                    201,

                "post_id":
                    post_id,

                "response":
                    response.text
            }

        return {

            "success":
                False,

            "status_code":
                response.status_code,

            "error":
                response.text
        }

    def send_mail(
        self,
        recipient,
        subject,
        body
    ):

        if not self.GMAIL_ADDRESS:
            raise ValueError(
                "GMAIL_ADDRESS is missing."
            )

        if not self.GMAIL_APP_PASSWORD:
            raise ValueError(
                "GMAIL_APP_PASSWORD is missing."
            )

        message = EmailMessage()

        message["From"] = self.GMAIL_ADDRESS
        message["To"] = recipient
        message["Subject"] = subject

        message.set_content(body)

        with smtplib.SMTP_SSL(
            self.SMTP_SERVER,
            self.SMTP_PORT
        ) as smtp:

            smtp.login(
                self.GMAIL_ADDRESS,
                self.GMAIL_APP_PASSWORD
            )

            smtp.send_message(message)

        return True

    def close(self):

        self.session.close()