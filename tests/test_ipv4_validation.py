import ipaddress
import unittest

from main import parse_ipv4_network


class IPv4ValidationTests(unittest.TestCase):
    def test_parses_ipv4_host_with_prefix_as_its_network(self):
        network = parse_ipv4_network("192.168.1.25/24")

        self.assertIsInstance(network, ipaddress.IPv4Network)
        self.assertEqual(str(network), "192.168.1.0/24")

    def test_rejects_ipv6_with_a_clear_message(self):
        with self.assertRaisesRegex(
            ValueError,
            "This calculator supports IPv4 addresses only",
        ):
            parse_ipv4_network("2001:db8::/64")

    def test_preserves_invalid_ipv4_errors(self):
        with self.assertRaises(ValueError):
            parse_ipv4_network("999.168.1.1/24")


if __name__ == "__main__":
    unittest.main()
