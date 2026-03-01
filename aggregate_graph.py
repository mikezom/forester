import json
import re
from pathlib import Path

def aggregate_graph(output_dir="output"):
    # Regex for edges
    edge_pattern = re.compile(
        r'<html:span\s+data-source="([^"]+)"\s+data-relation="([^"]+)"\s+data-target="([^"]+)"\s+data-mentioned="([^"]+)"\s+class="semantic-relation"\s*/>'
    )
    # Regex for extracting the title from Forester XML frontmatter
    title_pattern = re.compile(r'<(?:f|fr):title[^>]*>(.*?)</(?:f|fr):title>', re.DOTALL)
    
    unique_edges = set()
    nodes_dict = {}
    output_path = Path(output_dir)
    
    if not output_path.exists():
        print(f"Error: Directory '{output_dir}' not found.")
        return

    for file_path in output_path.glob('**/*.xml'):
        # Correctly extract the node_id based on Forester's directory structure
        if file_path.stem == 'index':
            node_id = file_path.parent.name
        else:
            node_id = file_path.stem
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Extract Edges
            matches = edge_pattern.findall(content)
            for match in matches:
                unique_edges.add((match[0], match[1], match[2], match[3]))
                
            # Extract Title
            title_match = title_pattern.search(content)
            if title_match:
                raw_title = title_match.group(1)
                # Strip inner XML tags (like <f:tex>) to get pure text for the graph label
                clean_title = re.sub(r'<[^>]+>', '', raw_title).strip()
                nodes_dict[node_id] = clean_title

    edges_list = [
        {"source": src, "relation": rel, "target": tgt, "mentioned": mentioned == "true"}
        for src, rel, tgt, mentioned in unique_edges
    ]
                
    output_file = output_path / "graph.json"
    with open(output_file, "w", encoding="utf-8") as out_file:
        # Save both nodes mapping and edges list
        json.dump({"nodes": nodes_dict, "edges": edges_list}, out_file, indent=2, ensure_ascii=False)
        
    print(f"Graph aggregation complete. Found {len(edges_list)} relations and {len(nodes_dict)} titles.")
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    aggregate_graph()