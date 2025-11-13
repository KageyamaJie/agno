#!/usr/bin/env python3
"""
Simplified documentation generator
"""

from pathlib import Path

def generate_docs():
    docs = []
    
    # Title
    docs.append("# Agno Framework - Complete API Documentation\n")
    docs.append("This comprehensive documentation covers all public APIs, functions, and components of the Agno framework.\n")
    
    # Table of Contents
    docs.append("## Table of Contents\n")
    docs.append("1. Introduction to Agno\n")
    docs.append("2. Core Concepts\n")
    docs.append("3. Agent API Reference\n")
    docs.append("4. Team API Reference\n")
    docs.append("5. Workflow API Reference\n")
    docs.append("6. Knowledge & VectorDB APIs\n")
    docs.append("7. Database APIs\n")
    docs.append("8. Model APIs\n")
    docs.append("9. Tool APIs\n")
    docs.append("10. AgentOS API\n")
    docs.append("11. Memory & Session Management\n")
    docs.append("12. Guardrails & Security\n")
    docs.append("13. Cookbook Examples\n")
    docs.append("14. Best Practices\n")
    
    # Section 1: Introduction
    docs.append("\n# 1. Introduction to Agno\n")
    docs.append("""
Agno is a multi-agent framework, runtime and control plane built for speed, privacy, and scale.
It provides tools for building:

- **Agents** with memory, knowledge, session management, and advanced features
- **Multi-Agent Teams** that operate autonomously under a team leader
- **Step-based Workflows** for controlled, deterministic execution
- **AgentOS** - A ready-to-use FastAPI app for serving agents in production

## Key Features

- **Model Agnostic**: Works with any model provider
- **Type Safe**: Enforce structured I/O through input_schema and output_schema
- **Persistent Storage**: Give your Agents, Teams, and Workflows a database
- **Agentic RAG**: Connect to 20+ vector stores with hybrid search + reranking
- **Human-in-the-Loop**: Native support for confirmations and manual overrides
- **Guardrails**: Built-in safeguards for validation and security
- **MCP Integration**: First-class support for Model Context Protocol
- **100+ Toolkits**: Built-in toolkits with thousands of tools
""")
    
    # Section 2: Core Concepts
    docs.append("\n# 2. Core Concepts\n")
    docs.append("""
## 2.1 Agents

An Agent is the fundamental building block in Agno. It represents an AI assistant that can:
- Process user queries
- Use tools to perform actions
- Access knowledge bases
- Maintain conversation history
- Store and recall user memories

## 2.2 Teams

A Team is a collection of Agents (or sub-teams) that work together to accomplish tasks.
Teams operate autonomously with a team leader that maintains shared state and context.

## 2.3 Workflows

Workflows are step-based execution systems for controlled, deterministic execution.
Steps can be Agents, Teams, or regular Python functions that run sequentially,
in parallel, in loops, branches, or conditionally.

## 2.4 Knowledge

Knowledge is Agno's way of providing Agents with information they can search at runtime.
It connects to 20+ vector stores with hybrid search and reranking capabilities.

## 2.5 Sessions

Sessions track conversations and maintain state across multiple interactions.
Each session can have its own state, history, and metadata.

## 2.6 Memory

Memory allows Agents to store insights and facts about users that persist across sessions.
This enables personalization and context retention.
""")
    
    # Section 3: Agent API
    docs.append("\n# 3. Agent API Reference\n")
    docs.append("""
## 3.1 Agent Class

The `Agent` class is the core component for creating AI assistants.

### Import

```python
from agno.agent import Agent
```

### Basic Agent Creation

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    instructions="You are a helpful assistant",
    markdown=True,
)
```

### Agent Parameters

#### Core Parameters

- **model** (Model, required): The language model to use
- **name** (str, optional): Name of the agent
- **id** (str, optional): Unique identifier (auto-generated if not set)
- **instructions** (str | list[str], optional): Instructions for the agent
- **description** (str, optional): Description of the agent's purpose
- **markdown** (bool, default=False): Enable markdown formatting in responses

#### Session Parameters

- **user_id** (str, optional): Default user ID for this agent
- **session_id** (str, optional): Default session ID (auto-generated if not set)
- **session_state** (dict, optional): Default session state
- **add_session_state_to_context** (bool, default=False): Add session state to context
- **enable_agentic_state** (bool, default=False): Give agent tools to update state
- **cache_session** (bool, default=False): Cache session in memory

#### History Parameters

- **add_history_to_context** (bool, default=False): Add conversation history to context
- **num_history_runs** (int, optional): Number of history runs to include
- **search_session_history** (bool, default=False): Search previous sessions

#### Knowledge Parameters

- **knowledge** (Knowledge, optional): Knowledge base to use
- **search_knowledge** (bool, default=False): Enable knowledge search
- **num_documents** (int, optional): Number of documents to retrieve
- **rerank** (bool, default=False): Enable reranking of results

#### Tool Parameters

- **tools** (list[Toolkit | Function], optional): Tools available to the agent
- **tool_choice** (str, optional): Tool selection strategy

#### Memory Parameters

- **memory** (MemoryManager, optional): Memory manager for user memories
- **add_memories_to_context** (bool, default=False): Add memories to context

#### Output Parameters

- **input_schema** (BaseModel, optional): Input validation schema
- **output_schema** (BaseModel, optional): Output validation schema

#### Other Parameters

- **db** (BaseDb, optional): Database for persistence
- **guardrails** (list[BaseGuardrail], optional): Guardrails for validation
- **reasoning** (bool, default=False): Enable reasoning mode
- **show_tool_calls** (bool, default=True): Show tool calls in output
- **debug_mode** (bool, default=False): Enable debug logging

### Agent Methods

#### run()

Execute the agent synchronously.

```python
response = agent.run("What is the weather today?")
print(response.content)
```

**Parameters:**
- **message** (str | Message | list[Message]): The input message
- **user_id** (str, optional): User ID for this run
- **session_id** (str, optional): Session ID for this run
- **stream** (bool, default=False): Stream the response
- ****kwargs**: Additional parameters

**Returns:** RunOutput object with content, messages, and metadata

#### arun()

Execute the agent asynchronously.

```python
response = await agent.arun("What is the weather today?")
print(response.content)
```

**Parameters:** Same as run()

**Returns:** RunOutput object

#### print_response()

Print the agent's response with formatting.

```python
agent.print_response("Hello!", stream=True)
```

**Parameters:**
- **message** (str): The input message
- **stream** (bool, default=False): Stream the response
- ****kwargs**: Additional parameters
""")
    
    # Add cookbook examples
    cookbook_path = Path("/workspace/cookbook/getting_started")
    if cookbook_path.exists():
        docs.append("\n## 3.2 Agent Examples from Cookbook\n")
        
        example_files = [
            ("01_basic_agent.py", "Basic Agent"),
            ("02_agent_with_tools.py", "Agent with Tools"),
            ("03_agent_with_knowledge.py", "Agent with Knowledge"),
            ("05_structured_output.py", "Structured Output"),
        ]
        
        for filename, title in example_files:
            filepath = cookbook_path / filename
            if filepath.exists():
                docs.append(f"\n### {title}\n")
                docs.append(f"**File:** `{filename}`\n\n")
                docs.append("```python\n")
                docs.append(filepath.read_text())
                docs.append("\n```\n")
    
    # Section 4: Team API
    docs.append("\n# 4. Team API Reference\n")
    docs.append("""
## 4.1 Team Class

The `Team` class enables multiple agents to work together autonomously.

### Import

```python
from agno.team.team import Team
```

### Basic Team Creation

```python
from agno.agent import Agent
from agno.team.team import Team
from agno.models.openai import OpenAIChat

# Create specialized agents
web_agent = Agent(
    name="Researcher",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
)

writer_agent = Agent(
    name="Writer",
    model=OpenAIChat(id="gpt-4o"),
)

# Create team
team = Team(
    members=[web_agent, writer_agent],
    model=OpenAIChat(id="gpt-4o"),
    instructions="Research and write articles",
)
```

### Team Parameters

- **members** (list[Agent | Team], required): List of agents or sub-teams
- **model** (Model, required): Model for the team leader
- **name** (str, optional): Name of the team
- **id** (str, optional): Unique identifier
- **instructions** (str | list[str], optional): Instructions for the team
- **db** (BaseDb, optional): Database for persistence
- **show_members_responses** (bool, default=True): Show individual agent responses
- **markdown** (bool, default=False): Enable markdown formatting

### Team Methods

#### run()

Execute the team synchronously.

```python
response = team.run("Research and write about AI")
print(response.content)
```

#### arun()

Execute the team asynchronously.

```python
response = await team.arun("Research and write about AI")
```
""")
    
    # Add team cookbook example
    team_file = cookbook_path / "17_agent_team.py"
    if team_file.exists():
        docs.append("\n### Team Example from Cookbook\n")
        docs.append("```python\n")
        docs.append(team_file.read_text())
        docs.append("\n```\n")
    
    # Section 5: Workflow API
    docs.append("\n# 5. Workflow API Reference\n")
    docs.append("""
## 5.1 Workflow Class

The `Workflow` class enables step-based, deterministic execution.

### Import

```python
from agno.workflow.workflow import Workflow
```

### Basic Workflow Creation

```python
from agno.workflow.workflow import Workflow
from agno.db.sqlite import SqliteDb

async def my_workflow(session_state, input_data: str):
    # Step 1: Process input
    result1 = await agent1.arun(input_data)
    
    # Step 2: Process result
    result2 = await agent2.arun(result1.content)
    
    return result2.content

workflow = Workflow(
    name="My Workflow",
    steps=my_workflow,
    db=SqliteDb(db_file="tmp/workflow.db"),
)
```

### Workflow Parameters

- **name** (str, required): Name of the workflow
- **steps** (callable, required): Function defining workflow steps
- **db** (BaseDb, optional): Database for persistence
- **description** (str, optional): Description of the workflow
- **session_state** (dict, optional): Initial session state

### Workflow Methods

#### run()

Execute the workflow synchronously.

```python
result = workflow.run(input_data="test")
```

#### arun()

Execute the workflow asynchronously.

```python
result = await workflow.arun(input_data="test")
```
""")
    
    # Add workflow cookbook example
    workflow_file = cookbook_path / "19_blog_generator_workflow.py"
    if workflow_file.exists():
        docs.append("\n### Workflow Example from Cookbook\n")
        docs.append("```python\n")
        docs.append(workflow_file.read_text())
        docs.append("\n```\n")
    
    # Continue with other sections...
    docs.append("\n# 6. Knowledge & VectorDB APIs\n")
    docs.append("""
## 6.1 Knowledge Class

The `Knowledge` class provides agentic RAG capabilities.

### Import

```python
from agno.knowledge.knowledge import Knowledge
```

### Basic Knowledge Setup

```python
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.knowledge.embedder.openai import OpenAIEmbedder

knowledge = Knowledge(
    vector_db=LanceDb(
        uri="tmp/lancedb",
        table_name="knowledge_base",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
)
```

### Knowledge Methods

#### add_documents()

Add documents to the knowledge base.

```python
knowledge.add_documents([
    "Document 1 content",
    "Document 2 content",
])
```

#### add_urls()

Add documents from URLs.

```python
knowledge.add_urls([
    "https://example.com/doc1",
    "https://example.com/doc2",
])
```

#### search()

Search the knowledge base.

```python
results = knowledge.search("query", num_documents=5)
```
""")
    
    docs.append("\n# 7. Database APIs\n")
    docs.append("""
## 7.1 Database Overview

Agno supports multiple database backends for persistence.

### Supported Databases

- **PostgreSQL** (Production recommended)
- **SQLite** (Development only)
- **MongoDB**
- **MySQL**
- **Redis**
- **DynamoDB**
- **Firestore**
- **SingleStore**
- **SurrealDB**
- **JSON files**
- **In-memory**

### PostgreSQL (Production)

```python
from agno.db.postgres import PostgresDb

db = PostgresDb(
    db_url="postgresql+psycopg://user:password@localhost:5432/dbname"
)

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    db=db,
)
```

### SQLite (Development)

```python
from agno.db.sqlite import SqliteDb

db = SqliteDb(db_file="tmp/agents.db")

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    db=db,
)
```
""")
    
    docs.append("\n# 8. Model APIs\n")
    docs.append("""
## 8.1 Model Overview

Agno is model-agnostic and supports 30+ model providers.

### Supported Providers

- OpenAI
- Anthropic (Claude)
- Google (Gemini)
- AWS Bedrock
- Azure OpenAI
- Groq
- Together AI
- Fireworks
- Mistral
- Cohere
- Perplexity
- xAI
- And more...

### OpenAI

```python
from agno.models.openai import OpenAIChat

model = OpenAIChat(id="gpt-4o")
agent = Agent(model=model)
```

### Anthropic Claude

```python
from agno.models.anthropic import Claude

model = Claude(id="claude-sonnet-4-5")
agent = Agent(model=model)
```
""")
    
    docs.append("\n# 9. Tool APIs\n")
    docs.append("""
## 9.1 Tool Overview

Agno provides 100+ built-in toolkits with thousands of tools.

### Built-in Toolkits

- **Web Search**: DuckDuckGo, Google Search, Exa
- **Finance**: YFinance, Financial Modeling Prep
- **Code**: GitHub, GitLab, Code Execution
- **Data**: SQL, CSV, Excel, JSON
- **APIs**: REST, GraphQL
- **Media**: Image generation, Video processing
- **And many more...**

### Using Toolkits

```python
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        DuckDuckGoTools(),
        YFinanceTools(stock_price=True, company_info=True),
    ],
)
```

### Custom Tools

Create custom tools using the `Function` class:

```python
from agno.tools.function import Function
from pydantic import BaseModel, Field

class WeatherInput(BaseModel):
    city: str = Field(..., description="City name")

def get_weather(city: str) -> str:
    '''Get weather for a city'''
    return f"Weather in {city}: Sunny, 72°F"

weather_tool = Function(
    name="get_weather",
    description="Get weather information for a city",
    fn=get_weather,
    input_schema=WeatherInput,
)

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[weather_tool],
)
```
""")
    
    docs.append("\n# 10. AgentOS API\n")
    docs.append("""
## 10.1 AgentOS Overview

AgentOS is a FastAPI-based runtime for serving agents in production.

### Basic Setup

```python
from agno.os import AgentOS
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.postgres import PostgresDb

# Create agents
agent = Agent(
    name="My Agent",
    model=OpenAIChat(id="gpt-4o"),
    db=PostgresDb(db_url="..."),
)

# Create AgentOS
agent_os = AgentOS(agents=[agent])
app = agent_os.get_app()

# Run
if __name__ == "__main__":
    agent_os.serve(app="my_app:app", reload=True)
```

### AgentOS Parameters

- **agents** (list[Agent], optional): List of agents
- **teams** (list[Team], optional): List of teams
- **workflows** (list[Workflow], optional): List of workflows
- **db** (BaseDb, optional): Shared database
- **description** (str, optional): Description of the OS

### API Endpoints

#### Run Agent
```
POST /agents/{agent_id}/runs
```

#### Run Team
```
POST /teams/{team_id}/runs
```

#### Run Workflow
```
POST /workflows/{workflow_id}/runs
```
""")
    
    docs.append("\n# 11. Memory & Session Management\n")
    docs.append("""
## 11.1 Memory Management

Memory allows agents to store and recall user-specific information.

### Basic Memory Setup

```python
from agno.memory import MemoryManager

memory = MemoryManager()

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    memory=memory,
    add_memories_to_context=True,
)
```

## 11.2 Session Management

Sessions track conversations and maintain state.

### Using Sessions

```python
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    db=SqliteDb(db_file="tmp/agents.db"),
    user_id="user-123",
    session_id="session-456",
    add_history_to_context=True,
    num_history_runs=5,
)

# Session state is automatically managed
response = agent.run("Hello!")
```
""")
    
    docs.append("\n# 12. Guardrails & Security\n")
    docs.append("""
## 12.1 Guardrails Overview

Guardrails provide validation and security for agents.

### Built-in Guardrails

- **PII Detection**: Detect personally identifiable information
- **Prompt Injection**: Detect prompt injection attacks
- **OpenAI Moderation**: Use OpenAI's moderation API

### Using Guardrails

```python
from agno.guardrails.pii import PIIDetection
from agno.guardrails.prompt_injection import PromptInjectionDetection

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    guardrails=[
        PIIDetection(),
        PromptInjectionDetection(),
    ],
)
```
""")
    
    docs.append("\n# 13. Cookbook Examples\n")
    docs.append("""
The Agno cookbook contains hundreds of examples demonstrating various features and use cases.
All examples are available in the `/cookbook` directory.

## 13.1 Getting Started Examples

The getting started cookbook provides step-by-step examples:

1. **Basic Agent** - Creating your first agent
2. **Agent with Tools** - Adding web search and other tools
3. **Agent with Knowledge** - Setting up RAG with knowledge bases
4. **Write Your Own Tool** - Creating custom tools
5. **Structured Output** - Using Pydantic models for type-safe outputs
6. **Agent with Storage** - Adding database persistence
7. **Agent State** - Managing session state
8. **Agent Context** - Dynamic context management
9. **Agent Session** - Session management
10. **User Memories** - Storing and recalling user information
11. **Retry Function Calls** - Error handling and retries
12. **Human-in-the-Loop** - User confirmation workflows
13. **Image Agent** - Multimodal image processing
14. **Generate Image** - Image generation
15. **Generate Video** - Video generation
16. **Audio Input/Output** - Audio processing
17. **Agent Team** - Multi-agent collaboration
18. **Research Agent** - Advanced research workflows
19. **Blog Generator Workflow** - Complete workflow example

## 13.2 Advanced Agent Examples

### Agentic Search
- Agentic RAG with hybrid search
- RAG with reasoning capabilities
- Infinity reranker integration

### Async Operations
- Basic async agent execution
- Concurrent tool calls
- Parallel agent execution
- Async streaming

### Caching
- Model response caching
- Async caching
- Stream caching

### Context Management
- Dynamic instructions
- Few-shot learning
- Location-aware instructions
- DateTime context

### Custom Logging
- Custom logging handlers
- File logging
- Advanced logging configurations

### Events Handling
- Basic agent events
- Reasoning agent events
- Custom event handlers

### Multimodal Agents
- Image processing
- Video generation
- Audio processing
- File handling

### RAG Implementation
- Basic RAG setup
- Advanced RAG patterns
- Knowledge base management

### Session Management
- Session state
- Session history
- Session summaries

### State Management
- Agent state
- Workflow state
- Team state

## 13.3 Database Examples

Examples for all supported databases:
- PostgreSQL
- SQLite
- MongoDB
- MySQL
- Redis
- DynamoDB
- Firestore
- SingleStore
- SurrealDB
- JSON files
- In-memory storage

## 13.4 Model Examples

Examples for all supported model providers:
- OpenAI
- Anthropic (Claude)
- Google (Gemini)
- AWS Bedrock
- Azure OpenAI
- Groq
- Together AI
- Fireworks
- Mistral
- Cohere
- Perplexity
- xAI
- And many more...

## 13.5 Tool Examples

Examples for built-in toolkits:
- Web Search (DuckDuckGo, Google, Exa)
- Finance (YFinance, Financial Modeling Prep)
- Code (GitHub, GitLab)
- Data (SQL, CSV, Excel)
- APIs (REST, GraphQL)
- Media (Image, Video, Audio)
- MCP Tools

## 13.6 Team Examples

- Basic team setup
- Multi-agent coordination
- Team with shared state
- Nested teams

## 13.7 Workflow Examples

- Sequential workflows
- Parallel execution
- Conditional steps
- Loops and branches
- Complex multi-step workflows

## 13.8 Knowledge Examples

- Setting up knowledge bases
- Adding documents
- URL ingestion
- PDF processing
- Hybrid search
- Reranking
- All vector database integrations

## 13.9 Memory Examples

- User memory management
- Memory search
- Memory updates
- Memory deletion
- Memory in context

## 13.10 Guardrails Examples

- PII detection
- Prompt injection detection
- OpenAI moderation
- Custom guardrails

## 13.11 Integration Examples

- Discord integration
- Slack integration
- Custom integrations

## 13.12 Evaluation Examples

- Accuracy evaluation
- Performance benchmarking
- Reliability testing
- Custom evaluation metrics
""")
    
    docs.append("\n# 14. Best Practices\n")
    docs.append("""
## 14.1 Agent Creation

**CRITICAL: Never create agents in loops**

```python
# ❌ WRONG - Recreates agent every time (significant overhead)
for query in queries:
    agent = Agent(...)  # DON'T DO THIS
    
# ✅ CORRECT - Create once, reuse
agent = Agent(...)
for query in queries:
    agent.run(query)
```

## 14.2 Database Selection

- **Development**: Use SQLiteDb for simplicity
- **Production**: Always use PostgresDb for scalability and reliability

## 14.3 Knowledge Base Setup

Always set `search_knowledge=True` when using Knowledge:

```python
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    knowledge=knowledge,
    search_knowledge=True,  # Critical: enables agentic RAG
    instructions="Use knowledge base, cite sources"
)
```

## 14.4 Structured Output

Use `output_schema` for predictable, composable behavior:

```python
from pydantic import BaseModel

class Result(BaseModel):
    summary: str
    findings: list[str]

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    output_schema=Result,
)
result: Result = agent.run(query).content
```

## 14.5 Error Handling

Always wrap agent.run() in try-except blocks:

```python
try:
    response = agent.run(query)
except Exception as e:
    logger.error(f"Agent error: {e}")
    # Handle error appropriately
```

## 14.6 Performance Optimization

- Reuse agents across requests
- Use async methods (arun) for concurrent operations
- Cache knowledge base results when appropriate
- Use session caching for frequently accessed sessions
""")
    
    return "".join(docs)

if __name__ == "__main__":
    markdown_content = generate_docs()
    
    # Write to file
    output_file = Path("/workspace/agno_complete_api_documentation.md")
    output_file.write_text(markdown_content)
    
    print(f"Documentation generated: {output_file}")
    print(f"Length: {len(markdown_content)} characters")
    print(f"Lines: {len(markdown_content.splitlines())} lines")
