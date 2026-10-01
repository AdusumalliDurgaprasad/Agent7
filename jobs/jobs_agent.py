# ============================================================
# AGENT7 - JOBS AGENT
# Real-source Tavily Internship Search
# ============================================================

import os
import re
import requests

from urllib.parse import urlparse
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

load_dotenv(
    os.path.join(
        BASE_DIR,
        ".env"
    )
)

TAVILY_API_KEY = os.getenv(
    "TAVILY_API_KEY",
    ""
).strip()

JOBS_AGENT_VERSION = (
    "JOBS-FINAL-INTEGRATED-V5"
)


# ============================================================
# URL HELPERS
# ============================================================

def clean_url(url):

    if not isinstance(
        url,
        str
    ):
        return ""

    url = url.strip()

    url = url.strip(
        " \t\r\n<>[](){}\\\"'"
    )

    url = url.rstrip(
        ".,!?;:"
    )

    if not url.startswith(
        (
            "http://",
            "https://"
        )
    ):
        return ""

    return url


def valid_url(url):

    url = clean_url(
        url
    )

    if not url:
        return False

    try:

        parsed = urlparse(
            url
        )

        return (
            parsed.scheme
            in ("http", "https")
            and
            bool(parsed.netloc)
        )

    except Exception:

        return False


def get_domain(url):

    try:

        domain = urlparse(
            url
        ).netloc.lower()

        if domain.startswith(
            "www."
        ):

            domain = domain[4:]

        return domain

    except Exception:

        return ""


# ============================================================
# TEXT HELPERS
# ============================================================

def safe_text(value):

    if value is None:
        return ""

    if isinstance(
        value,
        str
    ):

        return value.strip()

    try:

        return str(
            value
        ).strip()

    except Exception:

        return ""


def normalize_text(value):

    return safe_text(
        value
    ).lower()


# ============================================================
# REQUEST COUNT
# ============================================================

def extract_requested_count(
    request
):

    text = normalize_text(
        request
    )

    patterns = [

        r"\btop\s+(\d+)\b",

        r"\b(\d+)\s+"
        r"(?:internships?|jobs?|"
        r"opportunities?)\b",

        r"\b(?:show|give|find|get)"
        r"\s+(\d+)\b",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            try:

                count = int(
                    match.group(1)
                )

                if count < 1:
                    return 10

                return min(
                    count,
                    10
                )

            except Exception:
                pass

    return 10


# ============================================================
# TAVILY QUERY BUILDER
# ============================================================

def build_queries(
    request
):

    request_text = safe_text(
        request
    )

    return [

        (
            "AI ML internship 2026 "
            "apply now official careers "
            f"{request_text}"
        ),

        (
            "AI engineer internship 2026 "
            "application official job "
            f"{request_text}"
        ),

        (
            "machine learning internship 2026 "
            "official careers apply "
            f"{request_text}"
        ),

        (
            "artificial intelligence internship "
            "2026 official careers apply "
            f"{request_text}"
        ),

        (
            "software engineering internship "
            "AI ML 2026 official careers "
            f"{request_text}"
        ),

        (
            "site:greenhouse.io AI internship 2026"
        ),

        (
            "site:lever.co AI internship 2026"
        ),

        (
            "site:jobs.ashbyhq.com AI internship 2026"
        ),

    ]


# ============================================================
# TAVILY SEARCH
# ============================================================

def tavily_search(
    query,
    max_results=10
):

    if not TAVILY_API_KEY:

        raise RuntimeError(
            "TAVILY_API_KEY is missing "
            "from .env"
        )

    url = (
        "https://api.tavily.com/search"
    )

    payload = {

        "api_key":
            TAVILY_API_KEY,

        "query":
            query,

        "search_depth":
            "advanced",

        "topic":
            "general",

        "max_results":
            max_results,

        "include_answer":
            False,

        "include_raw_content":
            False,

        "include_images":
            False,

    }

    try:

        response = requests.post(

            url,

            json=payload,

            timeout=45

        )

    except requests.RequestException as exc:

        print(
            "Tavily request error:",
            exc
        )

        return []

    print(
        "Tavily status:",
        response.status_code
    )

    if response.status_code != 200:

        print(
            "Tavily response:",
            response.text[:1000]
        )

        return []

    try:

        data = response.json()

    except Exception as exc:

        print(
            "Tavily JSON error:",
            exc
        )

        return []

    results = data.get(
        "results",
        []
    )

    if not isinstance(
        results,
        list
    ):

        return []

    return results


# ============================================================
# RESULT EXTRACTION
# ============================================================

def extract_result(
    item
):

    if not isinstance(
        item,
        dict
    ):

        return None

    title = safe_text(
        item.get(
            "title"
        )
    )

    content = safe_text(
        item.get(
            "content"
        )
    )

    url = clean_url(
        item.get(
            "url"
        )
    )

    if not valid_url(
        url
    ):

        return None

    return {

        "title":
            title or "Internship opportunity",

        "content":
            content,

        "url":
            url,

    }


# ============================================================
# BLOCKED DOMAINS
# ============================================================

SOCIAL_DOMAINS = {

    "facebook.com",
    "instagram.com",
    "twitter.com",
    "x.com",
    "youtube.com",
    "tiktok.com",
    "reddit.com",
    "linkedin.com",

}


# ============================================================
# GENERIC GUIDE SIGNALS
# ============================================================

GENERIC_GUIDE_TERMS = [

    "best internships",
    "top internships",
    "internships guide",
    "internship guide",
    "companies hiring interns",
    "list of internships",
    "internship list",
    "internships for college students",
    "career guide",
    "internship opportunities guide",

]


# ============================================================
# CLOSED SIGNALS
# ============================================================

CLOSED_SIGNALS = [

    "applications closed",
    "application closed",
    "applications are closed",

    "no longer accepting applications",

    "position closed",
    "position has been filled",

    "role has been filled",

    "expired",
    "deadline passed",

    "applications have closed",

]


# ============================================================
# OPPORTUNITY TERMS
# ============================================================

OPPORTUNITY_TERMS = [

    "internship",
    "intern",

    "machine learning",
    "artificial intelligence",

    "ai engineer",
    "machine learning engineer",

    "software engineer",
    "software engineering",

    "data science",
    "data scientist",

    "generative ai",
    "genai",

    "deep learning",

]


# ============================================================
# APPLICATION TERMS
# ============================================================

APPLICATION_TERMS = [

    "apply",
    "application",
    "applications open",
    "apply now",

    "job description",
    "deadline",

    "careers",
    "job",

]


# ============================================================
# DIRECT APPLICATION DOMAINS
# ============================================================

DIRECT_APPLICATION_DOMAINS = {

    "greenhouse.io",
    "lever.co",
    "ashbyhq.com",
    "workday.com",
    "myworkdayjobs.com",
    "smartrecruiters.com",
    "jobvite.com",
    "icims.com",

}


# ============================================================
# FILTER HELPERS
# ============================================================

def is_social_domain(
    url
):

    domain = get_domain(
        url
    )

    return any(

        domain == blocked
        or
        domain.endswith(
            "." + blocked
        )

        for blocked
        in SOCIAL_DOMAINS

    )


def is_direct_application_url(
    url
):

    domain = get_domain(
        url
    )

    return any(

        domain == direct
        or
        domain.endswith(
            "." + direct
        )

        for direct
        in DIRECT_APPLICATION_DOMAINS

    )


def contains_generic_guide_signal(
    result
):

    combined = (
        normalize_text(
            result.get(
                "title"
            )
        )
        + " "
        +
        normalize_text(
            result.get(
                "content"
            )
        )
    )

    return any(
        term in combined
        for term in GENERIC_GUIDE_TERMS
    )


def is_closed(
    text
):

    lowered = normalize_text(
        text
    )

    return any(
        signal in lowered
        for signal in CLOSED_SIGNALS
    )


def has_opportunity_terms(
    text
):

    lowered = normalize_text(
        text
    )

    return any(
        term in lowered
        for term in OPPORTUNITY_TERMS
    )


def has_application_terms(
    text
):

    lowered = normalize_text(
        text
    )

    return any(
        term in lowered
        for term in APPLICATION_TERMS
    )


# ============================================================
# SCORING
# ============================================================

def score_result(
    result
):

    title = normalize_text(
        result.get(
            "title"
        )
    )

    content = normalize_text(
        result.get(
            "content"
        )
    )

    url = normalize_text(
        result.get(
            "url"
        )
    )

    combined = (
        f"{title} {content}"
    )

    score = 0

    # Internship
    if "internship" in title:
        score += 30

    if "intern" in title:
        score += 15

    # AI/ML
    ai_terms = [

        "artificial intelligence",
        "machine learning",
        "ai engineer",
        "generative ai",
        "genai",
        "deep learning",
        "data science",

    ]

    for term in ai_terms:

        if term in combined:
            score += 10

    # Application
    if "apply" in combined:
        score += 10

    if "application" in combined:
        score += 6

    if "deadline" in combined:
        score += 5

    # Current year
    if "2026" in combined:
        score += 10

    # Direct application source
    if is_direct_application_url(
        url
    ):

        score += 30

    # Career page
    if "careers" in url:
        score += 8

    if "jobs" in url:
        score += 8

    # Penalize generic guides
    if contains_generic_guide_signal(
        result
    ):

        score -= 30

    return score


# ============================================================
# DEDUPLICATION
# ============================================================

def deduplicate(
    results
):

    unique = {}

    for result in results:

        if not isinstance(
            result,
            dict
        ):

            continue

        url = clean_url(
            result.get(
                "url"
            )
        )

        if not valid_url(
            url
        ):

            continue

        key = (
            url.lower()
            .rstrip("/")
        )

        if key not in unique:

            unique[key] = result

    return list(
        unique.values()
    )


# ============================================================
# FILTER + RANK
# ============================================================

def filter_and_rank(
    results
):

    valid_results = []

    for item in results:

        result = extract_result(
            item
        )

        if result is None:
            continue

        url = result["url"]

        title = result["title"]

        content = result["content"]

        combined = (
            f"{title} {content}"
        )

        # Social
        if is_social_domain(
            url
        ):
            continue

        # Closed
        if is_closed(
            combined
        ):
            continue

        # Opportunity
        if not has_opportunity_terms(
            combined
        ):
            continue

        # Application
        if not has_application_terms(
            combined
        ):
            continue

        result["score"] = (
            score_result(
                result
            )
        )

        result["direct_apply"] = (
            is_direct_application_url(
                url
            )
        )

        valid_results.append(
            result
        )

    valid_results.sort(

        key=lambda item:
            item.get(
                "score",
                0
            ),

        reverse=True

    )

    return valid_results


# ============================================================
# MAIN SEARCH
# ============================================================

def find_opportunities(
    request
):

    print()
    print("=" * 60)
    print("AGENT7 JOBS AGENT")
    print("=" * 60)

    print(
        "Request:",
        request
    )

    print(
        "Version:",
        JOBS_AGENT_VERSION
    )

    requested_count = (
        extract_requested_count(
            request
        )
    )

    print(
        "Requested count:",
        requested_count
    )

    queries = build_queries(
        request
    )

    all_results = []

    for query in queries:

        print()
        print(
            "Tavily query:",
            query
        )

        try:

            results = tavily_search(
                query,
                max_results=10
            )

            print(
                "Results returned:",
                len(results)
            )

            if isinstance(
                results,
                list
            ):

                all_results.extend(
                    results
                )

        except Exception as exc:

            print(
                "Tavily query error:",
                repr(exc)
            )

    print()
    print(
        "Raw Tavily results:",
        len(all_results)
    )

    unique_results = deduplicate(
        all_results
    )

    print(
        "Unique results:",
        len(unique_results)
    )

    final_results = filter_and_rank(
        unique_results
    )

    print(
        "Valid opportunity results:",
        len(final_results)
    )

    # --------------------------------------------------------
    # Prefer real application pages
    # --------------------------------------------------------

    direct_results = [

        item

        for item
        in final_results

        if item.get(
            "direct_apply",
            False
        )

    ]

    other_results = [

        item

        for item
        in final_results

        if not item.get(
            "direct_apply",
            False
        )

    ]

    # Direct application pages first.
    ordered_results = (
        direct_results
        +
        other_results
    )

    final_results = ordered_results[
        :requested_count
    ]

    print()
    print(
        "FINAL OPPORTUNITIES:",
        len(final_results)
    )

    for index, result in enumerate(
        final_results,
        start=1
    ):

        print()
        print(
            f"{index}.",
            result.get(
                "title",
                ""
            )
        )

        print(
            "URL:",
            result.get(
                "url",
                ""
            )
        )

        print(
            "Direct application:",
            result.get(
                "direct_apply",
                False
            )
        )

    print("=" * 60)

    return final_results


# ============================================================
# WHATSAPP FORMATTER
# ============================================================

def format_results(
    results
):

    if not results:

        return (
            "I couldn't find suitable current "
            "AI/ML internship opportunities.\n\n"
            "Try:\n"
            "AI internships 2026\n"
            "AI/ML internships\n"
            "Machine learning internships"
        )

    lines = [

        "🤖 Agent7 - AI Internship Opportunities",
        "",
        f"Found {len(results)} relevant results:",
        "",

    ]

    for index, result in enumerate(
        results,
        start=1
    ):

        title = safe_text(
            result.get(
                "title"
            )
        )

        url = clean_url(
            result.get(
                "url"
            )
        )

        if not valid_url(
            url
        ):
            continue

        if not title:
            title = "Internship opportunity"

        direct_apply = result.get(
            "direct_apply",
            False
        )

        lines.append(
            f"{index}. {title}"
        )

        if direct_apply:

            lines.append(
                f"Apply: {url}"
            )

        else:

            lines.append(
                f"Source: {url}"
            )

        lines.append("")

    lines.append(
        "Note: Verify eligibility, deadline, "
        "location and current application status "
        "on the linked page before applying."
    )

    return "\n".join(
        lines
    )


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def search_jobs(
    request
):

    try:

        results = find_opportunities(
            request
        )

        return format_results(
            results
        )

    except Exception as exc:

        print()
        print(
            "JOBS AGENT ERROR:",
            repr(exc)
        )

        return (
            "Jobs search failed.\n\n"
            f"Reason: {str(exc)}"
        )


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print()

    response = search_jobs(
        "AI internships top 5"
    )

    print()
    print(response)