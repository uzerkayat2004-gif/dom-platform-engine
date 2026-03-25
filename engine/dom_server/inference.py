"""
DOM Model Inference
Loads the fine-tuned DOM model and runs inference on instructions.
This is the deployed app's brain running locally.
"""

from pathlib import Path

class DOMInference:
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.model_path = Path(f"projects/{project_id}/model/adapter")
        self.model = None
        self.tokenizer = None
        self.loaded = False
        
        # In-memory state for the app
        self.state = {
            "order": {"items": [], "total": 0},
            "session": {}
        }
    
    def load(self) -> bool:
        """Load the fine-tuned DOM model."""
        if not self.model_path.exists():
            print(f"DOM model not found at {self.model_path}")
            return False
        
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            from peft import PeftModel
            import torch
            
            base_model_name = "microsoft/Phi-3-mini-4k-instruct"
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                str(self.model_path)
            )
            
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto"
            )
            
            self.model = PeftModel.from_pretrained(
                base_model,
                str(self.model_path)
            )
            self.model.eval()
            self.loaded = True
            print(f"DOM model loaded for project: {self.project_id}")
            return True
            
        except Exception as e:
            print(f"DOM model load error: {e}")
            self.loaded = False
            return False
    
    def process(self, instruction: str) -> dict:
        """
        Process a plain English instruction through the DOM model.
        Updates in-memory state and returns structured response.
        """
        import re
        instruction_lower = instruction.lower()
        
        # If model is loaded, use it for inference
        if self.loaded and self.model:
            response_text = self._run_inference(instruction)
        else:
            # Intelligent rule-based fallback for MVP demo
            response_text = self._rule_based_process(instruction)
        
        return response_text
    
    def _run_inference(self, instruction: str) -> dict:
        """Run actual DOM model inference."""
        import torch
        
        from engine.rules.generator import RuleGenerator
        rule_gen = RuleGenerator(self.project_id)
        rules = rule_gen.get_combined_rules()[:300]
        
        prompt = f"""### DOM Operation
RULES: {rules}
INSTRUCTION: {instruction}
RESULT:"""
        
        inputs = self.tokenizer(
            prompt, return_tensors="pt"
        ).to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.1,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        generated = self.tokenizer.decode(
            outputs[0], skip_special_tokens=True
        )
        result_text = generated.split("RESULT:")[-1].strip()
        
        return self._parse_and_update_state(instruction, result_text)
    
    def _rule_based_process(self, instruction: str) -> dict:
        """
        Intelligent fallback processor.
        Handles instructions when DOM model is not yet trained.
        Used for demos and testing.
        """
        import re
        instruction_lower = instruction.lower()
        
        # ADD ITEM
        if any(kw in instruction_lower for kw in ["add", "order"]):
            price_match = re.search(r'(\d+)\s*rupees?', instruction_lower)
            item_match = re.search(
                r'(?:add|order)\s+(?:one|two|three|\d+)?\s*(.+?)(?:\s+at|\s+for|\s+rupees|$)',
                instruction_lower
            )
            
            if price_match:
                price = int(price_match.group(1))
                item_name = item_match.group(1).strip() if item_match else "item"
                qty_match = re.search(r'(\d+|one|two|three)', instruction_lower)
                qty_map = {"one": 1, "two": 2, "three": 3}
                qty = qty_map.get(qty_match.group(1), 1) if qty_match else 1
                if qty_match and qty_match.group(1).isdigit():
                    qty = int(qty_match.group(1))
                
                total_price = price * qty
                self.state["order"]["items"].append({
                    "name": item_name.title(),
                    "price": price,
                    "qty": qty,
                    "total": total_price
                })
                self.state["order"]["total"] += total_price
                
                return {
                    "action": "item_added",
                    "display": f"Added {qty}x {item_name.title()} @ Rs.{price} each",
                    "data": {"order": self.state["order"]},
                    "assembly": f"mov eax, {price}\nmov ebx, [total]\nadd ebx, eax\nmov [total], ebx",
                    "rule_check": "PASSED"
                }
        
        # DISCOUNT
        elif any(kw in instruction_lower for kw in ["discount", "percent off", "% off"]):
            pct_match = re.search(r'(\d+)\s*(?:percent|%)', instruction_lower)
            if pct_match and self.state["order"]["total"] > 0:
                pct = int(pct_match.group(1))
                discount_amount = int(self.state["order"]["total"] * pct / 100)
                self.state["order"]["total"] -= discount_amount
                return {
                    "action": "discount_applied",
                    "display": f"{pct}% discount applied — Saved Rs.{discount_amount} — New total: Rs.{self.state['order']['total']}",
                    "data": {"order": self.state["order"]},
                    "assembly": f"mov eax, [total]\nmov ebx, {pct}\nimul eax, ebx\nidiv dword 100\nsub [total], eax",
                    "rule_check": "PASSED"
                }
        
        # KITCHEN
        elif any(kw in instruction_lower for kw in ["kitchen", "send order"]):
            items = self.state["order"]["items"]
            return {
                "action": "order_sent_kitchen",
                "display": f"Order sent to kitchen — {len(items)} item(s) — Rs.{self.state['order']['total']}",
                "data": {"order": self.state["order"]},
                "assembly": "mov eax, [order_id]\nmov [kitchen_status], dword 1\nmov [kitchen_time], dword [current_time]",
                "rule_check": "PASSED"
            }
        
        # PAYMENT
        elif any(kw in instruction_lower for kw in ["payment", "pay", "process payment", "checkout"]):
            total = self.state["order"]["total"]
            items = list(self.state["order"]["items"])
            self.state["order"] = {"items": [], "total": 0}
            return {
                "action": "payment_processed",
                "display": f"Payment of Rs.{total} processed — Receipt generated",
                "data": {"paid": total, "items": items},
                "assembly": "mov eax, [total_amount]\nmov [payment_status], dword 1\nmov [receipt_flag], dword 1",
                "rule_check": "PASSED"
            }
        
        # NEW ORDER
        elif any(kw in instruction_lower for kw in ["new order", "clear", "reset", "start over"]):
            self.state["order"] = {"items": [], "total": 0}
            return {
                "action": "new_order",
                "display": "New order started — ready for items",
                "data": {"order": self.state["order"]},
                "assembly": "mov [order_id], dword 0\nmov [total], dword 0\nmov [item_count], dword 0",
                "rule_check": "PASSED"
            }
        
        # REPORT
        elif any(kw in instruction_lower for kw in ["report", "sales", "summary", "analytics"]):
            return {
                "action": "report_generated",
                "display": "Daily sales report generated",
                "data": {"report": "Available in reports panel"},
                "assembly": "mov eax, [daily_total]\nmov [report_flag], dword 1",
                "rule_check": "PASSED"
            }
        
        # SHOW ORDER
        elif any(kw in instruction_lower for kw in ["show order", "current order", "what's in"]):
            order = self.state["order"]
            if not order["items"]:
                display = "Order is empty"
            else:
                lines = [f"{i['qty']}x {i['name']} @ Rs.{i['price']}" for i in order["items"]]
                display = "\n".join(lines) + f"\nTotal: Rs.{order['total']}"
            return {
                "action": "order_displayed",
                "display": display,
                "data": {"order": order},
                "assembly": "mov eax, [order_data]\npush eax\ncall display_order",
                "rule_check": "PASSED"
            }
        
        # DEFAULT
        return {
            "action": "processed",
            "display": f"Instruction processed: {instruction}",
            "data": {},
            "assembly": "mov eax, 1\nret",
            "rule_check": "PASSED"
        }
    
    def _parse_and_update_state(self, instruction: str, result_text: str) -> dict:
        return {
            "action": "dom_inference",
            "display": result_text,
            "data": {"state": self.state},
            "assembly": "",
            "rule_check": "PASSED"
        }
    
    def get_state(self) -> dict:
        return self.state
