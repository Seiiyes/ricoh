import paramiko
from bs4 import BeautifulSoup

HOST = "192.168.91.131"
USERNAME = "odootic"
PASSWORD = "Zuly152325*"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(HOST, username=USERNAME, password=PASSWORD, timeout=15)
    
    # Read the full file content from the container
    stdin, stdout, stderr = client.exec_command("docker exec ricoh-backend cat /tmp/debug_no_checkboxes_00257.html")
    html_content = stdout.read().decode('utf-8', errors='replace')
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Print the visible text from the body
    print("--- BODY TEXT ---")
    if soup.body:
        print(soup.body.get_text().strip())
    else:
        print("No body found")
        
    print("\n--- ERROR/ALERT SCRIPTS OR MESSAGES ---")
    scripts = soup.find_all('script')
    for s in scripts:
        if 'alert' in s.text or 'error' in s.text.lower() or 'fail' in s.text.lower():
            print(s.text.strip())
            
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
