from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

api_key = os.environ.get("OPEN_API_KEY")
client = OpenAI(api_key=api_key)

class TranslationRequest(BaseModel):
    input_str: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

def answer(input_str):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"""Tolong jawab pertanyaan dengan bahasa Indonesia dengan baik
            Pertanyaan: {input_str}
            jawaban: """}
        ],
        max_tokens = 1000
    )
    return completion.choices[0].message.content


@app.post("/answer/")  # This line decorates 'answer' as a POST endpoint
async def translate(request: TranslationRequest):
    try:
        # Call your translation function
        answer_text = answer(request.input_str)
        return {"Answer": answer_text}
    except Exception as e:
        # Handle exceptions or errors during translation
        raise HTTPException(status_code=500, detail=str(e))