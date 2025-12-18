#!/usr/bin/env python3
"""
LLM Council CLI Interface

Allows interacting with the LLM Council backend from the command line,
useful for integration with other tools like `claude-code`.

Usage:
    python council_cli.py "Why is this code failing?" --files src/main.py src/utils.py
"""

import argparse
import sys
import json
import base64
import mimetypes
import os
import httpx
from typing import List, Dict, Any, Optional

API_BASE = "http://localhost:8001/api"

def create_conversation() -> str:
    """Create a new conversation and return its ID."""
    try:
        response = httpx.post(f"{API_BASE}/conversations", json={})
        response.raise_for_status()
        return response.json()["id"]
    except Exception as e:
        print(f"Error creating conversation: {e}", file=sys.stderr)
        sys.exit(1)

def read_file_as_attachment(filepath: str) -> Dict[str, Any]:
    """Read a file and format it as an attachment object."""
    try:
        if not os.path.exists(filepath):
            print(f"Warning: File not found: {filepath}", file=sys.stderr)
            return None
            
        mime_type, _ = mimetypes.guess_type(filepath)
        if not mime_type:
            mime_type = "text/plain"
            
        with open(filepath, "rb") as f:
            data = f.read()
            
        encoded = base64.b64encode(data).decode("utf-8")
        
        return {
            "type": "file",
            "mimeType": mime_type,
            "data": encoded,
            "filename": os.path.basename(filepath)
        }
    except Exception as e:
        print(f"Error reading file {filepath}: {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description="Consult the LLM Council")
    parser.add_argument("query", help="The question for the council")
    parser.add_argument("--files", nargs="*", help="List of files to attach context from")
    parser.add_argument("--conversation-id", help="Continue an existing conversation")
    
    args = parser.parse_args()
    
    # 1. Setup conversation
    conversation_id = args.conversation_id
    if not conversation_id:
        conversation_id = create_conversation()
        print(f"Created conversation: {conversation_id}", file=sys.stderr)
    
    # 2. Prepare attachments
    attachments = []
    if args.files:
        print(f"Reading {len(args.files)} files...", file=sys.stderr)
        for filepath in args.files:
            att = read_file_as_attachment(filepath)
            if att:
                attachments.append(att)
    
    # 3. Send message stream
    payload = {
        "content": args.query,
        "attachments": attachments
    }
    
    print("\n--- Consulting the Council ---\n")
    
    try:
        url = f"{API_BASE}/conversations/{conversation_id}/message/stream"
        
        with httpx.stream("POST", url, json=payload, timeout=None) as response:
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    if line.startswith("data: "):
                        data_str = line[6:]
                        try:
                            event = json.loads(data_str)
                            event_type = event.get("type")
                            
                            if event_type == "stage1_start":
                                print("\n[Stage 1] Collecting individual opinions...", end="", flush=True)
                            
                            elif event_type == "stage1_complete":
                                print(" Done.")
                                results = event.get("data", [])
                                for res in results:
                                    print(f"  - {res['model']}")
                            
                            elif event_type == "stage2_start":
                                print("\n[Stage 2] Peer review and ranking...", end="", flush=True)
                                
                            elif event_type == "stage2_complete":
                                print(" Done.")
                                metadata = event.get("metadata", {})
                                rankings = metadata.get("aggregate_rankings", [])
                                print("  Agreed quality ranking:")
                                for r in rankings:
                                    print(f"  {r['average_rank']}. {r['model']}")

                            elif event_type == "stage3_start":
                                print("\n[Stage 3] Synthesizing final answer...", end="", flush=True)

                            elif event_type == "stage3_complete":
                                print(" Done.\n")
                                result = event.get("data", {})
                                print("=" * 60)
                                print(f"CHAIRMAN'S VERDICT ({result.get('model', 'Unknown')})")
                                print("=" * 60)
                                print(result.get("response", ""))
                                print("\n" + "=" * 60)

                            elif event_type == "error":
                                print(f"\nError: {event.get('message')}")
                                
                        except json.JSONDecodeError:
                            pass
                            
    except KeyboardInterrupt:
        print("\nRequest cancelled.")
    except Exception as e:
        print(f"\nError consulting council: {e}")

if __name__ == "__main__":
    main()
