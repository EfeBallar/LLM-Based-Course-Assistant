from langchain.prompts.chat import ChatPromptTemplate
from sentence_transformers import SentenceTransformer
from langchain_ollama import ChatOllama
from datetime import datetime, timezone
from flask import request, jsonify
from dotenv import load_dotenv
from bson import ObjectId
import torch.nn.functional as F
import faiss
import pickle
import os
import re

import time

load_dotenv()
LLM_MODEL=os.getenv("LLM_MODEL")
V_DB_PATH = os.getenv("V_DB_PATH")
THRESHOLD = float(os.getenv("CHUNK_RELEVANCY_THRESHOLD"))
TITLE_GENERATION_MODEL = os.getenv("TITLE_GENERATION_MODEL")
llm_model = ChatOllama(model=LLM_MODEL, temperature = 0)
transformer_model = SentenceTransformer("all-MiniLM-L6-v2")
title_model = ChatOllama(model=TITLE_GENERATION_MODEL, temperature = 0)

CONTENT_PROMPT = """
    You are provided with the following context extracted from a document.
    Please answer the question using only the information provided in the context.
    Do not include any additional knowledge or assumptions beyond what is given.

    Context:
    {context}

    Question:
    {question}

    Answer:
"""

def retrieve_from_vector_database(question,course):
    question_embedding = transformer_model.encode(question, convert_to_tensor=True)
    question_embedding = question_embedding.cpu().numpy().astype("float32")
    faiss.normalize_L2(question_embedding.reshape(1, -1))
    
    # Load FAISS index and metadata
    index = faiss.read_index(V_DB_PATH +"\\" + course+"_faiss_index.idx")
    with open(V_DB_PATH +"\\" + course+"_metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
    
    # Perform a search: retrieve top k most similar chunks
    k = 5
    distances, indices = index.search(question_embedding.reshape(1, -1), k)

    context_chunks = []
    sources = []  # This will store dictionaries with file and page info.
    for dist, idx in zip(distances[0], indices[0]):
        if dist >= THRESHOLD:
            meta = metadata[idx]
            context_chunks.append(meta["chunk"])
            
            # Append source information: file name and page number.
            sources.append({
                "file": meta.get("file", "Unknown"),
                "page": meta.get("page", "Unknown")
            })
    
    return context_chunks, sources

def answer_from_chat_history(question, messages, llm_model):
    # Build a strict prompt that forces usage of ONLY the chat history.
    chat_history = ""
    for message in messages:
        chat_history += f"{message['sender']}: {message['message_content']}\n"

    print(chat_history)

    # Construct the prompt with very strict instructions.
    prompt_text = (
        "Below is the full conversation between a user and a context-based AI assistant:\n\n"
        f"{chat_history}\n\n"
        "Based ONLY on the conversation above, answer the following question using ONLY the CHAT HISTORY provided."
        "If the answer cannot be determined solely from the above conversation, respond with 'I cannot answer this question based solely on our chat history alone.'\n\n"
        f"Question: {question}\n"
        "Answer:"
    )
    
    response = llm_model.invoke(prompt_text).content
    print(response)
    return response

def save_chat(course_db, course, user_id, question, response_text, sources, chat_id=None):
    # Save the chat to the database.
    user_message = {
        "sender": "user",
        "message_content": question,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    chatbot_message = {
        "sender": "chatbot",
        "message_content": response_text,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sources": sources
    }
    chat_id = chat_id if chat_id else None
    title = None
    if chat_id:
        course_db.Chats.update_one(
            {"_id": ObjectId(chat_id)},
            {"$push": {"messages": {"$each": [user_message, chatbot_message]}},
             "$set": {"last_message_time": datetime.now(timezone.utc).isoformat()}}
        )
        
        title = course_db.Chats.find_one({"_id": ObjectId(chat_id)})["title"]
        
    else:
        
        title_prompt = ChatPromptTemplate.from_template(
            "Create a concise title (up to 6 words) for this conversation based on the user query:\n\nUser Query: {question}. "
        )
        title_input = title_prompt.format(question=question)
        title = title_model.invoke(title_input).content.strip('"')
                
        chat_entry = {
            "course": course,
            "user_id": user_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "last_message_time": datetime.now(timezone.utc).isoformat(),
            "messages": [user_message, chatbot_message],
            "title": title
        }

        result = course_db.Chats.insert_one(chat_entry)
        chat_id = str(result.inserted_id)
    
    return jsonify({
        "course": course,
        "chat_id": chat_id,
        "last_message_time": datetime.now(timezone.utc).isoformat(),
        "model_response": response_text,
        "sources": sources,
        "title": title,
        "server_response": True
    }), 200

def update_chat_memory(chat_doc):
    # Reconstruct the most recent exchange(s).
    messages = chat_doc.get("messages", [])
    last_three_messages = messages[-6:]
    return last_three_messages

def query(course_db):
    course = request.json.get('course')
    question = request.json.get('question')
    user_id = request.json.get('user_id')
    chat_id = request.json.get('chat_id')

    if not question or not course or not user_id:
        return jsonify({"error": "Missing query text, course, or user_id"}), 400
        
    context_chunks, sources = retrieve_from_vector_database(question,course)
    response_text = ""
    if not context_chunks: # If no context is found
        if not chat_id:
            return jsonify({
                "response": "I'm sorry, I don't have enough information to answer that.",
                "sources": []
            })

        else:  # If there is a chat_id, use chat history only
            chat_id_obj = ObjectId(chat_id)
            chat_doc = course_db.Chats.find_one({"_id": chat_id_obj})
            if chat_doc:
                last_3_messages = update_chat_memory(chat_doc) # Update the memory with the last three chat history
                # Get from chat history
                response_text = answer_from_chat_history(question, last_3_messages, llm_model)

            else:
                response_text = "Chat not found."

    else:
        # If context is found, use it to generate a response
        context = "\n\n".join(context_chunks)
        content_prompt_obj = ChatPromptTemplate.from_template(CONTENT_PROMPT)
        prompt = content_prompt_obj.format(context=context, question=question)
        try:
            response_text = llm_model.invoke(prompt).content
        except:
            print("You might need to open Ollama Server.")
        
    # Post-process the response if needed.
    if "</think>" in response_text:
        response_text = response_text[response_text.index("</think>") + len("</think>") + 1:]

    return save_chat(course_db, course, user_id, question, response_text, sources, chat_id)
    # Saves chat to the database and returns the response