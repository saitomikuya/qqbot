## 使用说明
### 目录架构

```
qqbot/
├── bot.py
├── config.py
├── plugins/
│   ├── test_plugin/
│   │   ├── __init__.py
│   │   └── test_plugin.py
│   └── plugin2/
│   └── plugin3/
│   └── ...
```
### 配置环境
```bash
pip install -r requirements.txt
```
### 配置机器人参数
修改`config.py`文件。
```python
# config.py
BOT_QQ = 11051480  # 替换为QQ机器人QQ号
WS_SERVER = 'ws://127.0.0.1:3001'  # WebSocket服务器地址
```
### 配置插件参数
若有不需要使用的插件，请删除这个插件文件夹。部分插件使用前需要配置参数。
#### 防撤回插件
修改`qqbot/plugins/anti_recall_plugin/anti_recall_plugin.py`文件第10行代码。
```python
self.NOTIFY_QQ = 4499149 # 替换为你要接受撤回消息的QQ号
```
#### ChatGPT插件
1. 修改`qqbot/plugins/chatgpt_plugin/chatgpt_plugin.py`文件第8-16行代码，填写 Azure OpenAI API 或 Google Gemini API 参数。
```python
# Azure OpenAI API
self.azure_url = 'https://YOUR_RESOURCE_NAME.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT_NAME'
self.azure_api_key = 'YOUR_API_KEY'
self.azure_api_version = '2024-02-01'
self.model = 'gpt-4o-2024-05-13'  # 部署的模型版本名称

# Google Gemini API
self.api_key = 'YOUR_API_KEY'
self.api_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent'
```
2. 修改`qqbot/plugins/chatgpt_plugin/chatgpt_plugin.py`文件第32-33行代码，选择你要使用 Azure OpenAI （`get_chatgpt_response(question)`）还是 Google Gemini （`get_gemini_response`），将不用一行的注释。
```python
#answer = await self.get_chatgpt_response(question)
answer = await self.get_gemini_response(question)
```
#### 每日消息插件
修改`qqbot/plugins/daily_message_plugin/daily_message_plugin.py`文件第7行代码。
```python
self.group_id = 723609186  # 替换为要发送每日消息的 QQ 群号
```
#### 复读机插件
修改`qqbot/plugins/daily_message_plugin/daily_message_plugin.py`文件第6行代码。
```python
self.target_qqs = ['252737224', '601904795', '136208872', '1318242449']  # 要复读消息的QQ号列表
```
### 启动QQ机器人
完成所有配置后，双击`qqbot/qqbot.py`，即可启动机器人。
如果加载了`test_plugin`插件，尝试在群内发送“test”，机器人发送“OK”即表示QQ机器人已经正常运行了。
