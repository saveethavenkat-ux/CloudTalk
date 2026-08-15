import os
from http.server import BaseHTTPRequestHandler
import json
from groq import Groq


class handler(BaseHTTPRequestHandler):

    def do_POST(self):

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            data = json.loads(body)

            messages = data.get("messages", [])

            api_key = os.environ.get("GROQ_API_KEY")

            if not api_key:
                raise Exception("GROQ_API_KEY is not configured.")

            client = Groq(api_key=api_key)

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are CloudTalk, a helpful and friendly "
                            "AI assistant. Give clear, accurate and "
                            "concise answers."
                        )
                    },
                    *messages
                ],
                temperature=0.7,
                max_tokens=500
            )

            result = {
                "response": response.choices[0].message.content
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(
                json.dumps(result).encode("utf-8")
            )

        except Exception as e:

            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(
                json.dumps({
                    "error": str(e)
                }).encode("utf-8")
            )