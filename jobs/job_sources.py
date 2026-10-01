import os
import requests
from dotenv import load_dotenv


# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================

load_dotenv()


# ==================================================
# TAVILY SEARCH
# ==================================================

def tavily_search(query, max_results=10):
    """
    Search the web using Tavily.

    Returns a list of opportunity dictionaries.
    """

    api_key = "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"

    if not api_key:
        print("\nTAVILY_API_KEY is missing.")
        print("Add it to your .env file.")
        return []

    url = "https://api.tavily.com/search"

    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "advanced",
        "topic": "general",
        "max_results": max_results,
        "include_answer": True
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

    except requests.exceptions.Timeout:
        print("\nTavily request timed out.")
        return []

    except requests.exceptions.RequestException as e:
        print("\nTavily search error:")
        print(e)
        return []

    except ValueError:
        print("\nTavily returned invalid JSON.")
        return []

    results = data.get("results", [])

    opportunities = []

    for result in results:

        title = result.get("title", "").strip()
        result_url = result.get("url", "").strip()
        content = result.get("content", "").strip()

        if not title or not result_url:
            continue

        opportunities.append({
            "title": title,
            "url": result_url,
            "description": content,
            "source": "Tavily"
        })

    return opportunities


# ==================================================
# SEARCH ONE OPPORTUNITY CATEGORY
# ==================================================

def search_category(category, queries):
    """
    Search multiple queries belonging to one category.
    """

    print("\n--------------------------------")
    print(f"SEARCHING: {category}")
    print("--------------------------------")

    all_results = []

    for query in queries:

        print(f"\nQuery: {query}")

        results = tavily_search(
            query,
            max_results=10
        )

        all_results.extend(results)

        print(f"Found: {len(results)}")

    return all_results


# ==================================================
# REMOVE DUPLICATES
# ==================================================

def remove_duplicates(opportunities):
    """
    Remove duplicate opportunities using URLs.
    """

    unique = {}

    for opportunity in opportunities:

        url = opportunity.get("url", "").strip()

        if not url:
            continue

        if url not in unique:
            unique[url] = opportunity

    return list(unique.values())


# ==================================================
# SEARCH ALL OPPORTUNITIES
# ==================================================

def search_opportunities():
    """
    Search broadly for AI, ML, GenAI, software,
    internship, apprenticeship and research
    opportunities.
    """

    print("\n==============================================")
    print("        AGENT7 OPPORTUNITY RADAR")
    print("==============================================")

    all_opportunities = []


    # ==================================================
    # AI / MACHINE LEARNING
    # ==================================================

    ai_queries = [

        "AI Engineer jobs India 2026",

        "AI ML Engineer jobs India 2026",

        "Machine Learning Engineer jobs India 2026",

        "Applied AI Engineer jobs India 2026",

        "Artificial Intelligence Engineer jobs India 2026",

        "AI Research Engineer jobs India 2026",

        "Deep Learning Engineer jobs India 2026",

        "Computer Vision Engineer jobs India 2026",

        "NLP Engineer jobs India 2026"
    ]

    all_opportunities.extend(
        search_category(
            "AI / MACHINE LEARNING",
            ai_queries
        )
    )


    # ==================================================
    # GENERATIVE AI / LLM / AGENTS
    # ==================================================

    genai_queries = [

        "Generative AI Engineer jobs India 2026",

        "GenAI Engineer jobs India 2026",

        "LLM Engineer jobs India 2026",

        "Large Language Model Engineer jobs India 2026",

        "AI Agent Engineer jobs India 2026",

        "Agentic AI Engineer jobs India 2026",

        "Generative AI internship India 2026",

        "LLM internship India 2026",

        "AI agent internship India 2026"
    ]

    all_opportunities.extend(
        search_category(
            "GENAI / LLM / AI AGENTS",
            genai_queries
        )
    )


    # ==================================================
    # SOFTWARE ENGINEERING
    # ==================================================

    software_queries = [

        "Software Engineer jobs India 2026",

        "Software Developer jobs India 2026",

        "Python Developer jobs India 2026",

        "Backend Engineer jobs India 2026",

        "Software Engineer AI ML India 2026",

        "Python AI developer jobs India 2026",

        "Entry level software engineer jobs India 2026",

        "Graduate software engineer jobs India 2026"
    ]

    all_opportunities.extend(
        search_category(
            "SOFTWARE ENGINEERING",
            software_queries
        )
    )


    # ==================================================
    # INTERNSHIPS
    # ==================================================

    internship_queries = [

        "AI internship India 2026",

        "Machine Learning internship India 2026",

        "Generative AI internship India 2026",

        "Software Engineering internship India 2026",

        "Python internship India 2026",

        "Computer Vision internship India 2026",

        "AI research internship India 2026",

        "ML research internship India 2026",

        "AI engineer internship India 2026"
    ]

    all_opportunities.extend(
        search_category(
            "INTERNSHIPS",
            internship_queries
        )
    )


    # ==================================================
    # APPRENTICESHIPS
    # ==================================================

    apprenticeship_queries = [

        "AI apprenticeship India 2026",

        "Machine Learning apprenticeship India 2026",

        "Software engineering apprenticeship India 2026",

        "Python apprenticeship India 2026",

        "Technology apprenticeship India 2026",

        "AI graduate apprenticeship India 2026"
    ]

    all_opportunities.extend(
        search_category(
            "APPRENTICESHIPS",
            apprenticeship_queries
        )
    )


    # ==================================================
    # RESEARCH
    # ==================================================

    research_queries = [

        "AI research internship India 2026",

        "Machine Learning research internship India 2026",

        "Artificial Intelligence research assistant India 2026",

        "Computer Vision research internship India 2026",

        "NLP research internship India 2026",

        "AI research engineer India 2026"
    ]

    all_opportunities.extend(
        search_category(
            "RESEARCH",
            research_queries
        )
    )


    # ==================================================
    # COMPANY CAREER PAGES
    # ==================================================

    company_queries = [

        "site:careers.google.com AI jobs India",

        "site:jobs.careers.microsoft.com AI jobs India",

        "site:amazon.jobs AI jobs India",

        "site:nvidia.com careers AI India",

        "site:jobs.apple.com AI India",

        "site:careers.ibm.com AI India",

        "site:careers.adobe.com AI India",

        "site:careers.oracle.com AI India",

        "site:careers.salesforce.com AI India",

        "site:careers.intel.com AI India",

        "site:careers.qualcomm.com AI India",

        "site:careers.amd.com AI India"
    ]

    all_opportunities.extend(
        search_category(
            "COMPANY CAREER PAGES",
            company_queries
        )
    )


    # ==================================================
    # INDIAN JOB PLATFORMS
    # ==================================================

    job_platform_queries = [

        "AI ML jobs India LinkedIn",

        "AI ML jobs India Naukri",

        "AI ML jobs India Indeed",

        "AI ML jobs India Foundit",

        "AI ML jobs India Cutshort",

        "AI ML jobs India Instahyre",

        "AI ML jobs India Hirist",

        "AI internships India Internshala",

        "AI internships India Unstop"
    ]

    all_opportunities.extend(
        search_category(
            "INDIAN JOB PLATFORMS",
            job_platform_queries
        )
    )


    # ==================================================
    # GOVERNMENT / PUBLIC SECTOR
    # ==================================================

    government_queries = [

        "AI jobs government India 2026",

        "Machine Learning jobs government India 2026",

        "AI internship government India 2026",

        "AI research internship government India 2026",

        "AI apprenticeship government India 2026",

        "software engineering government internship India 2026",

        "AI jobs research institutes India 2026"
    ]

    all_opportunities.extend(
        search_category(
            "GOVERNMENT / PUBLIC SECTOR",
            government_queries
        )
    )


    # ==================================================
    # REMOVE DUPLICATES
    # ==================================================

    print("\n==============================================")
    print("REMOVING DUPLICATES")
    print("==============================================")

    before = len(all_opportunities)

    all_opportunities = remove_duplicates(
        all_opportunities
    )

    after = len(all_opportunities)

    print(f"\nCollected: {before}")
    print(f"Unique:    {after}")
    print(f"Removed:   {before - after}")


    return all_opportunities


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    opportunities = search_opportunities()

    print("\n==============================================")
    print("             AGENT7 RESULTS")
    print("==============================================")

    print(
        f"\nTotal unique opportunities: "
        f"{len(opportunities)}"
    )


    for index, opportunity in enumerate(
        opportunities,
        start=1
    ):

        print("\n----------------------------------------------")

        print(
            f"[{index}] "
            f"{opportunity['title']}"
        )

        print(
            f"\nSource: "
            f"{opportunity['source']}"
        )

        print(
            f"\nURL:\n"
            f"{opportunity['url']}"
        )

        print(
            f"\nDescription:\n"
            f"{opportunity['description'][:500]}"
        )

    print("\n==============================================")
    print("       OPPORTUNITY COLLECTION COMPLETE")
    print("==============================================")