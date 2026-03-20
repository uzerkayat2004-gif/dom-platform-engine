"""
Hardware Bridge
Interface to the LLM4Binary model for x86/ARM assembly generation.
Translates plain English instructions into hardware language.
"""

from pathlib import Path
from typing import Optional

class HardwareBridge:
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.loaded = False
        self.model_path = "LLM4Binary/llm4decompile-6.7b-v2"
    
    def load(self):
        """Load the hardware language model."""
        if self.loaded:
            return
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            print(f"Loading hardware model: {self.model_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto"
            )
            self.model.eval()
            self.loaded = True
            print("Hardware model loaded successfully")
        except Exception as e:
            print(f"Hardware model load failed: {e}")
            self.loaded = False
    
    def generate_assembly(self, instruction: str, max_tokens: int = 150) -> str:
        """Generate x86 assembly for a plain English instruction."""
        if not self.loaded:
            self.load()
        
        if not self.loaded:
            return self._fallback_assembly(instruction)
        
        import torch
        prompt = f"# Translate to x86 assembly\n# Instruction: {instruction}\n# Assembly:\n"
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.1,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        assembly = generated.split("# Assembly:")[-1].strip()
        return assembly
    
    def _fallback_assembly(self, instruction: str) -> str:
        """Fallback when hardware model is not available."""
        return f"; x86 assembly for: {instruction}\nmov eax, 0x1\nmov ebx, [operand]\nadd eax, ebx\nmov [result], eax\nret"

hardware_bridge = HardwareBridge()
