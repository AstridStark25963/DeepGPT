class AIChat {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.clearButton = document.getElementById('clearButton');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.modelSelector = document.getElementById('modelSelector');
        this.deepseekStatus = document.getElementById('deepseekStatus').querySelector('.model-status-dot');
        this.qwenStatus = document.getElementById('qwenStatus').querySelector('.model-status-dot');
        this.kimiStatus = document.getElementById('kimiStatus').querySelector('.model-status-dot');
        
        this.sessionId = 'user_' + Date.now();
        this.activeModel = 'deepseek'; // 默认使用 DeepSeek
        
        this.initEventListeners();
        this.checkStatus();
        this.autoResizeTextarea();
    }
    
    initEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.clearButton.addEventListener('click', () => this.clearConversation());
        
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        this.messageInput.addEventListener('input', () => {
            this.autoResizeTextarea();
        });
        
        // 模型选择事件
        const modelOptions = this.modelSelector.querySelectorAll('.model-option');
        modelOptions.forEach(option => {
            option.addEventListener('click', () => {
                modelOptions.forEach(opt => opt.classList.remove('active'));
                option.classList.add('active');
                this.activeModel = option.dataset.model;
            });
        });
    }
    
    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }
    
    async checkStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            // 更新 DeepSeek 状态
            if (data.deepseek_available) {
                this.deepseekStatus.classList.add('available');
                this.deepseekStatus.classList.remove('unavailable');
                this.deepseekStatus.title = 'DeepSeek API 已配置';
            } else {
                this.deepseekStatus.classList.add('unavailable');
                this.deepseekStatus.classList.remove('available');
                this.deepseekStatus.title = 'DeepSeek API 未配置';
            }
            
            // 更新通义千问状态
            if (data.qwen_available) {
                this.qwenStatus.classList.add('available');
                this.qwenStatus.classList.remove('unavailable');
                this.qwenStatus.title = '通义千问 API 已配置';
            } else {
                this.qwenStatus.classList.add('unavailable');
                this.qwenStatus.classList.remove('available');
                this.qwenStatus.title = '通义千问 API 未配置';
            }
            
            // 更新KIMI状态
            if (data.kimi_available) {
                this.kimiStatus.classList.add('available');
                this.kimiStatus.classList.remove('unavailable');
                this.kimiStatus.title = 'KIMI API 已配置';
            } else {
                this.kimiStatus.classList.add('unavailable');
                this.kimiStatus.classList.remove('available');
                this.kimiStatus.title = 'KIMI API 未配置';
            }
            
            // 总体状态
            if (data.deepseek_available || data.qwen_available || data.kimi_available) {
                this.statusIndicator.style.background = '#10b981';
                this.statusIndicator.title = '服务正常运行中';
            } else {
                this.statusIndicator.style.background = '#ef4444';
                this.statusIndicator.title = '所有 API 均未配置';
                this.showError('请配置至少一个 API Key（DeepSeek、通义千问或KIMI）');
            }
        } catch (error) {
            this.statusIndicator.style.background = '#ef4444';
            this.statusIndicator.title = '服务器连接失败';
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.sendButton.disabled) return;
        
        // 检查当前所选模型是否可用
        let modelStatusDot;
        let modelName;
        
        if (this.activeModel === 'deepseek') {
            modelStatusDot = this.deepseekStatus;
            modelName = 'DeepSeek';
        } else if (this.activeModel === 'qwen') {
            modelStatusDot = this.qwenStatus;
            modelName = '通义千问';
        } else if (this.activeModel === 'kimi') {
            modelStatusDot = this.kimiStatus;
            modelName = 'KIMI';
        }
        
        if (!modelStatusDot.classList.contains('available')) {
            this.showError(`${modelName} API 未配置，请选择其他模型或配置 API Key`);
            return;
        }
        
        // 显示用户消息
        this.addMessage('user', message);
        this.messageInput.value = '';
        this.autoResizeTextarea();
        
        // 禁用发送按钮
        this.sendButton.disabled = true;
        
        // 显示加载状态
        const loadingElement = this.addLoadingMessage();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId,
                    model_type: this.activeModel
                })
            });
            
            const data = await response.json();
            
            // 移除加载状态
            this.removeLoadingMessage(loadingElement);
            
            if (data.success) {
                this.addMessage('assistant', data.response, data.model_type);
            } else {
                this.showError(data.error || '发送消息失败');
            }
            
        } catch (error) {
            this.removeLoadingMessage(loadingElement);
            this.showError('网络连接失败，请检查服务器状态');
        } finally {
            this.sendButton.disabled = false;
            this.messageInput.focus();
        }
    }
    
    addMessage(role, content, modelType = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const avatar = document.createElement('div');
        avatar.className = `avatar ${role}`;
        avatar.textContent = role === 'user' ? '你' : 'AI';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = this.formatMessage(content);
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        
        if (role === 'assistant' && modelType) {
            let modelName = modelType;
            if (modelType === 'deepseek') modelName = 'DeepSeek AI';
            else if (modelType === 'qwen') modelName = '通义千问';
            else if (modelType === 'kimi') modelName = 'KIMI';
            
            messageTime.textContent = `${new Date().toLocaleTimeString()} · ${modelName}`;
        } else {
            messageTime.textContent = new Date().toLocaleTimeString();
        }
        
        messageContent.appendChild(messageTime);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        // 移除欢迎消息
        const welcomeMessage = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        this.chatMessages.appendChild(messageDiv);
        
        // 初始化代码高亮
        messageDiv.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
        
        this.scrollToBottom();
    }
    
    addLoadingMessage() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message assistant loading-message';
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar assistant';
        avatar.textContent = 'AI';
        
        const loadingContent = document.createElement('div');
        loadingContent.className = 'message-content';
        
        let modelName = '模型';
        if (this.activeModel === 'deepseek') modelName = 'DeepSeek';
        else if (this.activeModel === 'qwen') modelName = '通义千问';
        else if (this.activeModel === 'kimi') modelName = 'KIMI';
        
        loadingContent.innerHTML = `
            <div class="loading">
                ${modelName} 正在思考中
                <div class="loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        loadingDiv.appendChild(avatar);
        loadingDiv.appendChild(loadingContent);
        this.chatMessages.appendChild(loadingDiv);
        this.scrollToBottom();
        
        return loadingDiv;
    }
    
    removeLoadingMessage(loadingElement) {
        if (loadingElement && loadingElement.parentNode) {
            loadingElement.parentNode.removeChild(loadingElement);
        }
    }
    
    formatMessage(content) {
        // 配置Marked选项
        marked.setOptions({
            breaks: true,  // 启用换行符转换为<br>
            gfm: true,     // 启用GitHub风格Markdown
            headerIds: false, // 禁用标题ID以避免安全问题
            sanitize: false,  // 已弃用，现在使用DOMPurify
            highlight: function(code, lang) {
                // 如果指定了语言且highlight.js支持该语言
                if (lang && hljs.getLanguage(lang)) {
                    try {
                        return hljs.highlight(code, { language: lang }).value;
                    } catch (e) {
                        console.error(e);
                    }
                }
                // 使用自动语言检测
                try {
                    return hljs.highlightAuto(code).value;
                } catch (e) {
                    console.error(e);
                }
                // 如果有错误，以纯文本返回
                return code;
            }
        });

        // 使用marked解析Markdown并返回HTML
        try {
            return marked.parse(content);
        } catch (e) {
            console.error('Markdown解析错误:', e);
            // 如果解析失败，回退到基本格式化
            return content
                .replace(/\n/g, '<br>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>');
        }
    }
    
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        this.chatMessages.appendChild(errorDiv);
        this.scrollToBottom();
        
        // 5秒后自动移除错误消息
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }
    
    async clearConversation() {
        if (!confirm('确定要清空所有对话记录吗？')) return;
        
        try {
            await fetch('/api/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    model_type: this.activeModel
                })
            });
            
            // 清空界面
            this.chatMessages.innerHTML = `
                <div class="welcome-message">
                    <h3>👋 欢迎使用 AI 对话系统</h3>
                    <p>请输入您的问题，我会尽力为您提供帮助！</p>
                </div>
            `;
            
        } catch (error) {
            this.showError('清空对话失败');
        }
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
}

// 初始化聊天应用
document.addEventListener('DOMContentLoaded', () => {
    new AIChat();
});