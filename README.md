# Clinical Insights: AI Medical Report Analyzer

A Flask web app that reads a medical report (PDF) and uses **Google Gemini 2.5 Pro** to explain it in plain, patient-friendly language. The app shows how serious the findings look, what is abnormal, what to do next, and which kind of doctor to see.

> ⚠️ **Disclaimer:** This project gives AI-generated insights for informational purposes only. It is **not** a medical diagnosis and does not replace advice from a qualified healthcare professional.

## Features

- **PDF report analysis**: upload a report; text is extracted with `pypdf` and analysed by Gemini
- **Structured, schema-enforced output**: Gemini must return exactly six fields defined by a Pydantic model, so every result has the same format
- **Results dashboard**: colour-coded sections for severity, abnormal findings, precautions, medication note and doctor recommendation
- **Chat mode**: type symptoms or test values instead of uploading a file and get the same structured analysis (each message is analysed on its own)
- **Safety-first design**: a fixed set of severity levels, a "consult a doctor" disclaimer requested in every medication note, and a disclaimer banner on every page

## How It Works

1. The user uploads a PDF (or types a message in chat mode).
2. `pypdf` extracts the text from the report.
3. The text is sent to Gemini 2.5 Pro with the `MedicalAnalysis` Pydantic model as the **response schema** (JSON mode).
4. The response is validated with Pydantic.
5. The result is displayed on the dashboard (or as a chat reply).

## Output Format

| Field | Description |
|-------|-------------|
| `severity_analysis` | One of: `Low`, `Moderate`, `High - Urgent Visit Recommended`, `Critical - Immediate Physician Visit Required` |
| `key_abnormal_findings` | 3–5 key abnormal findings in simple language |
| `precautions_and_next_steps` | Practical next steps and precautions |
| `medication_suggestion` | A cautious note; the model is instructed to begin with "CONSULT A DOCTOR. This AI cannot prescribe medications." |
| `physician_recommendation` | Whether to see a doctor, and how urgently |
| `recommended_doctor_type` | One of: General Practitioner, Cardiologist, Endocrinologist, Oncologist, Pediatrician, Gastroenterologist, Other Specialist |

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| Backend | Python, Flask |
| AI | Google Gemini 2.5 Pro (`google-genai` SDK), structured JSON output |
| Validation | Pydantic |
| PDF processing | pypdf |
| Frontend | HTML, CSS, JavaScript (Jinja2 templates) |

## Project Structure

```
Clinical-Insights/
├── app.py              # Flask routes
├── analyzer_core.py    # PDF text extraction + Gemini request
├── models.py           # MedicalAnalysis Pydantic schema
├── requirements.txt
├── templates/
│   ├── index.html      # Landing page
│   ├── upload.html     # PDF upload page
│   ├── results.html    # Analysis dashboard
│   └── chat.html       # Chat interface
└── static/
    ├── style.css
    ├── user.svg
    └── doctor.svg
```

## Getting Started

### Prerequisites

- Python 3.10+
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### Installation

```bash
git clone <repository-url>
cd Clinical-Insights

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_api_key_here
```

### Run

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

## Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Landing page |
| `/upload` | GET, POST | Upload a PDF and run the analysis |
| `/results` | GET | Show the analysis dashboard |
| `/chat` | GET | Chat interface |
| `/chat_api` | POST | `{"message": "..."}` → `{"analysis": {...}}` |

## Limitations

- Works with **text-based PDFs** only. Scanned or image-only reports have no extractable text.
- Report text is sent to the Gemini API for analysis. Use sample or anonymised reports and avoid uploading real personal health information.
- AI output can be incomplete or wrong; always confirm with a doctor.
