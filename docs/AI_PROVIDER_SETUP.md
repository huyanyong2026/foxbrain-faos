# VAFOX AI Provider Setup

VAFOX AI Assistant can run in two modes:

- Built-in mode: no API key required. Jarvis uses existing SAP summaries, knowledge, memory, graph and task data.
- AI provider mode: set an OpenAI-compatible API key. Jarvis first gathers internal evidence, then asks the model to write a clearer business answer with sources.

## Tencent Cloud Production

Keep real secrets only on the server:

```text
/opt/foxbrain/.env
```

Recommended DeepSeek configuration:

```env
AI_PROVIDER=deepseek
AI_BASE_URL=https://api.deepseek.com
AI_MODEL_NAME=deepseek-chat
DEEPSEEK_API_KEY=replace_with_real_key
AI_REQUEST_TIMEOUT=45
AI_MAX_TOKENS=900
```

OpenAI-compatible alternatives:

```env
AI_PROVIDER=openai
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL_NAME=gpt-4o-mini
OPENAI_API_KEY=replace_with_real_key
```

```env
AI_PROVIDER=qwen
AI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_MODEL_NAME=qwen-plus
DASHSCOPE_API_KEY=replace_with_real_key
```

## Verify

After restarting the service, open:

```text
/api/jarvis/status
```

Expected fields:

```json
{
  "ai_api": "configured",
  "ai_provider": "deepseek",
  "ai_model": "deepseek-chat"
}
```

Never commit real API keys, database passwords, SAP passwords or server private keys.
