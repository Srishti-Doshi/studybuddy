import json
from channels.generic.websocket import AsyncWebsocketConsumer
from groq import Groq
from django.conf import settings

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data["message"]

        # ✅ Initialize AFTER settings are loaded
        client = Groq(api_key=settings.GROQ_API_KEY)

        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are a helpful study assistant."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.6,
            max_tokens=300
        )

        ai_reply = completion.choices[0].message.content

        await self.send(text_data=json.dumps({
            "reply": ai_reply
        }))
