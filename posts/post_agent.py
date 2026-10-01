# ============================================================
# AGENT7 - POST AGENT
# Research + LinkedIn Post Generation
# ============================================================

import os
import re
import requests
import ollama

from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

TAVILY_API_KEY = os.getenv(
    "TAVILY_API_KEY",
    ""
).strip()

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "gemma3:4b"
).strip()


# ============================================================
# OLLAMA POST GENERATION
# ============================================================

def generate_post(
    prompt,
    model=None
):

    model = model or OLLAMA_MODEL

    response = ollama.chat(

        model=model,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]

    )

    return str(
        response["message"]["content"]
    ).strip()


# ============================================================
# TAVILY RESEARCH
# ============================================================

def research_topic(topic):

    print()
    print("AGENT7 POST RESEARCH")

    if not TAVILY_API_KEY:

        print(
            "TAVILY_API_KEY is missing."
        )

        return ""

    url = (
        "https://api.tavily.com/search"
    )

    payload = {

        "api_key":
            TAVILY_API_KEY,

        "query":
            topic,

        "search_depth":
            "advanced",

        "topic":
            "general",

        "max_results":
            5,

        "include_answer":
            True,

        "include_raw_content":
            True,
    }

    try:

        response = requests.post(

            url,

            json=payload,

            timeout=45

        )

        print(
            "Tavily status:",
            response.status_code
        )

        response.raise_for_status()

        data = response.json()

    except requests.exceptions.RequestException as exc:

        print(
            "Tavily search error:",
            exc
        )

        return ""

    except ValueError as exc:

        print(
            "Tavily JSON error:",
            exc
        )

        return ""

    results = data.get(
        "results",
        []
    )

    if not isinstance(
        results,
        list
    ):

        return ""

    research_information = []

    answer = data.get(
        "answer",
        ""
    )

    if answer:

        research_information.append(
            f"""
TAVILY SUMMARY:

{answer}
"""
        )

    for index, result in enumerate(
        results,
        start=1
    ):

        if not isinstance(
            result,
            dict
        ):
            continue

        title = str(
            result.get(
                "title",
                ""
            )
        ).strip()

        source_url = str(
            result.get(
                "url",
                ""
            )
        ).strip()

        content = str(
            result.get(
                "content",
                ""
            )
        ).strip()

        raw_content = str(
            result.get(
                "raw_content",
                ""
            )
        ).strip()

        source_content = (
            raw_content
            if raw_content
            else content
        )

        if not source_content:

            continue

        source_content = (
            source_content[:6000]
        )

        research_information.append(

            f"""
SOURCE {index}

TITLE:
{title}

URL:
{source_url}

CONTENT:
{source_content}
"""
        )

    print(
        "Research sources:",
        len(results)
    )

    if not research_information:

        return ""

    return "\n\n".join(
        research_information
    )


# ============================================================
# CLEAN POST OUTPUT
# ============================================================

def clean_post_output(text):

    text = str(
        text or ""
    ).strip()

    # --------------------------------------------------------
    # Remove markdown code fences
    # --------------------------------------------------------

    text = re.sub(
        r"^```(?:linkedin|text|markdown)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    ).strip()

    # --------------------------------------------------------
    # Remove common model introductions
    # --------------------------------------------------------

    prefixes = [

        "Here is the LinkedIn post:",
        "Here's the LinkedIn post:",
        "Here is a LinkedIn post:",
        "Here's a LinkedIn post:",
        "LinkedIn post:",
        "Here is the post:",
        "Here's the post:",
        "Post:",
    ]

    changed = True

    while changed:

        changed = False

        for prefix in prefixes:

            if text.lower().startswith(
                prefix.lower()
            ):

                text = text[
                    len(prefix):
                ].strip()

                changed = True

    # --------------------------------------------------------
    # Remove model meta-introductions
    # --------------------------------------------------------

    unwanted_openers = [

        "Here's a LinkedIn post based on the provided research",
        "Here is a LinkedIn post based on the provided research",
        "Here's a LinkedIn post based on the research",
        "Here is a LinkedIn post based on the research",
        "Here's a LinkedIn post based on the provided content",
        "Here is a LinkedIn post based on the provided content",
        "Here's a LinkedIn post based on the provided article",
        "Here is a LinkedIn post based on the provided article",

    ]

    for opener in unwanted_openers:

        if text.lower().startswith(
            opener.lower()
        ):

            remaining = text[
                len(opener):
            ].lstrip(
                " :\n-"
            )

            text = remaining

    # --------------------------------------------------------
    # Remove accidental "aiming for..." type explanation
    # --------------------------------------------------------

    meta_patterns = [

        r"^Here's a LinkedIn post.*?:\s*",
        r"^Here is a LinkedIn post.*?:\s*",
        r"^This LinkedIn post.*?:\s*",

    ]

    for pattern in meta_patterns:

        text = re.sub(
            pattern,
            "",
            text,
            count=1,
            flags=re.IGNORECASE
        ).strip()

    return text


# ============================================================
# RESEARCH + POST
# ============================================================

def research_and_post(topic):

    topic = str(
        topic or ""
    ).strip()

    if not topic:

        return (
            "Please provide a topic for the "
            "LinkedIn post."
        )

    print()
    print("=" * 50)
    print("AGENT7 POST AGENT")
    print("=" * 50)

    print(
        "Topic:",
        topic
    )

    research_information = (
        research_topic(topic)
    )

    if not research_information:

        return (
            "I couldn't find enough reliable "
            "information about this topic."
        )

    prompt = f"""
You are Agent7, my personal LinkedIn content writer.

The user wants to publish a LinkedIn post about:

{topic}

You have researched the topic below.

--------------------------------
RESEARCH
--------------------------------

{research_information}

--------------------------------
YOUR TASK
--------------------------------

Write ONE strong, natural LinkedIn post.

The post MUST be specifically about:

{topic}

Do not change the topic.

Do not turn the post into a generic article about AI.

Do not mention unrelated companies, products,
stock prices, financial markets, analysts,
technologies or events unless they are directly
relevant to the requested topic.

--------------------------------
STYLE
--------------------------------

Write like a real professional sharing an
interesting idea on LinkedIn.

Use:

- A strong first line
- Natural human language
- Simple English
- Short paragraphs
- Clear observations
- Useful information
- Mobile-friendly spacing
- A natural closing thought

Avoid:

- Corporate jargon
- Generic AI buzzwords
- Fake personal experiences
- Excessive emojis
- Clickbait
- Overly dramatic language
- "In today's rapidly evolving world..."
- "The future is here..."
- "As we all know..."
- Generic motivational language

--------------------------------
IMPORTANT
--------------------------------

Use only facts supported by the research.

Do not invent numbers.

Do not invent quotes.

Do not exaggerate.

Do not copy source wording.

Do not mention:

- Tavily
- research
- sources
- this prompt
- Agent7
- AI assistant
- language model

Do not write:

"Here's a LinkedIn post..."
"Here is a LinkedIn post..."
"Based on the research..."
"Based on the provided article..."

Start DIRECTLY with the actual post.

Return ONLY the final LinkedIn post.
"""

    try:

        result = generate_post(
            prompt
        )

    except Exception as exc:

        print(
            "Ollama generation error:",
            exc
        )

        return (
            "I couldn't generate the "
            "LinkedIn post."
        )

    result = clean_post_output(
        result
    )

    return result


# ============================================================
# OPTIONAL DIRECT TEST
# ============================================================

if __name__ == "__main__":

    topic = input(
        "Enter LinkedIn post topic: "
    ).strip()

    print()
    print(
        research_and_post(
            topic
        )
    )