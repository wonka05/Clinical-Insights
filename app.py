import os
from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, flash, session, url_for, jsonify
from werkzeug.utils import secure_filename

from analyzer_core import extract_text_from_pdf, analyze_report_with_gemini
from schemas import MedicalAnalysis
from database import db

# Load environment variables
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

app.config['SECRET_KEY'] = 'super_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed extensions for file uploads
ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Landing Page
@app.route('/')
def landing():
    return render_template('index.html')


# Upload Page
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():

    if request.method == 'POST':

        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):

            report_text = extract_text_from_pdf(file.stream)

            if not report_text:
                flash("PDF could not be read. It might be scanned or empty.")
                return redirect(request.url)

            analysis_result = analyze_report_with_gemini(report_text)

            if isinstance(analysis_result, MedicalAnalysis):

                session['analysis'] = analysis_result.model_dump()

                return redirect(url_for('show_results'))

            else:
                flash(f"Analysis Failed: {analysis_result.get('error', 'Unknown Error')}")
                return redirect(request.url)

        else:
            flash('Only PDF files allowed.')
            return redirect(request.url)

    return render_template('upload.html')


# Results Page
@app.route('/results')
def show_results():

    analysis_data = session.get('analysis')

    if not analysis_data:
        flash("No analysis found. Upload a report first.")
        return redirect(url_for('upload_file'))

    return render_template('results.html', analysis=analysis_data)


# Chat Page
@app.route('/chat')
def chat_ui():

    session['chat_history'] = []

    return render_template('chat.html')


# Chat API
@app.route('/chat_api', methods=['POST'])
def chat_api():

    user_msg = request.json.get("message", "")

    if not user_msg:
        return jsonify({"error": "Empty message"}), 400

    analysis_result = analyze_report_with_gemini(user_msg)

    if isinstance(analysis_result, MedicalAnalysis):
        return jsonify({"analysis": analysis_result.model_dump()})
    else:
        return jsonify({"error": "Analysis failed"}), 500


# Test Database Connection
with app.app_context():
    try:
        db.create_all()
        print("✅ Database connected successfully!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")


# Run Application
if __name__ == '__main__':
    app.run(debug=True) 