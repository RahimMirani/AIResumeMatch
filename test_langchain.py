from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import os

load_dotenv()

def test_langchain_connection():
    try:
        # Initialize LangChain with Claude
        llm = ChatAnthropic(
            model="claude-3-opus-20240229",
            anthropic_api_key=os.getenv('CLAUDE_API_KEY')
        )
        
        # Test simple completion
        response = llm.invoke("Hello, what is your name?")
        
        print("\nResponse from Claude:")
        print(response.content)
        return True
        
    except Exception as e:
        print(f"\nError testing LangChain:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing LangChain connection...")
    success = test_langchain_connection()
    if success:
        print("\nAPI test successful! ✅")
    else:
        print("\nAPI test failed! ❌") 