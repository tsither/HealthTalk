# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjNkMjMzOTQ5In0.eyJzdWIiOiI3Y2Y1ZGNhZi0yYmY3LTQzMGItODFmNC0zNjcxMWE2ODgzZDQiLCJ0eXBlIjoidXNlckFjY2Vzc1Rva2VuIiwidGVuYW50SWQiOiI0Y2JmY2YxZC02ODRmLTRlMmEtOGY5Yi0xNjQyNzdkNjk3Y2UiLCJ1c2VySWQiOiIwNjdjOGFmNi00ODRhLTRmYmMtYmU2Yy0xNDY1NTczMTdkZjkiLCJhcHBsaWNhdGlvbklkIjoiYTkyNmZlYmQtMjFlYS00ODdiLTg1ZjUtMzQ5NDA5N2VjODMzIiwicm9sZXMiOlsiRkVUQ0gtUk9MRVMtQlktQVBJIl0sInBlcm1pc3Npb25zIjpbIkZFVENILVBFUk1JU1NJT05TLUJZLUFQSSJdLCJhdWQiOiIzZDIzMzk0OS1hMmZiLTRhYjAtYjdlYy00NmY2MjU1YzUxMGUiLCJpc3MiOiJodHRwczovL2lkZW50aXR5Lm9jdG8uYWkiLCJpYXQiOjE3MjMyMDA1NzV9.I2ynUTDQcrEC4tN0Z88umYxrA-eDUNedPRncA8PL7gWM0wmlF2aKMN2CkvMm2NyLInWJXCrALzTMumy8S9NVcNVSCudtLooaYu2yWD_FCUd58LW_kjE7ZEUbdIysQ8sB2PE4wok65EuB57WcVlowZ6NmwuabZ6CM_5yG1_zatnM95cInUMUYuvUtEPndQ_KJ7Y6HAPSC3eRUoHXNC-DsuEztvnd1gJ_6b26aOuGykSqNuzamC6q8tKA9Kk2YcmvXkoPIdFsztFX2N8JQLaMg3eH4lVwxTn9c8GvQlNFjOd5E2FHUtXuhEfkFj8p1cCGo4SnJsrzFTZgKgXU3z8olZg

import json
from octoai.client import OctoAI
from octoai.text_gen import ChatMessage

def main():
    print("TEST")
    client = OctoAI()
    completion = client.text_gen.create_chat_completion(
    model="mixtral-8x22b-instruct",
    messages=[
        ChatMessage(
            role="system",
            content="Below is an instruction that describes a task. Write a response that appropriately completes the request.",
        ),
        ChatMessage(role="user", content="Write a blog about Seattle"),
    ],
    max_tokens=150,
    )

    print(json.dumps(completion.dict(), indent=2))

    
if __name__ == "__main__":    
    main()