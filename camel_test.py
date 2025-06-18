import os
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.agents import ChatAgent
from camel.models.model_manager import ModelProcessingError

# ✅ Ensure API key is set
if not os.getenv("MISTRAL_API_KEY"):
    raise EnvironmentError("MISTRAL_API_KEY is not set in environment variables.")

def create_mistral_agent():
    """
    Initializes a Mistral-powered ChatAgent without tools.
    """
    model = ModelFactory.create(
        model_platform=ModelPlatformType.MISTRAL,
        model_type=ModelType.MISTRAL_LARGE,  # or MISTRAL_SMALL for lighter usage
        model_config_dict={
            "temperature": 0.3,  # slight randomness for richer responses
            "top_p": 0.95,
            "max_tokens": 512
        }
    )
    return ChatAgent(model=model, tools=[])

def query_agent(agent, query):
    """
    Sends a query to the agent and returns the response content.
    Handles errors gracefully.
    """
    try:
        response = agent.step(query)
        return response.msgs[0].content
    except ModelProcessingError as e:
        return f"[Error] Mistral API issue: {e}"
    except Exception as ex:
        return f"[Unexpected Error] {ex}"

# ✅ Main execution
if __name__ == "__main__":
    agent = create_mistral_agent()
    print("Welcome to the Mistral AI Chat Interface!")
    print("Type 'exit' or 'quit' to end the conversation.")
    print("-" * 50)
    
    while True:
        user_input = input("\nEnter your query: ").strip()
        
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
            
        if not user_input:
            print("Please enter a valid query.")
            continue
            
        result = query_agent(agent, user_input)
        print("\nResponse:\n", result)
        print("-" * 50)
