import requests
import sys
import time
import threading


API_KEY = "AIzaSyAyix3tmpanFejTLcyPkxUH1B1d3OA6850"
API_MODEL = "gemini-1.5-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{API_MODEL}:generateContent?key={API_KEY}"


chat_history = []


def print_message(message, role="user", is_error=False):
    """Print formatted messages"""
    if is_error:
        print(f"\033[91mError: {message}\033[0m")  # Red for errors
    elif role == "user":
        print(f"\033[94mYou: {message}\033[0m")    # Blue for user
    else:
        print(f"\033[92mAI: {message}\033[0m")     # Green for AI
    print()


def show_loading():
    """Console loading animation"""
    chars = "/-\\|"
    for _ in range(5):
        for char in chars:
            sys.stdout.write(f"\rLoading {char}")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\r" + " " * 20 + "\r")
    sys.stdout.flush()


def call_gemini_api(message):
    """Send user message → get AI response"""
    try:
        request_body = {
            "contents": [
                {"parts": [{"text": message}]}
            ]
        }

        response = requests.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            json=request_body,
        )

        # If API rate-limit → 429
        if response.status_code == 429:
            return "You are sending too many requests. Please wait 10–20 seconds.", True

        if response.status_code != 200:
            return f"API request failed with status {response.status_code}", True

        data = response.json()

        # Extract text
        if "candidates" in data and len(data["candidates"]) > 0:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return text, False
        else:
            return "No response from AI.", True

    except Exception as e:
        return f"Error: {str(e)}", True


def main():
    print("Welcome to the Gemini Console Chatbot!")
    print("Type 'exit' to quit.")
    print("----------------------------------------\n")

    if not sys.stdin.isatty():
        print("Please run this script in a normal terminal.")
        return

    while True:
        try:
            user_input = input("You: ").strip()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if user_input == "":
            continue

        print_message(user_input, "user")
        chat_history.append({"role": "user", "content": user_input})

        # Start loading animation
        loading_thread = threading.Thread(target=show_loading)
        loading_thread.start()

        response, is_error = call_gemini_api(user_input)

        # Stop loading animation
        loading_thread.join()

        print_message(response, "assistant", is_error)
        chat_history.append({"role": "assistant", "content": response})

        # Prevent rate-limit
        time.sleep(1)


if __name__ == "__main__":
    main()
