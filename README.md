# DeepGPT

![DeepGPT](https://img.shields.io/badge/DeepGPT-v0.3.0-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![Flask](https://img.shields.io/badge/Flask-2.3+-red)

DeepGPT 是一个**上下文感知的混合模型对话系统**，允许你在同一个对话流中无缝切换不同的 AI 模型（DeepSeek、Qwen、Kimi）。它通过智能的上下文隔离机制，让多个模型像“专家评审团”一样协同工作，共同完成复杂的对话任务。

## 🌟 核心特性 (v0.3.0)

- 🧠 **混合专家协作 (MoE-like Experience)**：
    - 支持在单次对话中随意切换模型（例如：DeepSeek 写代码 -> Qwen 润色 -> Kimi 总结）。
    - 模型间共享上下文记忆，且不会发生身份混淆（通过 System Prompt 注入与历史标记技术实现）。
- 💾 **会话持久化**：
    - 基于 SQLite 的本地数据库，自动保存所有对话历史。
    - 支持创建新会话、切换历史会话、删除会话。
    - 页面刷新或重启程序后，聊天记录依然存在。
- 🎭 **动态身份识别**：
    - 聊天界面会根据实际生成回复的模型显示对应的头像（DeepSeek/Qwen/Kimi），清晰展示对话流的贡献者。
- 🚀 **简洁美观的 Web UI**：
    - 类似 ChatGPT 的侧边栏会话管理。
    - 完整的 Markdown 渲染与代码高亮支持。
- 🔧 **稳健的错误处理**：
    - 自动清洗 Emoji 等特殊字符，防止 API 兼容性报错。
    - 数据库自动初始化，开箱即用。

## 📥 安装

### 先决条件

- Python 3.7+
- pip (Python 包管理器)

### 安装步骤

1. 克隆仓库

```bash
git clone https://github.com/AstridStark25963/DeepGPT.git
cd DeepGPT
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 配置 API 密钥

在项目根目录创建一个 `deepgpt_config.json` 文件，格式如下：

```json
{
  "DEEPSEEK_API_KEY": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "QWEN_API_KEY": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "KIMI_API_KEY": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

## 🚀 使用方法

1. 启动应用程序

```bash
python main.py
```

2. 应用程序将自动打开窗口（或浏览器访问 `http://localhost:5000`）。

3. **混合会话玩法**：
   - **开始**：选择 **DeepSeek**，输入 "帮我写一个 Python 爬虫脚本"。
   - **接力**：点击顶部模型栏切换到 **Qwen**，输入 "请评价一下这段代码的安全性"。
   - **总结**：点击切换到 **Kimi**，输入 "把刚才的代码和评价整理成一份 Markdown 文档"。
   - *你会发现，三个模型在一个对话流中完美配合，且清楚知道上下文是谁生成的。*

## 🤖 支持的模型

- **DeepSeek V3**：擅长逻辑推理、代码生成。
- **通义千问 (Qwen-Turbo)**：擅长中文理解、创意写作、情感分析。
- **Kimi (Moonshot-v1)**：擅长长上下文阅读、归纳总结。

## 🛠️ 开发计划

- [ ] 流式输出 (Streaming Response) - 打字机效果
- [ ] AI 自动生成会话标题
- [ ] 界面主题切换（明/暗模式）
- [ ] 文件上传与 RAG (检索增强生成) 支持
- [ ] 封装到 Electron 框架（或其他桌面应用框架）
- [ ] 用户认证系统与会话管理
- [ ] 单对话重新生成、对话可复制功能
- [ ] 聊天重命名、置顶（收藏）、导出

## 🔧 项目结构

```
DeepGPT/
│
├── main.py                # 桌面应用入口 (PyWebview)
├── app.py                 # Flask 后端核心逻辑 & API 路由
├── deepgpt_config.json    # API 密钥配置文件 (需手动创建)
├── chat_history.db        # SQLite 数据库 (自动生成)
├── requirements.txt       # Python 依赖项
│
├── templates/             # HTML 模板
│   └── index.html         # 主页面结构
│
├── static/                # 静态资源
│   ├── css/
│   │   └── styles.css     # 样式表
│   ├── js/
│   │   └── script.js      # 前端交互逻辑
│   └── images/            # 图标与头像资源
│
├── test_compatibility.py  # (开发用) 模型兼容性测试脚本
└── README.md              # 项目说明文档
```

## 🤝 贡献

欢迎提交 Pull Request 或创建 Issue 来帮助改进这个项目！特别是如果你发现了其他模型间的有趣互动或兼容性问题。

## 📃 许可证

[MIT License](LICENSE)

## 📞 联系方式

如有任何问题或建议，请通过 GitHub Issues 与我们联系。
