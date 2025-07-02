from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from chat import get_response
import os
from dotenv import load_dotenv         
load_dotenv()


class Message(BaseModel):
    input :str


app=FastAPI()

allowed = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
def func(msg: Message):
    return {"response":get_response(msg.input)}

@app.get("/")
def root():
    return {"response":"Chatbot is Live"}