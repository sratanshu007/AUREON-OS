import unittest
import sys
import os
import importlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import modules with hyphens
system_service_mod = importlib.import_module("services.system-service.system_service")
security_service_mod = importlib.import_module("services.security-service.security_service")

SystemMetricsCollector = system_service_mod.SystemMetricsCollector
SecurityService = security_service_mod.SecurityService

class TestServicesIntegration(unittest.TestCase):
    def test_metrics_collector(self):
        m = SystemMetricsCollector.get_metrics()
        self.assertIn("cpu", m)
        self.assertIn("memory", m)
        self.assertIn("storage", m)
        self.assertGreaterEqual(m["cpu"]["usage_percent"], 0.0)

    def test_security_service(self):
        sec = SecurityService()
        perm = sec.check_permission("aur-browser", "network")
        self.assertTrue(perm)

if __name__ == '__main__':
    unittest.main()
