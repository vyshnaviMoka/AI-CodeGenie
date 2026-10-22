# CodeGenie AI Explainer & Code Generator

CodeGenie is a Flask web application that uses a generative AI model to help users generate code from natural-language prompts and understand code step by step. It brings AI-assisted coding, user accounts, saved generation history, feedback, and administrative usage insights into one application.

## Features

- **AI code generation:** Generate code from a description of what you want to build.
- **Code explanation:** Request a step-by-step explanation of code.
- **Multiple programming languages:** Choose a programming language for code generation.
- **User authentication:** Register and sign in to access the coding dashboard.
- **Generation history:** Store generated code and related prompts in the database.
- **Admin dashboard:** View user, generation, feedback, and language-usage information.
- **Feedback:** Submit a rating and feedback from the application.

## Technology Stack

- **Backend:** Python, Flask, Flask-Login
- **Frontend:** HTML, CSS, JavaScript, Jinja templates
- **Database:** SQLite with Flask-SQLAlchemy / SQLAlchemy
- **AI integration:** Hugging Face Inference API
- **Model:** Qwen/Qwen2.5-Coder-7B-Instruct
- **Deployment configuration:** Gunicorn and a Procfile

## Repository Structure

```text
AI-CodeGenie/
├── backend/        # Flask application, authentication, models, database
├── static/         # CSS, JavaScript, and other static assets
├── templates/      # HTML/Jinja templates
├── requirements.txt
├── Procfile
├── LICENSE
└── README.md
```

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/vyshnaviMoka/AI-CodeGenie.git
cd AI-CodeGenie
```

### 2. Create and activate a virtual environment (recommended)

Windows:

```powershell
py -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the Hugging Face API token

Create a `.env` file in the project root and add your own Hugging Face token:

```env
HUGGINGFACE_API_TOKEN=your_hugging_face_token_here
```

Get a token from [Hugging Face Settings](https://huggingface.co/settings/tokens). Keep the token private. Do not commit the `.env` file to GitHub.

### 5. Start the application

Run this command from the repository root:

```bash
python -m backend.app
```

Then open the local address printed by Flask in your browser (usually http://127.0.0.1:5000).

## How It Works

1. The user signs in and opens the coding dashboard.
2. The user enters a prompt, selects a programming language, and chooses code generation or code explanation.
3. The Flask backend sends the request to the Hugging Face inference endpoint.
4. The response is shown in the web interface; generated code and prompts are saved to the application's database.
5. Administrative pages summarize usage and feedback data.

AI output can contain mistakes. Review and test generated code before using it in real projects.

## Engineering Focus

This project demonstrates full-stack web development, integration with an external AI inference API, user authentication, database-backed history, feedback handling, and an administrative dashboard with usage summaries.

## Author

**Vyshnavi Moka**

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
