import webview
import threading
import subprocess
import sys
import os
import time
import socket
import json
import traceback

# 全局变量
flask_process = None
server_url = "http://127.0.0.1:5000"
CONFIG_FILE = "deepgpt_config.json"  # 配置文件路径

def load_config():
    """从配置文件加载API密钥"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
                # 设置环境变量
                if 'DEEPSEEK_API_KEY' in config:
                    os.environ['DEEPSEEK_API_KEY'] = config['DEEPSEEK_API_KEY']
                if 'QWEN_API_KEY' in config:
                    os.environ['QWEN_API_KEY'] = config['QWEN_API_KEY']
                # 添加KIMI API密钥加载
                if 'KIMI_API_KEY' in config:
                    os.environ['KIMI_API_KEY'] = config['KIMI_API_KEY']
                
                print(f"已加载配置: DeepSeek={'已设置' if config.get('DEEPSEEK_API_KEY') else '未设置'}, "
                      f"千问={'已设置' if config.get('QWEN_API_KEY') else '未设置'}, "
                      f"KIMI={'已设置' if config.get('KIMI_API_KEY') else '未设置'}")
                return True
        else:
            print(f"配置文件不存在: {os.path.abspath(CONFIG_FILE)}")
        return False
    except Exception as e:
        print(f"加载配置失败: {e}")
        return False

def check_api_keys():
    """检查是否配置了API密钥"""
    deepseek_key = os.getenv('DEEPSEEK_API_KEY', '')
    qwen_key = os.getenv('QWEN_API_KEY', '')
    kimi_key = os.getenv('KIMI_API_KEY', '')
    
    return bool(deepseek_key or qwen_key or kimi_key)

def is_port_in_use(port):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def wait_for_server(url, timeout=10):
    """等待服务器启动"""
    import requests
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/api/status")
            if response.status_code == 200:
                print(f"服务器已启动: {url}")
                return True
        except requests.RequestException:
            time.sleep(0.5)
    return False

def start_backend():
    """启动Flask后端服务"""
    global flask_process
    
    # 检查端口是否已被占用
    if is_port_in_use(5000):
        print("警告: 端口5000已被占用，可能是Flask服务已在运行")
        return True
    
    # 修改环境变量以禁用Flask调试模式
    env = os.environ.copy()
    env["FLASK_ENV"] = "production"
    
    # 启动Flask应用
    flask_process = subprocess.Popen(
        [sys.executable, 'app.py'],
        env=env,
        # 将Flask输出重定向到主进程
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    # 在后台读取Flask输出
    def read_output():
        for line in flask_process.stdout:
            print(f"[Flask] {line.strip()}")
    threading.Thread(target=read_output, daemon=True).start()
    
    # 等待服务器启动
    if not wait_for_server(server_url):
        print("错误: Flask服务未能在指定时间内启动")
        if flask_process:
            flask_process.terminate()
        return False
    return True

def show_api_key_error(window):
    """显示API密钥缺失错误"""
    window.evaluate_js("""
        alert('未找到有效的API密钥配置。请在deepgpt_config.json文件中配置至少一个API密钥后重新启动应用。');
    """)

def main():
    """主函数"""
    print("启动 DeepGPT 桌面应用...")
    
    # 尝试加载配置
    load_config()
    
    # 启动后端服务
    if not start_backend():
        print("无法启动Flask服务器")
        return
    
    # 创建主窗口
    window = webview.create_window(
        'DeepGPT - 多模型AI聊天界面', 
        server_url, 
        width=1000, 
        height=800
    )
    
    # 添加关闭事件
    window.events.closed += lambda: cleanup()
    
    # 检查API密钥状态，如果未设置则提示用户
    window.events.loaded += lambda: check_and_show_error(window)
    
    # 启动应用
    webview.start(debug=False)

def check_and_show_error(window):
    """检查API密钥状态并显示错误"""
    if not check_api_keys():
        # 延迟1秒显示提示，确保页面已完全加载
        def delayed_error():
            time.sleep(1)
            show_api_key_error(window)
        
        threading.Thread(target=delayed_error, daemon=True).start()

def cleanup():
    """清理资源"""
    global flask_process
    if flask_process:
        print("关闭Flask服务...")
        flask_process.terminate()
        flask_process = None

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"错误: {e}")
        traceback.print_exc()
    finally:
        cleanup()