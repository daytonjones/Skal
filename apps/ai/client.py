import logging

logger = logging.getLogger(__name__)

ANTHROPIC_MODEL = 'claude-haiku-4-5-20251001'
OPENAI_MODEL = 'gpt-4o-mini'


def call_ai(provider, api_key, system_prompt, messages):
    """
    Call the configured AI provider.

    messages: list of {role: 'user'|'assistant', content: str}
    Returns: (reply_text, input_tokens, output_tokens)
    """
    if provider == 'anthropic':
        return _call_anthropic(api_key, system_prompt, messages)
    elif provider == 'openai':
        return _call_openai(api_key, system_prompt, messages)
    else:
        raise ValueError(f"Unknown AI provider: {provider}")


def _call_anthropic(api_key, system_prompt, messages):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )
    reply = next(block.text for block in response.content if block.type == 'text')
    return reply, response.usage.input_tokens, response.usage.output_tokens


def _call_openai(api_key, system_prompt, messages):
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=full_messages,
        max_tokens=1024,
    )
    reply = response.choices[0].message.content or ''
    usage = response.usage
    input_tokens = usage.prompt_tokens if usage else 0
    output_tokens = usage.completion_tokens if usage else 0
    return reply, input_tokens, output_tokens
