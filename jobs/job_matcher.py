import json
import os
import ollama


# ==================================================
# CONFIGURATION
# ==================================================

PROFILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "profile",
    "career_profile.json"
)

OLLAMA_MODEL = "gemma3:4b"


# ==================================================
# LOAD CAREER PROFILE
# ==================================================

def load_career_profile():
    """
    Load the user's career profile from JSON.
    """

    if not os.path.exists(PROFILE_PATH):

        print("\nCareer profile not found:")
        print(PROFILE_PATH)

        return None

    try:

        with open(
            PROFILE_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            profile = json.load(file)

        return profile

    except json.JSONDecodeError as e:

        print("\nInvalid career_profile.json:")
        print(e)

        return None

    except OSError as e:

        print("\nCould not read career profile:")
        print(e)

        return None


# ==================================================
# MATCH ONE OPPORTUNITY
# ==================================================

def match_opportunity(opportunity, profile):
    """
    Analyze one job opportunity against
    the user's career profile.
    """

    title = opportunity.get(
        "title",
        ""
    )

    description = opportunity.get(
        "description",
        ""
    )

    url = opportunity.get(
        "url",
        ""
    )

    # Limit extremely large descriptions
    description = description[:10000]

    prompt = f"""
You are Agent7, a career opportunity matching assistant.

Your job is to determine whether a job, internship,
research opportunity, or apprenticeship is genuinely
relevant to the user's career profile.

========================================
USER CAREER PROFILE
========================================

{json.dumps(profile, indent=2)}

========================================
OPPORTUNITY
========================================

TITLE:
{title}

URL:
{url}

DESCRIPTION:
{description}

========================================
MATCHING RULES
========================================

Analyze the opportunity carefully.

Consider:

1. Job title
2. Required skills
3. Preferred skills
4. Education requirements
5. Experience requirements
6. Student eligibility
7. Internship/apprenticeship eligibility
8. Technology/domain
9. Location when available
10. Whether the opportunity is actually relevant
   to the user's career direction

The user is primarily interested in:

- AI
- Machine Learning
- Generative AI
- LLMs
- AI Agents
- Applied AI
- Computer Vision
- Python
- Software Engineering
- AI research
- ML research

However, do not reject a role simply because
the title does not contain "AI".

Look at the actual job description.

========================================
IMPORTANT
========================================

A student should NOT be considered a strong match
for a role requiring several years of professional
experience.

Internships, apprenticeships, graduate roles and
entry-level positions should be considered when
the user's profile fits.

Do not invent requirements.

If information is missing, say so.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "match": true,
    "match_level": "strong",
    "reason": "Short explanation",
    "matched_skills": [
        "Python",
        "Machine Learning"
    ],
    "missing_skills": [
        "Docker"
    ],
    "experience_fit": true,
    "education_fit": true,
    "opportunity_type": "internship"
}}

Rules for match_level:

"strong"
- Clearly relevant
- User appears eligible

"possible"
- Relevant but some important information
  is missing or there are noticeable gaps

"weak"
- Some connection but poor overall fit

"not_fit"
- Clearly unsuitable

The "match" field must be true only for
"strong" or "possible".

The opportunity_type can be:

"full_time"
"internship"
"apprenticeship"
"research"
"graduate"
"unknown"
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

    except Exception as e:

        print("\nOllama error:")
        print(e)

        return None

    result = response["message"]["content"].strip()

    # ----------------------------------------------
    # Remove markdown JSON fences if Ollama adds them
    # ----------------------------------------------

    if result.startswith("```"):

        result = result.replace(
            "```json",
            ""
        )

        result = result.replace(
            "```",
            ""
        )

        result = result.strip()

    # ----------------------------------------------
    # Parse JSON
    # ----------------------------------------------

    try:

        match_result = json.loads(result)

    except json.JSONDecodeError:

        print("\nOllama returned invalid JSON:")

        print(result)

        return None

    return match_result


# ==================================================
# MATCH ALL OPPORTUNITIES
# ==================================================

def match_opportunities(opportunities):
    """
    Match all collected opportunities
    against the user's profile.
    """

    print("\n==============================================")
    print("          AGENT7 PROFILE MATCHER")
    print("==============================================")

    profile = load_career_profile()

    if profile is None:

        return []

    matched_opportunities = []

    total = len(opportunities)

    print(
        f"\nAnalyzing {total} opportunities..."
    )

    for index, opportunity in enumerate(
        opportunities,
        start=1
    ):

        print(
            f"\n[{index}/{total}] "
            f"{opportunity.get('title', 'Unknown')}"
        )

        result = match_opportunity(
            opportunity,
            profile
        )

        if result is None:

            print("Could not analyze.")

            continue

        opportunity["match"] = result

        if result.get("match") is True:

            matched_opportunities.append(
                opportunity
            )

            print(
                f"✓ MATCH - "
                f"{result.get('match_level', 'unknown')}"
            )

        else:

            print(
                f"✗ NOT FIT - "
                f"{result.get('match_level', 'unknown')}"
            )

    print("\n==============================================")
    print("           MATCHING COMPLETE")
    print("==============================================")

    print(
        f"\nTotal opportunities: {total}"
    )

    print(
        f"Profile matches:     "
        f"{len(matched_opportunities)}"
    )

    return matched_opportunities


# ==================================================
# DISPLAY MATCHES
# ==================================================

def display_matches(opportunities):
    """
    Display opportunities that matched
    the user's profile.
    """

    print("\n==============================================")
    print("          AGENT7 PROFILE MATCHES")
    print("==============================================")

    if not opportunities:

        print("\nNo matching opportunities found.")

        return

    for index, opportunity in enumerate(
        opportunities,
        start=1
    ):

        match = opportunity.get(
            "match",
            {}
        )

        print("\n----------------------------------------------")

        print(
            f"[{index}] "
            f"{opportunity.get('title', 'Unknown')}"
        )

        print(
            f"\nMatch level: "
            f"{match.get('match_level', 'unknown')}"
        )

        print(
            f"\nReason:\n"
            f"{match.get('reason', 'No reason provided')}"
        )

        print(
            f"\nMatched skills:"
        )

        for skill in match.get(
            "matched_skills",
            []
        ):

            print(
                f"  ✓ {skill}"
            )

        print(
            f"\nMissing skills:"
        )

        for skill in match.get(
            "missing_skills",
            []
        ):

            print(
                f"  - {skill}"
            )

        print(
            f"\nType: "
            f"{match.get('opportunity_type', 'unknown')}"
        )

        print(
            f"\nURL:\n"
            f"{opportunity.get('url', '')}"
        )


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    from job_sources import search_opportunities

    print("\n==============================================")
    print("              AGENT7 JOB TEST")
    print("==============================================")

    # ----------------------------------------------
    # Collect opportunities
    # ----------------------------------------------

    opportunities = search_opportunities()

    # ----------------------------------------------
    # Match opportunities
    # ----------------------------------------------

    matched = match_opportunities(
        opportunities
    )

    # ----------------------------------------------
    # Display matches
    # ----------------------------------------------

    display_matches(
        matched
    )