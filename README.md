# Aucterra MCP Server

This repository configures an MCP-compatible server for Aucterra's Document Understanding APIs using the [aucterra-mcp](https://github.com/japisuru/aucterra-mcp) package.

It enables LLM agents to interact with Aucterra's document classification, extraction, etc. services using [Google's Agent Development Kit (ADK)](https://github.com/google/agent-development-kit).


## 🔧 Configuration

Include this block in your `mcpServers` configuration (e.g., `config.json` or `mcp.yaml`):

```json
{
  "mcpServers": {
    "aucterra": {
      "command": "pipx",
      "args": [
        "run",
        "--spec",
        "git+https://github.com/japisuru/aucterra-mcp",
        "aucterra-mcp"
      ],
      "env": {
        "AUCTERRA_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### 🔐 Required Environment Variables

| Variable           | Description                                        |
|-------------------|----------------------------------------------------|
| `AUCTERRA_API_KEY` | Your API key for accessing Aucterra's services     |



## ⚙️ Tool Behavior

This MCP tool provides structured access to Aucterra's:

- 📁 Document Classification  
- 🗂️ Key-Value Field Extraction (Simple + List fields)

The tool accepts `pdf` or `image` files and returns structured JSON output.



## ✅ Agent Integration (Google ADK)

To use this tool within your `LlmAgent`, configure it as follows:

```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

aucterra_tool = MCPToolset(
    connection_params=StdioServerParameters(
        command="pipx",
        args=[
            "run",
            "--spec",
            "git+https://github.com/japisuru/aucterra-mcp",
            "aucterra-mcp"
        ],
        env={"AUCTERRA_API_KEY": "your_api_key_here"}
    )
)
```

Add this tool to your agent via `tools=[aucterra_tool]`.



## 📚 Example Use Cases

```plaintext
User: Classify this document (/path/to/the/document/doc.pdf) into invoice or identity document.
User: Extract the following fields: NIC, Full Name, Date of Birth from this document (/path/to/the/document/doc.pdf) 
User: Extract Tax ID as 'Tax Identification Number' from this document (/path/to/the/document/doc.pdf).
```

The agent will use the Aucterra MCP server to extract fields, filling in missing values (e.g., using the same value for `field_key` and `field_name` if only one is provided).



## 📦 Dependencies

Ensure `pipx` is installed and available on your system.  
Install it via:

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```



## 🛠️ Issues

If you encounter issues, ensure your API key is correct and the tool is up to date:

```bash
pipx upgrade aucterra-mcp
```



## 🔗 Related Projects

- [Aucterra MCP](https://github.com/japisuru/aucterra-mcp)
- [Google ADK](https://github.com/google/agent-development-kit)
- [MCP Protocol](https://github.com/google/mcp)
