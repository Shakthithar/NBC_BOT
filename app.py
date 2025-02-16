from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session management

# Initialize the GenerativeModel
API_KEY = "AIzaSyC8PKlS5Ippsf9QPdj7G6kG76D-RrxxaTA"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Store all chat sessions in memory (consider database for production)
chat_sessions = {}
settings = {"temperature": 0.7, "max_tokens": 100}

# ...existing code...

@app.route('/')
def index():
    # Initialize with a default session
    if 'active_session' not in session or session['active_session'] not in chat_sessions:
        session['active_session'] = str(uuid.uuid4())
        chat_sessions[session['active_session']] = []
    return render_template('index.html', 
                         chat_history=chat_sessions[session['active_session']],
                         sessions=chat_sessions.keys(),
                         settings=settings)

# ...existing code...

@app.route('/new_chat', methods=['POST'])
def new_chat():
    # Create new session
    new_session_id = str(uuid.uuid4())
    session['active_session'] = new_session_id
    chat_sessions[new_session_id] = []
    return jsonify({"status": "success", "session_id": new_session_id})

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['user_input']
    current_session = session.get('active_session')
    
    if not current_session or current_session not in chat_sessions:
        return jsonify({"error": "Session not found"}), 400
    
    # Generate response
    response = model.generate_content(user_input)
    
    # Store in current session
    chat_sessions[current_session].append({
        "user": user_input,
        "bot": response.text
    })
    
    return jsonify({
        "response": response.text,
        "session_id": current_session
    })

@app.route('/switch_session', methods=['POST'])
def switch_session():
    session_id = request.json['session_id']
    if session_id in chat_sessions:
        session['active_session'] = session_id
        return jsonify({"status": "success"})
    return jsonify({"error": "Session not found"}), 404

@app.route('/update_settings', methods=['POST'])
def update_settings():
    settings['temperature'] = float(request.json['temperature'])
    settings['max_tokens'] = int(request.json['max_tokens'])
    return jsonify({"status": "success", "settings": settings})

if __name__ == '__main__':
    app.run(debug=True)