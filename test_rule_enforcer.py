
import unittest
import os
import shutil
from engine.dom_server.rule_enforcer import RuleEnforcer

class TestRuleEnforcer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_id = "test_project"
        path = f"projects/{cls.project_id}/rules"
        os.makedirs(path, exist_ok=True)

        with open(f"{path}/limits.md", "w") as f:
            f.write("Maximum single item price: Rs. 5000\n")
            f.write("Maximum discount allowed: 25%\n")

        with open(f"{path}/security.md", "w") as f:
            f.write("Some security rules here.\n")

        with open(f"{path}/skills.md", "w") as f:
            f.write("Skill: Add item\n")
            f.write("Skill: Remove item\n")
            f.write("Skill: Checkout\n")

        cls.enforcer = RuleEnforcer(cls.project_id)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(f"projects/{cls.project_id}")

    def test_price_limit_pass(self):
        res = self.enforcer.check("Add item for 100 rupees")
        self.assertTrue(res["allowed"])

    def test_price_limit_fail(self):
        res = self.enforcer.check("Add item for 6000 rupees")
        self.assertFalse(res["allowed"])
        self.assertIn("exceeds Rs.5,000 limit", res["reason"])

    def test_discount_limit_pass(self):
        res = self.enforcer.check("Give 10% discount")
        self.assertTrue(res["allowed"])

    def test_discount_limit_fail(self):
        res = self.enforcer.check("Give 50% discount")
        self.assertFalse(res["allowed"])
        self.assertIn("50% discount exceeds 25% maximum", res["reason"])

    def test_skills_pass(self):
        res = self.enforcer.check("Add item")
        self.assertTrue(res["allowed"])

    def test_skills_fail(self):
        res = self.enforcer.check("Hack the system")
        self.assertFalse(res["allowed"])
        self.assertIn("Action not found in skills.md", res["reason"])

if __name__ == "__main__":
    unittest.main()
