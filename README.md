CodeBin - A Simple Pastebin Clone
CodeBin is a lightweight, self-contained web application that allows you to paste, save, and share text snippets. It's built with Python using the FastAPI framework and requires no external database—it saves everything to a local SQLite file.

This project is a great example of a full-stack application contained within a single Python file, serving both the frontend (HTML/CSS/JS) and the backend API.

✨ Features
Simple Interface: A clean, modern UI for pasting text.

Instant Sharing: Save your text to generate a unique, shareable link.

Zero Dependencies: Runs entirely on its own without needing a separate database server.

Fast & Modern: Built with the high-performance FastAPI framework.

View Raw Content: Shared links display the raw text, which is perfect for code snippets.

🛠️ Tech Stack
Backend: Python 3, FastAPI

Server: Uvicorn

Database: SQLite (built-in Python library)

Frontend: HTML5, Tailwind CSS, vanilla JavaScript

🚀 Setup and Installation
To run this project locally, you'll need Python 3.7+ installed.

Create and Activate a Virtual Environment:
Before installing dependencies, it's highly recommended to create a virtual environment. This isolates the project's packages from your system's Python.

Create the environment:

py -m venv venv

Activate it:

On Windows (PowerShell):

First, you may need to allow scripts to run in your current terminal session. Run this command:

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

Now, activate the environment:

.\venv\Scripts\Activate

On macOS/Linux:

source venv/bin/activate

Your terminal prompt should now show (venv) at the beginning.

Install Dependencies:
With your virtual environment active, navigate to the project directory in your terminal and install the required Python packages using pip.

pip install fastapi "uvicorn[standard]"

Run the Server:
Once the installation is complete, start the web server with Uvicorn.

uvicorn main:app --reload

The --reload flag is optional but recommended for development, as it automatically restarts the server when you make changes to the code.

usage
Open the App:
Once the server is running, open your web browser and navigate to http://127.0.0.1:8000.

Create a Paste:

Type or paste your text/code into the large text area.

Click the "Save & Get Link" button.

Share the Link:

A shareable link will appear below the button.

Use the "Copy" button to copy it to your clipboard.

Anyone with this link can now view the raw text you saved.
