import streamlit as st
import ollama
import os
import dotenv
dotenv.load_dotenv()
import json
import re
import base64
from upload import search_db, Internet_search
import tools

tools = tools.tools

# Get Ollama model name from environment or use default
ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")

# Page config must be first Streamlit command
st.set_page_config(
    page_title="ChenAi",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Grok-like dark theme CSS
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Chat container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }
    
    /* Chat messages */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* User messages */
    .stChatMessage[data-testid="user"] {
        background: rgba(99, 102, 241, 0.15);
        border-left: 4px solid #6366f1;
    }
    
    /* Assistant messages */
    .stChatMessage[data-testid="assistant"] {
        background: rgba(34, 197, 94, 0.1);
        border-left: 4px solid #22c55e;
    }
    
    /* Chat input */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 24px;
        color: white;
        padding: 1rem 1.5rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
    }
    
    /* Text color */
    .stMarkdown, .stText {
        color: #e5e7eb;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #6366f1;
    }
    
    /* Title styling */
    .title-container {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
    }
    
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .logo-container img {
        max-width: 300px;
        height: auto;
        filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.3));
    }
    
    .title-container p {
        color: #9ca3af;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        background: rgba(34, 197, 94, 0.2);
        border: 1px solid #22c55e;
        border-radius: 20px;
        color: #22c55e;
        font-size: 0.9rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Load logo image
def load_logo(image_path):
    """Load and encode logo image to base64"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        print(f"Error loading logo: {e}")
        return None

logo_base64 = load_logo("assets/ChenAI.jpeg")
if logo_base64 is None:
    # Fallback to text if logo can't be loaded
    logo_html = '<h1 style="font-size: 3rem; font-weight: 700; background: linear-gradient(135deg, #6366f1 0%, #22c55e 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.5rem;">ChenAI</h1>'
else:
    logo_html = f'<img src="data:image/jpeg;base64,{logo_base64}" alt="ChenAI Logo" style="max-width: 300px; height: auto; filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.3));">'

# Check if Ollama is running
ollama_status = None
try:
    ollama.list()
    ollama_status = f"✅ Connected to Ollama (using model: {ollama_model})"
except Exception as e:
    ollama_status = f"⚠️ Ollama is not running. Please start Ollama first.\n\nError: {str(e)}\n\nTo install and start Ollama:\n1. Visit https://ollama.ai and install Ollama\n2. Run: ollama pull {ollama_model}\n3. Make sure Ollama is running"

def parse_function_call(response_text, user_query):
    """Parse function call from Ollama response"""
    # Look for explicit function call patterns like [FUNCTION:search_db]{...}
    function_pattern = r'\[FUNCTION:(\w+)\]\s*(\{.*?\})'
    matches = re.findall(function_pattern, response_text, re.DOTALL)
    
    if matches:
        function_name, args_text = matches[0]
        try:
            args = json.loads(args_text.strip())
            return function_name, args
        except:
            pass
    
    # Check for natural language indicators that suggest function calls
    response_lower = response_text.lower()
    user_lower = user_query.lower() if user_query else ""
    
    # Check if we need to search the database
    agent_keywords = ['agent', 'llm agent', 'autonomous agent', 'task decomposition', 'memory', 'tool use']
    prompt_keywords = ['prompt', 'prompting', 'zero-shot', 'few-shot', 'chain-of-thought', 'cot']
    attack_keywords = ['adversarial', 'attack', 'jailbreak', 'mitigation', 'white-box', 'black-box']
    
    if any(keyword in user_lower for keyword in agent_keywords):
        return "search_db", {"collection_name": "Agent_Post", "input_query": user_query, "n": 5}
    elif any(keyword in user_lower for keyword in prompt_keywords):
        return "search_db", {"collection_name": "Prompt_Engineering_Post", "input_query": user_query, "n": 5}
    elif any(keyword in user_lower for keyword in attack_keywords):
        return "search_db", {"collection_name": "Adv_Attack_LLM_Post", "input_query": user_query, "n": 5}
    
    # Check if internet search is needed
    if 'realtime' in response_lower or 'current' in response_lower or 'latest' in response_lower or 'recent' in response_lower:
        return "Internet_search", {"input": user_query}
    
    # If response suggests searching but no specific collection, try Agent_Post as default
    if 'search' in response_lower and 'database' in response_lower:
        return "search_db", {"collection_name": "Agent_Post", "input_query": user_query, "n": 5}
    
    return None, None

def run_conversation(user_input):
    try:
        # Get the latest user message
        user_query = None
        for msg in reversed(user_input):
            if msg.get("role") == "user":
                user_query = msg.get("content", "")
                break
        
        if not user_query:
            return "Please provide a question or query."
        
        # PROACTIVELY check if we should call a function based on user query
        # This ensures we search the database before generating a response
        user_lower = user_query.lower()
        function_name = None
        function_args = None
        
        # PRIORITY 1: Check for internet search needs FIRST (before database search)
        # These keywords indicate real-time information that should come from the web
        internet_keywords = ['latest', 'current', 'recent', 'now', 'today', 'news', 'realtime', 'breaking', 'update', 'trending', 'happening now']
        if any(word in user_lower for word in internet_keywords):
            function_name = "Internet_search"
            function_args = {"input": user_query}
        # PRIORITY 2: Check for database search keywords (only if not internet search)
        else:
            agent_keywords = ['agent', 'agents', 'llm agent', 'autonomous agent', 'task decomposition', 'memory', 'tool use', 'agentic']
            prompt_keywords = ['prompt', 'prompting', 'zero-shot', 'few-shot', 'chain-of-thought', 'cot', 'prompt engineering']
            attack_keywords = ['adversarial', 'attack', 'jailbreak', 'mitigation', 'white-box', 'black-box', 'adversarial attack']
            
            if any(keyword in user_lower for keyword in agent_keywords):
                function_name = "search_db"
                function_args = {"collection_name": "Agent_Post", "input_query": user_query, "n": 5}
            elif any(keyword in user_lower for keyword in prompt_keywords):
                function_name = "search_db"
                function_args = {"collection_name": "Prompt_Engineering_Post", "input_query": user_query, "n": 5}
            elif any(keyword in user_lower for keyword in attack_keywords):
                function_name = "search_db"
                function_args = {"collection_name": "Adv_Attack_LLM_Post", "input_query": user_query, "n": 5}
            # PRIORITY 3: If no database match, use internet search as fallback for general queries
            else:
                function_name = "Internet_search"
                function_args = {"input": user_query}
        
        # Convert messages to Ollama format (skip system messages, Ollama handles them differently)
        ollama_messages = []
        system_content = ""
        for msg in user_input:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                ollama_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        available_functions = {
        "search_db": search_db,
        "Internet_search": Internet_search,
        }
        
        # If we detected a function call, execute it first
        if function_name and function_name in available_functions:
            with st.spinner(f'Searching {function_args.get("collection_name", "database") if function_name == "search_db" else "internet"}...'):
                function_to_call = available_functions[function_name]
                
                try:
                    if function_name == "search_db":
                        function_response = function_to_call(
                            collection_name=function_args.get("collection_name", "Agent_Post"),
                            input_query=function_args.get("input_query", user_query),
                            n=function_args.get("n", 5),
                        )
                    elif function_name == "Internet_search":
                        function_response = function_to_call(
                            input=function_args.get("input", user_query),
                        )
                        # Internet search returns plain text, not JSON
                        func_content = function_response
                    
                    # Parse function response (only for database searches)
                    if function_name == "search_db":
                        try:
                            func_data = json.loads(function_response)
                            if "Error" in func_data:
                                return f"⚠️ Error from {function_name}: {func_data['Error']}"
                            else:
                                func_content = func_data.get("Data", function_response)
                        except:
                            func_content = function_response
                    # For Internet_search, func_content is already set above
                    
                    # Build enhanced prompt with function results
                    if system_content:
                        enhanced_system = f"""{system_content}

You have access to search results from the database. Use this information to provide a comprehensive answer."""
                        ollama_messages.insert(0, {
                            "role": "system",
                            "content": enhanced_system
                        })
                    
                    # Add function results to the conversation
                    if function_name == "search_db":
                        results_text = "\n\n".join(func_content) if isinstance(func_content, list) else str(func_content)
                        prompt_content = f"""User question: {user_query}

Here is relevant information from the database:

{results_text}

Please provide a comprehensive and helpful answer based on this information. Write naturally and directly, as if you know this information. Do NOT mention:
- "According to my search"
- "I found in the database"
- "From the database collection"
- Source citations or result numbers

Just provide the answer naturally and confidently."""
                    elif function_name == "Internet_search":
                        prompt_content = f"""User question: {user_query}

Here is information from the internet:

{func_content}

Please provide a comprehensive and helpful answer based on this information. Write naturally and directly, as if you know this information. Do NOT mention:
- "After conducting an internet search"
- "According to my search"
- Source citations like "(Source: [Result X] from Website)"
- Result numbers like "[Result 1]", "[Result 2]"
- Website names in citations

Just provide the answer naturally and confidently, using the information above."""
                    else:
                        prompt_content = f"Here is the result from {function_name}: {func_content}\n\nPlease provide a comprehensive and helpful answer based on this information."
                    
                    ollama_messages.append({
                        "role": "user",
                        "content": prompt_content
                    })
                    
                    # Get final response from Ollama with the function results
                    response = ollama.chat(
                        model=ollama_model,
                        messages=ollama_messages
                    )
                    return str(response['message']['content'])
                    
                except Exception as func_error:
                    return f"⚠️ Error calling {function_name}: {str(func_error)}"
        
        # If no function was detected proactively, just get a response from Ollama
        # Build enhanced prompt with system instructions
        if system_content:
            enhanced_system = f"""{system_content}

Available functions:
1. search_db(collection_name, input_query, n) - Search in database collections (Agent_Post, Prompt_Engineering_Post, Adv_Attack_LLM_Post)
2. Internet_search(input) - Search the internet for real-time information

When you need information, use these functions. For database searches, choose the appropriate collection based on the topic."""
            
            # Add system message at the beginning
            if ollama_messages:
                ollama_messages.insert(0, {
                    "role": "system",
                    "content": enhanced_system
                })
        
        # Get response from Ollama
        response = ollama.chat(
            model=ollama_model,
            messages=ollama_messages
        )
        
        return str(response['message']['content'])
            
    except Exception as e:
        error_msg = f"⚠️ **Error**: {str(e)}\n\n"
        error_msg += f"Please make sure:\n"
        error_msg += f"1. Ollama is running (check with: `ollama list`)\n"
        error_msg += f"2. The model '{ollama_model}' is installed (run: `ollama pull {ollama_model}`)\n"
        error_msg += f"3. For embeddings, install: `ollama pull nomic-embed-text`"
        return error_msg


# Title and branding with logo
st.markdown(f"""
<div class="title-container">
    <div class="logo-container">
        {logo_html}
    </div>
    <p>Your intelligent AI assistant powered by ChenAi</p>
</div>
""", unsafe_allow_html=True)

# Status badge
if ollama_status and "✅" in ollama_status:
    st.markdown(f'<div class="status-badge">{ollama_status}</div>', unsafe_allow_html=True)
else:
    st.error(ollama_status)

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": """You are ChenAi, a smart AI assistant. Your task is to answer the user's query based on information from three relevant database collections:
            1. `Agent_Post`: Contains information on LLM Powered Autonomous Agents, including task decomposition, memory, and tool use, as well as case studies like scientific discovery agents and generative agent simulations.
            2. `Prompt_Engineering_Post`: Contains detailed resources on prompt engineering, including techniques like zero-shot, few-shot, chain-of-thought prompting, and automatic prompt design, as well as the use of external APIs and augmented language models.
            3. `Adv_Attack_LLM_Post`: Contains content on adversarial attacks on LLMs, including text generation, white-box vs black-box attacks, jailbreak prompting, and various mitigation strategies.

            Attempt to search in the relevant database collection that matches the user's query. If no relevant information is found in the database, perform an internet search. 
            Also perform Internet search to get realtime data.
            
            IMPORTANT: When responding, write naturally and directly. Do NOT mention:
            - "According to my search"
            - "I found in the database"
            - "After conducting an internet search"
            - Source citations or result numbers
            - Just provide the answer confidently as if you know it.
         """},
        {"role": "assistant", "content": "Hello Buddy, How can I help you today?"}
    ]

previous_role = None

for msg in st.session_state.messages:
    if isinstance(msg, dict):
        role = msg["role"]
        content = msg["content"]

        if role == "system" or role == "tool" or ("tool_calls" in msg):
            continue

        if role == previous_role:
            continue

        with st.chat_message(role):
            st.markdown(content)

        previous_role = role

# Chat input with custom styling
if prompt := st.chat_input("Ask ChenAi anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            msg = run_conversation(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.markdown(msg)