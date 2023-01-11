#!/usr/bin/env python3
import os
import traceback
import argparse
import re
import requests
import json


def main():
    try:
        cli = Cli()
        args = cli.getConfig()
        out = cli.action(args)
        print(out)
    except CliException as e:
        exit(e)
    except Exception as e:
        exit(traceback.format_exc())


class CliException(Exception):
    """Incorrect command line invocation."""

    pass


class Cli:
    def getConfig(self):
        """parse and validate user input, return args"""
        parser = argparse.ArgumentParser(
            prog="Trello CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="A command-line tool for interacting with the Trello API.",
            epilog=r"""
EXAMPLES:
  export TRELLO_API_KEY=...
  export TRELLO_API_TOKEN=...
  ./trello_cli.py --list-boards
  ./trello_cli.py --list-columns --board 63bf64bde649ea019b59ac9d
  ./trello_cli.py --list-labels --board 63bf64bde649ea019b59ac9d
  ./trello_cli.py --add-card --list-id 63bf668eeea146001ad17e56 \
                    --name "test card name" \
                    --description "test card description" \
                    --label_ids 63bf64bdbfa825468a035190,63bf64bdbfa825468a035191
  ./trello_cli.py --add-comment --card-id 63bf9a20e0e2720065fad56e \
                    --comment "test comment"
""",
        )
        parser.add_argument(
            "--key",
            default=os.environ.get("TRELLO_API_KEY"),
            help="(required) Trello API Key",
        )
        parser.add_argument(
            "--token",
            default=os.environ.get("TRELLO_API_TOKEN"),
            help="(required) Trello API Token",
        )
        parser.add_argument(
            "--list-boards", action="store_true", help="Action: List all boards."
        )
        parser.add_argument(
            "--list-columns",
            action="store_true",
            help="Action: List all columns of a board.",
        )
        parser.add_argument(
            "--add-card",
            action="store_true",
            help="Action: Add card to an existing board list.",
        )
        parser.add_argument(
            "--add-comment",
            action="store_true",
            help="Action: Add a comment to an existing card.",
        )
        parser.add_argument(
            "--list-labels",
            action="store_true",
            help="Action: List labels from a given board.",
        )
        parser.add_argument("--board-id", help="Board id to interact with.")
        parser.add_argument("--list-id", help="List id to interact with.")
        parser.add_argument("--card-id", help="Card id to interact with.")
        parser.add_argument("--name", help="Card name to add")
        parser.add_argument("--description", help="Card description to add.")
        parser.add_argument("--comment", help="Card comment to add.")
        parser.add_argument(
            "--label_ids",
            default="",
            help="Comma-separated list of label ids to attach.",
        )
        parser.add_argument(
            "-v", "--version", action="version", version="%(prog)s 1.0.0"
        )
        parsed = parser.parse_args()
        if not parsed.key or not parsed.token:
            raise CliException(
                "--key and --token are required to interact with the Trello API."
            )
        args = {
            "key": parsed.key,
            "token": parsed.token,
            "list_boards": parsed.list_boards,
            "list_columns": parsed.list_columns,
            "list_labels": parsed.list_labels,
            "add_card": parsed.add_card,
            "add_comment": parsed.add_comment,
            "board_id": parsed.board_id,
            "list_id": parsed.list_id,
            "card_id": parsed.card_id,
            "name": parsed.name,
            "description": parsed.description,
            "comment": parsed.comment,
            "label_ids": re.split("\s+,\s+", parsed.label_ids),
        }
        return args

    def action(self, args):
        """execute the requested action, return console output"""
        out = ""
        trello = Trello(args["key"], args["token"])
        if args["list_boards"]:
            boards = trello.listBoards()
            for board in boards:
                out += board["id"] + " " + board["name"] + "\n"

        elif args["list_columns"]:
            if not args["board_id"]:
                raise CliException("--board_id is required to list columns.")
            lists = trello.listColumns(args["board_id"])
            for list in lists:
                out += list["id"] + " " + list["name"] + "\n"

        elif args["list_labels"]:
            if not args["board_id"]:
                raise CliException("--board_id is required to list labels.")
            labels = trello.listLabels(args["board_id"])
            for label in labels:
                out += label["id"] + " " + label["name"] + " " + label["color"] + "\n"

        elif args["add_card"]:
            if not args["list_id"] or not args["name"] or not args["description"]:
                raise CliException(
                    "--list_id, --name, and --description are required to add a card."
                )
            card = trello.addCard(
                args["list_id"],
                args["name"],
                args["description"],
                args["label_ids"],
            )
            out += card["id"] + " added.\n"

        elif args["add_comment"]:
            if not args["card_id"] or not args["comment"]:
                raise CliException(
                    "--card_id and --comment are required to add a comment."
                )
            comment = trello.addComment(
                args["card_id"],
                args["comment"],
            )
            out += comment["id"] + " added.\n"

        else:
            raise CliException(
                """Please specify an action:

  --list-boards
  --list-columns
  --list-labels
  --add-card
  --add-comment
    
or specify --help for more information."""
            )
        return out


class ApiRequestException(Exception):
    """Failed to query Trello API"""

    pass


# Trello API Docs
# https://developer.atlassian.com/cloud/trello/guides/rest-api/api-introduction/
# https://developer.atlassian.com/cloud/trello/rest/


class Trello:
    BASE_URI = "https://api.trello.com"
    HEADERS = {"Accept": "application/json"}

    def __init__(self, key, token):
        self.key, self.token = key, token

    def request(self, method, uri, query=None):
        """perform an HTTP POST request to the Trello API, return parsed json response"""
        url = f"{self.BASE_URI}{uri}?key={self.key}&token={self.token}"
        if "GET" == method:
            r = requests.get(url, headers=self.HEADERS, params=query)
        elif "POST" == method:
            r = requests.post(url, headers=self.HEADERS, params=query)
        if 200 == r.status_code:
            parsed = json.loads(r.text)
            return parsed
        else:
            raise ApiRequestException(
                f"Trello API returned status code {r.status_code}. response body: {r.text}"
            )

    def listBoards(self):
        """query Trello API, return list of boards"""
        boards = self.request("GET", "/1/members/me/boards")
        return boards

    def listColumns(self, boardId):
        """query Trello API, return list of board columns"""
        lists = self.request("GET", "/1/boards/" + boardId + "/lists")
        return lists

    def listLabels(self, boardId):
        """query Trello API, return list of board labels"""
        labels = self.request("GET", "/1/boards/" + boardId + "/labels")
        return labels

    def addCard(self, listId, name, description, labels=None):
        """POST a new card to the Trello API"""
        if labels is None:
            labels = []
        card = self.request(
            "POST",
            "/1/cards",
            {
                "idList": listId,
                "name": name,
                "desc": description,
                "idLabels": ",".join(labels),
            },
        )
        return card

    def addComment(self, cardId, comment):
        """post a new comment to the Trello API"""
        comment = self.request(
            "POST",
            f"/1/cards/{cardId}/actions/comments",
            {
                "id": cardId,
                "text": comment,
            },
        )
        return comment


if __name__ == "__main__":
    main()
