# app/utils/instagram_api.py
import requests
import logging
import json
from app.core.config import settings

logger = logging.getLogger(__name__)

ACCOUNT_CREDENTIALS = {}  # Initialize here

def load_account_credentials():
    global ACCOUNT_CREDENTIALS
    try:
        ACCOUNT_CREDENTIALS = json.loads(settings.accounts_json) # Use settings
        logger.info("Account credentials loaded from environment variable ACCOUNTS.")
    except json.JSONDecodeError:
        ACCOUNT_CREDENTIALS = {}
        logger.error("Failed to parse ACCOUNTS environment variable as JSON. Using empty account credentials.")

load_account_credentials() # Load credentials when module is imported

def get_access_token_for_account(account_id):
    """Retrieve access token for a given account ID."""
    access_token = ACCOUNT_CREDENTIALS.get(account_id)
    if not access_token:
        logger.error(f"No access token found for account ID: {account_id}")
        raise ValueError(f"No access token found for account ID: {account_id}")
    return access_token

def postmsg(access_token, recipient_id, message_to_be_sent):
    """Sends a direct message to Instagram."""
    logger.info(f"Post Function Triggered: Sending DM to recipient {recipient_id}")
    url = "https://graph.instagram.com/v21.0/me/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    json_body = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_to_be_sent
        }
    }
    response = requests.post(url, headers=headers, json=json_body)
    data = response.json()
    logger.info(f"Response from Instagram API: {data}")
    return data

def sendreply(access_token, comment_id, message_to_be_sent):
    """Sends a reply to an Instagram comment."""
    logger.info(f"Send Reply Function Triggered: Sending reply to comment {comment_id}")
    url = f"https://graph.instagram.com/v22.0/{comment_id}/replies"
    params = {
        "message": message_to_be_sent,
        "access_token": access_token
    }
    response = requests.post(url, params=params)
    data = response.json()
    logger.info(f"Response from Instagram Reply API: {data}")
    return data