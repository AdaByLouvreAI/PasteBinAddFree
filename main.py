# main.py
# To run this app:
# 1. Install FastAPI and Uvicorn: pip install fastapi "uvicorn[standard]"
# 2. Run the server: uvicorn main:app --reload

import secrets
import sqlite3
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from pydantic import BaseModel

# --- 1. App and Database Setup ---

app = FastAPI()
DB_NAME = "pastes.db"

def init_db():
    """Initializes the database and creates the table if it doesn't exist."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pastes (
                paste_id TEXT PRIMARY KEY,
                content TEXT NOT NULL
            )
        """)
        conn.commit()

# --- Database Dependency ---
def get_db_conn():
    """
    Dependency function to get a database connection for each request.
    This ensures that each request uses a connection created in its own thread.
    """
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
    finally:
        conn.close()


# --- 2. Pydantic Model for Incoming Data ---

class Paste(BaseModel):
    """Defines the structure for the incoming paste data."""
    content: str


# --- 3. Frontend HTML ---
# We serve the user interface directly from this string.

html_content = """
<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeBin - Simple Pastebin</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Fira+Code:wght@400&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        textarea { font-family: 'Fira Code', monospace; }
    </style>
</head>
<body class="bg-slate-900 text-slate-100 flex items-center justify-center min-h-full p-4">

    <main class="w-full max-w-3xl mx-auto">
        <div class="bg-slate-800 border border-slate-700 rounded-2xl shadow-2xl p-6 sm:p-8">
            
            <div class="text-center mb-8">
                <h1 class="text-3xl sm:text-4xl font-bold text-emerald-400">CodeBin</h1>
                <p class="text-slate-400 mt-2">Paste, save, and share your text snippets.</p>
            </div>

            <textarea 
                id="paste-input"
                rows="15"
                placeholder="Paste your text or code here..."
                class="w-full bg-slate-900 border border-slate-600 rounded-lg p-4 resize-y focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-all placeholder-slate-500"
            ></textarea>
            
            <button 
                id="save-button"
                class="mt-4 w-full bg-emerald-500 hover:bg-emerald-600 text-slate-900 font-bold py-3 px-6 rounded-lg transition-all shadow-md hover:shadow-lg"
            >
                Save & Get Link
            </button>

            <div id="result-container" class="mt-6 text-center hidden">
                <p class="text-slate-300">Your shareable link is ready:</p>
                <div class="mt-2 bg-slate-900 border border-slate-700 rounded-lg p-4 flex items-center justify-between gap-4">
                    <a id="share-link" href="#" target="_blank" class="text-lg font-mono text-emerald-400 truncate hover:underline"></a>
                    <button id="copy-button" class="bg-slate-700 hover:bg-slate-600 text-slate-200 font-semibold py-2 px-4 rounded-lg text-sm">
                        Copy
                    </button>
                </div>
                <p id="copy-feedback" class="text-green-400 text-sm mt-2 h-5"></p>
            </div>
        </div>
    </main>

    <script>
        const pasteInput = document.getElementById('paste-input');
        const saveButton = document.getElementById('save-button');
        const resultContainer = document.getElementById('result-container');
        const shareLink = document.getElementById('share-link');
        const copyButton = document.getElementById('copy-button');
        const copyFeedback = document.getElementById('copy-feedback');

        saveButton.addEventListener('click', async () => {
            const content = pasteInput.value;
            if (!content.trim()) {
                alert('Please enter some text to save.');
                return;
            }

            try {
                const response = await fetch('/paste', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content: content })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Failed to save paste.');
                }

                const result = await response.json();
                const pasteUrl = `${window.location.origin}/${result.paste_id}`;
                
                shareLink.href = pasteUrl;
                shareLink.textContent = pasteUrl;
                resultContainer.classList.remove('hidden');

            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred: ' + error.message);
            }
        });

        copyButton.addEventListener('click', () => {
            navigator.clipboard.writeText(shareLink.href).then(() => {
                copyFeedback.textContent = 'Copied!';
                setTimeout(() => { copyFeedback.textContent = ''; }, 2000);
            }).catch(err => {
                copyFeedback.textContent = 'Failed to copy.';
            });
        });
    </script>
</body>
</html>
"""


# --- 4. API Endpoints ---

@app.on_event("startup")
def on_startup():
    """Initialize the database when the app starts."""
    init_db()

@app.get("/", response_class=HTMLResponse)
def get_homepage():
    """Serves the main HTML page for the frontend."""
    return html_content

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Handles browser requests for a favicon, preventing 404 errors in logs."""
    return Response(status_code=204)

@app.post("/paste")
def create_paste(paste: Paste, conn: sqlite3.Connection = Depends(get_db_conn)):
    """
    Creates a new paste.
    Generates a unique ID, saves the content to the database using a
    thread-safe connection, and returns the ID.
    """
    content = paste.content
    paste_id = secrets.token_urlsafe(8)
    
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO pastes (paste_id, content) VALUES (?, ?)", (paste_id, content))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Could not save paste to the database.")

    return {"paste_id": paste_id}


@app.get("/{paste_id}")
def get_paste(paste_id: str, conn: sqlite3.Connection = Depends(get_db_conn)):
    """
    Retrieves and displays a paste.
    Looks up the ID in the database using a thread-safe connection
    and returns the content as plain text.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM pastes WHERE paste_id = ?", (paste_id,))
        result = cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve paste from the database.")

    if result:
        content = result[0]
        return PlainTextResponse(content=content)
    else:
        raise HTTPException(status_code=404, detail="Paste not found.")
