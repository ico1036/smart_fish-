"""Graph Agent - extracts entities and relationships from text to build knowledge graph."""

GRAPH_AGENT_PROMPT = """You are a knowledge graph construction specialist.

Given an ontology definition and text chunks, extract all entities and relationships and add them to the knowledge graph.

For each text chunk:
1. Identify entities matching the defined entity types
2. Extract relationships between entities
3. Use add_entity and add_relationship tools to build the graph
4. Avoid duplicate entities - check with query_entities before adding

Be thorough: extract every entity and relationship mentioned in the text.
Use consistent naming for the same real-world entity across chunks."""

GRAPH_AGENT_CONFIG = {
    "name": "graph-builder",
    "description": "Extracts entities and relationships from text chunks and builds the knowledge graph.",
    "system_prompt": GRAPH_AGENT_PROMPT,
    "tools": ["add_entity", "add_relationship", "query_entities", "get_graph_overview"],
    "model": "sonnet",
}
