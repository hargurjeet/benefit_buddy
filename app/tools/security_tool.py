import re

# Comprehensive list of adversarial signature phrases (case-insensitive)
INJECTION_SIGNATURES = [
    r"ignore\s+(?:all\s+)?(?:previous\s+)?instructions",
    r"ignore\s+(?:the\s+)?rules",
    r"ignore\s+(?:the\s+)?guidelines",
    r"you\s+are\s+now\s+a\b",
    r"act\s+as\s+a\b",
    r"\bjailbreak\b",
    r"\bdan\s+mode\b",
    r"\bdeveloper\s+mode\b",
    r"reveal\s+(?:your\s+)?system\s+prompt",
    r"reveal\s+(?:your\s+)?instructions",
    r"reveal\s+(?:your\s+)?rules",
    r"print\s+(?:your\s+)?instructions",
    r"what\s+is\s+your\s+system\s+prompt",
    r"what\s+is\s+your\s+prompt",
    r"do\s+not\s+follow\s+the\s+guidelines",
    r"bypass\s+the\s+constraints",
    r"override\s+instructions",
    r"disregard\s+instructions"
]

def detect_prompt_injection(user_input: str) -> bool:
    """
    Scans user input for standard prompt injection and instruction leakage signatures.
    
    Args:
        user_input: The raw message string from the user.
        
    Returns:
        True if an adversarial attempt is detected, else False.
    """
    if not user_input:
        return False
        
    normalized_input = user_input.lower()
    
    # Check each regex signature
    for signature in INJECTION_SIGNATURES:
        if re.search(signature, normalized_input):
            return True
            
    return False
