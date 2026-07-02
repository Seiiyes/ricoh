import json
import os

brain_dir = r"C:\Users\juan.lizarazo\.gemini\antigravity-ide\brain"
output_file = r"c:\Users\juan.lizarazo\Desktop\ricoh\scripts\results.txt"

with open(output_file, 'w', encoding='utf-8') as out:
    out.write("All directories in brain_dir:\n")
    for d in os.listdir(brain_dir):
        out.write(d + "\n")
    
    out.write("\n--- Searching for first prompt or deletion details in all transcript.jsonl files ---\n")
    for folder in os.listdir(brain_dir):
        folder_path = os.path.join(brain_dir, folder)
        if os.path.isdir(folder_path):
            log_path = os.path.join(folder_path, ".system_generated", "logs", "transcript.jsonl")
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                    for idx, line in enumerate(f):
                        try:
                            data = json.loads(line)
                            if data.get("type") == "USER_INPUT":
                                content = data.get("content", "")
                                content_lower = content.lower()
                                # Look for headers, preview, cgi, storedjob, cookies, etc.
                                if any(x in content_lower for x in ["wimtoken", "cgi", "elim", "delete", "header", "preview"]):
                                    out.write(f"\n============================================\n")
                                    out.write(f"Conv: {folder} | Step: {data.get('step_index') or idx}\n")
                                    out.write(f"Created at: {data.get('created_at')}\n")
                                    out.write(f"Content:\n{content}\n")
                        except Exception as e:
                            pass

print("Done writing to", output_file)
