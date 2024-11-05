import os
from logging.config import dictConfig

import vertexai
from cloudevents.http import from_http
from flask import Flask, request
from google.cloud import firestore, storage
from tenacity import retry, wait_exponential
from vertexai.generative_models import Content, GenerationConfig, Part
from vertexai.preview import rag
from vertexai.preview.generative_models import GenerativeModel, Tool

# Logging config
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stdout',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
app.config.from_prefixed_env()

# Global variables for Google Cloud SDK
PROJECT_ID = ""
VERTEX_AI_LOCATION = ""
PUBLISHER_MODEL = "publishers/google/models/text-multilingual-embedding-002"
GENERATIVE_MODEL_NAME = "gemini-1.5-flash-001"
RAG_CHUNK_SIZE = 512
RAG_CHUNK_OVERLAP = 100
RAG_MAX_EMBEDDING_REQUESTS_PER_MIN = 900
RAG_SIMILARITY_TOP_K = 3
RAG_VECTOR_DISTANCE_THRESHOLD = 0.5
QUESTION_FAILED_MESSAGE = "申し訳ございません。回答の生成に失敗しました。再度質問をやり直してください。"
MAX_SUMMARIZATION_LENGTH = 2048
MAX_TOTAL_COMMON_QUESTIONS_LENGTH = 1024
SUMMARIZATION_FAILED_MESSAGE = "申し訳ございません。要約の生成に失敗しました。"
MEANINGFUL_MINIMUM_QUESTION_LENGTH = 7

# Obtain project_id from environment variable and will raise exception if not set
try:
    PROJECT_ID = app.config["PROJECT_ID"]
except KeyError:
    raise Exception("Set FLASK_PROJECT_ID environment variable.")

# Obtain vertex_ai_location from environment variable or use the default value
try:
    VERTEX_AI_LOCATION = app.config["VERTEX_AI_LOCATION"]
except KeyError:
    VERTEX_AI_LOCATION = "us-central1"

bucket_name = f"{PROJECT_ID}.firebasestorage.app"

vertexai.init(project=PROJECT_ID, location=VERTEX_AI_LOCATION)
db = firestore.Client()

# Retry with exponential backoff since only one file can be imported at the same time
@retry(wait=wait_exponential(multiplier=5, max=40))
def import_files(corpus_name, gcs_path):
    return rag.import_files(
        corpus_name,
        [gcs_path],
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP,
        max_embedding_requests_per_min=RAG_MAX_EMBEDDING_REQUESTS_PER_MIN,
    )

@app.route("/add_user", methods=["POST"])
def add_user():
    event = from_http(request.headers, request.get_data())
    document = event.get("document")
    event_id = event.get("id")

    users, uid = document.split('/')

    app.logger.info(f"{event_id}: start adding a user: {uid}")

    embedding_model_config = rag.EmbeddingModelConfig(
        publisher_model=PUBLISHER_MODEL
    )

    app.logger.info(f"{event_id}: start creating a rag corpus for a user: {uid}")
    rag_corpus = rag.create_corpus(
        display_name=uid,
        embedding_model_config=embedding_model_config,
    )
    app.logger.info(f"{event_id}: finished creating a rag corpus for a user: {uid}")
    
    doc_ref = db.collection(users).document(uid)
    doc_ref.update({"corpusName": rag_corpus.name, "status": "created"})

    app.logger.info(f"{event_id}: finished adding a user: {uid}")

    return ("finished", 204)

@app.route("/add_source", methods=["POST"])
def add_source():
    event = from_http(request.headers, request.get_data())
    event_id = event.get("id")

    document = event.get("document")
    users, uid, notebooks, notebookId, sources, sourceId = document.split('/')

    app.logger.info(f"{event_id}: start adding a source: {sourceId}")

    user_ref = db.collection(users).document(uid)
    user = user_ref.get()
    corpus_name = user.get("corpusName")

    doc_ref = db.collection(users).document(uid).collection(notebooks).document(notebookId).collection(sources).document(sourceId)
    doc = doc_ref.get()
    name = doc.get("name")
    storagePath = doc.get("storagePath")

    gcs_path = f"gs://{PROJECT_ID}.firebasestorage.app{storagePath}"

    app.logger.info(f"{event_id}: start importing a source file: {name}")
    response = import_files(corpus_name, gcs_path)
    app.logger.info(f"{event_id}: finished importing a source file: {response}")

    app.logger.info(f"{event_id}: start finding rag_file_id: {name}")
    rag_files = rag.list_files(corpus_name=corpus_name)
    rag_file_name = ""
    filename = storagePath.split('/')[-1]
    for rag_file in rag_files:
        if rag_file.display_name == filename:
            rag_file_name = rag_file.name
    rag_file_id = rag_file_name.split('/')[-1]
    app.logger.info(f"{event_id}: found rag_file_id: {rag_file_id}")

    doc_ref.update({"status": "created", "ragFileId": rag_file_id})

    app.logger.info(f"{event_id}: finished adding a source: {sourceId} / {name} => {rag_file_id}")

    return ("finished", 204)

@app.route("/question", methods=["POST"])
def question():
    event = from_http(request.headers, request.get_data())
    event_id = event.get("id")
    document = event.get("document")

    users, uid, notebooks, notebookId, chat, messageId = document.split('/')

    app.logger.info(f"{event_id}: start generating an answer: {messageId}")

    message_ref = db.collection(users).document(uid).collection(notebooks).document(notebookId).collection(chat).document(messageId)
    message = message_ref.get()

    if message.get("role") == "model":
        return ("skip message from model", 204)

    add_time, answer_ref = db.collection(users).document(uid).collection(notebooks).document(notebookId).collection(chat).add({
        "content": '',
        "loading": True,
        "ragFileIds": None,
        "role": 'model',
        "createdAt": firestore.SERVER_TIMESTAMP
    })

    user_ref = db.collection(users).document(uid)
    user = user_ref.get()
    corpus_name = user.get("corpusName")

    source_ids = message.get("ragFileIds")
    app.logger.info(f"{event_id}: {len(source_ids)} sources are selected")

    rag_retrieval_tool = Tool.from_retrieval(
        retrieval=rag.Retrieval(
            source=rag.VertexRagStore(
                rag_resources=[
                    rag.RagResource(
                        rag_corpus=corpus_name,
                        rag_file_ids=source_ids
                    )
                ],
                similarity_top_k=RAG_SIMILARITY_TOP_K,
                vector_distance_threshold=RAG_VECTOR_DISTANCE_THRESHOLD,
            ),
        )
    )

    rag_model = GenerativeModel(
        model_name=GENERATIVE_MODEL_NAME,
        tools=[rag_retrieval_tool],
        system_instruction=["Output the result in markdown format."]
    )

    chat_messages = (
        db.collection(users).document(uid)
        .collection(notebooks).document(notebookId)
        .collection('chat')
        .order_by('createdAt')
        .stream()
    )

    contents = [Content(role=chat_message.get("role"), parts=[Part.from_text(chat_message.get("content"))]) 
            for chat_message in chat_messages if not chat_message.get("loading") and chat_message.get("status") == "success"]
    app.logger.info(f"{event_id}: {len(contents)} contents are used")

    try:
        app.logger.info(f"{event_id}: start generating content")
        response = rag_model.generate_content(contents=contents)
        app.logger.info(f"{event_id}: finished generating content")

        answer_ref.update({"content": response.text, "loading": False, "status": "success"})
        message_ref.update({"loading": False, "status": "success"})
        app.logger.info(f"{event_id}: finished generating an answer: {messageId}")
    except Exception as err:
        message_ref.update({"loading": False, "status": "failed"})
        answer_ref.update({"content": QUESTION_FAILED_MESSAGE, "loading": False, "status": "failed"})
        app.logger.info(f"{event_id}: failed generating an answer: {err=}, {type(err)=}")

    return ("finished", 204)

@app.route("/update_source", methods=["POST"])
def update_source():
    event = from_http(request.headers, request.get_data())
    event_id = event.get("id")
    document = event.get("document")

    users, uid, notebooks, notebookId, sources, sourceId = document.split('/')

    doc_ref = db.collection(users).document(uid).collection(notebooks).document(notebookId).collection(sources).document(sourceId)
    doc = doc_ref.get()

    name = doc.get("name")
    status = doc.get("status")
    if status != "deleting":
        app.logger.info(f"{event_id}: skipping since source is not deleting: {name}")
        return ("finished", 204)

    app.logger.info(f"{event_id}: start deleting a source: {name}")

    user_ref = db.collection(users).document(uid)
    user = user_ref.get()
    corpus_name = user.get("corpusName")

    rag_file_id = doc.get("ragFileId")
    rag_file = f"{corpus_name}/ragFiles/{rag_file_id}"

    app.logger.info(f"{event_id}: start deleting a rag file: {rag_file}")
    rag.delete_file(rag_file)
    app.logger.info(f"{event_id}: finished deleting a rag file: {rag_file}")

    storage_client = storage.Client()
    storagePath = doc.get("storagePath")
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(storagePath[1:])
    app.logger.info(f"{event_id}: start deleting a source file from cloud storage: {bucket_name}{storagePath}")
    blob.delete()
    app.logger.info(f"{event_id}: finished deleting a source file from cloud storage: {bucket_name}{storagePath}")

    notebook_ref = db.collection(users).document(uid).collection(notebooks).document(notebookId)
    notebook_ref.update({"sourceCount": firestore.Increment(-1)})

    doc_ref.delete()

    app.logger.info(f"{event_id}: finished deleting a source: {name}")

    return ("finished", 204)

@app.route("/summarize", methods=["POST"])
def summarize():
    event = from_http(request.headers, request.get_data())
    event_id = event.get("id")
    document = event.get("document")

    users, uid, notebooks, notebookId, sources, sourceId = document.split('/')

    app.logger.info(f"{event_id}: start summarizing a source: {sourceId}")

    doc_ref = db.collection(users).document(uid).collection(notebooks).document(notebookId).collection(sources).document(sourceId)
    doc = doc_ref.get()

    file_type = doc.get("type")
    storagePath = doc.get("storagePath")
    gcs_path = f"gs://{PROJECT_ID}.firebasestorage.app{storagePath}"

    model = GenerativeModel(model_name=GENERATIVE_MODEL_NAME)

    doc_part = Part.from_uri(gcs_path, file_type)

    config = GenerationConfig(
        max_output_tokens=MAX_SUMMARIZATION_LENGTH + 1000, temperature=0, top_p=1, top_k=32,
    )

    prompt = f"""You are an AI assistant.
    
    Summarize the contents for readers who doesn't have enough domain knowledge.
    Output the result in Japanese and the result must be less than {MAX_SUMMARIZATION_LENGTH} characters.
    Surround the keypoint sentence or words by **.
    """

    try:
        app.logger.info(f"{event_id}: start generating a summary for a source: {sourceId}")
        response = model.generate_content([doc_part, prompt], generation_config=config)
        app.logger.info(f"{event_id}: finished generating a summary for a source: {sourceId}")
        doc_ref.update({"summarization": response.text})
        app.logger.info(f"{event_id}: finished summarizing a source: {sourceId}")
    except Exception as err:
        app.logger.info(f"{event_id}: failed generating a summary for a source: {sourceId}")
        doc_ref.update({"summarization": SUMMARIZATION_FAILED_MESSAGE})
        app.logger.info(f"{event_id}: failed summarizing a source: {err=}, {type(err)=}")

    return ("finished", 204)

@app.route("/generate_common_questions", methods=["POST"])
def generate_common_questions():
    event = from_http(request.headers, request.get_data())
    event_id = event.get("id")
    document = event.get("document")

    users, uid, notebooks, notebookId, sources, sourceId = document.split('/')

    app.logger.info(f"{event_id}: start generating common questions: {sourceId}")

    doc_ref = db.collection(users).document(uid).collection(notebooks).document(notebookId).collection(sources).document(sourceId)
    doc = doc_ref.get()

    file_type = doc.get("type")
    storagePath = doc.get("storagePath")
    gcs_path = f"gs://{PROJECT_ID}.firebasestorage.app{storagePath}"

    model = GenerativeModel(model_name=GENERATIVE_MODEL_NAME)

    doc_part = Part.from_uri(gcs_path, file_type)

    config = GenerationConfig(
        max_output_tokens=MAX_TOTAL_COMMON_QUESTIONS_LENGTH, temperature=0, top_p=1, top_k=32,
    )

    prompt = """You are an AI assistant.

    I want you to propose up to 5 common, simple questions based on the content.
    Output the result in Japanese and print per question per line.
    Each question should be one sentence and up to 30 characters long."""

    questions = []
    raw_questions = []
    try:
        app.logger.info(f"{event_id}: start generating commmon raw questions: {sourceId}")
        response = model.generate_content([doc_part, prompt], generation_config=config)
        app.logger.info(f"{event_id}: finished generating commmon raw questions: {sourceId}")
        raw_questions = response.text.splitlines()
    except Exception:
        app.logger.info(f"{event_id}: failed generating common questions: {sourceId}")

    # Remove unnecessary numbers (1. ,2. ,3. ) or hyphens (- ) at the beginning of the questions.
    for raw_question in raw_questions:
        question = raw_question.split()[1] if ' ' in raw_question else raw_question
        # Skip if the question is too short
        if len(question) < MEANINGFUL_MINIMUM_QUESTION_LENGTH:
            app.logger.info(f"{event_id}: skipping generated common question: {question}")
            continue
        questions.append(question)

    # Delete duplicate questions
    questions = list(set(questions))

    doc_ref.update({"questions": questions})
    app.logger.info(f"{event_id}: finished generating common questions: {len(questions)} questions -> {sourceId}")

    return ("finished", 204)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

