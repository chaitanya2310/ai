import re
import unicodedata
from guardrails_validate.topic_classifier import classify_topic
allowed_topics=["technology", "programming", "computer science", "artificial intelligence", "machine learning","data science", "python", "java", "sql"]
suspicious_patterns = [
    r"ignore\s+(all\s+)?(previous|prior|earlier)\s+instructions",
    r"reveal\s+(your\s+)?(system\s+prompt|hidden\s+instructions)",
    r"ignore\s+(all\s+)?rules",
    r"bypass\s+(your\s+)?(safety|security|restrictions)",
    r"act\s+as\s+if\s+you\s+have\s+no\s+restrictions"
]

suspicious_words=["ignore all previous instructions",
        "reveal your system prompt",
        "ignore all rules"]
def detect_prompt_injection(text: str):

    patterns = [
        # Attempts to override existing instructions
        r"(ignore|disregard|forget|override).{0,60}(previous|prior|earlier|all).{0,40}(instructions|rules)",

        # Attempts to access hidden prompts
        r"(reveal|show|print|repeat|disclose).{0,50}(system prompt|hidden instructions|developer message)",

        # Attempts to bypass restrictions
        r"(bypass|disable|remove).{0,40}(safety|security|restrictions|guardrails)",

        # Attempts to change the AI's identity or behavior
        r"(pretend|act|behave).{0,40}(unrestricted|no restrictions|without rules)",

        # Attempts to override the AI's role
        r"(you are now|from now on).{0,40}(admin|developer|unrestricted)"
    ]
    normalized_text = re.sub(r"\s+", " ", text.casefold())
    for pattern in patterns:
        if re.search(pattern,normalized_text,re.IGNORECASE):
            return True, "Prompt injection detected"
    return False, "No prompt injection detected"

def validate_input(user_input:str):
    """
    Validates the user input against the allowed topics and suspicious patterns."""
    #check input type
    if not isinstance(user_input,str):
        return False,"invalid input type"
    #normalize input
    text=unicodedata.normalize('NFKC',user_input).strip()
    #check for empty input
    if not text:
        return False,'please enter a topic'
    #check input length
    if len(text)>1000:
        return False,'input too long'
    if any(unicodedata.category(char)=='Cc'and char not in ("\n\t\r") for char in text):
        return False,"invalid characters detected"
    #advanced security checks
    is_suspicious,security_message=detect_prompt_injection(text)
    if is_suspicious:
        return False, security_message
    #check for suspicious patterns
    for pattern in suspicious_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False,'suspicious content detected'
    #check for suspicious words
    for word in suspicious_words:
        if word in text.lower():
            return False,'suspicious content detected'
    return True,"Input accepted"
    # semantic toipc validation
    valid,message = classify_topic(text)
    if not valid:
        return False,message
    return True, "Input accepted"

if __name__=="__main__":
    while True:

       n=input("enter a topic:")

       if n.lower()=="exit":
           break
       valid,message=validate_input(n)
       print(f"Input: {n}")
       print(f"Valid: {valid}, Message: {message}")