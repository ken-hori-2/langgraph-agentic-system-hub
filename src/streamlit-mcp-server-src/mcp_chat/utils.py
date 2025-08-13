from typing import Any, Dict, List, Callable, Optional
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
import uuid


def random_uuid():
    return str(uuid.uuid4())


async def astream_graph(
    graph: CompiledStateGraph,
    inputs: dict,
    config: Optional[RunnableConfig] = None,
    node_names: List[str] = [],
    callback: Optional[Callable] = None,
    stream_mode: str = "messages",
    include_subgraphs: bool = False,
) -> Dict[str, Any]:
    """
    Function to asynchronously stream and directly output LangGraph execution results.

    Args:
        graph (CompiledStateGraph): Compiled LangGraph object to execute
        inputs (dict): Dictionary of input values to pass to the graph
        config (Optional[RunnableConfig]): Execution configuration (optional)
        node_names (List[str], optional): List of node names to output. Default is empty list
        callback (Optional[Callable], optional): Callback function for processing each chunk. Default is None
            The callback function receives a dictionary in the form {"node": str, "content": Any}.
        stream_mode (str, optional): Streaming mode ("messages" or "updates"). Default is "messages"
        include_subgraphs (bool, optional): Whether to include subgraphs. Default is False

    Returns:
        Dict[str, Any]: Final result (optional)
    """
    config = config or {}
    final_result = {}

    def format_namespace(namespace):
        return namespace[-1].split(":")[0] if len(namespace) > 0 else "root graph"

    prev_node = ""

    if stream_mode == "messages":
        async for chunk_msg, metadata in graph.astream(
            inputs, config, stream_mode=stream_mode
        ):
            curr_node = metadata["langgraph_node"]
            final_result = {
                "node": curr_node,
                "content": chunk_msg,
                "metadata": metadata,
            }

            # Process only if node_names is empty or current node is in node_names
            if not node_names or curr_node in node_names:
                # Execute callback function if available
                if callback:
                    result = callback({"node": curr_node, "content": chunk_msg})
                    if hasattr(result, "__await__"):
                        await result
                # Default output if no callback
                else:
                    # Output separator only when node changes
                    if curr_node != prev_node:
                        print("\n" + "=" * 50)
                        print(f"🔄 Node: \033[1;36m{curr_node}\033[0m 🔄")
                        print("- " * 25)

                    # Process Claude/Anthropic model token chunks - always extract text only
                    if hasattr(chunk_msg, "content"):
                        # List-type content (Anthropic/Claude style)
                        if isinstance(chunk_msg.content, list):
                            for item in chunk_msg.content:
                                if isinstance(item, dict) and "text" in item:
                                    print(item["text"], end="", flush=True)
                        # String-type content
                        elif isinstance(chunk_msg.content, str):
                            print(chunk_msg.content, end="", flush=True)
                    # Process other types of chunk_msg
                    else:
                        print(chunk_msg, end="", flush=True)

                prev_node = curr_node

    elif stream_mode == "updates":
        # Error fix: Change unpacking method
        # Some graphs like REACT agents return only a single dictionary
        async for chunk in graph.astream(
            inputs, config, stream_mode=stream_mode, subgraphs=include_subgraphs
        ):
            # Branch processing method based on return format
            if isinstance(chunk, tuple) and len(chunk) == 2:
                # Expected format: (namespace, chunk_dict)
                namespace, node_chunks = chunk
            else:
                # Case where only single dictionary is returned (REACT agents, etc.)
                namespace = []  # Empty namespace (root graph)
                node_chunks = chunk  # chunk itself is the node chunk dictionary

            # Check if it's a dictionary and process items
            if isinstance(node_chunks, dict):
                for node_name, node_chunk in node_chunks.items():
                    final_result = {
                        "node": node_name,
                        "content": node_chunk,
                        "namespace": namespace,
                    }

                    # Filter only if node_names is not empty
                    if len(node_names) > 0 and node_name not in node_names:
                        continue

                    # Execute callback function if available
                    if callback is not None:
                        result = callback({"node": node_name, "content": node_chunk})
                        if hasattr(result, "__await__"):
                            await result
                    # Default output if no callback
                    else:
                        # Output separator only when node changes (same as messages mode)
                        if node_name != prev_node:
                            print("\n" + "=" * 50)
                            print(f"🔄 Node: \033[1;36m{node_name}\033[0m 🔄")
                            print("- " * 25)

                        # Output node chunk data - process with text focus
                        if isinstance(node_chunk, dict):
                            for k, v in node_chunk.items():
                                if isinstance(v, BaseMessage):
                                    # Process cases where BaseMessage's content attribute is text or list
                                    if hasattr(v, "content"):
                                        if isinstance(v.content, list):
                                            for item in v.content:
                                                if (
                                                    isinstance(item, dict)
                                                    and "text" in item
                                                ):
                                                    print(
                                                        item["text"], end="", flush=True
                                                    )
                                        else:
                                            print(v.content, end="", flush=True)
                                    else:
                                        v.pretty_print()
                                elif isinstance(v, list):
                                    for list_item in v:
                                        if isinstance(list_item, BaseMessage):
                                            if hasattr(list_item, "content"):
                                                if isinstance(list_item.content, list):
                                                    for item in list_item.content:
                                                        if (
                                                            isinstance(item, dict)
                                                            and "text" in item
                                                        ):
                                                            print(
                                                                item["text"],
                                                                end="",
                                                                flush=True,
                                                            )
                                                else:
                                                    print(
                                                        list_item.content,
                                                        end="",
                                                        flush=True,
                                                    )
                                            else:
                                                list_item.pretty_print()
                                        elif (
                                            isinstance(list_item, dict)
                                            and "text" in list_item
                                        ):
                                            print(list_item["text"], end="", flush=True)
                                        else:
                                            print(list_item, end="", flush=True)
                                elif isinstance(v, dict) and "text" in v:
                                    print(v["text"], end="", flush=True)
                                else:
                                    print(v, end="", flush=True)
                        elif node_chunk is not None:
                            if hasattr(node_chunk, "__iter__") and not isinstance(
                                node_chunk, str
                            ):
                                for item in node_chunk:
                                    if isinstance(item, dict) and "text" in item:
                                        print(item["text"], end="", flush=True)
                                    else:
                                        print(item, end="", flush=True)
                            else:
                                print(node_chunk, end="", flush=True)

                        # Don't output separator here (same as messages mode)

                    prev_node = node_name
            else:
                # Output entire chunk if not a dictionary
                print("\n" + "=" * 50)
                print(f"🔄 Raw output 🔄")
                print("- " * 25)
                print(node_chunks, end="", flush=True)
                # Don't output separator here
                final_result = {"content": node_chunks}

    else:
        raise ValueError(
            f"Invalid stream_mode: {stream_mode}. Must be 'messages' or 'updates'."
        )

    # Return final result as needed
    return final_result


async def ainvoke_graph(
    graph: CompiledStateGraph,
    inputs: dict,
    config: Optional[RunnableConfig] = None,
    node_names: List[str] = [],
    callback: Optional[Callable] = None,
    include_subgraphs: bool = True,
) -> Dict[str, Any]:
    """
    Function to asynchronously stream and output LangGraph app execution results.

    Args:
        graph (CompiledStateGraph): Compiled LangGraph object to execute
        inputs (dict): Dictionary of input values to pass to the graph
        config (Optional[RunnableConfig]): Execution configuration (optional)
        node_names (List[str], optional): List of node names to output. Default is empty list
        callback (Optional[Callable], optional): Callback function for processing each chunk. Default is None
            The callback function receives a dictionary in the form {"node": str, "content": Any}.
        include_subgraphs (bool, optional): Whether to include subgraphs. Default is True

    Returns:
        Dict[str, Any]: Final result (output of the last node)
    """
    config = config or {}
    final_result = {}

    def format_namespace(namespace):
        return namespace[-1].split(":")[0] if len(namespace) > 0 else "root graph"

    # Include subgraph output through subgraphs parameter
    async for chunk in graph.astream(
        inputs, config, stream_mode="updates", subgraphs=include_subgraphs
    ):
        # Branch processing method based on return format
        if isinstance(chunk, tuple) and len(chunk) == 2:
            # Expected format: (namespace, chunk_dict)
            namespace, node_chunks = chunk
        else:
            # Case where only single dictionary is returned (REACT agents, etc.)
            namespace = []  # Empty namespace (root graph)
            node_chunks = chunk  # chunk itself is the node chunk dictionary

        # Check if it's a dictionary and process items
        if isinstance(node_chunks, dict):
            for node_name, node_chunk in node_chunks.items():
                final_result = {
                    "node": node_name,
                    "content": node_chunk,
                    "namespace": namespace,
                }

                # Filter only if node_names is not empty
                if node_names and node_name not in node_names:
                    continue

                # Execute callback function if available
                if callback is not None:
                    result = callback({"node": node_name, "content": node_chunk})
                    # Await if it's a coroutine
                    if hasattr(result, "__await__"):
                        await result
                # Default output if no callback
                else:
                    print("\n" + "=" * 50)
                    formatted_namespace = format_namespace(namespace)
                    if formatted_namespace == "root graph":
                        print(f"🔄 Node: \033[1;36m{node_name}\033[0m 🔄")
                    else:
                        print(
                            f"🔄 Node: \033[1;36m{node_name}\033[0m in [\033[1;33m{formatted_namespace}\033[0m] 🔄"
                        )
                    print("- " * 25)

                    # Output node chunk data
                    if isinstance(node_chunk, dict):
                        for k, v in node_chunk.items():
                            if isinstance(v, BaseMessage):
                                v.pretty_print()
                            elif isinstance(v, list):
                                for list_item in v:
                                    if isinstance(list_item, BaseMessage):
                                        list_item.pretty_print()
                                    else:
                                        print(list_item)
                            elif isinstance(v, dict):
                                for node_chunk_key, node_chunk_value in v.items():
                                    print(f"{node_chunk_key}:\n{node_chunk_value}")
                            else:
                                print(f"\033[1;32m{k}\033[0m:\n{v}")
                    elif node_chunk is not None:
                        if hasattr(node_chunk, "__iter__") and not isinstance(
                            node_chunk, str
                        ):
                            for item in node_chunk:
                                print(item)
                        else:
                            print(node_chunk)
                    print("=" * 50)
        else:
            # Output entire chunk if not a dictionary
            print("\n" + "=" * 50)
            print(f"🔄 Raw output 🔄")
            print("- " * 25)
            print(node_chunks)
            print("=" * 50)
            final_result = {"content": node_chunks}

    # Return final result
    return final_result
