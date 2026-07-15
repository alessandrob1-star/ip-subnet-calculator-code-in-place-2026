import ipaddress
import unittest

from main import SubnetCalculatorGUI, get_usable_host_info


class UsableHostTests(unittest.TestCase):
    def test_standard_subnet_excludes_network_and_broadcast(self):
        count, first, last, rule = get_usable_host_info(
            ipaddress.ip_network("192.168.1.0/24")
        )

        self.assertEqual(count, 254)
        self.assertEqual(str(first), "192.168.1.1")
        self.assertEqual(str(last), "192.168.1.254")
        self.assertEqual(rule, "Total - 2")

    def test_slash_31_uses_both_point_to_point_addresses(self):
        count, first, last, rule = get_usable_host_info(
            ipaddress.ip_network("192.168.1.0/31")
        )

        self.assertEqual(count, 2)
        self.assertEqual(str(first), "192.168.1.0")
        self.assertEqual(str(last), "192.168.1.1")
        self.assertEqual(rule, "RFC 3021 point-to-point")

    def test_slash_32_is_a_single_host_route(self):
        count, first, last, rule = get_usable_host_info(
            ipaddress.ip_network("192.168.1.25/32")
        )

        self.assertEqual(count, 1)
        self.assertEqual(first, last)
        self.assertEqual(str(first), "192.168.1.25")
        self.assertEqual(rule, "Single-host route")

    def test_offline_tutor_explains_slash_31_and_slash_32(self):
        gui = object.__new__(SubnetCalculatorGUI)

        slash_31 = gui.get_local_ai_response("How many hosts are in /31?")
        slash_32 = gui.get_local_ai_response("How many hosts are in /32?")

        self.assertIn("2 usable hosts", slash_31)
        self.assertIn("RFC 3021 point-to-point", slash_31)
        self.assertIn("1 usable host", slash_32)
        self.assertIn("Single-host route", slash_32)

    def test_subnet_split_lists_only_usable_host_ranges(self):
        gui = object.__new__(SubnetCalculatorGUI)

        standard = gui.explain_subnet_split(
            ipaddress.ip_network("192.168.0.0/24"),
            4,
        )
        point_to_point = gui.explain_subnet_split(
            ipaddress.ip_network("192.168.0.0/29"),
            4,
        )

        self.assertIn("range: 192.168.0.1 - 192.168.0.62", standard)
        self.assertNotIn("range: 192.168.0.0 - 192.168.0.63", standard)
        self.assertIn("hosts: 2 | range: 192.168.0.0 - 192.168.0.1", point_to_point)


if __name__ == "__main__":
    unittest.main()
