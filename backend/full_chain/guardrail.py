from litellm import completion
import os
from guardrails import Guard
from guardrails.hub import ProfanityFree



# os.environ.get("ANYSCALE_API_KEY")
# os.environ.get("ANYSCALE_BASE_URL")

# # Create a Guard class
# guard = Guard().use(ProfanityFree())

# # Call the Guard to wrap the LLM API call
# validated_response = guard(
#     completion,
#     model="mistralai/Mistral-7B-Instruct-v0.1",
#     max_tokens=500,
#     api_key=os.environ.get("ANYSCALE_API_KEY"),
#     api_base=os.environ.get("ANYSCALE_BASE_URL"),
#     msg_history=[{"role": "user", "content": "hello"}]
# )

# Import Guard and Validator
from guardrails.hub import ProfanityFree
from guardrails import Guard

# Use the Guard with the validator
guard = Guard().use(ProfanityFree, on_fail="exception")

# Test passing response
guard.validate(
    """
    Director Denis Villeneuve's Dune is a visually stunning and epic adaptation of the classic science fiction novel.
    It is reminiscent of the original Star Wars trilogy, with its grand scale and epic storytelling.
    """
)

try:
    # Test failing response
    guard.validate(
        """
        He is such a dickhead and a fucking idiot.
        """
    )
except Exception as e:
    print(e)