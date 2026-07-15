import unittest

from main import get_chat_message_replacement


class ChatConcurrencyTests(unittest.TestCase):
    def test_response_targets_its_own_pending_request(self):
        content = (
            "AI Tutor: Thinking... (request #1)\n\n"
            "AI Tutor: Thinking... (request #2)\n\n"
        )

        replacement = get_chat_message_replacement(
            content,
            "AI Tutor",
            1,
            "First answer",
        )

        self.assertIsNotNone(replacement)
        index, length, text = replacement
        updated = content[:index] + text + content[index + length:]
        self.assertTrue(updated.startswith("AI Tutor: First answer"))
        self.assertIn("Thinking... (request #2)", updated)

    def test_out_of_order_response_does_not_replace_another_request(self):
        content = (
            "AI Tutor: Thinking... (request #1)\n\n"
            "AI Tutor: Thinking... (request #2)\n\n"
        )

        replacement = get_chat_message_replacement(
            content,
            "AI Tutor",
            2,
            "Second answer",
        )

        index, length, text = replacement
        updated = content[:index] + text + content[index + length:]
        self.assertIn("Thinking... (request #1)", updated)
        self.assertTrue(updated.endswith("AI Tutor: Second answer\n\n"))

    def test_cleared_pending_request_drops_stale_response(self):
        content_after_clear = "AI Tutor: Hi! Ask me about CIDR.\n\n"

        replacement = get_chat_message_replacement(
            content_after_clear,
            "AI Tutor",
            1,
            "Stale answer",
        )

        self.assertIsNone(replacement)


if __name__ == "__main__":
    unittest.main()
