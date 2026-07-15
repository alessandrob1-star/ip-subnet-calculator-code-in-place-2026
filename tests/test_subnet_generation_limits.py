import ipaddress
import unittest
from unittest.mock import Mock, patch

from main import MAX_SUBNETS_TO_DISPLAY, SubnetCalculatorGUI


class SubnetGenerationLimitTests(unittest.TestCase):
    def test_gui_rejects_more_subnets_than_it_can_display(self):
        gui = object.__new__(SubnetCalculatorGUI)
        gui.entry_network = Mock()
        gui.entry_network.get.return_value = "0.0.0.0/0"
        gui.entry_subnets = Mock()
        gui.entry_subnets.get.return_value = str(MAX_SUBNETS_TO_DISPLAY * 2)
        gui.result_text2 = Mock()

        with patch("main.messagebox.showerror") as showerror:
            gui.do_subnetting()

        showerror.assert_called_once()
        self.assertIn("at most", showerror.call_args.args[1])
        gui.result_text2.insert.assert_not_called()

    def test_tutor_generates_only_first_four_large_subnets(self):
        gui = object.__new__(SubnetCalculatorGUI)
        answer = gui.explain_subnet_split(
            ipaddress.ip_network("0.0.0.0/0"),
            2**32,
        )

        self.assertIn("1. 0.0.0.0/32", answer)
        self.assertIn("4. 0.0.0.3/32", answer)
        self.assertIn("I showed the first 4 subnets", answer)


if __name__ == "__main__":
    unittest.main()
