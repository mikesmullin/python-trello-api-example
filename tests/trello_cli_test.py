import unittest
import sys
import fixtures

sys.path.append("../src/")
from trello_cli import Trello


class TestTrello(unittest.TestCase):
    """A suite of integration tests"""

    def test_list_boards(self):
        args = fixtures.getMockArgs()
        trello = Trello(args["key"], args["secret"], args["token"])
        boards = trello.listBoards()
        board = next(
            (board for board in boards if board["id"] == fixtures.FIXTURE_BOARD_ID)
        )
        self.assertIsNotNone(board)

    def test_list_columns(self):
        args = fixtures.getMockArgs()
        trello = Trello(args["key"], args["secret"], args["token"])
        lists = trello.listColumns(fixtures.FIXTURE_BOARD_ID)
        expected = [list["id"] for list in lists]
        self.assertTrue(fixtures.FIXTURE_LIST_IDS == expected)

    def test_list_labels(self):
        args = fixtures.getMockArgs()
        trello = Trello(args["key"], args["secret"], args["token"])
        labels = trello.listLabels(fixtures.FIXTURE_BOARD_ID)
        expected = [label["id"] for label in labels]
        self.assertTrue(fixtures.FIXTURE_LABEL_IDS == expected)

    def test_add_card(self):
        args = fixtures.getMockArgs()
        trello = Trello(args["key"], args["secret"], args["token"])
        card = trello.addCard(
            fixtures.FIXTURE_LIST_IDS[0],  # A
            "test card",
            "test description",
            fixtures.FIXTURE_LABEL_IDS,
        )
        return card

    def test_add_comment(self):
        args = fixtures.getMockArgs()
        trello = Trello(args["key"], args["secret"], args["token"])
        comment = trello.addComment(
            fixtures.FIXTURE_COMMENT_ID,
            "test comment",
        )
        return comment


if __name__ == "__main__":
    unittest.main()
