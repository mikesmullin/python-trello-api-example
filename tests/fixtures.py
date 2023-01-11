import os

# NOTICE: You'll need to customize these values according to your environment.
FIXTURE_BOARD_ID = "63bf64bde649ea019b59ac9d"
FIXTURE_LIST_IDS = [
    "63bf668dfa06cf0066442182",
    "63bf668eeea146001ad17e56",
    "63bf668f97cfe800db5d74b2",
]
FIXTURE_LABEL_IDS = [
    "63bf64bdbfa825468a035190",
    "63bf64bdbfa825468a035191",
    "63bf64bdbfa825468a035195",
    "63bf64bdbfa825468a035198",
    "63bf64bdbfa825468a03519b",
    "63bf64bdbfa825468a03519d",
]
FIXTURE_COMMENT_ID = "63bf9a20e0e2720065fad56e"


def getMockArgs():
    args = {
        "key": os.environ.get("TRELLO_API_KEY"),
        "token": os.environ.get("TRELLO_API_TOKEN"),
    }
    return args
