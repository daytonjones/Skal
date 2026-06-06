import logging

logger = logging.getLogger(__name__)

ANTHROPIC_MODEL = 'claude-haiku-4-5-20251001'
OPENAI_MODEL = 'gpt-4o-mini'

# Tool definition — shared schema, formatted per-provider below
_RECIPE_TOOL_DESCRIPTION = (
    "Call this when suggesting a complete, specific mead recipe the user could "
    "actually brew. Do NOT call it for partial suggestions, ingredient tips, or "
    "general advice — only for a full recipe with honey, yeast, and batch size."
)

_RECIPE_TOOL_PARAMS = {
    "type": "object",
    "properties": {
        "name":         {"type": "string", "description": "Recipe name"},
        "batch_size":   {"type": "number", "description": "Batch size in gallons"},
        "honey_name":   {"type": "string", "description": "Honey variety, e.g. 'Wildflower'"},
        "honey_quantity": {"type": "string", "description": "Amount with unit, e.g. '12 lbs'"},
        "yeast":        {"type": "string", "description": "Yeast strain, e.g. 'Lalvin D-47'"},
        "additional_ingredients": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name":     {"type": "string"},
                    "quantity": {"type": "string"},
                },
                "required": ["name", "quantity"],
            },
            "description": "Any extra ingredients beyond honey and yeast",
        },
        "instructions": {"type": "string", "description": "Brewing notes and instructions"},
    },
    "required": ["name", "batch_size", "honey_name", "honey_quantity", "yeast"],
}

ANTHROPIC_TOOLS = [
    {
        "name": "suggest_recipe",
        "description": _RECIPE_TOOL_DESCRIPTION,
        "input_schema": _RECIPE_TOOL_PARAMS,
    }
]

OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "suggest_recipe",
            "description": _RECIPE_TOOL_DESCRIPTION,
            "parameters": _RECIPE_TOOL_PARAMS,
        },
    }
]


def call_ai(provider, api_key, system_prompt, messages):
    """
    Call the configured AI provider.

    messages: list of {role: 'user'|'assistant', content: str}
    Returns: (reply_text, input_tokens, output_tokens, recipe_data_or_None)
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
        tools=ANTHROPIC_TOOLS,
        tool_choice={"type": "auto"},
    )

    text_parts = [block.text for block in response.content if block.type == 'text']
    reply = ' '.join(text_parts).strip()

    recipe_data = None
    for block in response.content:
        if block.type == 'tool_use' and block.name == 'suggest_recipe':
            recipe_data = block.input
            break

    if not reply and recipe_data:
        reply = f"Here's a recipe for {recipe_data.get('name', 'your next mead')}! Save it below."

    return reply, response.usage.input_tokens, response.usage.output_tokens, recipe_data


def _call_openai(api_key, system_prompt, messages):
    import json
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=full_messages,
        max_tokens=1024,
        tools=OPENAI_TOOLS,
        tool_choice="auto",
    )
    choice = response.choices[0]
    reply = choice.message.content or ''

    recipe_data = None
    if choice.message.tool_calls:
        for tc in choice.message.tool_calls:
            if tc.function.name == 'suggest_recipe':
                try:
                    recipe_data = json.loads(tc.function.arguments)
                except (json.JSONDecodeError, ValueError):
                    logger.warning("Failed to parse OpenAI tool call arguments")
                break

    if not reply and recipe_data:
        reply = f"Here's a recipe for {recipe_data.get('name', 'your next mead')}! Save it below."

    usage = response.usage
    input_tokens = usage.prompt_tokens if usage else 0
    output_tokens = usage.completion_tokens if usage else 0
    return reply, input_tokens, output_tokens, recipe_data
