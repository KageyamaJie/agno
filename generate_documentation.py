#!/usr/bin/env python3
"""
Comprehensive API Documentation Generator for Agno Framework
Generates documentation covering all public APIs, functions, and components
"""

import ast
import inspect
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import importlib.util
import sys

class APIDocumentationGenerator:
    def __init__(self, base_path: str = "/workspace"):
        self.base_path = Path(base_path)
        self.libs_path = self.base_path / "libs" / "agno" / "agno"
        self.cookbook_path = self.base_path / "cookbook"
        self.docs = []
        self.imported_modules = {}
        
    def generate(self) -> str:
        """Generate comprehensive documentation"""
        self.docs = []
        
        # Title and Introduction
        self._add_section("Agno Framework - Complete API Documentation", level=1)
        self._add_text("""
This comprehensive documentation covers all public APIs, functions, and components of the Agno framework.
It includes detailed explanations, code examples, and usage instructions suitable for beginners.

**Table of Contents:**
1. Introduction to Agno
2. Core Concepts
3. Agent API Reference
4. Team API Reference
5. Workflow API Reference
6. Knowledge & VectorDB APIs
7. Database APIs
8. Model APIs
9. Tool APIs
10. AgentOS API
11. Memory & Session Management
12. Guardrails & Security
13. Cookbook Examples
14. Best Practices
        """)
        
        # Introduction
        self._add_section("1. Introduction to Agno", level=1)
        self._add_text("""
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
        
        # Core Concepts
        self._add_section("2. Core Concepts", level=1)
        self._add_text("""
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
        
        # Agent API
        self._document_agent_api()
        
        # Team API
        self._document_team_api()
        
        # Workflow API
        self._document_workflow_api()
        
        # Knowledge API
        self._document_knowledge_api()
        
        # Database APIs
        self._document_database_apis()
        
        # Model APIs
        self._document_model_apis()
        
        # Tool APIs
        self._document_tool_apis()
        
        # AgentOS API
        self._document_agentos_api()
        
        # Memory & Session
        self._document_memory_session()
        
        # Guardrails
        self._document_guardrails()
        
        # Cookbook Examples
        self._document_cookbook_examples()
        
        # Best Practices
        self._add_section("14. Best Practices", level=1)
        self._add_text("""
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
        
        return "\n".join(self.docs)
    
    def _add_section(self, title: str, level: int = 1):
        """Add a section header"""
        self.docs.append(f"\n{'#' * level} {title}\n")
    
    def _add_text(self, text: str):
        """Add text content"""
        self.docs.append(text)
    
    def _add_code_block(self, code: str, language: str = "python"):
        """Add a code block"""
        self.docs.append(f"```{language}\n{code}\n```")
    
    def _document_agent_api(self):
        """Document Agent API"""
        self._add_section("3. Agent API Reference", level=1)
        
        self._add_text("""
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

### Example: Agent with Tools

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    instructions="Search the web for information",
)

response = agent.run("What's the latest news about AI?")
print(response.content)
```

### Example: Agent with Knowledge

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
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

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    knowledge=knowledge,
    search_knowledge=True,  # Critical: enables agentic RAG
    instructions="Use knowledge base, cite sources"
)

# Add documents to knowledge base
knowledge.add_documents(["Document 1", "Document 2"])

response = agent.run("What information do you have?")
```

### Example: Agent with Structured Output

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from pydantic import BaseModel

class Result(BaseModel):
    summary: str
    findings: list[str]

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    output_schema=Result,
)

response = agent.run("Analyze this topic and provide findings")
result: Result = response.content
print(result.summary)
print(result.findings)
```

### Example: Agent with Database

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    db=SqliteDb(db_file="tmp/agents.db"),
    user_id="user-123",
    add_history_to_context=True,
    num_history_runs=3,
)

response = agent.run("Hello!")
# Next run will have access to previous conversation
response2 = agent.run("What did I just say?")
```
        """)
    
    def _document_team_api(self):
        """Document Team API"""
        self._add_section("4. Team API Reference", level=1)
        
        self._add_text("""
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

### Example: Multi-Agent Team

```python
from agno.agent import Agent
from agno.team.team import Team
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

web_agent = Agent(
    name="Web Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    instructions="Search the web for information",
)

finance_agent = Agent(
    name="Finance Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YFinanceTools()],
    instructions="Get financial data",
)

team = Team(
    members=[web_agent, finance_agent],
    model=OpenAIChat(id="gpt-4o"),
    instructions="Coordinate research and financial analysis",
)

response = team.run("Analyze NVDA stock and recent news")
```
        """)
    
    def _document_workflow_api(self):
        """Document Workflow API"""
        self._add_section("5. Workflow API Reference", level=1)
        
        self._add_text("""
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

### Workflow Components

#### Steps

Steps can be:
- Agents
- Teams
- Regular Python functions
- Async functions

#### Step Decorators

- **@Step**: Mark a function as a workflow step
- **@Parallel**: Execute steps in parallel
- **@Loop**: Execute steps in a loop
- **@Condition**: Conditional step execution
- **@Router**: Route to different steps based on condition

### Example: Sequential Workflow

```python
from agno.workflow.workflow import Workflow
from agno.workflow.step import Step
from agno.db.sqlite import SqliteDb

@Step
async def research_step(session_state, topic: str):
    return await research_agent.arun(topic)

@Step
async def write_step(session_state, research_result: str):
    return await writer_agent.arun(research_result)

async def blog_workflow(session_state, topic: str):
    research = await research_step(session_state, topic)
    article = await write_step(session_state, research.content)
    return article.content

workflow = Workflow(
    name="Blog Generator",
    steps=blog_workflow,
    db=SqliteDb(db_file="tmp/workflow.db"),
)
```

### Example: Parallel Workflow

```python
from agno.workflow.parallel import Parallel

@Parallel
async def parallel_research(session_state, topic: str):
    results = await asyncio.gather(
        agent1.arun(f"Research {topic} from perspective 1"),
        agent2.arun(f"Research {topic} from perspective 2"),
        agent3.arun(f"Research {topic} from perspective 3"),
    )
    return [r.content for r in results]
```

### Example: Conditional Workflow

```python
from agno.workflow.condition import Condition

@Condition(lambda session_state, x: x > 10)
async def handle_large_input(session_state, x: int):
    return await agent.arun(f"Process large input: {x}")

@Condition(lambda session_state, x: x <= 10)
async def handle_small_input(session_state, x: int):
    return await agent.arun(f"Process small input: {x}")
```
        """)
    
    def _document_knowledge_api(self):
        """Document Knowledge API"""
        self._add_section("6. Knowledge & VectorDB APIs", level=1)
        
        self._add_text("""
## 6.1 Knowledge Class

The `Knowledge` class provides agentic RAG capabilities.

### Import

```python
from agno.knowledge.knowledge import Knowledge
```

### Supported Vector Databases

Agno supports 20+ vector databases:
- LanceDB
- Pinecone
- Qdrant
- Weaviate
- Chroma
- Milvus
- PGVector
- MongoDB Atlas
- Redis
- And more...

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

### Example: Knowledge Base with Documents

```python
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.reader.pdf import PDFReader

knowledge = Knowledge(
    vector_db=LanceDb(
        uri="tmp/lancedb",
        table_name="knowledge_base",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    reader=PDFReader(),
)

# Add PDF documents
knowledge.add_documents(["path/to/doc1.pdf", "path/to/doc2.pdf"])

# Use with agent
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    knowledge=knowledge,
    search_knowledge=True,
)
```

### Example: Knowledge Base with URLs

```python
knowledge.add_urls([
    "https://docs.agno.com",
    "https://example.com/knowledge",
])
```

### Reranking

Enable reranking for better results:

```python
from agno.knowledge.reranker.cohere import CohereReranker

knowledge = Knowledge(
    vector_db=LanceDb(...),
    reranker=CohereReranker(),
)
```
        """)
    
    def _document_database_apis(self):
        """Document Database APIs"""
        self._add_section("7. Database APIs", level=1)
        
        self._add_text("""
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

### MongoDB

```python
from agno.db.mongo import MongoDb

db = MongoDb(
    connection_string="mongodb://localhost:27017",
    database_name="agno_db"
)
```

### Redis

```python
from agno.db.redis import RedisDb

db = RedisDb(
    host="localhost",
    port=6379,
    db=0
)
```

### Database Features

All databases support:
- Session storage
- Message history
- User memories
- Session summaries
- State management
        """)
    
    def _document_model_apis(self):
        """Document Model APIs"""
        self._add_section("8. Model APIs", level=1)
        
        self._add_text("""
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

### Google Gemini

```python
from agno.models.google import Gemini

model = Gemini(id="gemini-1.5-pro")
agent = Agent(model=model)
```

### AWS Bedrock

```python
from agno.models.aws import Bedrock

model = Bedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region="us-east-1"
)
```

### Azure OpenAI

```python
from agno.models.azure import AzureOpenAI

model = AzureOpenAI(
    model="gpt-4",
    api_key="...",
    api_base="https://your-resource.openai.azure.com"
)
```

### Model Parameters

Common parameters across models:
- **id** (str): Model identifier
- **api_key** (str, optional): API key (can use env var)
- **temperature** (float, optional): Sampling temperature
- **max_tokens** (int, optional): Maximum tokens
- **timeout** (int, optional): Request timeout
        """)
    
    def _document_tool_apis(self):
        """Document Tool APIs"""
        self._add_section("9. Tool APIs", level=1)
        
        self._add_text("""
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
    """Get weather for a city"""
    # Your implementation
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

### MCP Tools

Agno has first-class support for Model Context Protocol:

```python
from agno.tools.mcp import MCPTools

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        MCPTools(
            transport="streamable-http",
            url="https://docs.agno.com/mcp"
        )
    ],
)
```
        """)
    
    def _document_agentos_api(self):
        """Document AgentOS API"""
        self._add_section("10. AgentOS API", level=1)
        
        self._add_text("""
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

#### Get Sessions

```
GET /sessions
```

#### Get Memories

```
GET /memories
```

### Example: Full AgentOS Setup

```python
from agno.os import AgentOS
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.postgres import PostgresDb
from agno.tools.duckduckgo import DuckDuckGoTools

db = PostgresDb(db_url=os.getenv("DATABASE_URL"))

web_agent = Agent(
    name="Web Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    db=db,
)

agent_os = AgentOS(
    agents=[web_agent],
    db=db,
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="agentos:app", reload=True)
```
        """)
    
    def _document_memory_session(self):
        """Document Memory and Session APIs"""
        self._add_section("11. Memory & Session Management", level=1)
        
        self._add_text("""
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

### Memory Methods

- **add()**: Add a memory
- **get()**: Get memories for a user
- **search()**: Search memories
- **update()**: Update a memory
- **delete()**: Delete a memory

## 11.2 Session Management

Sessions track conversations and maintain state.

### Session Features

- **State Management**: Store arbitrary state
- **History**: Automatic conversation history
- **Summaries**: Automatic session summaries
- **Metadata**: Custom metadata

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

### Session State

```python
# Access session state
session = agent.get_session(user_id="user-123", session_id="session-456")
print(session.state)

# Update session state
agent.update_session_state(
    user_id="user-123",
    session_id="session-456",
    state={"key": "value"}
)
```

### Session Summaries

```python
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    enable_session_summaries=True,
    add_session_summary_to_context=True,
)
```
        """)
    
    def _document_guardrails(self):
        """Document Guardrails"""
        self._add_section("12. Guardrails & Security", level=1)
        
        self._add_text("""
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

### Custom Guardrails

```python
from agno.guardrails import BaseGuardrail

class CustomGuardrail(BaseGuardrail):
    def validate(self, input: str) -> bool:
        # Your validation logic
        return True
```
        """)
    
    def _document_cookbook_examples(self):
        """Document Cookbook Examples"""
        self._add_section("13. Cookbook Examples", level=1)
        
        # Read and include key cookbook examples
        cookbook_files = [
            ("01_basic_agent.py", "Basic Agent"),
            ("02_agent_with_tools.py", "Agent with Tools"),
            ("03_agent_with_knowledge.py", "Agent with Knowledge"),
            ("05_structured_output.py", "Structured Output"),
            ("17_agent_team.py", "Multi-Agent Team"),
            ("19_blog_generator_workflow.py", "Workflow Example"),
        ]
        
        for filename, title in cookbook_files:
            filepath = self.cookbook_path / "getting_started" / filename
            if filepath.exists():
                content = filepath.read_text()
                self._add_section(f"13.{cookbook_files.index((filename, title)) + 1} {title}", level=2)
                self._add_text(f"**File:** `{filename}`\n\n")
                self._add_code_block(content)
                self._add_text("\n")


if __name__ == "__main__":
    generator = APIDocumentationGenerator()
    markdown_content = generator.generate()
    
    # Write to file
    output_file = Path("/workspace/agno_complete_api_documentation.md")
    output_file.write_text(markdown_content)
    
    print(f"Documentation generated: {output_file}")
    print(f"Length: {len(markdown_content)} characters")
