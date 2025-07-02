import os
from dotenv import load_dotenv         
load_dotenv()

from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph.message import add_messages
from typing import Sequence
from typing_extensions import Annotated,TypedDict

GROQ_API_KEY = os.getenv("GROQ_API_KEY")    # raises below if missing
if not GROQ_API_KEY:
    raise RuntimeError("❌ GROQ_API_KEY env var not set")

model = ChatGroq(
    temperature=0,
    model_name="llama-3.1-8b-instant",     
    groq_api_key=GROQ_API_KEY,
)

prompt_template = ChatPromptTemplate.from_messages([
    # 1) Core behavior & formatting
    (
        "system",
        """You are the customer-facing AI for DeepX Hub.
When you reply, output ONLY the answer text—no “User:” or “Bot:” labels, no extra commentary.

Rules:
1. If the user asks something you HAVE INFO for, answer directly based on that info.
2. If the user's question is about DeepX Hub but not covered by your info, reply:
   I'm not sure about that—please reach out via contact@deepxhub.com or visit https://deepxhub.com/contact.
3. If the question is completely unrelated to DeepX Hub, reply:
   I'm sorry, I can't help with that."""
    ),

    # 2) The company “knowledge base”
    (
        "system",
        """DeepX Hub — Services & Examples

Services
--------
Custom Software Development
• Full-Stack Web Applications  
• Front-End Only Development  
• Back-End & API Development  
• Responsive Dashboards & Admin Panels  
• Website & App Deployment  

AI & Machine Learning Solutions
• AI Chatbots & Conversational Agents  
• GPT Integration & CRM AI Assistants  
• LangChain + RAG-Based Systems  
• Voice Assistants (Voice-to-Text / Text-to-Speech)  
• NLP: Summarization, Sentiment, Entity Recognition  
• Computer Vision Systems (Detection, OCR, Image AI)  
• Audio AI: Transcription & Emotion Detection  
• Custom Fine-Tuned AI Models  

AI Infrastructure & Automation
• Data Wrangling & Cleaning Pipelines  
• Async Task Systems (Celery, Redis)  
• AI SaaS Dashboards & Analytics  
• Full AI Pipelines & Model Hosting  
• MLOps: Versioning, Monitoring & Deployment  

Emerging Tech & Consulting
• AI Strategy & System Design  
• API Integration (Stripe, Twilio, GPT APIs, etc.)  
• Mobile-Friendly & Cross-Platform Builds  
• Cloud Architecture (AWS, GCP, Azure)  
• Ongoing Maintenance & Feature Support  
• On-demand solutions  

Real-world examples
-------------------
• AI Chatbot App  
• Healthcare Assistant App  
• Voice-to-Text Transcriber  
• E-commerce Recommendation Engine"""
    ),

    # 3) Conversation history
    MessagesPlaceholder(variable_name="messages"),
])

trim = trim_messages(
    max_tokens=1000,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human"
)

class State(TypedDict):
  messages: Annotated[Sequence[BaseMessage],add_messages]
  language:str

workflow = StateGraph(state_schema=State)

def call_model(state: State):
  trimmed = trim.invoke(state["messages"])
  prompt = prompt_template.invoke({
      "messages":trimmed
  })
  res = model.invoke(prompt)
  return {"messages":[res]}

workflow.add_edge(START,"model")
workflow.add_node("model",call_model)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

def get_response(prompt:str) ->str:
  config = {"configurable":{"thread_id":"1"}}
  messages = [HumanMessage(prompt)]
  output = app.invoke({"messages": messages},config,)
  return output["messages"][-1].content
