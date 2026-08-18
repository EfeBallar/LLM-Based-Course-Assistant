# LLM-Based Course Assistant for Sabancı University

This repository contains the source code for the **ENS 491-492 Graduation Project: An LLM-based Course Assistant for Sabancı University**, developed to provide students with a reliable, automated question-answering system based directly on instructor-provided course materials.

For a detailed description of the methodology and results, please refer to the [📄 Final Report](ENS492_Final_Report.pdf)

## 📖 Project Overview
The aim of this project is to develop a Retrieval-Augmented Generation (RAG) system that answers students' questions based on documents uploaded by their instructors. By utilizing a quantized open-source Large Language Model hosted on a university GPU server, the assistant offloads repetitive queries from human Teaching Assistants and ensures answers are grounded in verified academic materials without relying on general training data.

## ✨ Key Features
* **RAG-Based Question Answering:** Retrieves the most relevant document chunks using FAISS and generates answers grounded strictly in instructor-provided context.
* **Role-Based Dashboards:** 
  * **Students:** Can log in, select enrolled courses, and submit queries via a React-based chat widget.
  * **Instructors:** Have a dedicated interface to upload (PDF, DOCX) or remove course materials to keep the vector database up to date.
  * **Admins:** Manage courses and personnel.
* **Source Attribution:** Responses include annotations with instructor-approved source snippets for traceability.
* **Secure Authentication:** Utilizes Google Authentication linked to Sabancı University credentials with role-based access control.
* **Conversation Logging:** Saves query history and chat metadata in a NoSQL MongoDB database for context retention and debugging.

## 🛠️ System Architecture & Tech Stack
* **Frontend:** React.js
* **Backend:** Flask (Python) REST API
* **Database:** MongoDB (NoSQL document store)
* **Vector Database:** FAISS (Facebook AI Similarity Search)
* **Embeddings:** Sentence Transformer (`all-MiniLM-L6-v2`)
* **LLM:** Quantized DeepSeek-R1-Distill-Qwen-14B (via vLLM for concurrency)

## 📂 Repositories
The project is divided into frontend and backend repositories:
* **Frontend:** [https://github.com/timurturut/sugpt](https://github.com/timurturut/sugpt)
* **Backend:** [https://github.com/EfeBallar/LLM-Based-Course-Assistant](https://github.com/EfeBallar/LLM-Based-Course-Assistant)
