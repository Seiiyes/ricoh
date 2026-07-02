import paramiko
from bs4 import BeautifulSoup

HOST = "192.168.91.131"
USERNAME = "odootic"
PASSWORD = "Zuly152325*"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(HOST, username=USERNAME, password=PASSWORD, timeout=15)
    
    # Read the file
    stdin, stdout, stderr = client.exec_command("docker exec ricoh-backend cat password_step2_error.html")
    html_content = stdout.read().decode('utf-8', errors='replace')
    
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        print("--- BODY TEXT ---")
        if soup.body:
            print(soup.body.get_text().strip())
        else:
            print("No body found")
            
        print("\n--- INPUTS ---")
        inputs = soup.find_all('input')
        for idx, inp in enumerate(inputs):
            print(f"{idx}: {inp}")
    else:
        print("File password_step2_error.html is empty or not found")
            
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
