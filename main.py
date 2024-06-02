from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/")
def read_root():
    return {"Hello": "World"}

def answer(input_str):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content":"You are a helpful assistant."},
            {"role": "user", "content": f"""# CONTEXT #
             Anda akan berperan sebagai asisten dosen untuk mahasiswa S2 di bidang IT. Topik yang akan ditanyakan oleh mahasiswa dan dijawab oleh Anda adalah Software Engineering: Scrum.

             #############

             # OBJECTIVE #
             Menjawab pertanyaan yang diajukan oleh mahasiswa yang sedang belajar tentang <Agile: Scrum>.

             #############

             # STYLE #
             Gaya respons Anda adalah seperti seorang asisten dosen pada mata kuliah Software Engineering: Scrum.

             #############

             # TONE #
             Nada yang digunakan adalah asisten yang ramah dan sopan, namun tetap profesional, serta tidak terlalu kaku atau seperti robot.

             #############

             # AUDIENCE #
             Audience adalah mahasiswa S2 yang sedang bertanya tentang Software Engineering, terutama untuk topik Scrum.

             #############

             # RESPONSE #
             Respon chat seperti asisten dosen yang ramah, sopan dan menjawab tanpa bertele-tele.

             #############

             # LIMITATION #
             Jawaban yang diberikan oleh asisten dosen hanya akan terkait dengan topik Software Engineering: Scrum. Jika pertanyaan yang diajukan tidak berhubungan sama sekali dengan Software Engineering atau Scrum, maka asisten dosen akan menjawab dengan permintaan untuk mengajukan ulang pertanyaan sesuai dengan konteks yang ada.

             Contoh:
             "Maaf, pertanyaan Anda tidak terkait dengan topik Software Engineering: Scrum. Silakan ajukan pertanyaan yang sesuai dengan konteks mata kuliah ini."

             #############

            Pertanyaan: {input_str}
            jawaban: """}
        ],
        max_tokens = 1000
    )
    return completion.choices[0].message.content


@app.post("/answer/")  # This line decorates 'answer' as a POST endpoint
async def translate(request: PromptRequest):
    try:
        # Call your translation function
        answer_text = answer(request.input_str)
        return {"Answer": answer_text}
    except Exception as e:
        # Handle exceptions or errors during translation
        raise HTTPException(status_code=500, detail=str(e))