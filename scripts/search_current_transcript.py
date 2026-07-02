import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

log_path = r"C:\Users\juan.lizarazo\.gemini\antigravity-ide\brain\0a299d2b-7a3b-41e4-8d53-58420d2718fc\.system_generated\logs\transcript.jsonl"

if os.path.exists(log_path):
    with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
        count = 0
        for line in f:
            try:
                data = json.loads(line)
                if data.get("type") == "USER_INPUT":
                    if 120 <= count <= 143:
                        print(f"\n==========================================")
                        print(f"Index: {count}")
                        print(data.get("content")[:1500])
                    count += 1
            except Exception as e:
                pass
