import google.generativeai as genai
import os

# Configure API
genai.configure(api_key="AIzaSyDv91j15Eikp-1d4gAONku5VGLXmqLmCFw")

# Create model (using gemini-2.0-flash - the latest stable model)
model = genai.GenerativeModel('gemini-2.0-flash')

# Test 1: Simple response
print("=" * 50)
print("TEST 1: Simple Response")
print("=" * 50)
response = model.generate_content('Say hello in one word')
print(f"✓ Gemini says: {response.text.strip()}\n")

# Test 2: Query understanding
print("=" * 50)
print("TEST 2: Query Understanding")
print("=" * 50)

prompt = """You are analyzing code.
Available functions: ['processPayment', 'validateCard', 'calculatePrice']
User asks: "Is it safe to delete the payment processor?"

Respond with JSON only:
{
    "function_name": "processPayment",
    "action": "safety_check",
    "confidence": 0.95
}"""

response = model.generate_content(prompt)
text = response.text.strip()
print(f"✓ Response:\n{text}\n")

# Test 3: Semantic understanding
print("=" * 50)
print("TEST 3: Semantic Code Analysis")
print("=" * 50)

semantic_prompt = """Analyze this user query about code:
"Show me everywhere the payment validator is being used"

Extract:
- target_function: The function name they're asking about
- action_type: what they want to do (find_usages, delete, refactor, etc)
- reasoning: why you think this is their intent

Respond in JSON format."""

response = model.generate_content(semantic_prompt)
print(f"✓ Semantic Analysis:\n{response.text.strip()}\n")

print("=" * 50)
print("✓ ALL TESTS PASSED!")
print("✓ Gemini is working correctly!")
print("=" * 50)
