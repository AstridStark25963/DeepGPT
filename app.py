from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime
from typing import List, Dict

app = Flask(__name__)
CORS(app)

class DeepSeekChat:
    def __init__(self):
        # DeepSeek API 配置
        self.api_key = os.getenv('DEEPSEEK_API_KEY', '')
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"
        
    def chat(self, message: str, conversation_history: List[Dict] = None) -> Dict:
        """
        与DeepSeek模型进行对话
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "DeepSeek API Key 未配置。请设置 DEEPSEEK_API_KEY 环境变量。"
            }
        
        # 构建消息历史
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({
            "role": "user", 
            "content": message
        })
        
        # API 请求数据
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7,
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result["choices"][0]["message"]["content"],
                    "model": self.model,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"API 请求失败: {response.status_code} - {response.text}"
                }
                
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"网络请求错误: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"未知错误: {str(e)}"
            }

class QwenChat:
    def __init__(self):
        # 通义千问 API 配置
        self.api_key = os.getenv('QWEN_API_KEY', '')
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.model = "qwen-turbo"  # 根据需要选择其他模型
        
    def chat(self, message: str, conversation_history: List[Dict] = None) -> Dict:
        """
        与通义千问模型进行对话
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "通义千问 API Key 未配置。请设置 QWEN_API_KEY 环境变量。"
            }
        
        messages = conversation_history or []
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result["choices"][0]["message"]["content"],
                    "model": self.model,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"API 请求失败: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"未知错误: {str(e)}"
            }

# 初始化 AI 客户端
deepseek_client = DeepSeekChat()
qwen_client = QwenChat()

# 存储对话历史（简单内存存储，重启后清空）
# 使用嵌套字典，第一层是会话ID，第二层是模型类型
conversation_sessions = {}

@app.route('/')
def index():
    """首页 - 提供聊天界面"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天API端点"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "缺少消息内容"
            }), 400
        
        message = data['message'].strip()
        session_id = data.get('session_id', 'default')
        model_type = data.get('model_type', 'deepseek')  # 默认使用 DeepSeek
        
        if not message:
            return jsonify({
                "success": False,
                "error": "消息不能为空"
            }), 400
        
        # 获取对话历史
        if session_id not in conversation_sessions:
            conversation_sessions[session_id] = {}
        
        if model_type not in conversation_sessions[session_id]:
            conversation_sessions[session_id][model_type] = []
        
        conversation_history = conversation_sessions[session_id][model_type]
        
        # 根据选择的模型类型调用相应的API
        if model_type == 'deepseek':
            result = deepseek_client.chat(message, conversation_history)
        elif model_type == 'qwen':
            result = qwen_client.chat(message, conversation_history)
        else:
            return jsonify({
                "success": False,
                "error": f"不支持的模型类型: {model_type}"
            }), 400
        
        if result["success"]:
            # 保存对话历史
            conversation_sessions[session_id][model_type].extend([
                {"role": "user", "content": message},
                {"role": "assistant", "content": result["response"]}
            ])
            
            # 限制历史记录长度（保留最近10轮对话）
            if len(conversation_sessions[session_id][model_type]) > 20:
                conversation_sessions[session_id][model_type] = conversation_sessions[session_id][model_type][-20:]
        
        # 在结果中添加模型类型信息
        result["model_type"] = model_type
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500

@app.route('/api/clear', methods=['POST'])
def clear_conversation():
    """清空对话历史"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        model_type = data.get('model_type', None)  # 如果不指定模型类型，则清空所有模型的对话
        
        if session_id in conversation_sessions:
            if model_type:
                if model_type in conversation_sessions[session_id]:
                    conversation_sessions[session_id][model_type] = []
            else:
                conversation_sessions[session_id] = {}
        
        return jsonify({
            "success": True,
            "message": "对话历史已清空"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"清空失败: {str(e)}"
        }), 500

@app.route('/api/status')
def status():
    """检查服务状态"""
    return jsonify({
        "status": "running",
        "deepseek_available": bool(deepseek_client.api_key),
        "qwen_available": bool(qwen_client.api_key),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 AI 对话系统启动中...")
    print("📝 请确保设置了以下环境变量:")
    print("   - DEEPSEEK_API_KEY（用于 DeepSeek AI）")
    print("   - QWEN_API_KEY（用于通义千问）")
    print("🌐 访问 http://localhost:5000 开始对话")
    
    app.run(debug=True, host='0.0.0.0', port=5000)