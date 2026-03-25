"""
DOM Model Fine-Tuner
QLoRA fine-tuning of Phi-3 Mini on domain-specific training data.
This creates the small, fast, domain-specific DOM model.
"""

import json
import asyncio
from pathlib import Path
from typing import Callable, Optional


EOS_TAG = "<|endoftext|>"


class FineTuner:

    BASE_MODEL = "microsoft/Phi-3-mini-4k-instruct"

    def __init__(self, project_id: str, broadcast_fn: Optional[Callable] = None):
        self.project_id = project_id
        self.broadcast = broadcast_fn or self._noop
        self.output_dir = Path(f"projects/{project_id}/model")
        self.data_path = Path(f"projects/{project_id}/training/dataset.jsonl")

    @staticmethod
    async def _noop(x):
        pass

    def _read_training_data(self):
        examples = []
        with open(self.data_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    examples.append(json.loads(line.strip()))
        return examples

    async def run(self):
        """Run the full fine-tuning pipeline."""

        await self._broadcast_msg("Loading base model...")
        await asyncio.sleep(0.1)

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
            from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, TaskType
            from trl import SFTTrainer, SFTConfig
            from datasets import Dataset

            # Load training data
            examples = await asyncio.to_thread(self._read_training_data)

            await self._broadcast_msg(f"Training data loaded: {len(examples)} examples")

            # Format training data
            from engine.rules.generator import RuleGenerator
            rule_gen = RuleGenerator(self.project_id)
            rules = rule_gen.get_combined_rules()

            formatted = []
            for ex in examples:
                text = (
                    "### DOM Model -- Rule-Constrained Operation\n\n"
                    f"RULES:\n{rules[:500]}\n\n"
                    f"INSTRUCTION: {ex['instruction']}\n\n"
                    f"RULE CHECK: {ex['rule_check']}\n\n"
                    f"ASSEMBLY:\n{ex['assembly']}\n\n"
                    f"RESULT: {ex['result']}\n"
                    + EOS_TAG
                )
                formatted.append({"text": text})

            dataset = Dataset.from_list(formatted)

            # Load model with 4-bit quantization
            await self._broadcast_msg("Loading base model with 4-bit quantization...")

            use_cuda = torch.cuda.is_available()

            if use_cuda:
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.bfloat16
                )
                tokenizer = AutoTokenizer.from_pretrained(self.BASE_MODEL, cache_dir="D:/RestaurantPOS/cache")
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                model = AutoModelForCausalLM.from_pretrained(
                    self.BASE_MODEL,
                    quantization_config=bnb_config,
                    device_map="auto",
                    cache_dir="D:/RestaurantPOS/cache"
                )
                model = prepare_model_for_kbit_training(model)
            else:
                tokenizer = AutoTokenizer.from_pretrained(self.BASE_MODEL, cache_dir="D:/RestaurantPOS/cache")
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                model = AutoModelForCausalLM.from_pretrained(
                    self.BASE_MODEL,
                    torch_dtype=torch.float32,
                    cache_dir="D:/RestaurantPOS/cache"
                )

            # Apply LoRA
            lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=16,
                lora_alpha=32,
                target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
                lora_dropout=0.05,
                bias="none"
            )
            model = get_peft_model(model, lora_config)

            await self._broadcast_msg("QLoRA adapters applied -- starting training...")

            # Train
            sft_config = SFTConfig(
                output_dir=str(self.output_dir),
                num_train_epochs=3,
                per_device_train_batch_size=2,
                gradient_accumulation_steps=4,
                learning_rate=2e-4,
                bf16=use_cuda,
                fp16=False,
                logging_steps=5,
                save_steps=50,
                warmup_steps=10,
                lr_scheduler_type="cosine",
                optim="paged_adamw_8bit" if use_cuda else "adamw_torch",
                report_to="none",
                dataloader_pin_memory=False,
            )

            trainer = SFTTrainer(
                model=model,
                train_dataset=dataset,
                args=sft_config,
                processing_class=tokenizer,
            )
            trainer.args.max_seq_length = 512

            trainer.train()

            # Save
            trainer.model.save_pretrained(str(self.output_dir / "adapter"))
            tokenizer.save_pretrained(str(self.output_dir / "adapter"))

            await self._broadcast_msg("DOM model training complete!")
            await self.broadcast({
                "type": "training_complete",
                "project_id": self.project_id,
                "model_path": str(self.output_dir / "adapter")
            })

        except Exception as e:
            await self._broadcast_msg(f"Training error: {str(e)}")
            await self.broadcast({
                "type": "training_error",
                "project_id": self.project_id,
                "error": str(e)
            })

    async def _broadcast_msg(self, message: str):
        await self.broadcast({
            "type": "training_progress",
            "message": message,
            "project_id": self.project_id
        })
