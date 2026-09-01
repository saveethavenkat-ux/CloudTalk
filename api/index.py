import os
import json
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler

from groq import Groq
from supabase import create_client


class handler(BaseHTTPRequestHandler):

    # ============================================================
    # GET /api
    # GET /api?chat_id=...
    # GET /api?session_id=...
    # ============================================================

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)

            chat_id = params.get("chat_id", [None])[0]
            session_id = params.get("session_id", [None])[0]

            supabase_url = os.environ.get(
                "SUPABASE_URL", ""
            ).strip()

            supabase_key = os.environ.get(
                "SUPABASE_KEY", ""
            ).strip()

            if not supabase_url:
                raise Exception(
                    "SUPABASE_URL is not configured."
                )

            if not supabase_key:
                raise Exception(
                    "SUPABASE_KEY is not configured."
                )

            if not supabase_url.startswith("https://"):
                raise Exception(
                    "SUPABASE_URL must start with https://"
                )

            supabase = create_client(
                supabase_url,
                supabase_key
            )

            # ----------------------------------------------------
            # If chat_id is provided, return messages
            # ----------------------------------------------------

            if chat_id:

                messages = (
                    supabase
                    .table("messages")
                    .select(
                        "id, role, content, created_at"
                    )
                    .eq("chat_id", chat_id)
                    .order("created_at")
                    .execute()
                )

                result = {
                    "chat_id": chat_id,
                    "messages": messages.data
                }

            # ----------------------------------------------------
            # If session_id is provided, find its chat first
            # ----------------------------------------------------

            elif session_id:

                chats = (
                    supabase
                    .table("chats")
                    .select("id")
                    .eq("session_id", session_id)
                    .limit(1)
                    .execute()
                )

                if not chats.data:

                    result = {
                        "chat_id": None,
                        "messages": []
                    }

                else:

                    chat_id = chats.data[0]["id"]

                    messages = (
                        supabase
                        .table("messages")
                        .select(
                            "id, role, content, created_at"
                        )
                        .eq("chat_id", chat_id)
                        .order("created_at")
                        .execute()
                    )

                    result = {
                        "chat_id": chat_id,
                        "messages": messages.data
                    }

            # ----------------------------------------------------
            # Simple API health check
            # ----------------------------------------------------

            else:

                result = {
                    "message": "CloudTalk API is running."
                }

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.end_headers()

            self.wfile.write(
                json.dumps(
                    result,
                    default=str
                ).encode("utf-8")
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


    # ============================================================
    # POST /api
    # ============================================================

    def do_POST(self):
        try:

            # ----------------------------------------------------
            # Read request body
            # ----------------------------------------------------

            content_length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            body = self.rfile.read(
                content_length
            )

            data = json.loads(body)

            messages = data.get(
                "messages",
                []
            )

            session_id = data.get(
                "session_id"
            )

            # ----------------------------------------------------
            # Environment variables
            # ----------------------------------------------------

            groq_key = os.environ.get(
                "GROQ_API_KEY",
                ""
            ).strip()

            supabase_url = os.environ.get(
                "SUPABASE_URL",
                ""
            ).strip()

            supabase_key = os.environ.get(
                "SUPABASE_KEY",
                ""
            ).strip()

            # ----------------------------------------------------
            # Validate environment variables
            # ----------------------------------------------------

            if not groq_key:
                raise Exception(
                    "GROQ_API_KEY is not configured."
                )

            if not supabase_url:
                raise Exception(
                    "SUPABASE_URL is not configured."
                )

            if not supabase_key:
                raise Exception(
                    "SUPABASE_KEY is not configured."
                )

            if not supabase_url.startswith(
                "https://"
            ):
                raise Exception(
                    "SUPABASE_URL must start with https://"
                )

            # ----------------------------------------------------
            # Create Supabase client
            # ----------------------------------------------------

            supabase = create_client(
                supabase_url,
                supabase_key
            )

            # ----------------------------------------------------
            # Create Groq client
            # ----------------------------------------------------

            groq = Groq(
                api_key=groq_key
            )

            # ----------------------------------------------------
            # Find existing chat
            # ----------------------------------------------------

            chat_id = None

            if session_id:

                existing_chat = (
                    supabase
                    .table("chats")
                    .select("id")
                    .eq(
                        "session_id",
                        session_id
                    )
                    .limit(1)
                    .execute()
                )

                if existing_chat.data:

                    chat_id = (
                        existing_chat
                        .data[0]["id"]
                    )

            # ----------------------------------------------------
            # Create new chat if necessary
            # ----------------------------------------------------

            if not chat_id:

                title = "New CloudTalk Chat"

                if messages:

                    first_message = (
                        messages[0]
                        .get(
                            "content",
                            ""
                        )
                    )

                    title = first_message[:50]

                new_chat = (
                    supabase
                    .table("chats")
                    .insert({
                        "session_id": (
                            session_id
                            or "anonymous"
                        ),
                        "title": title
                    })
                    .execute()
                )

                if not new_chat.data:

                    raise Exception(
                        "Could not create chat in Supabase."
                    )

                chat_id = (
                    new_chat
                    .data[0]["id"]
                )

            # ----------------------------------------------------
            # Save user message
            # ----------------------------------------------------

            if messages:

                last_message = messages[-1]

                if (
                    last_message.get("role")
                    == "user"
                ):

                    (
                        supabase
                        .table("messages")
                        .insert({
                            "chat_id": chat_id,
                            "role": "user",
                            "content": (
                                last_message
                                .get(
                                    "content",
                                    ""
                                )
                            )
                        })
                        .execute()
                    )

            # ----------------------------------------------------
            # Call Groq AI
            # ----------------------------------------------------

            response = (
                groq
                .chat
                .completions
                .create(
                    model="openai/gpt-oss-20b",

                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are CloudTalk, "
                                "a helpful and friendly "
                                "AI assistant. Give clear, "
                                "accurate and concise answers."
                            )
                        },
                        *messages
                    ],

                    temperature=0.7,

                    max_tokens=500
                )
            )

            # ----------------------------------------------------
            # Get AI response
            # ----------------------------------------------------

            ai_response = (
                response
                .choices[0]
                .message
                .content
            )

            # ----------------------------------------------------
            # Save AI response
            # ----------------------------------------------------

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

            # ----------------------------------------------------
            # Send successful response
            # ----------------------------------------------------

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
                json.dumps(
                    result,
                    default=str
                ).encode("utf-8")
            )

        # --------------------------------------------------------
        # Error handling
        # --------------------------------------------------------

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