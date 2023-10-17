import unittest
from UPISAS.test import create_strategy


class TestStrategy(unittest.TestCase):
    """
    Test cases for the Strategy class, monitor and execute methods
    Run by `python -m UPISAS.test.test_strategy` on the parent folder.
    """
    def setUp(self):
        self.proc = None
        self.exemplar = None

    def tearDown(self):
        self.exemplar.stop()
        if self.proc is not None:
            self.proc.kill()
            self.proc.wait()

    def test_monitor_successfully(self):
        self.proc, self.exemplar, strategy = create_strategy("UPISAS/test/http-test-server/app.js",
                                                             "http://localhost:3000", "gabrielmoreno/swim", "swim")
        successful = strategy.monitor()
        self.assertTrue(successful)
        self.assertNotEqual(strategy.knowledge.monitored_data, dict())

    def test_monitor_endpoint_not_present(self):
        self.proc, self.exemplar, strategy = create_strategy("UPISAS/test/http-test-server/app-no-m-e-endpoints.js",
                                                             "http://localhost:3000","gabrielmoreno/swim", "swim")
        successful = strategy.monitor()
        self.assertFalse(successful)
        self.assertDictEqual(strategy.knowledge.monitored_data, dict())

    def test_execute_successfully(self):
        self.proc, self.exemplar, strategy = create_strategy("UPISAS/test/http-test-server/app.js",
                                                             "http://localhost:3000", "gabrielmoreno/swim", "swim")
        successful = strategy.execute({"o1": 2, "o2": 5})
        self.assertTrue(successful)

    def test_execute_endpoint_not_present(self):
        self.proc, self.exemplar, strategy = create_strategy("UPISAS/test/http-test-server/app-no-m-e-endpoints.js",
                                                              "http://localhost:3000","gabrielmoreno/swim", "swim")
        successful = strategy.execute({"o1": 2, "o2": 5})
        self.assertFalse(successful)

    def test_analyze_successfully(self):
        self.proc, self.exemplar, strategy = create_strategy("UPISAS/test/http-test-server/app.js",
                                                             "http://localhost:3000", "gabrielmoreno/swim", "swim")
        strategy.monitor()
        successful = strategy.analyze()
        self.assertTrue(successful)
        self.assertNotEqual(strategy.knowledge.analysis_data, dict())

    def test_plan_successfully(self):
        self.proc, self.exemplar, strategy = create_strategy("UPISAS/test/http-test-server/app.js",
                                                             "http://localhost:3000", "gabrielmoreno/swim", "swim")
        strategy.monitor()
        strategy.analyze()
        successful = strategy.plan()
        self.assertTrue(successful)
        self.assertNotEqual(strategy.knowledge.plan_data, dict())


if __name__ == '__main__':
    unittest.main()
