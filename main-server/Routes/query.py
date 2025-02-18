from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from sentence_transformers import SentenceTransformer
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain
from langchain_ollama import ChatOllama
from datetime import datetime, timezone
from flask import request, jsonify
from dotenv import load_dotenv
from bson import ObjectId
import torch.nn.functional as F
import torch
import faiss
import pickle
import os
import re

import time


load_dotenv()
LLM_MODEL=os.getenv("LLM_MODEL")
V_DB_PATH = os.getenv("V_DB_PATH")
THRESHOLD = float(os.getenv("CHUNK_RELEVANCY_THRESHOLD"))

llm_model = ChatOllama(model=LLM_MODEL, temperature = 0)
transformer_model = SentenceTransformer("all-MiniLM-L6-v2")
# code_transformer_model = SentenceTransformer("microsoft/codebert-base")
# title_model = ChatOllama(model="", temperature = 0)

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

def compute_similarity_between_query_and_chat_history(question, messages):
    # Compute similarity between the new query and both the last question and last answer.
    previous_question = messages[-2]["message_content"]
    previous_answer = messages[-1]["message_content"]

    query_embedding = transformer_model.encode(question, convert_to_tensor=True)
    question_embedding = transformer_model.encode(previous_question, convert_to_tensor=True)
    answer_embedding = transformer_model.encode(previous_answer, convert_to_tensor=True)

    similarity_q = F.cosine_similarity(query_embedding, question_embedding, dim=0).item()
    similarity_a = F.cosine_similarity(query_embedding, answer_embedding, dim=0).item()
    print(f"Similarity between new query and last question: {similarity_q}")
    print(f"Similarity between new query and last answer: {similarity_a}")
    similarity = max(similarity_q, similarity_a)

    return similarity

def retrieve_from_chat_history(question, last_3_memory, llm_model):
    # Build a strict prompt that forces usage of ONLY the chat history.
    system_message = SystemMessagePromptTemplate.from_template(
        "You are a helpful AI assistant. You MUST ONLY use the provided chat history to answer questions. "
        "Do not use any external knowledge. If the answer cannot be determined solely from the chat history, "
        "respond exactly with: \"I cannot answer this question based solely on our chat history alone.\""
    )
    human_message = HumanMessagePromptTemplate.from_template(
        "Chat History:\n{history}\nHuman: {input}\n\nBased solely on the above chat history, answer the question. "
    )
    chat_prompt = ChatPromptTemplate.from_messages([system_message, human_message])
    conversation = ConversationChain(
        llm=llm_model,
        verbose=True,
        memory=last_3_memory,
        prompt=chat_prompt
    )
    response_text = conversation.predict(input=question)
    return response_text

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
        chat = course_db.Chats.update_one(
            {"_id": ObjectId(chat_id)},
            {"$push": {"messages": {"$each": [user_message, chatbot_message]}},
             "$set": {"last_message_time": datetime.now(timezone.utc).isoformat()}}
        )
        title = chat["title"]
    else:
        title_prompt = ChatPromptTemplate.from_template(
            "Create a concise title (up to 6 words) for this conversation based on the user query:\n\nUser Query: {question}. Make sure you only return the title itself wrapped in <title> and </title>. For example, if the generated title is 'Title', then the output will be ['Title']"
        )
        title_input = title_prompt.format(question=question)
        title_creation_start = time.time()
        title_response = llm_model.invoke(title_input)
        title_creation_finish = time.time()
        
        print(f"title_creation {title_creation_finish - title_creation_start}")

        matches = re.findall(r'<title>\s*(.*?)\s*</title>', title_response.content, re.IGNORECASE | re.DOTALL)
        print(title_response.content)
        print()
        if matches:
            # Get the last match (the most recent title)
            title = matches[-1].strip().replace('"', '').replace("'", '')
            print(f"title sonuc: {title}")  # Output: Constrained Execution Limits
        else:
            print("No match found")
        
        
        # title = title_response.content[title_response.content.rfind("[") + 1:-1].strip().replace('"', '').replace("'", '')
    
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
        "server_response": True,
    }), 200

def update_chat_memory(chat_doc):
    # Reconstruct the most recent exchange(s).
    last_3_memory = ConversationBufferWindowMemory(k=3)
    messages = chat_doc.get("messages", [])
    for i in range(0, len(messages) - 1, 2):
        if i + 1 < len(messages):
            last_3_memory.save_context(
                {"input": messages[i]["message_content"]},
                {"output": messages[i + 1]["message_content"]}
            )
    
    return last_3_memory, messages

def query(course_db):
    course = request.json.get('course')
    question = request.json.get('question')
    user_id = request.json.get('user_id')
    chat_id = request.json.get('chat_id')

    if not question or not course or not user_id:
        return jsonify({"error": "Missing query text, course, or user_id"}), 400
        
    context_chunks, sources = retrieve_from_vector_database(question,course)

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
                last_3_memory, messages = update_chat_memory(chat_doc) # Update the memory with the last three chat history

                memory_relevance_threshold = 0.3
                edit_keywords = [
                    "make it shorter",
                    "shorten it", 
                    "in fewer words",
                    "make it brief",
                    "trim it down",
                    "cut it down",
                    "can you shorten that",
                    "give me a brief version",
                    "in short",
                    "keep it concise",
                    "bullet point",
                    "summarize",
                    "give me a summary",
                    "sum it up",
                    "make it simpler",
                    "simplify",
                    "quick summary",
                    "more",
                    "detailed"
                ]
                if not any(keyword in question.lower() for keyword in edit_keywords): # If the question is not about editing the previous answer
                    similarity = compute_similarity_between_query_and_chat_history(question, messages)

                    if similarity < memory_relevance_threshold:
                        return jsonify({
                            "response": "I cannot answer this question based solely on our chat history alone.",
                            "sources": []
                            })
                
                # Get from chat history
                response_text = retrieve_from_chat_history(question, last_3_memory, llm_model)

            else:
                response_text = "I'm sorry, I don't have enough information to answer that."

    else:
        # If context is found, use it to generate a response
        context = "\n\n".join(context_chunks)
        content_prompt_obj = ChatPromptTemplate.from_template(CONTENT_PROMPT)
        prompt = content_prompt_obj.format(context=context, question=question)
        
        response_creation_start = time.time()
        response_text = llm_model.invoke(prompt).content
        response_creation_finish = time.time()
        
        print(f"response_creation {response_creation_finish - response_creation_start}")

    # Post-process the response if needed.
    if "</think>" in response_text:
        response_text = response_text[response_text.index("</think>") + len("</think>") + 1:]

    return save_chat(course_db, course, user_id, question, response_text, sources, chat_id)
    # Saves chat to the database and returns the response