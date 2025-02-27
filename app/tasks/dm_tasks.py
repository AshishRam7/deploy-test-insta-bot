# app/tasks/dm_tasks.py
from app.core.celery_utils import celery
from app.utils.instagram_api import postmsg, get_access_token_for_account
from app.utils.llm_api import llm_response
from app.utils.sentiment import analyze_sentiment
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

@celery.task(name="send_dm")
def send_dm(conversation_id_to_process, message_queue_snapshot, account_id_to_use):
    """Celery task to process and respond to a conversation's messages."""
    try:
        if conversation_id_to_process not in message_queue_snapshot or not message_queue_snapshot[conversation_id_to_process]:
            logger.info(f"No messages to process for conversation: {conversation_id_to_process}. Task exiting.")
            return {"status": "no_messages_to_process", "conversation_id": conversation_id_to_process}

        messages = message_queue_snapshot[conversation_id_to_process]
        recipient_id = messages[0]["sender_id"]
        combined_text = "\n".join([msg["text"] for msg in messages])

        sentiment = analyze_sentiment(combined_text)
        logger.info(f"Sentiment Analysis Result: Sentiment: {sentiment}, Combined Text: '{combined_text}'")

        if sentiment == "Positive":
            llm_prompt_suffix = "Respond with a very enthusiastic and thankful tone, acknowledging the compliment. Keep it concise and friendly."
        elif sentiment == "Negative":
            llm_prompt_suffix = "Respond with an apologetic and helpful tone, asking for more details about the issue so we can improve. Keep it concise and professional."
        else:  # Neutral or mixed
            llm_prompt_suffix = "Respond in a helpful and neutral tone. Keep it concise and informative."

        system_prompt_content = ""
        with open("collection_system_prompt/system_prompt.txt", "r") as file: # Adjust path if needed
            system_prompt_content = file.read().strip()
        full_prompt = system_prompt_content + " Message/Conversation input from user: " + combined_text + " "

        try:
            response_text = llm_response(settings.gemini_api_key, settings.model_name, full_prompt)
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            if sentiment == "Positive":
                response_text = settings.default_dm_response_positive # Access from settings
            else:
                response_text = settings.default_dm_response_negative # Access from settings

        try:
            access_token_to_use = get_access_token_for_account(account_id_to_use)
            result = postmsg(access_token_to_use, recipient_id, response_text)
            logger.info(f"Sent combined response to {recipient_id} using account {account_id_to_use}. Result: {result}")
        except Exception as e:
            logger.error(f"Error sending message to {recipient_id} using account {account_id_to_use}: {e}")

        # --- Access and clear global message_queue and conversation_task_schedules ---
        from app.api.webhook import message_queue, conversation_task_schedules
        if conversation_id_to_process in message_queue:
            del message_queue[conversation_id_to_process]
            logger.info(f"Cleared message queue for conversation: {conversation_id_to_process}")
        if conversation_id_to_process in conversation_task_schedules:
            del conversation_task_schedules[conversation_id_to_process]
        # --- End global access ---

        return {"status": "success", "processed_conversation": conversation_id_to_process, "message_count": len(messages)}

    except Exception as e:
        logger.error(f"Error in send_dm task for conversation {conversation_id_to_process}: {e}")
        raise