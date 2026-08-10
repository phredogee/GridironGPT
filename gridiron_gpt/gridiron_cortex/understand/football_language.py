from dataclasses import dataclass


@dataclass(frozen=True)
class FootballConcept:
    name: str
    category: str
    sentiment: str
    impact: float
    confidence: float
    keywords: tuple[str, ...]


CONCEPTS = [
    # -----------------------------------------------------------------
    # HEALTH
    # -----------------------------------------------------------------
    FootballConcept(
        name="return_to_play",
        category="health",
        sentiment="positive",
        impact=0.90,
        confidence=0.90,
        keywords=(
            "returns",
            "returned",
            "returns to practice",
            "back at practice",
            "cleared",
            "activated",
            "aims to play",
            "expected to play",
            "full participant",
        ),
    ),

    FootballConcept(
        name="injury",
        category="health",
        sentiment="negative",
        impact=-1.00,
        confidence=0.95,
        keywords=(
            "injured",
            "injury",
            "out",
            "game-time decision",
            "gametime decision",
            "snap count",
            "questionable",
            "doubtful",
            "setback",
            "missed practice",
            "limited",
            "limited participant",
        ),
    ),

    # -----------------------------------------------------------------
    # OPPORTUNITY
    # -----------------------------------------------------------------
    FootballConcept(
        name="role_expansion",
        category="opportunity",
        sentiment="positive",
        impact=0.85,
        confidence=0.85,
        keywords=(
            # First-team usage
            "working with the starters",
            "running with the starters",
            "taking starter reps",

            # Role increases
            "named starter",
            "expected to start",
            "earned starting job",
            "won the starting job",
            "promoted to starter",
            "listed atop the depth chart",
            "moving up the depth chart",
            "climbing the depth chart",
            "moving up the depth chart",
            "working ahead of",
            "ahead of",
            "listed ahead of",


            # Usage increases
            "larger role",
            "expanded role",
            "increased role",
            "more opportunities",
            "increased touches",
            "increased workload",
            "featured role",
            "more snaps",
            "larger snap share",
        ),
    ),

    FootballConcept(
        name="timeshare",
        category="opportunity",
        sentiment="negative",
        impact=-0.60,
        confidence=0.85,
        keywords=(
            "timeshare",
            "committee",
            "rotation",
            "split reps",
            "shared workload",
            "backfield competition",
        ),
    ),

    FootballConcept(
        name="workhorse_back",
        category="rushing_opportunity",
        sentiment="positive",
        impact=0.90,
        confidence=0.92,
        keywords=(
            "workhorse",
            "bell cow",
            "bell-cow",
            "every-down back",
            "three-down back",
            "featured back",
            "lead back",
            "heavy workload",
            "carry the load",
        ),
    ),

    # -----------------------------------------------------------------
    # PASSING GAME
    # -----------------------------------------------------------------
    FootballConcept(
        name="favorite_receiver",
        category="receiving_opportunity",
        sentiment="positive",
        impact=0.85,
        confidence=0.90,
        keywords=(
            "favorite receiver",
            "favorite target",
            "quarterback's favorite receiver",
            "quarterback's favorite target",
            "qb's favorite receiver",
            "qb's favorite target",
            "go-to receiver",
            "go-to target",
            "primary receiver",
            "primary target",
            "top target",
            "security blanket",
        ),
    ),

    # -----------------------------------------------------------------
    # DISCIPLINE / AVAILABILITY
    # -----------------------------------------------------------------
    FootballConcept(
        name="suspension",
        category="availability",
        sentiment="negative",
        impact=-1.00,
        confidence=1.00,
        keywords=(
            "suspended",
            "suspension",
        ),
    ),

# -----------------------------------------------------------------
# TRAINING CAMP — POSITIVE
# -----------------------------------------------------------------
    FootballConcept(
        name="camp_standout",
        category="training_camp",
        sentiment="positive",
        impact=0.70,
        confidence=0.78,
        keywords=(
            "camp standout",
            "standout performer",
            "standing out in camp",
            "impressive camp",
            "impressing in camp",
            "turned heads",
            "turning heads",
            "making plays every day",
            "one of the best players in camp",
        ),
    ),

    FootballConcept(
        name="looked_explosive",
        category="training_camp",
        sentiment="positive",
        impact=0.65,
        confidence=0.75,
        keywords=(
            "looked explosive",
            "looks explosive",
            "showed explosiveness",
            "has his burst back",
            "showing burst",
            "moving well",
            "looked fast",
            "looks fast",
        ),
    ),

    FootballConcept(
        name="camp_chemistry",
        category="training_camp",
        sentiment="positive",
        impact=0.60,
        confidence=0.72,
        keywords=(
            "building chemistry",
            "strong chemistry",
            "developing chemistry",
            "on the same page",
            "connection is growing",
            "rapport is improving",
            "working well together",
        ),
    ),

    FootballConcept(
        name="coach_praise",
        category="training_camp",
        sentiment="positive",
        impact=0.55,
        confidence=0.70,
        keywords=(
            "earned praise",
            "drawing praise",
            "coach praised",
            "coaches praised",
            "coaching staff praised",
            "impressed the coaching staff",
            "coach spoke highly of",
            "staff is excited about",
        ),
    ),

    FootballConcept(
        name="camp_role_gain",
        category="training_camp",
        sentiment="positive",
        impact=0.80,
        confidence=0.84,
        keywords=(
            "earning more reps",
            "seeing more reps",
            "running with the starters",
        ),
    ),

# -----------------------------------------------------------------
# TRAINING CAMP — NEGATIVE
# -----------------------------------------------------------------
    FootballConcept(
        name="camp_struggles",
        category="training_camp",
        sentiment="negative",
        impact=-0.65,
        confidence=0.76,
        keywords=(
            "struggled in camp",
            "struggling in camp",
            "has struggled",
            "inconsistent in camp",
            "poor camp",
            "rough camp",
            "having trouble",
            "failing to stand out",
        ),
    ),

    FootballConcept(
        name="camp_role_loss",
        category="training_camp",
        sentiment="negative",
        impact=-0.75,
        confidence=0.82,
        keywords=(
            "losing reps",
            "fewer reps",
            "seeing fewer reps",
        ),
    ),

    FootballConcept(
        name="conditioning_concern",
        category="training_camp",
        sentiment="negative",
        impact=-0.55,
        confidence=0.74,
        keywords=(
            "conditioning concern",
            "conditioning concerns",
            "not in football shape",
            "out of shape",
            "working into shape",
            "needs better conditioning",
            "fatigued during practice",
        ),
    ),

    FootballConcept(
        name="limited_camp_reps",
        category="training_camp",
        sentiment="negative",
        impact=-0.45,
        confidence=0.72,
        keywords=(
            "limited reps",
            "limited in camp",
            "being eased in",
            "on a pitch count",
            "practice pitch count",
            "restricted workload",
            "not participating fully",
        ),
    ),

# -----------------------------------------------------------------
# DEPTH CHART — POSITIVE
# -----------------------------------------------------------------
FootballConcept(
    name="named_starter",
    category="depth_chart",
    sentiment="positive",
    impact=0.85,
    confidence=0.90,
    keywords=(
        "named starter",
        "named the starter",
        "announced as the starter",
        "will start",
        "expected to start",
        "earned the starting job",
        "won the starting job",
        "secured the starting job",
        "listed as the starter",
        "listed first on the depth chart",
        "atop the depth chart",
    ),
),

FootballConcept(
    name="depth_chart_promotion",
    category="depth_chart",
    sentiment="positive",
    impact=0.75,
    confidence=0.84,
    keywords=(
        "promoted",
        "moved up the depth chart",
        "moving up the depth chart",
        "climbing the depth chart",
        "moved ahead of",
        "working ahead of",
        "listed ahead of",
        "passed on the depth chart",
        "elevated to the first team",
    ),
),

FootballConcept(
    name="first_team_role",
    category="depth_chart",
    sentiment="positive",
    impact=0.80,
    confidence=0.86,
    keywords=(
        "taking first-team reps",
        "taking first team reps",
        "practicing with the first team",
        "practicing with first team",
        "working with the first team",
        "working with first team",
        "running with the first team",
        "running with first team",
        "running with the first-team offense",
        "working with the starters",
        "running with the starters",
        "taking starter reps",
    ),
),

# -----------------------------------------------------------------
# DEPTH CHART — NEGATIVE
# -----------------------------------------------------------------
    FootballConcept(
        name="lost_starting_job",
        category="depth_chart",
        sentiment="negative",
        impact=-0.85,
        confidence=0.90,
        keywords=(
            "lost the starting job",
            "no longer the starter",
            "replaced as starter",
            "removed from the starting lineup",
            "benched in favor of",
            "moved out of the starting lineup",
        ),
    ),

    FootballConcept(
        name="depth_chart_demotion",
        category="depth_chart",
        sentiment="negative",
        impact=-0.75,
        confidence=0.85,
        keywords=(
            "demoted",
            "moved down the depth chart",
            "slipping down the depth chart",
            "fell behind",
            "falling behind",
            "moved behind",
            "listed behind",
            "placed on the practice squad",
            "passed on the depth chart by",
            "buried on the depth chart",
        ),
    ),

    FootballConcept(
        name="second_team_role",
        category="depth_chart",
        sentiment="negative",
        impact=-0.65,
        confidence=0.82,
        keywords=(
            "working with the second team",
            "running with the second team",
            "taking second-team reps",
            "taking second team reps",
            "working with the backups",
            "running with the backups",
            "second-team offense",
            "backup reps",
        ),
    ),

]
