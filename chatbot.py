import os
import time
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.agents import ChatAgent
from camel.models.model_manager import ModelProcessingError
import re

# ✅ Ensure API key is set
if not os.getenv("MISTRAL_API_KEY"):
    raise EnvironmentError("MISTRAL_API_KEY is not set in environment variables.")

# Create Mistral agent with retry logic
def create_mistral_agent():
    model = ModelFactory.create(
        model_platform=ModelPlatformType.MISTRAL,
        model_type=ModelType.MISTRAL_LARGE,
        model_config_dict={"temperature": 0.3, "top_p": 0.95, "max_tokens": 512}
    )
    return ChatAgent(model=model, tools=[])

agent = create_mistral_agent()

# ✅ Enhanced File Handling Function
def handle_file_operations(query):
    """Detects file creation requests and executes them with enhanced functionality."""
    # Pattern to match file creation requests
    file_pattern = r"create\s+(?:a|an)?\s+(\w+)\.(\w+)\s+(?:file|with|containing)?\s*(?:content)?\s*[:=]?\s*['\"](.*?)['\"]"
    match = re.search(file_pattern, query.lower())
    
    if match:
        try:
            filename, extension, content = match.groups()
            # Validate filename and extension
            if not filename or not extension:
                return "Invalid filename or extension provided."
            
            # Create full file path
            file_path = os.path.join(os.getcwd(), f"{filename}.{extension}")
            
            # Check if file already exists
            if os.path.exists(file_path):
                return f"File '{file_path}' already exists."
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write content to file
            with open(file_path, "w", encoding='utf-8') as file:
                file.write(content)
            
            return f"File '{file_path}' created successfully with the provided content."
            
        except Exception as e:
            return f"Error creating file: {str(e)}"
    
    return None

def is_rate_limit_error(error_msg):
    """Check if the error is a rate limit error."""
    rate_limit_indicators = [
        "Status 429",
        "rate limit",
        "capacity exceeded",
        "too many requests",
        "quota exceeded"
    ]
    return any(indicator.lower() in error_msg.lower() for indicator in rate_limit_indicators)

# ✅ Query Handling with Retry Logic
def query_agent(query, max_retries=3, initial_delay=1):
    """Handles file operations alongside Mistral responses with retry logic."""
    file_response = handle_file_operations(query)
    if file_response:
        return file_response

    retry_count = 0
    delay = initial_delay

    while retry_count < max_retries:
        try:
            response = agent.step(query)
            return response.msgs[0].content
        except ModelProcessingError as e:
            error_msg = str(e)
            
            if is_rate_limit_error(error_msg):
                if retry_count < max_retries - 1:
                    retry_count += 1
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                    continue
                else:
                    return "I'm currently experiencing high demand. Please try again in a few minutes."
            
            return f"[Error] Mistral API issue: {error_msg}"
        except Exception as ex:
            return f"[Unexpected Error] {str(ex)}"

# ✅ Run Chatbot in a Loop
if __name__ == "__main__":
    print("Welcome to the Chatbot! You can create files by saying something like:")
    print("'create a test.txt file with content: Hello World'")
    print("Type 'exit' or 'quit' to end the session.")
    
    while True:
        user_input = input("\nEnter your query: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Chatbot shutting down.")
            break

        result = query_agent(user_input)
        print("Response:", result)