import ipaddress
import unittest

from main import get_network_scope


class NetworkScopeTests(unittest.TestCase):
    def assert_scope(self, cidr, expected):
        network = ipaddress.ip_network(cidr)
        self.assertEqual(get_network_scope(network), expected)

    def test_rfc1918_networks_are_private(self):
        for cidr in ("10.0.0.0/8", "172.20.0.0/16", "192.168.1.0/24"):
            with self.subTest(cidr=cidr):
                self.assert_scope(cidr, "Private (RFC 1918)")

    def test_globally_routable_network_is_public(self):
        self.assert_scope("8.8.8.0/24", "Public (globally routable)")

    def test_shared_address_space_is_not_public(self):
        self.assert_scope("100.64.0.0/10", "Shared Address Space (CGNAT)")

    def test_documentation_network_is_identified(self):
        self.assert_scope("203.0.113.0/24", "Documentation (TEST-NET)")

    def test_special_address_scopes_are_identified(self):
        cases = {
            "127.0.0.0/8": "Loopback",
            "169.254.0.0/16": "Link-local",
            "224.0.0.0/4": "Multicast",
            "240.0.0.0/4": "Reserved",
            "0.0.0.0/32": "Unspecified",
        }
        for cidr, expected in cases.items():
            with self.subTest(cidr=cidr):
                self.assert_scope(cidr, expected)


if __name__ == "__main__":
    unittest.main()
