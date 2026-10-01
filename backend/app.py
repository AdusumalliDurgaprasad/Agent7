import os
import re
import time
import json
import threading
from pathlib import Path

import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv


# ============================================================
# PATH / ENV
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in os.sys.path:
    os.sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")


# ============================================================
# CONFIG
# ============================================================

WHATSAPP_ACCESS_TOKEN = os.getenv(
    "WHATSAPP_ACCESS_TOKEN",
    ""
).strip()

WHATSAPP_VERIFY_TOKEN = os.getenv(
    "WHATSAPP_VERIFY_TOKEN",
    ""
).strip()

PHONE_NUMBER_ID = os.getenv(
    "PHONE_NUMBER_ID",
    ""
).strip()

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "gemma3:4b"
).strip()

GRAPH_API_VERSION = "v21.0"

OLLAMA_URL = (
    "http://127.0.0.1:11434/api/generate"
)

app = Flask(__name__)


# ============================================================
# IMPORT AGENTS
# ============================================================

from posts import post_agent
from comments import comment_agent
from jobs import jobs_agent


# ============================================================
# MEMORY SYSTEM
# ============================================================

from memory.conversation_memory import (
    initialize_conversation_memory,
    start_conversation,
    save_message
)

from memory.memory_context import (
    format_memory_for_ai
)


# ============================================================
# INITIALIZE MEMORY
# ============================================================

try:

    initialize_conversation_memory()

    print("Agent7 memory: AVAILABLE")

except Exception as e:

    print(
        "WARNING: Agent7 memory initialization failed:"
    )

    print(e)


# ============================================================
# MEMORY CONVERSATION MAPPING
# ============================================================

MEMORY_SESSION_FILE = (
    BASE_DIR / "backend" / "memory_sessions.json"
)

memory_sessions_lock = threading.Lock()


def load_memory_sessions():

    try:

        if not MEMORY_SESSION_FILE.exists():
            return {}

        with open(
            MEMORY_SESSION_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, dict):
            return data

        return {}

    except Exception as e:

        print(
            "MEMORY SESSION LOAD ERROR:"
        )

        print(e)

        return {}


def save_memory_sessions(data):

    try:

        MEMORY_SESSION_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        temporary_file = (
            MEMORY_SESSION_FILE.with_suffix(".tmp")
        )

        with open(
            temporary_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False
            )

        os.replace(
            temporary_file,
            MEMORY_SESSION_FILE
        )

        return True

    except Exception as e:

        print(
            "MEMORY SESSION SAVE ERROR:"
        )

        print(e)

        return False


def get_memory_conversation_id(sender):

    sender = str(sender)

    with memory_sessions_lock:

        sessions = load_memory_sessions()

        conversation_id = sessions.get(
            sender
        )

        if conversation_id:
            return conversation_id

        conversation_id = start_conversation(
            "Agent7 Chat Conversation"
        )

        sessions[sender] = conversation_id

        save_memory_sessions(
            sessions
        )

        print(
            f"New memory conversation created for {sender}"
        )

        return conversation_id


# ============================================================
# LINKEDIN INTEGRATION
# ============================================================

try:

    from integrations.connect import Integrations

    integrations = Integrations()

    LINKEDIN_AVAILABLE = True

    print(
        "LinkedIn integration: AVAILABLE"
    )

except Exception as e:

    integrations = None

    LINKEDIN_AVAILABLE = False

    print(
        "WARNING: LinkedIn integration unavailable:"
    )

    print(e)


# ============================================================
# PENDING POSTS
# ============================================================

# IMPORTANT:
#
# Pending posts are stored in a JSON file instead of only
# being stored in RAM.
#
# This means:
#
# Process 1:
#     create post
#
# Process 2:
#     OK, SHARE
#
# can still find the pending post.
#
# It also survives an Agent7 restart.

PENDING_POST_FILE = (
    BASE_DIR / "backend" / "pending_posts.json"
)

PENDING_POST_TTL = 30 * 60

pending_posts_lock = threading.Lock()


def load_pending_posts():

    try:

        if not PENDING_POST_FILE.exists():
            return {}

        with open(
            PENDING_POST_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, dict):
            return data

        return {}

    except Exception as e:

        print(
            "PENDING POST LOAD ERROR:"
        )

        print(e)

        return {}


def save_pending_posts_file(data):

    try:

        PENDING_POST_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        temporary_file = (
            PENDING_POST_FILE.with_suffix(".tmp")
        )

        with open(
            temporary_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False
            )

        os.replace(
            temporary_file,
            PENDING_POST_FILE
        )

        return True

    except Exception as e:

        print(
            "PENDING POST SAVE ERROR:"
        )

        print(e)

        return False


# ============================================================
# PENDING POST MANAGEMENT
# ============================================================

def save_pending_post(
    sender,
    post_text
):

    sender = str(sender)

    with pending_posts_lock:

        data = load_pending_posts()

        data[sender] = {
            "text": post_text,
            "created_at": time.time()
        }

        save_pending_posts_file(
            data
        )

    print(
        f"PENDING POST SAVED FOR {sender}"
    )


def get_pending_post(sender):

    sender = str(sender)

    with pending_posts_lock:

        data = load_pending_posts()

        pending = data.get(
            sender
        )

        if not pending:
            return None

        created_at = pending.get(
            "created_at",
            0
        )

        try:

            age = (
                time.time()
                - float(created_at)
            )

        except Exception:

            age = PENDING_POST_TTL + 1

        if age > PENDING_POST_TTL:

            data.pop(
                sender,
                None
            )

            save_pending_posts_file(
                data
            )

            print(
                f"PENDING POST EXPIRED FOR {sender}"
            )

            return None

        post_text = pending.get(
            "text",
            ""
        )

        if not post_text:
            return None

        return post_text


def clear_pending_post(sender):

    sender = str(sender)

    with pending_posts_lock:

        data = load_pending_posts()

        if sender in data:

            data.pop(
                sender,
                None
            )

            save_pending_posts_file(
                data
            )

            print(
                f"PENDING POST CLEARED FOR {sender}"
            )


def get_pending_post_count():

    with pending_posts_lock:

        data = load_pending_posts()

        return len(data)


# ============================================================
# WEBHOOK DEDUPLICATION
# ============================================================

processed_messages = {}

processed_lock = threading.Lock()

MESSAGE_TTL = 5 * 60


def cleanup_processed_messages():

    now = time.time()

    with processed_lock:

        expired = [
            message_id
            for message_id, timestamp
            in processed_messages.items()
            if now - timestamp > MESSAGE_TTL
        ]

        for message_id in expired:

            processed_messages.pop(
                message_id,
                None
            )


def is_duplicate_message(message_id):

    if not message_id:
        return False

    cleanup_processed_messages()

    with processed_lock:

        if message_id in processed_messages:
            return True

        processed_messages[
            message_id
        ] = time.time()

    return False


# ============================================================
# WHATSAPP HELPERS
# ============================================================

def normalize_phone_number(number):

    if not number:
        return ""

    return re.sub(
        r"[^\d]",
        "",
        number
    )


def send_whatsapp_message(
    recipient,
    message,
    phone_number_id=None
):

    recipient = normalize_phone_number(
        recipient
    )

    phone_number_id = (
        phone_number_id
        or PHONE_NUMBER_ID
    )

    if not WHATSAPP_ACCESS_TOKEN:

        print(
            "ERROR: WHATSAPP_ACCESS_TOKEN is missing."
        )

        return False

    if not phone_number_id:

        print(
            "ERROR: WhatsApp Phone Number ID is missing."
        )

        return False

    if not recipient:

        print(
            "ERROR: WhatsApp recipient is missing."
        )

        return False

    url = (
        f"https://graph.facebook.com/"
        f"{GRAPH_API_VERSION}/"
        f"{phone_number_id}/messages"
    )

    headers = {
        "Authorization":
            f"Bearer {WHATSAPP_ACCESS_TOKEN}",

        "Content-Type":
            "application/json",
    }

    payload = {

        "messaging_product":
            "whatsapp",

        "to":
            recipient,

        "type":
            "text",

        "text": {
            "body": message
        }
    }

    try:

        response = requests.post(

            url,

            headers=headers,

            json=payload,

            timeout=30
        )

        print(
            f"WhatsApp API status: "
            f"{response.status_code}"
        )

        if response.status_code not in (
            200,
            201
        ):

            print(
                "WhatsApp API error:"
            )

            print(
                response.text
            )

            return False

        print(
            "WhatsApp message sent successfully."
        )

        return True

    except Exception as e:

        print(
            "WhatsApp send error:"
        )

        print(e)

        return False


def send_long_whatsapp_message(
    recipient,
    message,
    phone_number_id=None
):

    if not message:
        return False

    max_length = 3500

    chunks = [
        message[i:i + max_length]
        for i in range(
            0,
            len(message),
            max_length
        )
    ]

    success = True

    for chunk in chunks:

        result = send_whatsapp_message(

            recipient,

            chunk,

            phone_number_id
        )

        if not result:
            success = False

    return success


# ============================================================
# OLLAMA
# ============================================================

def ask_ollama(prompt):

    payload = {

        "model":
            OLLAMA_MODEL,

        "prompt":
            prompt,

        "stream":
            False
    }

    try:

        response = requests.post(

            OLLAMA_URL,

            json=payload,

            timeout=120
        )

        print(
            f"Ollama status: "
            f"{response.status_code}"
        )

        if response.status_code != 200:

            print(
                "Ollama error:"
            )

            print(
                response.text
            )

            return (
                "Sorry, I couldn't "
                "process that right now."
            )

        data = response.json()

        return data.get(
            "response",
            "Sorry, I couldn't generate a response."
        ).strip()

    except Exception as e:

        print(
            "Ollama exception:"
        )

        print(e)

        return (
            "Sorry, I couldn't "
            "process that right now."
        )


# ============================================================
# MEMORY-AWARE OLLAMA BRIDGE
# ============================================================

memory_context_local = threading.local()

_original_ask_ollama = ask_ollama


def ask_ollama(prompt):

    memory_context = getattr(
        memory_context_local,
        "context",
        ""
    )

    if memory_context:

        prompt = f"""
You are Agent7, my personal LinkedIn AI assistant.

You have access to the user's previous conversation
and long-term memory below.

Use this memory when it is relevant.

Do not mention that you are reading a memory database.

Do not invent information that is not present in the memory.

================ MEMORY ================

{memory_context}

================ END MEMORY ================

USER REQUEST:

{prompt}
"""

    return _original_ask_ollama(
        prompt
    )


# ============================================================
# REQUEST DETECTION
# ============================================================

def is_comment_request(message):

    text = message.lower().strip()

    if "comment" not in text:
        return False

    comment_patterns = [

        "comment on",
        "comment for",
        "write a comment",
        "generate a comment",
        "linkedin comment",
        "create a comment",

    ]

    return any(
        pattern in text
        for pattern in comment_patterns
    )


def is_post_request(message):

    text = message.lower().strip()

    post_patterns = [

        "create a post",
        "write a post",
        "generate a post",
        "linkedin post",
        "make a post",
        "create linkedin",

        "post into linkedin",
        "post to linkedin",
        "post on linkedin",

        "publish on linkedin",
        "publish to linkedin",

        "create linkedin post",
        "write linkedin post",
        "generate linkedin post",

    ]

    return any(
        pattern in text
        for pattern in post_patterns
    )


def is_publish_request(message):

    text = message.lower().strip()

    # Normalize commas and repeated spaces.
    normalized = re.sub(
        r"[\s,]+",
        " ",
        text
    ).strip()

    publish_patterns = [

        "share this post into my linkedin",
        "share this post to my linkedin",
        "share this into my linkedin",
        "share this to my linkedin",

        "publish this post on linkedin",
        "publish this post to linkedin",

        "post this on linkedin",
        "post this to linkedin",

        "publish it on linkedin",
        "publish it to linkedin",

        "share it on linkedin",
        "share it to linkedin",

        "ok share",
        "okay share",

        "share",
        "publish",

    ]

    return (
        normalized in publish_patterns
        or text in publish_patterns
    )


def extract_linkedin_url(message):

    match = re.search(

        r"https?://(?:www\.)?"
        r"(?:linkedin\.com|lnkd\.in)/[^\s]+",

        message,

        re.IGNORECASE
    )

    if match:

        return match.group(0).rstrip(
            ".,)"
        )

    return None


def is_opportunity_request(message):

    text = message.lower()

    opportunity_words = [

        "internship",
        "internships",
        "intern",

        "job",
        "jobs",

        "opportunity",
        "opportunities",

        "placement",

        "hiring",

        "vacancy",

        "career"

    ]

    return any(
        word in text
        for word in opportunity_words
    )


# ============================================================
# TOPIC EXTRACTION
# ============================================================

def extract_post_topic(message):

    text = message.strip()

    patterns = [

        r"post\s+into\s+linkedin\s+about\s*:?\s*(.+)",

        r"post\s+to\s+linkedin\s+about\s*:?\s*(.+)",

        r"post\s+on\s+linkedin\s+about\s*:?\s*(.+)",

        r"create\s+(?:a\s+)?linkedin\s+post\s+about\s*:?\s*(.+)",

        r"write\s+(?:a\s+)?linkedin\s+post\s+about\s*:?\s*(.+)",

        r"generate\s+(?:a\s+)?linkedin\s+post\s+about\s*:?\s*(.+)",

        r"create\s+(?:a\s+)?post\s+about\s*:?\s*(.+)",

        r"write\s+(?:a\s+)?post\s+about\s*:?\s*(.+)",

        r"generate\s+(?:a\s+)?post\s+about\s*:?\s*(.+)",

        r"linkedin\s+post\s+about\s*:?\s*(.+)",

        r"post\s+about\s*:?\s*(.+)",

    ]

    for pattern in patterns:

        match = re.search(

            pattern,

            text,

            re.IGNORECASE
        )

        if match:

            topic = match.group(
                1
            ).strip()

            if topic:
                return topic

    return text


# ============================================================
# POST PROCESSING
# ============================================================

def process_post_request(
    message,
    sender
):

    print(
        "AGENT7 POST ROUTER"
    )

    topic = extract_post_topic(
        message
    )

    print(
        "Post topic:",
        topic
    )

    try:

        post_text = (
            post_agent.research_and_post(
                topic
            )
        )

        if not post_text:

            return (
                "I couldn't generate "
                "the LinkedIn post."
            )

        # Store generated post.
        save_pending_post(
            sender,
            post_text
        )

        response = (

            "📝 LinkedIn post draft:\n\n"

            f"{post_text}\n\n"

            "If you want me to publish "
            "this directly to LinkedIn, "
            "reply:\n"
            "OK, SHARE"
        )

        return response

    except Exception as e:

        print(
            "POST PROCESSING ERROR:"
        )

        print(e)

        return (
            "I couldn't create the "
            "LinkedIn post right now."
        )


# ============================================================
# LINKEDIN PUBLISH RESULT CHECK
# ============================================================

def linkedin_publish_succeeded(result):

    print(
        "Checking LinkedIn publish result..."
    )

    print(
        "Result type:",
        type(result)
    )

    # --------------------------------------------------------
    # Your connect.py returns a dictionary.
    # --------------------------------------------------------

    if isinstance(result, dict):

        success = result.get(
            "success"
        )

        status_code = result.get(
            "status_code"
        )

        if success is True:

            return True

        if status_code == 201:

            return True

        return False

    # --------------------------------------------------------
    # Support response objects too.
    # --------------------------------------------------------

    if hasattr(
        result,
        "status_code"
    ):

        if result.status_code == 201:

            return True

    if hasattr(
        result,
        "ok"
    ):

        if result.ok:

            return True

    # --------------------------------------------------------
    # Support True.
    # --------------------------------------------------------

    if result is True:

        return True

    return False


# ============================================================
# PUBLISH PENDING POST DIRECTLY TO LINKEDIN
# ============================================================

def publish_pending_post(sender):

    print()
    print(
        "======================================"
    )

    print(
        "AGENT7 LINKEDIN PUBLISH ROUTER"
    )

    print(
        "======================================"
    )

    # --------------------------------------------------------
    # Get saved post.
    # --------------------------------------------------------

    post_text = get_pending_post(
        sender
    )

    if not post_text:

        return (

            "I don't have a pending "
            "LinkedIn post to publish.\n\n"

            "First ask me to create "
            "a LinkedIn post."
        )

    print(
        "Pending LinkedIn post found."
    )

    print(
        "Post length:",
        len(post_text)
    )

    # --------------------------------------------------------
    # Check LinkedIn integration.
    # --------------------------------------------------------

    if not LINKEDIN_AVAILABLE:

        return (

            "❌ LinkedIn integration "
            "is not available right now."
        )

    if integrations is None:

        return (

            "❌ LinkedIn integration "
            "is not initialized."
        )

    # --------------------------------------------------------
    # DIRECT PUBLISH
    #
    # This calls YOUR connect.py:
    #
    # integrations.create_text_post(
    #     post_text,
    #     publish=True
    # )
    #
    # connect.py handles:
    #
    # LinkedIn access token
    # Userinfo
    # Author URN
    # LinkedIn REST API
    # Actual publication
    # --------------------------------------------------------

    print()
    print(
        "Publishing directly to LinkedIn..."
    )

    try:

        result = integrations.create_text_post(

            post_text,

            publish=True
        )

        print()
        print(
            "LinkedIn publish result:"
        )

        print(result)

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # Your connect.py returns:
        #
        # {
        #     "success": True,
        #     "status_code": 201,
        #     "post_id": "..."
        # }
        #
        # So we check BOTH success and status_code.
        # ----------------------------------------------------

        if linkedin_publish_succeeded(
            result
        ):

            clear_pending_post(
                sender
            )

            post_id = None

            if isinstance(
                result,
                dict
            ):

                post_id = result.get(
                    "post_id"
                )

            print()
            print(
                "======================================"
            )

            print(
                "LINKEDIN POST PUBLISHED SUCCESSFULLY"
            )

            if post_id:

                print(
                    "Post ID:",
                    post_id
                )

            print(
                "======================================"
            )

            return (

                "✅ Published successfully "
                "to LinkedIn."
            )

        # ----------------------------------------------------
        # Publication failed.
        # ----------------------------------------------------

        error_message = ""

        if isinstance(
            result,
            dict
        ):

            error_message = result.get(
                "error",
                ""
            )

        print()
        print(
            "LinkedIn publication failed."
        )

        if error_message:

            print(
                "LinkedIn error:",
                error_message
            )

        return (

            "❌ I couldn't publish the "
            "post to LinkedIn.\n\n"

            "The post is still saved, "
            "so you can try "
            "`OK, SHARE` again."
        )

    except Exception as e:

        print()
        print(
            "LINKEDIN PUBLISH ERROR:"
        )

        print(e)

        return (

            "❌ LinkedIn publishing failed.\n\n"

            f"Error: {str(e)}\n\n"

            "The post is still saved. "
            "You can try `OK, SHARE` again."
        )


# ============================================================
# COMMENT PROCESSING
# ============================================================

def process_comment_request(message):

    print(
        "AGENT7 COMMENT ROUTER"
    )

    linkedin_url = extract_linkedin_url(
        message
    )

    if not linkedin_url:

        return (

            "Please send me the LinkedIn "
            "post URL you want me to "
            "comment on."
        )

    try:

        comment = (
            comment_agent.create_comment(
                linkedin_url
            )
        )

        if not comment:

            return (

                "I couldn't generate a "
                "comment for that "
                "LinkedIn post."
            )

        return comment

    except Exception as e:

        print(
            "COMMENT ERROR:"
        )

        print(e)

        return (
            "I couldn't generate the "
            "comment right now."
        )


# ============================================================
# JOB PROCESSING
# ============================================================
#
# DO NOT CHANGE THIS SECTION.
# jobs_agent.py remains untouched.
# ============================================================

def process_jobs_request(message):

    print(
        "AGENT7 JOB ROUTER"
    )

    try:

        return jobs_agent.search_jobs(
            message
        )

    except Exception as e:

        print(
            "JOBS ERROR:"
        )

        print(e)

        return (
            "I couldn't search for "
            "jobs right now."
        )


# ============================================================
# GENERAL CHAT
# ============================================================

def normal_chat(message):

    print(
        "AGENT7 GENERAL CHAT ROUTER"
    )

    prompt = f"""
You are Agent7, my personal LinkedIn AI assistant.

The user sent this message:

{message}

Respond naturally and briefly.

Important:

- Do not pretend you posted something to LinkedIn.
- Do not pretend you commented on LinkedIn.
- Do not pretend you searched jobs unless the jobs router handled it.
- Do not invent LinkedIn actions.
- If the user asks for an action that Agent7 supports, the specialized router should handle it.

Return only the response.
"""

    return ask_ollama(
        prompt
    )


# ============================================================
# MAIN MESSAGE ROUTER
# ============================================================

def process_message(
    message,
    sender
):

    message = message.strip()

    print()
    print(
        "=" * 60
    )

    print(
        "AGENT7 MESSAGE"
    )

    print(
        "=" * 60
    )

    print(
        f"Incoming: {message}"
    )

    # --------------------------------------------------------
    # 1. PUBLISH
    # --------------------------------------------------------

    if is_publish_request(
        message
    ):

        response = (
            publish_pending_post(
                sender
            )
        )

        print()
        print(
            "AGENT7 RESPONSE:"
        )

        print(
            response
        )

        return response

    # --------------------------------------------------------
    # 2. COMMENT
    # --------------------------------------------------------

    if is_comment_request(
        message
    ):

        response = (
            process_comment_request(
                message
            )
        )

        print()
        print(
            "AGENT7 RESPONSE:"
        )

        print(
            response
        )

        return response

    # --------------------------------------------------------
    # 3. CREATE LINKEDIN POST
    # --------------------------------------------------------

    if is_post_request(
        message
    ):

        response = (
            process_post_request(
                message,
                sender
            )
        )

        print()
        print(
            "AGENT7 RESPONSE:"
        )

        print(
            response
        )

        return response

    # --------------------------------------------------------
    # 4. JOBS
    # --------------------------------------------------------

    if is_opportunity_request(
        message
    ):

        response = (
            process_jobs_request(
                message
            )
        )

        print()
        print(
            "AGENT7 RESPONSE:"
        )

        print(
            response
        )

        return response

    # --------------------------------------------------------
    # 5. GENERAL CHAT
    # --------------------------------------------------------

    response = normal_chat(
        message
    )

    print()
    print(
        "AGENT7 RESPONSE:"
    )

    print(
        response
    )

    return response


# ============================================================
# MEMORY-AWARE MESSAGE WRAPPER
# ============================================================
#
# IMPORTANT:
#
# The original process_message() above is NOT modified.
#
# This wrapper adds memory around it.
#
# Flow:
#
# WhatsApp message
#       ↓
# Save user message
#       ↓
# Load memory
#       ↓
# Existing Agent7 router
#       ↓
# Save Agent7 response
#
# ============================================================

_original_process_message = process_message


def process_message(
    message,
    sender
):

    conversation_id = None
    response = None

    try:

        # -----------------------------------------------
        # Get persistent conversation for this sender
        # -----------------------------------------------

        conversation_id = (
            get_memory_conversation_id(
                sender
            )
        )

        # -----------------------------------------------
        # Save user message
        # -----------------------------------------------

        save_message(
            conversation_id,
            "user",
            message
        )

        print(
            "Agent7 memory: user message saved."
        )

        # -----------------------------------------------
        # Retrieve existing memory
        # -----------------------------------------------

        memory_context = format_memory_for_ai(
            conversation_id
        )

        memory_context_local.context = (
            memory_context
        )

        print(
            "Agent7 memory: context loaded."
        )

        # -----------------------------------------------
        # Run EXISTING Agent7 router
        # -----------------------------------------------

        response = _original_process_message(
            message,
            sender
        )

        # -----------------------------------------------
        # Save Agent7 response
        # -----------------------------------------------

        if response:

            save_message(
                conversation_id,
                "assistant",
                response
            )

            print(
                "Agent7 memory: assistant response saved."
            )

        return response

    except Exception as e:

        print()
        print(
            "MEMORY INTEGRATION ERROR:"
        )

        print(e)

        # -----------------------------------------------
        # IMPORTANT:
        #
        # Memory must NEVER break Agent7.
        # -----------------------------------------------

        if response is not None:

            return response

        return _original_process_message(
            message,
            sender
        )

    finally:

        # Clear thread-local memory context.

        if hasattr(
            memory_context_local,
            "context"
        ):

            del memory_context_local.context


# ============================================================
# HEALTH
# ============================================================

@app.route(
    "/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "status":
            "ok",

        "agent":
            "Agent7",

        "ollama_model":
            OLLAMA_MODEL,

        "whatsapp_configured":
            bool(
                WHATSAPP_ACCESS_TOKEN
            ),

        "linkedin_available":
            LINKEDIN_AVAILABLE,

        "pending_posts":
            get_pending_post_count()

    })


# ============================================================
# WHATSAPP WEBHOOK VERIFICATION
# ============================================================

@app.route(
    "/webhook",
    methods=["GET"]
)
def verify_webhook():

    mode = request.args.get(
        "hub.mode"
    )

    token = request.args.get(
        "hub.verify_token"
    )

    challenge = request.args.get(
        "hub.challenge"
    )

    print(
        "Webhook verification request"
    )

    if (
        mode == "subscribe"
        and token == WHATSAPP_VERIFY_TOKEN
    ):

        print(
            "Webhook verification successful."
        )

        return challenge, 200

    print(
        "Webhook verification failed."
    )

    return (
        "Forbidden",
        403
    )


# ============================================================
# WHATSAPP WEBHOOK
# ============================================================

@app.route(
    "/webhook",
    methods=["POST"]
)
def webhook():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        entries = data.get(
            "entry",
            []
        )

        for entry in entries:

            changes = entry.get(
                "changes",
                []
            )

            for change in changes:

                value = change.get(
                    "value",
                    {}
                )

                metadata = value.get(
                    "metadata",
                    {}
                )

                webhook_phone_number_id = (
                    metadata.get(
                        "phone_number_id",
                        ""
                    )
                )

                messages = value.get(
                    "messages",
                    []
                )

                # Ignore status-only events.
                if not messages:
                    continue

                print()
                print(
                    "=" * 60
                )

                print(
                    "WHATSAPP MESSAGE RECEIVED"
                )

                print(
                    "=" * 60
                )

                print(
                    "Webhook Phone Number ID:",
                    webhook_phone_number_id
                )

                for msg in messages:

                    message_id = msg.get(
                        "id"
                    )

                    if is_duplicate_message(
                        message_id
                    ):

                        print(
                            "Duplicate message ignored:",
                            message_id
                        )

                        continue

                    message_type = msg.get(
                        "type"
                    )

                    print(
                        "Message type:",
                        message_type
                    )

                    if message_type != "text":

                        print(
                            "Unsupported message type:",
                            message_type
                        )

                        continue

                    sender = msg.get(
                        "from"
                    )

                    text_data = msg.get(
                        "text",
                        {}
                    )

                    message_text = (
                        text_data.get(
                            "body",
                            ""
                        ).strip()
                    )

                    if (
                        not sender
                        or not message_text
                    ):

                        continue

                    print(
                        "Sender:",
                        sender
                    )

                    print(
                        "PROCESSING:",
                        message_text
                    )

                    response = process_message(

                        message_text,

                        sender
                    )

                    send_long_whatsapp_message(

                        sender,

                        response,

                        webhook_phone_number_id
                    )

        return jsonify({
            "status": "ok"
        }), 200

    except Exception as e:

        print()
        print(
            "WEBHOOK ERROR:"
        )

        print(e)

        # Always return 200 to Meta.
        return jsonify({
            "status": "error"
        }), 200


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    print()
    print(
        "=" * 60
    )

    print(
        "AGENT7 STARTING"
    )

    print(
        "=" * 60
    )

    print(
        "Ollama model:",
        OLLAMA_MODEL
    )

    print(
        "LinkedIn integration:",
        "AVAILABLE"
        if LINKEDIN_AVAILABLE
        else "NOT AVAILABLE"
    )

    print(
        "Agent7 memory:",
        "AVAILABLE"
    )

    print(
        "WhatsApp token:",
        "CONFIGURED"
        if WHATSAPP_ACCESS_TOKEN
        else "MISSING"
    )

    print(
        "Pending post file:",
        PENDING_POST_FILE
    )

    print(
        "Memory session file:",
        MEMORY_SESSION_FILE
    )

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=False,

        use_reloader=False
    )