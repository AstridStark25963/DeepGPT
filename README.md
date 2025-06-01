# DeepGPT

![DeepGPT](https://img.shields.io/badge/DeepGPT-v1.0-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![Flask](https://img.shields.io/badge/Flask-2.0+-red)

DeepGPT 是一个集成多种大型语言模型的聊天应用程序，提供简单易用的 Web 界面，支持多模型切换，让用户可以方便地与不同的 AI 模型进行对话交流。

## 🌟 特性

- 🚀 简洁美观的用户界面
- 🔄 实时对话体验
- 🔀 支持多种 AI 大模型（目前支持 DeepSeek、通义千问）
- 📝 完整的对话历史记录
- 🔧 简单易用的 API 配置
- 💨 快速响应，流畅体验

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
```bash
# Linux/macOS
export DEEPSEEK_API_KEY="your_deepseek_api_key"
export QWEN_API_KEY="your_qwen_api_key"

# Windows
set DEEPSEEK_API_KEY=your_deepseek_api_key
set QWEN_API_KEY=your_qwen_api_key
```

或者可以创建一个 `.env` 文件，并在其中输入 API 密钥，格式如下：

```properties
DEEPSEEK_API_KEY=your_deepseek_api_key
QWEN_API_KEY=your_qwen_api_key
```

## 🚀 使用方法

1. 启动应用程序
```bash
python app.py
```

2. 在浏览器中访问
```
http://localhost:5000
```

3. 在界面上选择要使用的 AI 模型，输入问题并开始对话！

## 🤖 支持的模型

### 当前支持
- **DeepSeek AI**：来自 DeepSeek 的强大语言模型
- **通义千问**：阿里云的智能对话引擎

### 计划支持
- **Kimi**：已有 API Key: `sk-WB0s79I7xgkCkrSVsQ5pp40k82nYpCup6T3E7YAT4PmoCMmW`

## 🛠️ 开发计划

我们正在计划添加以下功能：

- [ ] Markdown 语法渲染支持
- [ ] 集成更多大型语言模型
- [ ] 封装到 Electron 框架（或其他桌面应用框架）
- [ ] 界面优化与改进
- [ ] 用户认证系统与会话管理
- [ ] 增强对话历史功能
- [ ] 文件上传与处理支持
- [ ] 多模型对比功能（用户故事）

## 🔧 项目结构

```
DeepGPT/
│
├── app.py               # Flask 后端应用
├── requirements.txt     # Python 依赖项
├── templates/           # HTML 模板
│   └── index.html       # 主页面
└── README.md            # 项目说明文档
```

## 🤝 贡献

欢迎提交 Pull Request 或创建 Issue 来帮助改进这个项目！

## 📃 许可证

[MIT License](LICENSE)

## 📞 联系方式

如有任何问题或建议，请通过 GitHub Issues 与我们联系。
