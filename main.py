from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

api_key = os.getenv("OPEN_API_KEY")
client = OpenAI(api_key=api_key)

class PromptRequest(BaseModel):
    input_str: str
    thread_id: Optional[str] = None

# Dictionary to store chat history
chat_history = {}

@app.get("/")
def read_root():
    return {"Hello": "World"}

def answer(input_str, thread_id=None):
    if thread_id and thread_id in chat_history:
        messages = chat_history[thread_id]
    else:
        messages = [
            {"role": "system", "content": """# CONTEXT #
Anda akan berperan sebagai asisten dosen untuk mahasiswa S2 di bidang IT. Topik yang akan ditanyakan oleh mahasiswa dan dijawab oleh Anda adalah Software Engineering: Scrum.

# OBJECTIVE #
Menjawab pertanyaan yang diajukan oleh mahasiswa yang sedang belajar tentang Agile: Scrum.

# STYLE #
Gaya respons Anda adalah seperti seorang asisten dosen pada mata kuliah Software Engineering: Scrum.

# TONE #
Nada yang digunakan adalah asisten yang ramah dan sopan, namun tetap profesional, serta tidak terlalu kaku atau seperti robot.

# AUDIENCE #
Audience adalah mahasiswa S2 yang sedang bertanya tentang Software Engineering, terutama untuk topik Scrum.

# LIMITATIONS #
Jawaban yang diberikan oleh asisten dosen hanya akan terkait dengan topik Software Engineering: Scrum. Jika pertanyaan yang diajukan tidak berhubungan dengan Software Engineering atau Scrum, maka asisten dosen akan menjawab dengan permintaan untuk mengajukan ulang pertanyaan sesuai dengan konteks yang ada.

Contoh:
"Maaf, pertanyaan Anda tidak terkait dengan topik Software Engineering: Scrum. Silakan ajukan pertanyaan yang sesuai dengan konteks mata kuliah ini."
            """}
        ]

    messages.append({"role": "user", "content": f"Tolong jawab pertanyaan dengan bahasa Indonesia dengan baik.\nPertanyaan: {input_str}\nJawaban:"})

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=1000
    )

    response_content = completion.choices[0].message["content"]

    # Update the chat history
    if thread_id:
        chat_history[thread_id] = messages + [{"role": "assistant", "content": response_content}]
    else:
        # Generate a new thread_id
        thread_id = str(len(chat_history) + 1)
        chat_history[thread_id] = messages + [{"role": "assistant", "content": response_content}]

    return response_content, thread_id


@app.post("/answer/")
async def get_answer(request: PromptRequest):
    try:
        answer_text, thread_id = answer(request.input_str, request.thread_id)
        return {"Answer": answer_text, "ThreadID": thread_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
