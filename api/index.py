import os
import json
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler
from groq import Groq
from supabase import create_client


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)
            data = json.loads(body)

            messages = data.get("messages", [])
            session_id = data.get("session_id")

            groq_key = os.environ.get("GROQ_API_KEY", "")
            supabase_url = os.environ.get("SUPABASE_URL", "")
            supabase_key = os.environ.get("SUPABASE_KEY", "")

            groq_key = groq_key.replace("\ufeff", "").strip().strip('"').strip("'")
            supabase_url = supabase_url.replace("\ufeff", "").strip().strip('"').strip("'")
            supabase_key = supabase_key.replace("\ufeff", "").strip().strip('"').strip("'")

            if not groq_key:
                raise Exception("GROQ_API_KEY is not configured.")

            if not supabase_url:
                raise Exception("SUPABASE_URL is not configured.")

            if not supabase_key:
                raise Exception("SUPABASE_KEY is not configured.")

            parsed_url = urlparse(supabase_url)

            if parsed_url.scheme != "https" or not parsed_url.netloc:
                raise Exception(
                    "SUPABASE_URL_FORMAT_ERROR: " + repr(supabase_url)
                )

            try:
                supabase = create_client(
                    supabase_url,
                    supabase_key
                )
            except Exception as e:
                raise Exception(
                    "SUPABASE_CREATE_CLIENT_ERROR: " + str(e)
                )

            groq = Groq(api_key=groq_key)

            chat_id = None

            if session_id:
                existing_chat = (
                    supabase
                    .table("chats")
                    .select("id")
                    .eq("session_id", session_id)
                    .limit(1)
                    .execute()
                )

                if existing_chat.data:
                    chat_id = existing_chat.data[0]["id"]

            if not chat_id:
                title = "New CloudTalk Chat"

                if messages:
                    first_message = messages[0].get(
                        "content",
                        ""
                    )
                    title = first_message[:50]

                new_chat = (
                    supabase
                    .table("chats")
                    .insert({
                        "session_id": session_id or "anonymous",
                        "title": title
                    })
                    .execute()
                )

                if not new_chat.data:
                    raise Exception(
                        "Could not create chat in Supabase."
                    )

                chat_id = new_chat.data[0]["id"]

            if messages:
                last_message = messages[-1]

                if last_message.get("role") == "user":
                    supabase.table("messages").insert({
                        "chat_id": chat_id,
                        "role": "user",
                        "content": last_message.get(
                            "content",
                            ""
                        )
                    }).execute()

            response = groq.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are CloudTalk, a helpful and "
                            "friendly AI assistant. Give clear, "
                            "accurate and concise answers."
                        )
                    },
                    *messages
                ],
                temperature=0.7,
                max_tokens=500
            )

            ai_response = response.choices[0].message.content

            supabase.table("messages").insert({
                "chat_id": chat_id,
                "role": "assistant",
                "content": ai_response
            }).execute()

            result = {
                "response": ai_response,
                "chat_id": chat_id
            }

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/json"
            )
            self.end_headers()

            self.wfile.write(
                json.dumps(result).encode("utf-8")
            )

        except Exception as e:

            self.send_response(500)
            self.send_header(
                "Content-Type",
                "application/json"
            )
            self.end_headers()

            self.wfile.write(
                json.dumps({
                    "error": str(e)
                }).encode("utf-8")
            )