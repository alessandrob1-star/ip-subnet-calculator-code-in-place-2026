import ipaddress
import unittest

from main import SubnetCalculatorGUI, is_power_of_two


class PowerOfTwoValidationTests(unittest.TestCase):
    def test_accepts_positive_powers_of_two(self):
        for value in (1, 2, 4, 8, 16, 1024):
            with self.subTest(value=value):
                self.assertTrue(is_power_of_two(value))

    def test_rejects_other_values(self):
        for value in (-2, -1, 0, 3, 5, 6, 12):
            with self.subTest(value=value):
                self.assertFalse(is_power_of_two(value))

    def test_offline_tutor_rejects_uneven_subnet_count(self):
        gui = object.__new__(SubnetCalculatorGUI)
        answer = gui.explain_subnet_split(
            ipaddress.ip_network("192.168.0.0/24"),
            3,
        )

        self.assertIn("power-of-two", answer)

    def test_offline_tutor_still_splits_valid_subnet_count(self):
        gui = object.__new__(SubnetCalculatorGUI)
        answer = gui.explain_subnet_split(
            ipaddress.ip_network("192.168.0.0/24"),
            4,
        )

        self.assertIn("new prefix is /26", answer)
        self.assertIn("4. 192.168.0.192/26", answer)


if __name__ == "__main__":
    unittest.main()
