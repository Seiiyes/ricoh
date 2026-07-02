import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

brain_dir = r"C:\Users\juan.lizarazo\.gemini\antigravity-ide\brain"

if not os.path.exists(brain_dir):
    print("Brain directory not found at:", brain_dir)
    sys.exit(1)

print("Searching recursively across all conversations:")
matches = 0
for root, dirs, files in os.walk(brain_dir):
    for file in files:
        if file == "transcript.jsonl":
            log_path = os.path.join(root, file)
            conv_id = os.path.basename(os.path.dirname(os.path.dirname(root)))
            try:
                with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                    for line in f:
                        data = json.loads(line)
                        if data.get("type") == "USER_INPUT":
                            content = data.get("content", "")
                            if "delete" in content.lower() or "elimin" in content.lower() or "storedjob.cgi" in content.lower():
                                # Let's print if it contains headers or payloads
                                if "headers" in content.lower() or "payload" in content.lower() or "request" in content.lower() or "cookie" in content.lower():
                                    print(f"\n==========================================")
                                    print(f"Conversation: {conv_id}")
                                    print(f"Date: {data.get('created_at')}")
                                    print(f"==========================================")
                                    print(content)
                                    matches += 1
            except Exception as e:
                pass

print(f"\nDone. Found {matches} matching historical inputs.")
