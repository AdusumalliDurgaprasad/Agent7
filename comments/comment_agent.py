# ============================================================
# AGENT7 - COMMENT AGENT
# LinkedIn Post -> Natural, Specific Comment
# ============================================================

import os
import re
import html as html_module
import requests
import ollama

from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "gemma3:4b"
).strip()


# ============================================================
# RESOLVE LINKEDIN URL
# ============================================================

def resolve_linkedin_url(url):

    print()
    print("Resolving LinkedIn URL...")

    try:

        response = requests.get(
            url,
            allow_redirects=True,
            timeout=20,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "Chrome/153.0 Safari/537.36"
                )
            }
        )

        print("Resolved URL:")
        print(response.url)

        return response.url

    except requests.exceptions.RequestException as exc:

        print(
            "URL resolution error:",
            exc
        )

        return url


# ============================================================
# EXTRACT LINKEDIN POST
# ============================================================

def extract_linkedin_post(linkedin_url):

    print()
    print("=" * 50)
    print("READING LINKEDIN POST")
    print("=" * 50)

    resolved_url = resolve_linkedin_url(
        linkedin_url
    )

    try:

        response = requests.get(
            resolved_url,
            timeout=30,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "Chrome/153.0 Safari/537.36"
                )
            }
        )

        response.raise_for_status()

    except requests.exceptions.RequestException as exc:

        print(
            "LinkedIn page error:",
            exc
        )

        return ""

    html = response.text

    print(
        "LinkedIn page characters:",
        len(html)
    )

    # --------------------------------------------------------
    # Remove scripts
    # --------------------------------------------------------

    html = re.sub(
        r"<script\b[^>]*>.*?</script>",
        " ",
        html,
        flags=re.DOTALL | re.IGNORECASE
    )

    # --------------------------------------------------------
    # Remove styles
    # --------------------------------------------------------

    html = re.sub(
        r"<style\b[^>]*>.*?</style>",
        " ",
        html,
        flags=re.DOTALL | re.IGNORECASE
    )

    # --------------------------------------------------------
    # Remove SVG
    # --------------------------------------------------------

    html = re.sub(
        r"<svg\b[^>]*>.*?</svg>",
        " ",
        html,
        flags=re.DOTALL | re.IGNORECASE
    )

    # --------------------------------------------------------
    # Try to capture useful meta descriptions
    # --------------------------------------------------------

    meta_content = []

    meta_matches = re.findall(
        r'<meta[^>]+(?:property|name)\s*=\s*["\']'
        r'(?:og:description|description|twitter:description)'
        r'["\'][^>]+content\s*=\s*["\']([^"\']+)["\']',
        html,
        flags=re.IGNORECASE
    )

    for item in meta_matches:

        item = html_module.unescape(
            item
        ).strip()

        if item:
            meta_content.append(item)

    # --------------------------------------------------------
    # Remove HTML tags
    # --------------------------------------------------------

    text = re.sub(
        r"<[^>]+>",
        " ",
        html
    )

    # --------------------------------------------------------
    # Decode HTML entities
    # --------------------------------------------------------

    text = html_module.unescape(
        text
    )

    # --------------------------------------------------------
    # Remove common LinkedIn UI noise
    # --------------------------------------------------------

    noise_patterns = [

        "Agree & Join LinkedIn",
        "By clicking Continue to join",
        "User Agreement",
        "Privacy Policy",
        "Cookie Policy",
        "Skip to main content",
        "Sign in",
        "Join now",
        "Top Content",
        "People",
        "Learning",
        "Jobs",
        "Games",
        "More",
        "Search",
        "Notifications",
        "Messaging",

    ]

    for noise in noise_patterns:

        text = text.replace(
            noise,
            " "
        )

    # --------------------------------------------------------
    # Normalize whitespace
    # --------------------------------------------------------

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    # --------------------------------------------------------
    # Combine useful meta content
    # --------------------------------------------------------

    if meta_content:

        meta_text = " ".join(
            meta_content
        )

        if meta_text not in text:

            text = (
                meta_text
                + " "
                + text
            )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    if not text:

        return ""

    # --------------------------------------------------------
    # Detect obvious login/block page
    # --------------------------------------------------------

    lower_text = text.lower()

    blocked_signals = [

        "join linkedin to view",
        "sign in to view",
        "log in to view",
        "this content is unavailable",
        "page not found",

    ]

    if any(
        signal in lower_text
        for signal in blocked_signals
    ):

        print(
            "LinkedIn content appears to be "
            "blocked or unavailable."
        )

        return ""

    # --------------------------------------------------------
    # Limit context sent to Ollama
    # --------------------------------------------------------

    text = text[:14000]

    print(
        "Extracted characters:",
        len(text)
    )

    return text


# ============================================================
# GENERATE COMMENT
# ============================================================

def generate_comment(post_content):

    post_content = str(
        post_content or ""
    ).strip()

    if not post_content:

        return ""

    print()
    print("=" * 50)
    print("GENERATING NATURAL COMMENT")
    print("=" * 50)

    prompt = f"""
You are Agent7, my personal LinkedIn comment assistant.

Your job is to write a comment that sounds like a REAL PERSON
who carefully read the LinkedIn post.

Here is the LinkedIn post:

--------------------------------
POST
--------------------------------

{post_content}

--------------------------------
COMMENT REQUIREMENTS
--------------------------------

Understand the ACTUAL main point of the post before writing.

The comment must:

- Directly respond to something specific in the post.
- Show that the post was actually understood.
- Sound natural and human.
- Be professional but conversational.
- Be short.
- Add a small observation, perspective, or thoughtful reaction.
- Feel like something a real professional would type on LinkedIn.

Avoid generic comments such as:

- Great post!
- Amazing insights!
- Very insightful!
- This is amazing!
- Well said!
- Great insights!

Do NOT simply summarize the post.

Do NOT invent facts.

Do NOT claim personal experience.

Do NOT mention AI.

Do NOT use hashtags.

Do NOT use emojis unless one is genuinely necessary.

Do NOT start with:
"That's a really interesting take..."
unless the post genuinely requires that wording.

Do NOT use corporate or robotic language.

Prefer natural wording such as:

- "The point about X really stood out..."
- "I think the interesting part here is..."
- "The shift from X to Y is especially interesting..."
- "This makes me think about..."
- "The part about X is easy to overlook..."

But only use such wording when it naturally fits the actual post.

Length:
1-3 sentences.
Approximately 20-45 words.

Return ONLY the comment.
No quotation marks.
No explanation.
"""

    try:

        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        comment = str(
            response["message"]["content"]
        ).strip()

        # ----------------------------------------------------
        # Clean accidental formatting
        # ----------------------------------------------------

        comment = re.sub(
            r"^```(?:text)?",
            "",
            comment,
            flags=re.IGNORECASE
        )

        comment = re.sub(
            r"```$",
            "",
            comment
        ).strip()

        comment = comment.strip(
            '"'
        ).strip()

        return comment

    except Exception as exc:

        print(
            "Ollama error:",
            exc
        )

        return ""


# ============================================================
# COMPLETE COMMENT WORKFLOW
# ============================================================

def create_comment(linkedin_url):

    print()
    print("=" * 60)
    print("AGENT7 COMMENT AGENT")
    print("=" * 60)

    if not linkedin_url:

        return (
            "Please provide a LinkedIn post URL."
        )

    post_content = extract_linkedin_post(
        linkedin_url
    )

    if not post_content:

        return (
            "I couldn't read this LinkedIn post.\n\n"
            "LinkedIn may require login or "
            "block public content extraction."
        )

    comment = generate_comment(
        post_content
    )

    if not comment:

        return (
            "I couldn't generate a comment "
            "for this post."
        )

    # IMPORTANT:
    # Return ONLY the actual comment.
    return comment


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    url = input(
        "Paste LinkedIn post URL: "
    ).strip()

    result = create_comment(
        url
    )

    print()
    print("RESULT:")
    print(result)