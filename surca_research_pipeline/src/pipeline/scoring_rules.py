FIELD_ORDER = [
    "aggression_present",
    "self_injury_present",
    "property_destruction_present",
    "elopement_present",
    "task_refusal_present",
    "verbal_disruption_present",
    "behavior_frequency_numeric_present",
    "behavior_duration_numeric_present",
    "baseline_data_present",
    "function_escape_stated",
    "function_attention_stated",
    "function_tangible_stated",
    "function_sensory_stated",
    "bip_exists",
    "fba_completed_stated",
    "speech_services_present",
    "ot_services_present",
    "visual_schedule_accommodation",
    "break_access_accommodation",
    "reduced_workload_accommodation",
    "safety_plan_present",
    "restraint_or_isolation_flagged",
    "ratio_1to1_explicitly_stated",
    "ratio_2to1_explicitly_stated",
]

FIELD_LABELS = {
    "aggression_present": "Aggression present",
    "self_injury_present": "Self-injury present",
    "property_destruction_present": "Property destruction present",
    "elopement_present": "Elopement present",
    "task_refusal_present": "Task refusal present",
    "verbal_disruption_present": "Verbal disruption present",
    "behavior_frequency_numeric_present": "Behavior frequency data present",
    "behavior_duration_numeric_present": "Behavior duration data present",
    "baseline_data_present": "Baseline data present",
    "function_escape_stated": "Escape function stated",
    "function_attention_stated": "Attention function stated",
    "function_tangible_stated": "Tangible function stated",
    "function_sensory_stated": "Sensory function stated",
    "bip_exists": "BIP exists",
    "fba_completed_stated": "FBA completed stated",
    "speech_services_present": "Speech services present",
    "ot_services_present": "OT services present",
    "visual_schedule_accommodation": "Visual schedule accommodation",
    "break_access_accommodation": "Break access accommodation",
    "reduced_workload_accommodation": "Reduced workload accommodation",
    "safety_plan_present": "Safety plan present",
    "restraint_or_isolation_flagged": "Restraint or isolation flagged",
    "ratio_1to1_explicitly_stated": "1:1 ratio explicitly stated",
    "ratio_2to1_explicitly_stated": "2:1 ratio explicitly stated",
}

BEHAVIOR_FIELDS = [
    "aggression_present",
    "self_injury_present",
    "property_destruction_present",
    "elopement_present",
    "task_refusal_present",
    "verbal_disruption_present",
]

FUNCTION_FIELDS = [
    "function_escape_stated",
    "function_attention_stated",
    "function_tangible_stated",
    "function_sensory_stated",
]

SERVICES_FIELDS = [
    "bip_exists",
    "fba_completed_stated",
    "speech_services_present",
    "ot_services_present",
]

ACCOMMODATION_FIELDS = [
    "visual_schedule_accommodation",
    "break_access_accommodation",
    "reduced_workload_accommodation",
]

SAFETY_FIELDS = [
    "safety_plan_present",
    "restraint_or_isolation_flagged",
]

RATIO_FIELDS = [
    "ratio_1to1_explicitly_stated",
    "ratio_2to1_explicitly_stated",
]

PROMPT_FILE_MAP = {
    "prompt_1": "PROMPT 1.md",
    "prompt_2": "PROMPT 2.md",
    "prompt_3": "PROMPT 3.md",
}

PROMPT_LABELS = {
    "prompt_1": "Broad teacher summary",
    "prompt_2": "Behavior and supports summary",
    "prompt_3": "Support level recommendation",
}

PROMPT_FIELD_COVERAGE = {
    "prompt_1": FIELD_ORDER[:],
    "prompt_2": (
        BEHAVIOR_FIELDS
        + FUNCTION_FIELDS
        + SERVICES_FIELDS
        + ACCOMMODATION_FIELDS
        + SAFETY_FIELDS
    ),
    "prompt_3": RATIO_FIELDS[:],
}

PROMPT_SCORING_NOTES = {
    "prompt_1": "Scores all 24 fields.",
    "prompt_2": "Scores behavior, function, services, accommodations, and safety fields only.",
    "prompt_3": "Scores staffing-ratio fields only.",
}

ABSTENTION_PATTERNS = {
    "not_specified": r"\bnot specified\b",
    "not_stated": r"\bnot stated\b",
    "not_documented": r"\bnot documented\b",
    "not_provided": r"\bnot provided\b",
    "not_mentioned": r"\bnot mentioned\b",
    "not_included": r"\bnot included\b",
    "cannot_determine": r"\bcannot determine\b",
    "unable_to_determine": r"\bunable to determine\b",
    "insufficient_information": r"\binsufficient information\b",
    "not_enough_information": r"\bnot enough information\b",
    "unclear": r"\bunclear\b",
    "unknown": r"\bunknown\b",
    "unable_to_tell": r"\bunable to tell\b",
}

RULES = {
    "aggression_present": {
        "positive": [
            r"\baggression\b",
            r"\baggressive\b",
            r"\bhitting\b",
            r"\bkicking\b",
            r"\bbiting\b",
            r"\bphysical aggression\b",
        ],
        "negative": [r"\bno aggression\b", r"\bnot aggressive\b"],
    },
    "self_injury_present": {
        "positive": [
            r"\bself[- ]injur",
            r"\bself harm\b",
            r"\bhead banging\b",
            r"\bscratching self\b",
            r"\bhurting (himself|herself)\b",
        ],
        "negative": [r"\bno self[- ]injur", r"\bno self harm\b"],
    },
    "property_destruction_present": {
        "positive": [
            r"\bproperty destruction\b",
            r"\bbreaking items\b",
            r"\bdamaging materials\b",
            r"\bthrowing furniture\b",
            r"\bdestroying objects\b",
        ],
        "negative": [r"\bno property destruction\b"],
    },
    "elopement_present": {
        "positive": [
            r"\belopement\b",
            r"\bruns away\b",
            r"\bleaves the classroom\b",
            r"\bwanders off\b",
            r"\bfleeing\b",
        ],
        "negative": [r"\bno elopement\b", r"\bno [^.]{0,20}\belopement\b"],
    },
    "task_refusal_present": {
        "positive": [
            r"\btask refusal\b",
            r"\bwork refusal\b",
            r"\brefuses tasks?\b",
            r"\bavoids tasks?\b",
            r"\bnoncompliance\b",
        ],
        "negative": [r"\bno task refusal\b", r"\bno work refusal\b"],
    },
    "verbal_disruption_present": {
        "positive": [
            r"\bverbal disruption\b",
            r"\byelling\b",
            r"\bscreaming\b",
            r"\bcalling out\b",
            r"\bverbal outburst\b",
            r"\bdisruptive vocalizations\b",
        ],
        "negative": [r"\bno verbal disruption\b"],
    },
    "behavior_frequency_numeric_present": {
        "positive": [
            r"\b\d+\s*(times?|x|incidents?)\s*(per|a)?\s*(day|week|class|hour)\b",
            r"\b\d+\s*-\s*\d+\s*(times?|x|incidents?)\s*(per|a)?\s*(day|week|class|hour)?\b",
            r"\bfrequency\s*:\s*\d+",
            r"\boccurs?\b[^.]{0,40}\b\d+\b",
        ],
        "negative": [],
    },
    "behavior_duration_numeric_present": {
        "positive": [
            r"\b\d+\s*(minutes?|min|hours?|hrs?)\b",
            r"\bduration\s*:\s*\d+",
            r"\blasts?\b[^.]{0,40}\b\d+\s*(minutes?|min|hours?|hrs?)\b",
        ],
        "negative": [],
    },
    "baseline_data_present": {
        "positive": [
            r"\bbaseline\b",
            r"\bcurrent level\b",
            r"\bpresent level\b",
            r"\bdata collected\b",
            r"\bdata shows\b",
        ],
        "negative": [],
    },
    "function_escape_stated": {
        "positive": [
            r"\bescape\b",
            r"\bavoid(ance|ing)?\b",
            r"\bto get out of\b",
            r"\btask avoidance\b",
        ],
        "negative": [],
    },
    "function_attention_stated": {
        "positive": [
            r"\battention\b",
            r"\badult attention\b",
            r"\bpeer attention\b",
            r"\bseeking attention\b",
        ],
        "negative": [],
    },
    "function_tangible_stated": {
        "positive": [
            r"\btangible\b",
            r"\baccess to (items|preferred items|objects|activities)\b",
        ],
        "negative": [],
    },
    "function_sensory_stated": {
        "positive": [
            r"\bsensory\b",
            r"\bautomatic reinforcement\b",
            r"\bself-stimulation\b",
        ],
        "negative": [],
    },
    "bip_exists": {
        "positive": [r"\bbip\b", r"\bbehavior intervention plan\b"],
        "negative": [r"\bno bip\b", r"\bdoes not have a bip\b"],
    },
    "fba_completed_stated": {
        "positive": [
            r"\bfba\b",
            r"\bfunctional behavioral assessment\b",
            r"\bfunctional behavior assessment\b",
        ],
        "negative": [r"\bno fba\b"],
    },
    "speech_services_present": {
        "positive": [
            r"\bspeech services\b",
            r"\bspeech therapy\b",
            r"\bslp\b",
            r"\bspeech-language\b",
        ],
        "negative": [r"\bno speech services\b"],
    },
    "ot_services_present": {
        "positive": [
            r"\bot services\b",
            r"\boccupational therapy\b",
            r"\bot sessions?\b",
        ],
        "negative": [r"\bno ot services\b", r"\bno occupational therapy\b"],
    },
    "visual_schedule_accommodation": {
        "positive": [r"\bvisual schedule\b", r"\bvisual supports?\b", r"\bvisual routine\b"],
        "negative": [],
    },
    "break_access_accommodation": {
        "positive": [
            r"\bbreak access\b",
            r"\baccess to breaks?\b",
            r"\bmovement breaks?\b",
            r"\bsensory breaks?\b",
            r"\brequesting a break\b",
            r"\bbreak card\b",
        ],
        "negative": [],
    },
    "reduced_workload_accommodation": {
        "positive": [
            r"\breduced workload\b",
            r"\bshortened assignments?\b",
            r"\breduced assignment\b",
            r"\bmodified workload\b",
        ],
        "negative": [],
    },
    "safety_plan_present": {
        "positive": [r"\bsafety plan\b", r"\bcrisis plan\b", r"\bemergency response protocol\b"],
        "negative": [],
    },
    "restraint_or_isolation_flagged": {
        "positive": [r"\brestraint\b", r"\bisolation\b", r"\bseclusion\b"],
        "negative": [r"\bno restraint\b", r"\bno isolation\b", r"\bnot using restraint\b"],
    },
    "ratio_1to1_explicitly_stated": {
        "positive": [r"\b1:1\b", r"\bone-to-one\b", r"\b1 to 1\b"],
        "negative": [
            r"\bnot 1:1\b",
            r"\bnot specified\b[^.]{0,40}\b1:1\b",
            r"\bnot stated\b[^.]{0,40}\b1:1\b",
            r"\bnot documented\b[^.]{0,40}\b1:1\b",
            r"\bcannot determine\b[^.]{0,40}\b1:1\b",
            r"\bunable to determine\b[^.]{0,40}\b1:1\b",
        ],
    },
    "ratio_2to1_explicitly_stated": {
        "positive": [r"\b2:1\b", r"\btwo-to-one\b", r"\b2 to 1\b"],
        "negative": [
            r"\bnot 2:1\b",
            r"\bnot specified\b[^.]{0,40}\b2:1\b",
            r"\bnot stated\b[^.]{0,40}\b2:1\b",
            r"\bnot documented\b[^.]{0,40}\b2:1\b",
            r"\bcannot determine\b[^.]{0,40}\b2:1\b",
            r"\bunable to determine\b[^.]{0,40}\b2:1\b",
        ],
    },
}
