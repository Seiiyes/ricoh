import json
import os

brain_dir = r"C:\Users\juan.lizarazo\.gemini\antigravity-ide\brain"
current_conv = "0a299d2b-7a3b-41e4-8d53-58420d2718fc"
output_file = r"c:\Users\juan.lizarazo\Desktop\ricoh\scripts\current_conv_steps.txt"

log_path = os.path.join(brain_dir, current_conv, ".system_generated", "logs", "transcript.jsonl")
if os.path.exists(log_path):
    with open(log_path, 'r', encoding='utf-8') as f:
        with open(output_file, 'w', encoding='utf-8') as out:
            for idx, line in enumerate(f):
                try:
                    data = json.loads(line)
                    if data.get("type") == "USER_INPUT":
                        out.write(f"Step {data.get('step_index') or idx} ({data.get('created_at')}):\n")
                        out.write(data.get("content", ""))
                        out.write("\n" + "="*80 + "\n")
                except Exception as e:
                    pass
    print("Done writing current conv steps to", output_file)
else:
    print("Log not found at", log_path)
