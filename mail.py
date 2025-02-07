import requests
import time
import json
import html
from pystyle import Write, Colors
from colorama import Fore, init

init(autoreset=True)

Write.Print(r"""
█████ █   █ ████ █   █  █    ███   ██  █████  ███  █    ████
█    █ █  █ █    █   █  █    █  ███ █  █   █   █   █    ██
█████   █   ██   █   █  █    █      █  █████   █   █      ██
█      █    ███   ███   ████ █      █  █   █  ███  ███  ████
            Made by the husband of Pyeul lihm
[1] Generate Mail
[2] Exit 
""", Colors.blue_to_white, interval=0.0001)

BASE_URL = "http://api.guerrillamail.com/ajax.php"

# Predefined list of domains
TEMP_DOMAINS = [
    "sharklasers.com",
    "guerrillamail.info",
    "guerrillamail.com",
    "guerrillamail.net",
    "guerrillamail.biz",
    "guerrillamail.org",
    "guerrillamail.de",
    "guerrillamailblock.com",
    "pokemail.net",
    "spam4.me",
    "grr.la"
]

# Function to get email address from a selected domain
def get_email_address(session, domain):
    params = {'f': 'get_email_address', 'domain': domain}
    response = session.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    # Ensure the correct domain is selected
    email_addr = data.get("email_addr", "")
    if email_addr:
        if "@" + domain not in email_addr:
            # Fix the domain if the returned email has a different domain
            email_addr = email_addr.split('@')[0] + '@' + domain
    return email_addr, data.get("sid_token", "")

def check_email(session, sid_token, seq):
    params = {'f': 'check_email', 'sid_token': sid_token, 'seq': seq}
    response = session.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data.get("list", []), data.get("seq", seq)

def fetch_email(session, mail_id, sid_token):
    params = {'f': 'fetch_email', 'email_id': mail_id, 'sid_token': sid_token}
    response = session.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    return html.unescape(data.get('mail_body', 'No content'))

def generate_mail():
    print(Fore.YELLOW + "[!] Generating email, please wait...")
    time.sleep(1.5)
    session = requests.Session()

    # Print available domains for selection
    print(Fore.YELLOW + "[!] Available domains:")
    for index, domain in enumerate(TEMP_DOMAINS, 1):
        print(Fore.GREEN + f"{index}. {domain}")

    domain_choice = Write.Input(Fore.YELLOW + "\nChoose a domain number: ", Colors.blue_to_white)
    try:
        domain_choice = int(domain_choice.strip())
        if domain_choice < 1 or domain_choice > len(TEMP_DOMAINS):
            print(Fore.RED + "Invalid domain choice!")
            return
    except ValueError:
        print(Fore.RED + "Invalid input! Please choose a valid number.")
        return

    selected_domain = TEMP_DOMAINS[domain_choice - 1]
    email_address, sid_token = get_email_address(session, selected_domain)

    if email_address:
        print(Fore.GREEN + f"[+] Email generated: {email_address}")
    else:
        print(Fore.RED + "[!] Failed to generate email. Please try again.")
        return

    print(Fore.YELLOW + "[!] Waiting for messages... (This may take a few minutes)")
    seq = 0
    start_time = time.time()

    while True:
        messages, seq = check_email(session, sid_token, seq)
        if messages:
            for msg in messages:
                mail_id = msg.get('mail_id')
                mail_from = msg.get('mail_from', 'Unknown')
                mail_subject = msg.get('mail_subject', 'No Subject')
                print(Fore.CYAN + f"\n[+] New message from {mail_from}:")
                print(Fore.WHITE + f"Subject: {mail_subject}")
                mail_content = fetch_email(session, mail_id, sid_token)
                print(Fore.WHITE + mail_content)
                time.sleep(2)
        else:
            print(Fore.YELLOW + "[!] No new messages yet. Checking again in 15 seconds...")
            time.sleep(15)  # Recheck every 15 seconds

        # Check if 50 seconds have passed and show the exit prompt
        elapsed_time = time.time() - start_time
        if elapsed_time >= 50:
            if exit_prompt():
                break
            else:
                start_time = time.time()  # Reset the timer after prompt

def exit_prompt():
    opc = Write.Input('\nWould you like to exit? (y/n): ', Colors.blue_to_white)
    if opc.strip().lower() == 'y':
        print(Fore.GREEN + "Exiting...")
        return True
    elif opc.strip().lower() == 'n':
        print(Fore.YELLOW + "Continuing to check for messages...")
        return False
    else:
        print(Fore.RED + "Invalid input! Please type 'y' for Yes or 'n' for No.")
        return exit_prompt()

while True:
    opc = Write.Input('\nroot@mail>> ', Colors.blue_to_white)
    if opc.strip() == '1':
        generate_mail()  # Generate mail and wait for new messages
    elif opc.strip().lower() == '2' or opc.strip().lower() == 'exit':
        print(Fore.GREEN + "Exiting...")
        break
    else:
        print(Fore.RED + "Invalid option!")
