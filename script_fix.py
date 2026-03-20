from pathlib import Path
p = Path("d:/DOMPlatform/engine/training/fine_tuner.py")
content = p.read_text(encoding="utf-8")
eos = chr(60) + "|endoftext|" + chr(62)
content = content.replace("EOS_PLACEHOLDER", eos)
p.write_text(content, encoding="utf-8")
print("Successfully replaced EOS_PLACEHOLDER with actual EOS token.")
