import os
import json
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler
from groq import Groq
from supabase import create_client


class handler(BaseHTTPRequestHandler):

    def get_supabase(self):
        supabase_url = os.environ.get("SUPABASE_URL", "").strip()
        supabase_key = os.environ.get("SUPABASE_KEY", "").strip()

        if not supabase_url:
            raise Exception("SUPABASE_URL is not configured.")

        if not supabase_key:
            raise Exception("SUPABASE_KEY is not configured.")

        if not supabase_url.startswith("https://"):
            raise Exception("SUPABASE_URL must start with https://")

        return create_client(
            supabase_url,
            supabase_key
        )

    def send_json(self, status, data):
        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json"
        )
        self.end_headers()

        self.wfile.write(
            json.dumps(data).encode("utf-8")
        )

    def do_GET(self):
        try:
            supabase = self.get_supabase()

            query = parse_qs(
                urlparse(self.path).query
            )

            chat_id = query.get("chat_id", [None])[0]
            history = query.get("history", [""])[0]

            if chat_id:
                chat = (
                    supabase
                    .table("chats")
                    .select("*")
                    .eq("id", chat_id)
                    .limit(1)
                    .execute()
                )

                if not chat.data:
                    raise Exception("Chat not found.")

                messages = (
                    supabase
                    .table("messages")
                    .select("role, content, created_at")
                    .eq("chat_id", chat_id)
                    .order("created_at")
                    .execute()
                )

                self.send_json(
                    200,
                    {
                        "chat": chat.data[0],
                        "messages": messages.data or []
                    }
                )
                return

            if history == "true":
                chats = (
                    supabase
                    .table("chats")
                    .select("*")
                    .order("created_at", desc=True)
                    .execute()
                )

                self.send_json(
                    200,
                    {
                        "chats": chats.data or []
                    }
                )
                return

            self.send_json(
                200,
                {
                    "message": "CloudTalk API is running."
                }
            )

        except Exception as e:
            self.send_json(
                500,
                {
                    "error": str(e)
                }
            )

    def do_POST(self):
        try:
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)
            data = json.loads(body)

            messages = data.get("messages", [])
            session_id = data.get("session_id")

            groq_key = os.environ.get(
                "GROQ_API_KEY",
                ""
            ).strip()

            if not groq_key:
                raise Exception(
                    "GROQ_API_KEY is not configured."
                )

            supabase = self.get_supabase()

            groq = Groq(
                api_key=groq_key
            )

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
                        "session_id": (
                            session_id or "anonymous"
                        ),
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
                    (
                        supabase
                        .table("messages")
                        .insert({
                            "chat_id": chat_id,
                            "role": "user",
                            "content": last_message.get(
                                "content",
                                ""
                            )
                        })
                        .execute()
                    )

            response = groq.chat.completions.create(
                model="openai/gpt-oss-20b",
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

            ai_response = (
                response.choices[0].message.content
            )

            (
                supabase
                .table("messages")
                .insert({
                    "chat_id": chat_id,
                    "role": "assistant",
                    "content": ai_response
                })
                .execute()
            )

            self.send_json(
                200,
                {
                    "response": ai_response,
                    "chat_id": chat_id
                }
            )

        except Exception as e:
            self.send_json(
                500,
                {
                    "error": str(e)
                }
            )