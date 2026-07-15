import unittest
from unittest.mock import patch

from main import SubnetCalculatorGUI


class ChatbotResponseSourceTests(unittest.TestCase):
    def setUp(self):
        self.gui = object.__new__(SubnetCalculatorGUI)

    def test_missing_api_key_returns_an_explicit_reason(self):
        with patch("main.os.getenv", return_value=None):
            answer, reason = self.gui.get_online_ai_response("What is CIDR?")

        self.assertIsNone(answer)
        self.assertEqual(reason, "OPENAI_API_KEY is not configured")

    def test_online_answer_is_labeled(self):
        with (
            patch.object(self.gui, "get_online_ai_response", return_value=("Online answer", None)),
            patch.object(self.gui, "get_local_ai_response") as local_answer,
        ):
            answer = self.gui.build_chat_answer("What is CIDR?")

        self.assertEqual(answer, "Mode: Online AI\n\nOnline answer")
        local_answer.assert_not_called()

    def test_offline_fallback_is_labeled_with_reason(self):
        with (
            patch.object(
                self.gui,
                "get_online_ai_response",
                return_value=(None, "OpenAI API is unavailable"),
            ),
            patch.object(self.gui, "get_local_ai_response", return_value="Offline answer"),
        ):
            answer = self.gui.build_chat_answer("What is CIDR?")

        self.assertEqual(
            answer,
            "Mode: Offline tutor (OpenAI API is unavailable)\n\nOffline answer",
        )


if __name__ == "__main__":
    unittest.main()
