# app/utils/webhook_utils.py
import hashlib
import hmac
import json
import logging
from fastapi import Request, HTTPException
from app.core.config import settings

logger = logging.getLogger(__name__)

def verify_webhook_signature(request: Request, raw_body: bytes) -> bool:
    """Verify that the webhook request is from Meta."""
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not signature or not signature.startswith("sha256="):
        logger.error("Signature is missing or not properly formatted")
        return False

    expected_signature = hmac.new(
        settings.app_secret.encode('utf-8'), # Use settings
        raw_body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature[7:], expected_signature):
        logger.error(f"Signature mismatch: {signature[7:]} != {expected_signature}")
        return False
    return True

def parse_instagram_webhook(data):
    """Parse Instagram webhook events for direct messages and comments."""
    results = []
    try:
        event_timestamp = data.get("timestamp")
        payload = data.get("payload", data) if isinstance(data, dict) else data
        entries = payload.get("entry", [])
        logger.info(f"Number of entries found: {len(entries)}")

        for entry in entries:
            messaging_events = entry.get("messaging", [])
            for messaging_event in messaging_events:
                sender = messaging_event.get("sender", {})
                recipient = messaging_event.get("recipient", {})
                message = messaging_event.get("message", {})

                if message:
                    message_event_details = {
                        "type": "direct_message",
                        "sender_id": sender.get("id"),
                        "recipient_id": recipient.get("id"),
                        "text": message.get("text"),
                        "message_id": message.get("mid"),
                        "timestamp": event_timestamp,
                        "entry_time": entry.get("time"),
                        "is_echo": message.get("is_echo", False)
                    }
                    results.append(message_event_details)

            changes = entry.get("changes", [])
            for change in changes:
                if change.get("field") == "comments":
                    comment_value = change.get("value", {})
                    if comment_value:
                        comment_details = {
                            "type": "comment",
                            "comment_id": comment_value.get("id"),
                            "text": comment_value.get("text"),
                            "timestamp": event_timestamp,
                            "media_id": comment_value.get("media", {}).get("id"),
                            "media_type": comment_value.get("media", {}).get("media_product_type"),
                            "from_username": comment_value.get("from", {}).get("username"),
                            "from_id": comment_value.get("from", {}).get("id"),
                            "to_id": entry.get("id"),
                            "entry_time": entry.get("time")
                        }
                        results.append(comment_details)

    except Exception as e:
        logger.error(f"Parsing error: {e}")
        logger.error(f"Problematic payload: {json.dumps(data, indent=2)}")
    return results