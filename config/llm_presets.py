"""
Presets LLM optimisés pour analyses ESG.
L'utilisateur choisit le niveau de détail, pas les paramètres techniques.
"""

LLM_PRESETS = {
    "standard": {
        "temperature": 0.3,
        "max_tokens": 4000,
    },
    "detailed": {
        "temperature": 0.4,
        "max_tokens": 8000,
    }
}

RECOMMENDED_MODELS = {
    "openai": "gpt-4-turbo-preview",
    "anthropic": "claude-sonnet-4-20250514",
    "deepseek": "deepseek-chat"
}
