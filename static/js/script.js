class AIChat {
    constructor() {
        this.currentSessionId = null;
        this.activeModel = 'deepseek';

        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.historyList = document.getElementById('historyList');
        this.newChatBtn = document.getElementById('newChatBtn');

        this.init();
    }

    init() {
        this.bindEvents();
        this.loadHistoryList();
    }

    bindEvents() {
        this.sendButton.onclick = () => this.sendMessage();
        this.messageInput.onkeydown = (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        };
        this.newChatBtn.onclick = () => this.startNewChat();

        const options = document.querySelectorAll('.model-option');
        options.forEach(opt => {
            opt.onclick = (e) => {
                // UI 切换
                options.forEach(o => o.classList.remove('active'));
                e.target.classList.add('active');
                // 变量同步
                this.activeModel = e.target.getAttribute('data-model');
                console.log("👆 点击切换模型:", this.activeModel);
            };
        });
    }

    async loadHistoryList() {
        try {
            const res = await fetch('/api/history');
            const data = await res.json();
            if(data.success) this.renderHistoryList(data.sessions);
        } catch(e) { console.error(e); }
    }

    renderHistoryList(sessions) {
        this.historyList.innerHTML = '';
        sessions.forEach(session => {
            const div = document.createElement('div');
            div.className = 'history-item';
            if(session.id === this.currentSessionId) div.classList.add('active');
            
            div.innerHTML = `<span>${session.title}</span><button class="delete-btn">×</button>`;
            
            div.onclick = (e) => {
                if(e.target.classList.contains('delete-btn')) {
                    this.deleteSession(session.id);
                } else {
                    this.switchSession(session.id);
                }
            };
            this.historyList.appendChild(div);
        });
    }

    async switchSession(sessionId) {
        this.currentSessionId = sessionId;
        this.chatMessages.innerHTML = '';
        this.loadHistoryList(); 

        const res = await fetch(`/api/history/${sessionId}`);
        const data = await res.json();
        if(data.success) {
            data.messages.forEach(msg => {
                this.appendMessage(msg.role, msg.content, msg.model);
            });
            this.scrollToBottom();
        }
    }

    startNewChat() {
        this.currentSessionId = null;
        this.chatMessages.innerHTML = '<div class="welcome-message"><h3>DeepGPT</h3><p>新对话</p></div>';
        this.loadHistoryList();
    }

    async sendMessage() {
        const text = this.messageInput.value.trim();
        if (!text) return;

        // 【关键修复】直接从 DOM 读取当前激活的模型，不依赖 this.activeModel 变量
        // 这样可以避免变量不同步的问题
        const activeOption = document.querySelector('.model-option.active');
        const currentModel = activeOption ? activeOption.getAttribute('data-model') : 'deepseek';

        console.log("🚀 真正发送的模型:", currentModel);

        this.appendMessage('user', text, null);
        this.messageInput.value = '';

        const loadingId = this.appendLoading(currentModel);

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    message: text,
                    model_type: currentModel, // 使用 DOM 读取的值
                    session_id: this.currentSessionId
                })
            });
            
            const data = await res.json();
            document.getElementById(loadingId)?.remove();

            if (data.success) {
                // 显示回复，确保使用后端返回的 model 字段（或者 fallback 到 currentModel）
                this.appendMessage('assistant', data.response, data.model || currentModel);
                
                if (!this.currentSessionId && data.session_id) {
                    this.currentSessionId = data.session_id;
                    this.loadHistoryList();
                }
            } else {
                this.appendMessage('assistant', "Error: " + data.error);
            }
        } catch (e) {
            document.getElementById(loadingId)?.remove();
            this.appendMessage('assistant', "网络错误");
        }
    }

    appendMessage(role, content, model) {
        document.querySelector('.welcome-message')?.remove();
        
        const div = document.createElement('div');
        div.className = `message ${role}`;
        
        // 头像逻辑 - 增强版匹配
        let imgUrl = '';
        if (role === 'user') {
            imgUrl = '/static/images/avatars/user.png';
        } else {
            const m = (model || '').toLowerCase();
            if (m.includes('qwen') || m.includes('千问')) imgUrl = '/static/images/avatars/qwen.png';
            else if (m.includes('kimi') || m.includes('moonshot')) imgUrl = '/static/images/avatars/kimi.png';
            else imgUrl = '/static/images/avatars/deepseek.png';
        }
        
        const avatarStyle = `background-image: url('${imgUrl}'); background-size: cover;`;
        
        div.innerHTML = `
            <div class="avatar" style="${avatarStyle}"></div>
            <div class="message-content">${marked.parse(content)}</div>
        `;

        this.chatMessages.appendChild(div);
        
        if (window.hljs) div.querySelectorAll('pre code').forEach(hljs.highlightElement);
        this.scrollToBottom();
    }

    appendLoading(model) {
        const id = 'loading-' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = 'message assistant';
        
        let imgUrl = '/static/images/avatars/deepseek.png';
        const m = (model || '').toLowerCase();
        if (m.includes('qwen')) imgUrl = '/static/images/avatars/qwen.png';
        else if (m.includes('kimi') || m.includes('moonshot')) imgUrl = '/static/images/avatars/kimi.png';
        
        div.innerHTML = `
            <div class="avatar" style="background-image: url('${imgUrl}'); background-size: cover;"></div>
            <div class="message-content">Thinking...</div>
        `;
        this.chatMessages.appendChild(div);
        this.scrollToBottom();
        return id;
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    async deleteSession(id) {
        if(!confirm('删除?')) return;
        await fetch(`/api/session/${id}`, {method: 'DELETE'});
        if(this.currentSessionId === id) this.startNewChat();
        else this.loadHistoryList();
    }
}

const app = new AIChat();