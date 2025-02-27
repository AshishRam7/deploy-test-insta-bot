# app/api/webhook.py
from fastapi import APIRouter, Request, Response, HTTPException, Query
from fastapi.responses import HTMLResponse
from sse_starlette.sse import EventSourceResponse
from typing import List, Dict
import json
import asyncio
from collections import deque
import logging
from datetime import datetime
import random
import os

from app.utils.webhook_utils import verify_webhook_signature, parse_instagram_webhook
from app.utils.sentiment import analyze_sentiment
from app.tasks.dm_tasks import send_dm
from app.tasks.comment_tasks import send_delayed_reply
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Global variables (consider alternatives for larger apps - dependency injection) ---
WEBHOOK_EVENTS = deque(maxlen=100)
CLIENTS: List[asyncio.Queue] = []
message_queue = {}  # Store messages per conversation_id
conversation_task_schedules = {}  # Track scheduled task IDs per conversation
# --- End Global Variables ---


def load_events_from_file():
    """Load webhook events from the JSON file (if it exists)."""
    global WEBHOOK_EVENTS
    webhook_file = settings.webhook_file # Access from settings
    if os.path.exists(webhook_file):
        try:
            with open(webhook_file, "r") as f:
                events = json.load(f)
                WEBHOOK_EVENTS.extend(events)
        except Exception as e:
            logger.error(f"Failed to load events from file: {e}")

def save_events_to_file():
    """Save webhook events to a JSON file."""
    webhook_file = settings.webhook_file # Access from settings
    with open(webhook_file, "w") as f:
        json.dump(list(WEBHOOK_EVENTS), f, indent=4)


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """Verify webhook from Meta."""
    if hub_mode == "subscribe" and hub_verify_token == settings.verify_token:
        logger.info("Webhook verification successful")
        return Response(content=hub_challenge, media_type="text/html")
    logger.error("Webhook verification failed")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def webhook_handler(request: Request):  # Renamed to webhook_handler to avoid name clash with module
    """Handle incoming webhook events from Meta."""
    raw_body = await request.body()
    logger.info(f"Received raw webhook payload: {raw_body.decode('utf-8')}")

    if not await verify_webhook_signature(request, raw_body):
        raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        payload = json.loads(raw_body)
        event_with_time = {
            "timestamp": datetime.now().isoformat(),
            "payload": payload
        }

        # Parse the webhook and get events
        parsed_events = parse_instagram_webhook(event_with_time)
        logger.info("Parsed Webhook Events:")
        for event in parsed_events:
            logger.info(json.dumps(event, indent=2))

            # Handle different types of events
            if event["type"] == "direct_message" and event["is_echo"] == False:
                conversation_id = str(event["sender_id"]) + "_" + str(event["recipient_id"])
                account_id_to_use = str(event["recipient_id"])  # Use recipient_id as account_id

                if conversation_id not in message_queue:
                    # New conversation
                    message_queue[conversation_id] = [event]
                    delay = random.randint(60, 120)  # 1-2 minutes
                    task = send_dm.apply_async(
                        args=(conversation_id, message_queue.copy(), account_id_to_use),
                        countdown=delay, expires=delay + 3600
                    )
                    conversation_task_schedules[conversation_id] = task.id
                    logger.info(f"Scheduled initial DM task for new conversation: {conversation_id}, task_id: {task.id}, delay: {delay}s, account_id: {account_id_to_use}")

                else:
                    # Existing conversation - add new message and re-schedule
                    message_queue[conversation_id].append(event)
                    logger.info(f"Added message to existing conversation: {conversation_id}")

                    if conversation_id in conversation_task_schedules:
                        task_id_to_extend = conversation_task_schedules[conversation_id]
                        celery.control.revoke(task_id_to_extend, terminate=False)
                        del conversation_task_schedules[conversation_id]

                        new_delay = 30  # Shorter delay
                        new_task = send_dm.apply_async(
                            args=(conversation_id, message_queue.copy(), account_id_to_use),
                            countdown=new_delay, expires=new_delay + 3600
                        )
                        conversation_task_schedules[conversation_id] = new_task.id
                        logger.info(f"Re-scheduled DM task for conversation: {conversation_id}, task_id: {new_task.id}, new delay: {new_delay}s (due to new message), account_id: {account_id_to_use}")

            elif event["type"] == "comment":
                if event["to_id"] in json.loads(settings.accounts_json): # Directly use settings
                    if event["from_id"] == event["to_id"]:
                        logger.info(f"Comment from same account ID: {event['from_id']}. Ignoring.")
                        continue  # Use continue to move to the next event
                    else:
                        sentiment = analyze_sentiment(event["text"])
                        if sentiment == "Positive":
                            message_to_be_sent = settings.default_comment_response_positive # Access from settings
                        else:
                            message_to_be_sent = settings.default_comment_response_negative # Access from settings

                        account_id_to_use = event["to_id"]
                        delay = random.randint(60, 120)  # 1-2 minutes
                        send_delayed_reply.apply_async(
                            args=(event["comment_id"], message_to_be_sent, account_id_to_use),
                            countdown=delay, expires=delay + 600
                        )
                        logger.info(f"Scheduled reply task for comment {event['comment_id']} in {delay} seconds using account {account_id_to_use}")
                else:
                    logger.warning(f"Comment for unconfigured account ID: {event['to_id']}. Ignoring.")

        # Store event and notify clients
        WEBHOOK_EVENTS.append(event_with_time)
        save_events_to_file()

        # Notify connected SSE clients
        for client_queue in CLIENTS:
            await client_queue.put(event_with_time)

        return {"success": True, "parsed_events": parsed_events}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")


@router.get("/webhook_events")
async def get_webhook_events():
    """Retrieve all stored webhook events."""
    return {"events": list(WEBHOOK_EVENTS)}


async def event_generator(request: Request):
    """Generate Server-Sent Events."""
    client_queue = asyncio.Queue()
    CLIENTS.append(client_queue)

    try:
        # Send existing events
        for event in WEBHOOK_EVENTS:
            yield f"data: {json.dumps(event)}\n\n"

        # Listen for new events
        while not await request.is_disconnected():
            try:
                event = await asyncio.wait_for(client_queue.get(), timeout=30)
                yield f"data: {json.dumps(event)}\n\n"
            except asyncio.TimeoutError:
                yield ": keepalive\n\n"

    finally:
        CLIENTS.remove(client_queue)


@router.get("/events")
async def events(request: Request):
    """SSE endpoint for real-time webhook events."""
    return EventSourceResponse(event_generator(request))