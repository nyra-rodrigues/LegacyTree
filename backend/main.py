from fastapi import FastAPI, Request
from pydantic import BaseModel
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
import torch
from typing import List

app = FastAPI()

# Load BlenderBot model and tokenizer at startup
MODEL_NAME = "facebook/blenderbot-400M-distill"
tokenizer = BlenderbotTokenizer.from_pretrained(MODEL_NAME)
model = BlenderbotForConditionalGeneration.from_pretrained(MODEL_NAME)

def build_conversation_input(history: List[str]):
    # BlenderBot expects the conversation as a single string, with each turn separated by </s>
    return " </s> ".join(history)

class ConversationRequest(BaseModel):
    history: List[str]

@app.post("/api/conversation")
def converse(req: ConversationRequest):
    # Build input from history
    input_text = build_conversation_input(req.history)
    inputs = tokenizer([input_text], return_tensors="pt")
    reply_ids = model.generate(**inputs, max_length=128)
    output = tokenizer.batch_decode(reply_ids, skip_special_tokens=True)[0]
    return {"response": output} 