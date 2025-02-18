# Personal-RAG

> A **Django Rest Framework (DRF)** based backend for document ingestion and a **Retrieval-Augmented Generation (RAG)** system that enables users to upload PDFs, generate embeddings, and retrieve relevant answers from documents.
---

## **Features**
- ✅ Upload **PDF documents**, extract text, and store embeddings.
- ✅ **Search documents** using embeddings stored in **PostgreSQL with pgvector**.
- ✅ **Ask questions** using a RAG-based **QnA API** powered by **Google Gemini** or **Ollama (Llama 3.1 8B)**.
- ✅ **Filter documents by title** and ask targeted questions.
- ✅ Uses **Celery & Redis** for asynchronous processing of document embeddings.

---

## **🛠 Tech Stack**
- **Backend**: Django, Django Rest Framework (DRF)
- **Database**: PostgreSQL (with `pgvector` for embeddings)
- **Vector Storage**: `langchain_community.vectorstores.PGVector`
- **Embeddings**: `HuggingFaceEmbeddings (all-MiniLM-L6-v2)`
- **LLM Models**: Google Gemini 1.5 Flash / Ollama Llama 3.1 8B
- **Async Tasks**: Celery, Redis
---

## **🚀 Setup & Installation**

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/HarshithKulkarni/Personal-RAG.git
cd Personal-RAG
```

### **2️⃣ Create a Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4️⃣ Set Up Environment Variables**
Create a `.env` file in the project root (rag_app) and add:
```env
GOOGLE_API_KEY=<your-google-api-key>
SECRET_KEY=<your-secret-key>
DATABASE_NAME=<db-name>
DATABASE_USER=<db-username>
DATABASE_PASSWORD=<db-password>
DATABASE_HOST=<db-host-name>
DATABASE_PORT=<db-port>
CELERY_BROKER_URL='redis://localhost:6379'
USE_RE_RANKING='True'/'False'
```

### **5️⃣ Set Up PostgreSQL**
Ensure PostgreSQL is installed, then create a database:
```sql
CREATE DATABASE <your-db-name>;
```

### **6️⃣ Run Migrations**
```bash
python manage.py migrate
```

### **7️⃣ Start Redis (for Celery)**
```bash
redis-server
```

### **8️⃣ Start Celery Workers**
```bash
celery -A rag_app worker -E -l INFO
```

### **9️⃣ Start the Server**
```bash
python manage.py runserver
```
Now, the API is available at **`http://127.0.0.1:8000/`**.

---

## **📀 API Endpoints**

### **🔹 Document Ingestion API**
- **URL**: `/api/documents/ingest/`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "title": "Deep Learning Basics",
    "files": [PDF FILE]
  }
  ```

### **🔹 Document Selection API**
- **URL**: `/api/documents/select-documents/`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "title": "Deep Learning Basics",
    "query": "What is deep learning?"
  }
  ```

### **🔹 QnA API**
- **URL**: `/api/documents/query/`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "query": "What is neural network?",
  }
  ```

## **👥 Contributing**
1. **Fork the repository**.
2. **Create a feature branch** (`git checkout -b feature-name`).
3. **Commit your changes** (`git commit -m "Added new feature"`).
4. **Push to GitHub** (`git push origin feature-name`).
5. **Submit a pull request**.

---

## **📞 Contact & Support**
- 💎 **Email**: harshithkulkarni@gmail.com  
- 🔗 **LinkedIn**: [Harshith K](www.linkedin.com/in/harshith-kulkarni-70a48a11b)  

🚀 _Happy Coding!_ 🚀

