import sqlite3
import os


# ==================================================
# DATABASE PATH
# ==================================================

DATABASE_PATH = os.path.join(
    os.path.dirname(__file__),
    "agent7_jobs.db"
)


# ==================================================
# CONNECT TO DATABASE
# ==================================================

def get_connection():
    """
    Create a connection to the Agent7 jobs database.
    """

    return sqlite3.connect(
        DATABASE_PATH
    )


# ==================================================
# CREATE DATABASE
# ==================================================

def initialize_database():
    """
    Create the opportunities table if it
    does not already exist.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            url TEXT UNIQUE NOT NULL,

            description TEXT,

            source TEXT,

            match_level TEXT,

            match_reason TEXT,

            opportunity_type TEXT,

            notified INTEGER DEFAULT 0,

            discovered_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
    """)

    connection.commit()

    connection.close()

    print("\nJobs database initialized.")


# ==================================================
# CHECK OPPORTUNITY
# ==================================================

def opportunity_exists(url):
    """
    Check whether an opportunity URL already
    exists in the database.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM opportunities
        WHERE url = ?
        """,
        (url,)
    )

    result = cursor.fetchone()

    connection.close()

    return result is not None


# ==================================================
# SAVE OPPORTUNITY
# ==================================================

def save_opportunity(opportunity):
    """
    Save one opportunity to the database.
    """

    url = opportunity.get(
        "url",
        ""
    )

    if not url:
        return False

    # ----------------------------------------------
    # Don't save duplicates
    # ----------------------------------------------

    if opportunity_exists(url):

        return False

    match = opportunity.get(
        "match",
        {}
    )

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO opportunities (
                title,
                url,
                description,
                source,
                match_level,
                match_reason,
                opportunity_type,
                notified
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                opportunity.get(
                    "title",
                    ""
                ),

                url,

                opportunity.get(
                    "description",
                    ""
                ),

                opportunity.get(
                    "source",
                    ""
                ),

                match.get(
                    "match_level",
                    ""
                ),

                match.get(
                    "reason",
                    ""
                ),

                match.get(
                    "opportunity_type",
                    "unknown"
                ),

                0
            )
        )

        connection.commit()

    except sqlite3.IntegrityError:

        connection.close()

        return False

    connection.close()

    return True


# ==================================================
# SAVE MULTIPLE OPPORTUNITIES
# ==================================================

def save_opportunities(opportunities):
    """
    Save multiple opportunities.
    """

    saved = 0
    skipped = 0

    for opportunity in opportunities:

        if save_opportunity(
            opportunity
        ):

            saved += 1

        else:

            skipped += 1

    print("\n================================")
    print("DATABASE SAVE COMPLETE")
    print("================================")

    print(
        f"\nSaved:   {saved}"
    )

    print(
        f"Skipped: {skipped}"
    )

    return saved


# ==================================================
# GET UNNOTIFIED MATCHES
# ==================================================

def get_unnotified_matches():
    """
    Return matching opportunities that
    have not been notified yet.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            title,
            url,
            description,
            source,
            match_level,
            match_reason,
            opportunity_type,
            discovered_at

        FROM opportunities

        WHERE
            notified = 0
            AND match_level IN (
                'strong',
                'possible'
            )

        ORDER BY discovered_at DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    opportunities = []

    for row in rows:

        opportunities.append({

            "id": row[0],

            "title": row[1],

            "url": row[2],

            "description": row[3],

            "source": row[4],

            "match_level": row[5],

            "reason": row[6],

            "opportunity_type": row[7],

            "discovered_at": row[8]

        })

    return opportunities


# ==================================================
# MARK AS NOTIFIED
# ==================================================

def mark_as_notified(opportunity_id):
    """
    Mark an opportunity as notified.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE opportunities

        SET notified = 1

        WHERE id = ?
        """,
        (opportunity_id,)
    )

    connection.commit()

    connection.close()


# ==================================================
# DATABASE STATISTICS
# ==================================================

def get_statistics():
    """
    Show basic database statistics.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM opportunities"
    )

    total = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM opportunities
        WHERE notified = 0
        AND match_level IN ('strong', 'possible')
        """
    )

    unnotified = cursor.fetchone()[0]

    connection.close()

    return {
        "total": total,
        "unnotified_matches": unnotified
    }


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    print("\n==============================================")
    print("          AGENT7 JOB DATABASE")
    print("==============================================")

    # ----------------------------------------------
    # Create database
    # ----------------------------------------------

    initialize_database()

    # ----------------------------------------------
    # Show statistics
    # ----------------------------------------------

    stats = get_statistics()

    print("\nDatabase statistics:")

    print(
        f"Total opportunities: "
        f"{stats['total']}"
    )

    print(
        f"Unnotified matches: "
        f"{stats['unnotified_matches']}"
    )

    print("\n==============================================")
    print("             DATABASE READY")
    print("==============================================")