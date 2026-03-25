
import time
import re
from engine.dom_server.rule_enforcer import RuleEnforcer
from engine.rules.generator import RuleGenerator
import os
import shutil

def setup_mock_project(project_id):
    path = f"projects/{project_id}/rules"
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
        for i in range(100):
            f.write(f"Skill: Skill_{i}\n")

def benchmark():
    project_id = "bench_project"
    setup_mock_project(project_id)

    enforcer = RuleEnforcer(project_id)

    # Instruction with many price matches to trigger the loop many times
    # and also some discount and skills
    instruction = "Add item for 100 rupees, another for 200 rupees, and one more for 300 rupees. Give 10% discount."

    iterations = 5000
    start_time = time.time()
    for _ in range(iterations):
        enforcer.check(instruction)
    end_time = time.time()

    total_time = end_time - start_time
    print(f"Total time for {iterations} iterations: {total_time:.4f} seconds")
    print(f"Average time per call: {total_time/iterations*1000:.4f} ms")

    # Cleanup
    shutil.rmtree(f"projects/{project_id}")

if __name__ == "__main__":
    benchmark()
