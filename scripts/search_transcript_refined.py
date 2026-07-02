import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

brain_dir = r"C:\Users\juan.lizarazo\.gemini\antigravity-ide\brain"

for root, dirs, files in os.walk(brain_dir):
    for file in files:
        if file == "transcript.jsonl":
            log_path = os.path.join(root, file)
            try:
                with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                    for line in f:
                        data = json.loads(line)
                        if data.get("type") == "USER_INPUT":
                            content = data.get("content", "")
                            content_lower = content.lower()
                            if "storedjob.cgi" in content_lower or "/jobs" in content_lower or "elimi" in content_lower:
                                print("\n-------------------------------------------")
                                print(f"File: {log_path}")
                                print(content[:1000]) # Print first 1000 chars of matching prompt
            except Exception as e:
                pass
print("\nSearch complete.")
