# DeepGPT

![DeepGPT](https://img.shields.io/badge/DeepGPT-v0.2.0-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![Flask](https://img.shields.io/badge/Flask-2.3+-red)

DeepGPT 是一个集成多种大型语言模型的聊天应用程序，提供简单易用的 Web 界面，支持多模型切换和并行对比，让用户可以方便地与不同的 AI 模型进行对话交流。

## 🌟 特性

- 🚀 简洁美观的用户界面
- 🔄 实时对话体验
- 🔀 支持多种 AI 大模型（DeepSeek、通义千问、KIMI）
- 📊 多模型并行对比功能，同时查看三个模型的回答
- ✨ Markdown 语法渲染支持，包括代码高亮
- 📝 完整的对话历史记录
- 🔧 简单易用的 JSON 配置
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

创建一个 `deepgpt_config.json` 文件，格式如下：

```json
{
  "DEEPSEEK_API_KEY": "your_deepseek_api_key",
  "QWEN_API_KEY": "your_qwen_api_key",
  "KIMI_API_KEY": "your_kimi_api_key"
}
```

## 🚀 使用方法

1. 启动应用程序

```bash
python main.py
```

2. 应用程序将自动打开窗口，显示聊天界面

3. 使用方式有两种：

   **单模型对话**：在开始对话前，选择要使用的模型（DeepSeek、千问或KIMI），然后输入问题并发送。
   
   **多模型对比**：直接输入问题，三个模型将同时生成回答，显示在各自的区域，方便您进行对比分析。

## 🤖 支持的模型

### 当前支持

- **DeepSeek AI**：来自 DeepSeek 的强大语言模型
- **通义千问**：阿里云的智能对话引擎
- **KIMI**：月之暗面推出的KIMI大模型

## 🛠️ 开发计划

我们正在计划添加以下功能：

- [ ] 封装到 Electron 框架（或其他桌面应用框架）
- [ ] 界面主题切换（明/暗模式）
- [ ] 用户认证系统与会话管理
- [ ] 增强对话历史功能
- [ ] 文件上传与处理支持
- [ ] 图像生成与处理支持

## 🔧 项目结构

```
DeepGPT/
│
├── main.py                # 主程序入口
├── app.py                 # Flask 后端应用
├── deepgpt_config.json    # 配置文件
├── requirements.txt       # Python 依赖项
│
├── templates/             # HTML 模板
│   └── index.html         # 主页面
│
├── static/                # 静态资源
│   ├── css/
│   │   └── styles.css     # 样式表
│   └── js/
│       └── script.js      # JavaScript 脚本
│
└── README.md              # 项目说明文档
```

## 🤝 贡献

欢迎提交 Pull Request 或创建 Issue 来帮助改进这个项目！

## 📃 许可证

[MIT License](LICENSE)

## 📞 联系方式

如有任何问题或建议，请通过 GitHub Issues 与我们联系。
