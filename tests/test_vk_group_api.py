import requests


def send_message(text: str, chat_id: int) -> None:
    "Send task to TaskManager"

    url = "http://localhost:8083/send_message"
    input = {
        "text": text,
        "meta": {
            "chat_id": chat_id
        }
    }
    output = requests.post(url, json=input).json()
    print(output)


if __name__ == "__main__":
    send_message("ку привет", 1)
