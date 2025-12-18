from mcp.server.fastmcp import FastMCP
from .council import run_full_council
import asyncio
import base64
import json

# Initialize FastMCP
mcp = FastMCP("LLM Council")

@mcp.tool()
async def consult_council(query: str, files: list[str] = []) -> str:
    """
    Ask the LLM Council for a fresh perspective on a problem.
    
    The Council will run a 3-Stage Process:
    1. Exploration (Multiple Models)
    2. Peer Review (Ranking)
    3. Synthesis (Chairman's Verdict)

    GUIDELINES FOR CLAUDE CODE/USERS:
    
    1. Query Construction:
       - Analyze the user's query and scan ONLY the project files relevant to the issue.
       - Explain the history: "Tried X, failed with Y."
       - Frame clearly: State suspicions but remain open to alternatives.
    
    2. Execution:
       - Pass full file contents in the `files` list.
    
    3. Response Handling (CRITICAL):
       - You MUST pass through the COMPLETE, UNALTERED council response to the user.
       - Print the ENTIRE "CHAIRMAN'S VERDICT" verbatim.
       - DO NOT summarize, paraphrase, or truncate.
       - After printing, ask the user what they want to do next.

    Args:
        query: The question or problem description.
        files: List of file contents (strings) to provide as context.
    """
    # Adapt file contents to 'attachments' format
    # Simple heuristic: treat all as text files for now
    attachments = []
    
    for i, file_content in enumerate(files):
        # We don't have filenames here, so we use generic names
        attachments.append({
            "type": "file",
            "mimeType": "text/plain",
            "data": base64.b64encode(file_content.encode("utf-8")).decode("utf-8"),
            "filename": f"Context File {i+1}"
        })
    
    # Run the council (stateless mode - no conversation ID needed for single turn)
    # run_full_council returns: stage1_results, stage2_results, stage3_result, metadata
    stage1, stage2, stage3, metadata = await run_full_council(query, attachments)
    
    # Format the Output as Markdown
    output = []
    
    output.append("# LLM Council Deliberation\n")
    
    # Stage 1 Summary
    output.append("## Stage 1: Exploration")
    output.append(f"Consulted {len(stage1)} models.\n")
    
    # Stage 2 Rankings
    output.append("## Stage 2: Peer Review & Ranking")
    if "aggregate_rankings" in metadata:
        for item in metadata["aggregate_rankings"]:
            output.append(f"- **{item['model']}**: Avg Rank {item['average_rank']}")
    output.append("\n")
    
    # Stage 3 Verdict (The most important part)
    output.append("## CHAIRMAN'S VERDICT")
    output.append(stage3.get("response", "Error: No verdict generated."))
    
    return "\n".join(output)
