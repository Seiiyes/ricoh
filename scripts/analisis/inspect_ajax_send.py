"""
Search for jQuery.ajax or XMLHttpRequest in ajax.js.
"""
with open("/tmp/ajax.js", "r", encoding="utf-8") as f:
    content = f.read()

# Print lines containing $.ajax, jQuery.ajax, or XMLHttpRequest
for i, line in enumerate(content.split('\n'), 1):
    if any(x in line for x in ['ajax', 'xmlhttp', 'XMLHttpRequest', 'send', 'POST', 'GET']):
        print(f"{i}: {line.strip()}")
