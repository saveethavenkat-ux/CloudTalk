import requests

VERCEL_API_URL = "https://cloud-talk-avinvduhk-savee1.vercel.app/api"


def get_ai_response(messages, session_id=None):
    try:
        payload = {
            "messages": messages,
            "session_id": session_id
        }

        response = requests.post(
            VERCEL_API_URL,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            return (
                f"Cloud API returned {response.status_code}: "
                f"{response.text}"
            )

        data = response.json()

        if "error" in data:
            return f"Cloud API error: {data['error']}"

        return data.get(
            "response",
            "Sorry, I couldn't generate a response."
        )

    except requests.exceptions.RequestException as e:
        return f"Cloud API connection error: {e}"

    except Exception as e:
        return f"Something went wrong: {e}"