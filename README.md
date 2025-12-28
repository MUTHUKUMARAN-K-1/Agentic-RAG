# AgenticRAG

AgenticRAG is a Python-based intelligent assistant application that combines Retrieval Augmented Generation (RAG) with autonomous agent capabilities. The system leverages local LLM inference through Ollama, vector database search via ChromaDB, and real-time internet search to provide comprehensive and contextually relevant responses.

## Overview

This application implements an agentic RAG system that intelligently routes user queries to either:
- **Vector Database Search (RAG)**: For queries related to pre-loaded knowledge bases on LLM-powered autonomous agents, prompt engineering, and adversarial attacks on LLMs
- **Internet Search (Agent)**: For real-time information, general queries, and topics not covered in the knowledge base

The system uses a custom function-calling mechanism to determine the appropriate search strategy and provides natural, conversational responses without exposing internal search processes.

## Key Features

- **Local LLM Processing**: Utilizes Ollama for local LLM inference, eliminating the need for external API keys
- **Intelligent Query Routing**: Automatically determines whether to search the vector database or perform internet searches based on query content
- **Vector Database Integration**: Uses ChromaDB with custom Ollama embeddings for efficient semantic search
- **Real-time Information Retrieval**: Integrates DuckDuckGo search for current events and general knowledge
- **Modern Web Interface**: Streamlit-based UI with a dark theme inspired by modern AI assistants
- **Custom Function Calling**: Implements keyword-based function detection for tool selection

## Architecture

The application consists of three main components:

1. **Main Application (`main.py`)**: Streamlit interface, conversation management, and Ollama integration
2. **Database Operations (`upload.py`)**: ChromaDB management, embedding generation, and search functions
3. **Tools (`tools.py`)**: Tool definitions and function schemas

## Technologies

- **Python 3.9+**: Primary programming language
- **Ollama**: Local LLM inference engine
- **ChromaDB**: Vector database for semantic search
- **Streamlit**: Web application framework
- **LangChain**: AI framework for LLM integration
- **DuckDuckGo Search**: Internet search API
- **BeautifulSoup4**: Web scraping utilities

## Prerequisites

- Python 3.9 or higher
- Ollama installed and running
- Required Ollama models pulled

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/MadhavanAR/Agentic-RAG.git
   cd Agentic-RAG
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install and configure Ollama:
   - Download and install Ollama from https://ollama.ai
   - Ensure Ollama service is running
   - Pull required models:
     ```bash
     ollama pull llama3.2
     ollama pull nomic-embed-text
     ```

5. (Optional) Configure environment variables:
   Create a `.env` file in the project root:
   ```
   OLLAMA_MODEL=llama3.2
   OLLAMA_EMBEDDING_MODEL=nomic-embed-text
   ```

## Usage

1. Ensure Ollama is running:
   ```bash
   ollama list
   ```

2. Start the application:
   ```bash
   streamlit run main.py
   ```
   Or:
   ```bash
   python -m streamlit run main.py
   ```

3. Access the web interface:
   - The application will open in your default browser
   - Default URL: http://localhost:8501

4. Interact with the assistant:
   - Ask questions about LLM-powered agents, prompt engineering, or adversarial attacks
   - Query general topics for internet search results
   - The system automatically routes queries to the appropriate search method

## Database Setup

The application includes three pre-configured knowledge base collections:

- **Agent_Post**: Information on LLM-powered autonomous agents, task decomposition, memory management, and tool use
- **Prompt_Engineering_Post**: Resources on prompt engineering techniques, zero-shot/few-shot prompting, and chain-of-thought reasoning
- **Adv_Attack_LLM_Post**: Content on adversarial attacks on LLMs, jailbreak prompting, and mitigation strategies

To populate the database with custom content, modify the `upload.py` file and run:
```bash
python upload.py
```

## Configuration

### Model Selection

You can customize the models used by setting environment variables:

- `OLLAMA_MODEL`: Chat/completion model (default: `llama3.2`)
- `OLLAMA_EMBEDDING_MODEL`: Embedding model (default: `nomic-embed-text`)

### Recommended Models

**Chat Models:**
- `llama3.2`: Fast and efficient
- `llama3.1`: More capable, larger context
- `mistral`: Alternative high-performance model
- `phi3`: Lightweight option

**Embedding Models:**
- `nomic-embed-text`: Recommended for general use
- `all-minilm`: Lightweight alternative

## Project Structure

```
Agentic-RAG/
├── main.py              # Main Streamlit application
├── upload.py            # Database operations and search functions
├── tools.py             # Tool definitions
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
├── assets/             # Static assets (logos, images)
│   └── ChenAI.jpeg
└── db/                 # ChromaDB data directory
```

## Query Routing Logic

The system uses keyword-based routing to determine search strategy:

1. **Internet Search Priority**: Queries containing time-sensitive keywords (`latest`, `current`, `recent`, `news`, etc.) trigger internet search
2. **Database Search**: Queries matching domain-specific keywords route to appropriate collections:
   - Agent-related: `agent`, `autonomous`, `task decomposition`, etc.
   - Prompt engineering: `prompt`, `engineering`, `few-shot`, etc.
   - Adversarial attacks: `adversarial`, `attack`, `jailbreak`, etc.
3. **Fallback**: General queries not matching database topics default to internet search

## Development

### Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Include docstrings for functions and classes
- Maintain consistent indentation (4 spaces)

### Testing

Before deploying changes:
1. Test with various query types (database queries, internet queries, general queries)
2. Verify Ollama connection and model availability
3. Check database search functionality
4. Validate internet search integration

## Troubleshooting

### Ollama Connection Issues

- Ensure Ollama service is running: `ollama list`
- Verify models are installed: `ollama list`
- Check Ollama service status: `ollama serve`

### Database Errors

- Ensure ChromaDB directory has proper permissions
- Verify embedding model is available: `ollama list | grep nomic-embed-text`
- Re-populate database if needed: `python upload.py`

### Import Errors

- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.9+)
- Ensure virtual environment is activated

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Commit Message Guidelines

- Use clear, descriptive commit messages
- Reference issue numbers when applicable
- Follow conventional commit format when possible

## License

This project is open source and available for use and modification.

## Acknowledgments

- Ollama team for providing local LLM infrastructure
- ChromaDB for vector database capabilities
- Streamlit for the web framework
- LangChain community for AI integration tools

## Contact

For questions, issues, or contributions, please open an issue on the GitHub repository.

---

*Last updated: February 2025*
