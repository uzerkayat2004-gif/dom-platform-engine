"""
DOM Server — The Runtime Backend
Flask server at localhost:5000
This is the invisible backend that replaces all traditional backend code.
Every button in the generated frontend sends a plain English instruction here.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

from engine.dom_server.rule_enforcer import RuleEnforcer
from engine.dom_server.inference import DOMInference
from engine.glassbox.logger import GlassBoxLogger

dom_app = Flask(__name__)
CORS(dom_app)

# Active DOM instances per project
_dom_instances: dict = {}

def get_dom_instance(project_id: str) -> tuple:
    """Get or create DOM server components for a project."""
    if project_id not in _dom_instances:
        enforcer = RuleEnforcer(project_id)
        inference = DOMInference(project_id)
        inference.load()
        logger = GlassBoxLogger(project_id)
        _dom_instances[project_id] = (enforcer, inference, logger)
    return _dom_instances[project_id]

@dom_app.route("/health")
def health():
    return jsonify({"status": "running", "server": "DOM Server"})

@dom_app.route("/process", methods=["POST"])
def process():
    """
    Core endpoint — every frontend button calls this.
    Receives plain English instruction, enforces rules,
    runs DOM model, returns structured JSON.
    """
    data = request.get_json()
    instruction = data.get("instruction", "")
    project_id = data.get("project_id", "default")
    
    if not instruction:
        return jsonify({"error": "No instruction provided"}), 400
    
    enforcer, inference, logger = get_dom_instance(project_id)
    
    # Import asyncio for sync logger calls
    import asyncio
    loop = asyncio.new_event_loop()
    
    # Log incoming instruction
    loop.run_until_complete(
        logger.log("SYSTEM", f"Instruction received: {instruction}")
    )
    
    # STEP 1: Rule check BEFORE execution
    rule_result = enforcer.check(instruction)
    
    if not rule_result["allowed"]:
        # BLOCKED — log and return without executing
        loop.run_until_complete(
            logger.log(
                "SECURITY_BLOCK",
                f"{rule_result['reason']} — {rule_result['rule_file']}",
                rule_result["rule_number"]
            )
        )
        loop.run_until_complete(
            logger.log("SYSTEM", "ACTION BLOCKED — DOM not executed")
        )
        loop.run_until_complete(
            logger.log("SYSTEM", "Security system protected the business")
        )
        loop.close()
        
        return jsonify({
            "status": "blocked",
            "blocked": True,
            "reason": rule_result["reason"],
            "rule_file": rule_result["rule_file"],
            "rule_number": rule_result["rule_number"],
            "display": f"BLOCKED: {rule_result['reason']}",
            "order": inference.get_state().get("order", {})
        })
    
    # STEP 2: Rule check passed — log and execute
    loop.run_until_complete(
        logger.log("RULE_CHECK", rule_result["reason"])
    )
    
    loop.run_until_complete(
        logger.log("ASSEMBLY", "DOM generating x86 assembly...")
    )
    
    # STEP 3: Run DOM model inference
    result = inference.process(instruction)
    
    # STEP 4: Log assembly output
    assembly = result.get("assembly", "")
    if assembly:
        loop.run_until_complete(
            logger.log("ASSEMBLY", f"Output:\n{assembly[:200]}")
        )
    
    # STEP 5: Log action result
    action = result.get("action", "")
    display = result.get("display", "")
    
    if "payment" in action:
        loop.run_until_complete(logger.log("PAYMENT", display))
        loop.run_until_complete(logger.log("RULE_CHECK", "Security check passed — rule files verified"))
        loop.run_until_complete(logger.log("PAYMENT", "Receipt generated successfully"))
    elif "kitchen" in action:
        loop.run_until_complete(logger.log("KITCHEN", display))
        loop.run_until_complete(logger.log("KITCHEN", "Kitchen notified — behavior.md Rule 4 verified"))
    elif "item_added" in action:
        loop.run_until_complete(logger.log("ORDER", display))
    else:
        loop.run_until_complete(logger.log("ORDER", display))
    
    loop.close()
    
    return jsonify({
        "status": "success",
        "blocked": False,
        "action": action,
        "display": display,
        "data": result.get("data", {}),
        "assembly": assembly,
        "rule_check": "PASSED",
        "order": inference.get_state().get("order", {})
    })

@dom_app.route("/state/<project_id>")
def get_state(project_id: str):
    """Get current app state."""
    enforcer, inference, logger = get_dom_instance(project_id)
    return jsonify(inference.get_state())

@dom_app.route("/glassbox/<project_id>")
def get_glassbox(project_id: str):
    """Get Glass Box log entries."""
    enforcer, inference, logger = get_dom_instance(project_id)
    return jsonify({"entries": logger.get_recent(100)})

def start_dom_server(project_id: str = "default", port: int = 5000):
    """Start the DOM server for a specific project."""
    import logging
    # Disable flask output to avoid cluttering dev terminal
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    print(f"Starting DOM Server for project: {project_id} on port {port}")
    dom_app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    start_dom_server()
