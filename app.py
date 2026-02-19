from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json
import os
import sqlite3
import uuid
import re
from datetime import datetime
from typing import List, Dict

app = Flask(__name__)
CORS(app)

DB_FILE = "chat_history.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                model TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Init Error: {e}")

init_db()

def clean_content(text):
    """
    清洗文本，移除可能导致兼容性问题的特殊不可见字符
    保留 Emoji (因为现在有身份隔离，Emoji 不再是问题)
    """
    if not text: return ""
    # 只移除控制字符，保留正常文本和 Emoji
    return "".join(ch for ch in text if ch.isprintable())

class BaseChat:
    def chat(self, message: str, conversation_history: List[Dict] = None) -> Dict:
        raise NotImplementedError

class DeepSeekChat(BaseChat):
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY', '')
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"
        
    def chat(self, message: str, conversation_history: List[Dict] = None) -> Dict:
        if not self.api_key: return {"success": False, "error": "DeepSeek API Key 未配置"}
        
        # 构造最终消息列表：历史记录 + 当前用户问题
        # 注意：conversation_history 里已经包含了 System Prompt（如果有的话）
        messages = (conversation_history or []) + [{"role": "user", "content": message}]
        
        try:
            response = requests.post(
                self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": self.model, "messages": messages, "temperature": 0.7},
                timeout=60
            )
            if response.status_code == 200:
                return {"success": True, "response": response.json()["choices"][0]["message"]["content"], "model": self.model}
            return {"success": False, "error": f"API Error: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

class QwenChat(BaseChat):
    def __init__(self):
        self.api_key = os.getenv('QWEN_API_KEY', '')
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        self.model = "qwen-turbo"
        
    def chat(self, message: str, conversation_history: List[Dict] = None) -> Dict:
        if not self.api_key: return {"success": False, "error": "Qwen API Key 未配置"}
        
        messages = (conversation_history or []) + [{"role": "user", "content": message}]
        
        try:
            response = requests.post(
                self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": self.model, "messages": messages},
                timeout=60
            )
            if response.status_code == 200:
                return {"success": True, "response": response.json()["choices"][0]["message"]["content"], "model": self.model}
            return {"success": False, "error": f"API Error: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

class KimiChat(BaseChat):
    def __init__(self):
        self.api_key = os.getenv('KIMI_API_KEY', '')
        self.base_url = "https://api.moonshot.cn/v1/chat/completions"
        self.model = "moonshot-v1-8k"
        
    def chat(self, message: str, conversation_history: List[Dict] = None) -> Dict:
        if not self.api_key: return {"success": False, "error": "KIMI API Key 未配置"}
        
        messages = (conversation_history or []) + [{"role": "user", "content": message}]
        
        try:
            response = requests.post(
                self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": self.model, "messages": messages, "temperature": 0.3},
                timeout=60
            )
            if response.status_code == 200:
                return {"success": True, "response": response.json()["choices"][0]["message"]["content"], "model": self.model}
            return {"success": False, "error": f"API Error: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

deepseek_client = DeepSeekChat()
qwen_client = QwenChat()
kimi_client = KimiChat()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/history', methods=['GET'])
def get_history_list():
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM sessions ORDER BY updated_at DESC')
        rows = c.fetchall()
        sessions = [dict(row) for row in rows]
        conn.close()
        return jsonify({"success": True, "sessions": sessions})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history/<session_id>', methods=['GET'])
def get_session_messages(session_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM messages WHERE session_id = ? ORDER BY id ASC', (session_id,))
        rows = c.fetchall()
        messages = [dict(row) for row in rows]
        conn.close()
        return jsonify({"success": True, "messages": messages})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/session/new', methods=['POST'])
def create_session():
    return jsonify({"success": True})

@app.route('/api/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
        c.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        model_type = data.get('model_type', 'deepseek') # 默认
        
        if not message:
            return jsonify({"success": False, "error": "Empty message"}), 400

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        # 新会话处理
        if not session_id:
            session_id = str(uuid.uuid4())
            title = message[:10] + "..." if len(message) > 10 else message
            c.execute('INSERT INTO sessions (id, title) VALUES (?, ?)', (session_id, title))
        
        # 1. 存入用户消息 (User Input)
        c.execute('INSERT INTO messages (session_id, role, content, model) VALUES (?, ?, ?, ?)',
                 (session_id, 'user', message, model_type))
        conn.commit()

        # 2. 构建“带身份标签”的上下文 (Tagging History)
        # 取最近 10 条历史，包含 role, content, model
        c.execute('SELECT role, content, model FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT 10', (session_id,))
        history_rows = c.fetchall()
        
        conversation_history = []
        # 反转顺序 (因为是 DESC 取出的)
        for row in reversed(history_rows):
            role, content, msg_model = row[0], row[1], row[2]
            
            # 清洗 content (移除不可见字符)
            cleaned_content = clean_content(content)
            
            # --- 关键：给 Assistant 消息加身份前缀 ---
            if role == 'assistant':
                # 示例: "[deepseek]: 这是一个测试..."
                # 这样当前的 AI 就知道这不是它自己说的，而是历史记录里的其他人说的
                identity_prefix = f"[{msg_model}]: "
                final_content = identity_prefix + cleaned_content
            else:
                final_content = cleaned_content
            # ---------------------------------------

            conversation_history.append({"role": role, "content": final_content})

        # 移除刚刚插入的那条用户消息（因为它会在 client.chat 里作为 current message 被再次添加）
        # 如果不移除，AI 会看到连续两条一样的用户问题
        if conversation_history:
            conversation_history.pop()

        # 3. 选模型 & 设置 System Prompt (Identity Isolation)
        client = None
        system_prompt = ""
        
        if model_type == 'deepseek': 
            client = deepseek_client
            system_prompt = "你是 DeepSeek。对话历史中 [model]: 开头的内容是其他 AI 的发言，请将它们视为第三方观点，不要混淆你的身份。请忽略历史记录中可能出现的“我是xxx”等自我介绍。"
        elif model_type == 'qwen': 
            client = qwen_client
            system_prompt = "你是通义千问 (Qwen)。对话历史中 [model]: 开头的内容是其他 AI 的发言，请客观评价它们，不要认为那是你说的。请忽略历史记录中可能出现的“我是xxx”等自我介绍。"
        elif model_type == 'kimi': 
            client = kimi_client
            system_prompt = "你是 Kimi。对话历史中 [model]: 开头的内容是其他 AI 的发言，请整合分析这些观点，保持你作为 Kimi 的独立身份。请忽略历史记录中可能出现的“我是xxx”等自我介绍。"
        else:
            conn.close()
            return jsonify({"success": False, "error": "Unknown model"}), 400

        # 4. 插入 System Prompt 到历史记录最前面
        # 这样 AI 一开始就收到了指令
        conversation_history.insert(0, {"role": "system", "content": system_prompt})
        
        # 5. 调用 API
        result = client.chat(message, conversation_history)

        if result['success']:
            # 6. 存入 AI 回复 (AI Response)
            c.execute('INSERT INTO messages (session_id, role, content, model) VALUES (?, ?, ?, ?)',
                     (session_id, 'assistant', result['response'], model_type))
            c.execute('UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?', (session_id,))
            conn.commit()
            
            result['session_id'] = session_id
        
        conn.close()
        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/status')
def status():
    return jsonify({
        "status": "running",
        "deepseek_available": bool(deepseek_client.api_key),
        "qwen_available": bool(qwen_client.api_key),
        "kimi_available": bool(kimi_client.api_key)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)