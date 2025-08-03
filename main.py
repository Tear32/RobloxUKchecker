import os
import sys

try:
    import requests
    from colorama import Fore, Style, init
except ImportError:
    print("[!] Missing dependencies. Installing now...")
    os.system(f"{sys.executable} -m pip install requests colorama")
    print("[!] Please restart the script after installing dependencies.")
    os.system("pause" if os.name == "nt" else "read -n 1 -s -r -p 'Press any key to continue...'")
    sys.exit(1)

init(autoreset=True)

def log_info(msg): print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {msg}")
def log_success(msg): print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {msg}")
def log_error(msg): print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")
def log_warn(msg): print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} {msg}")
def log_section(title): print(f"\n{Fore.MAGENTA}[{title.upper()}]{Style.RESET_ALL} ─{'─'*40}")

def format_user_entry(index, username, display_name, user_id):
    username_fmt = f"{username:<14}"
    display_fmt = f"{display_name:<14}"
    user_link = f"roblox://user?id={user_id}"
    return f"[{str(index).zfill(3)}] {Fore.WHITE}{username_fmt} → {display_fmt} {Fore.LIGHTBLACK_EX}| {user_link}{Style.RESET_ALL}"

def display_section(title, users):
    log_section(title)
    if not users:
        msg = "[!] No outbound follows detected." if title == "following" else f"[!] No {title} found."
        color = Fore.RED if title == "following" else Fore.YELLOW
        print(f"{color}{msg}{Style.RESET_ALL}")
        return

    for idx, user in enumerate(users, 1):
        uname = user.get("name") or "Unknown"
        dname = user.get("displayName") or "Unknown"
        uid = user.get("id") or "?"
        print(format_user_entry(idx, uname, dname, uid))

def fetch_user_id(username):
    lookup_url = "https://users.roblox.com/v1/usernames/users"
    payload = {
        "usernames": [username],
        "excludeBannedUsers": False
    }
    try:
        res = requests.post(lookup_url, json=payload, timeout=10)
        res.raise_for_status()
        data = res.json().get("data")
        if not data:
            log_error(f"User '{username}' not found.")
            return None
        user_id = data[0]["id"]
        log_success(f"userId for '{username}': {user_id}")
        return user_id
    except requests.RequestException as e:
        log_error(f"Network error fetching userId: {e}")
        return None
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        return None

def input_limit(category):
    while True:
        try:
            val = input(f"{Fore.YELLOW}Set limit for {category} (1-100, default 50): {Style.RESET_ALL}").strip()
            if val == "":
                return 50
            limit = int(val)
            if 1 <= limit <= 100:
                return limit
            else:
                log_warn("Input must be a number between 1 and 100.")
        except ValueError:
            log_warn("Invalid input. Please enter a number.")

def query_friends_api(user_id):
    limits = {cat: input_limit(cat) for cat in ["friends", "followers", "following"]}

    endpoints = {
        "friends": f"https://friends.roblox.com/v1/users/{user_id}/friends?limit={limits['friends']}",
        "followers": f"https://friends.roblox.com/v1/users/{user_id}/followers?limit={limits['followers']}",
        "following": f"https://friends.roblox.com/v1/users/{user_id}/followings?limit={limits['following']}",
        "friendCount": f"https://friends.roblox.com/v1/users/{user_id}/friends/count"
    }

    for category, url in endpoints.items():
        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            json_data = res.json()

            if category == "friendCount":
                count = json_data.get("count", 0)
                log_section("friend count")
                print(f"{Fore.GREEN}[✔] Total friends: {count}{Style.RESET_ALL}")
            else:
                users = json_data.get("data", [])
                display_section(category, users)

        except requests.RequestException as e:
            log_error(f"Request failed for '{category}': {e}")
        except Exception as e:
            log_error(f"Unexpected error in '{category}': {e}")

def main():
    log_info("Roblox Friends/Follower Info Tool v1.0")
    log_info("Type 'exit' or 'quit' to exit.")

    try:
        while True:
            username = input(f"{Fore.RED}roblox@{Fore.WHITE}username --> {Style.RESET_ALL}").strip()
            if not username:
                log_warn("No username entered.")
                continue
            if username.lower() in {"exit", "quit"}:
                log_info("Exiting...")
                break

            user_id = fetch_user_id(username)
            if user_id:
                query_friends_api(user_id)

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[CTRL+C] Exiting on user request.{Style.RESET_ALL}")
        sys.exit(0)

if __name__ == "__main__":
    main()
