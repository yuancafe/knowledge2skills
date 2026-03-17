#!/usr/bin/env python3
"""
Interactive Visualization Generator for LightRAG
Generates data files + interactive HTML viewer with:
- Entity type classification & color coding
- Entity descriptions on click
- Type filter bar
- Collapsible side panels
- Search & highlight
"""

import json
import networkx as nx
from pathlib import Path
from collections import Counter


# Type inference keywords
TYPE_KEYWORDS = {
    "Character": ["character", "person", "narrator", "poet", "guide", "hero", "protagonist", "pilgrim", "soul", "shade", "spirit", "sinner"],
    "Location": ["location", "place", "circle", "region", "realm", "river", "city", "mountain", "valley", "gate", "bridge", "pit", "heaven", "hell", "purgatory", "limbo", "paradise", "inferno"],
    "Literary_Work": ["work", "book", "poem", "comedy", "canto", "text", "writing", "literature", "epic", "divine comedy"],
    "Event": ["event", "journey", "descent", "encounter", "battle", "punishment", "transformation"],
    "Creature": ["creature", "beast", "demon", "angel", "monster", "serpent", "dragon", "wolf", "lion", "leopard"],
    "Concept": ["concept", "idea", "virtue", "sin", "love", "justice", "faith", "hope", "reason", "wisdom", "punishment"],
    "Organization": ["organization", "group", "order", "church", "school", "faction"],
    "Symbol": ["symbol", "represent", "signif", "metaphor", "allegory"],
    "Mythological_Figure": ["god", "goddess", "mytholog", "greek", "roman", "trojan", "olymp"],
    "Religious_Figure": ["saint", "biblical", "prophet", "apostle", "moses", "abraham", "noah", "christ", "mary", "angel"],
}

TYPE_COLORS = {
    "Character": "#ff6b6b",
    "Location": "#4ecdc4",
    "Literary_Work": "#ffe66d",
    "Event": "#a29bfe",
    "Creature": "#fd79a8",
    "Concept": "#74b9ff",
    "Organization": "#ffeaa7",
    "Symbol": "#dfe6e9",
    "Mythological_Figure": "#e17055",
    "Religious_Figure": "#00b894",
    "Other": "#636e72",
}


def infer_entity_type(name, description):
    text = (name + " " + description).lower()
    scores = {}
    for etype, keywords in TYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[etype] = score
    return max(scores, key=scores.get) if scores else "Other"


def generate(rag_dir, viz_dir, title="Knowledge Graph"):
    """
    Main entry point.
    rag_dir: Path to LightRAG working directory (contains graphml, vdb_entities.json, etc.)
    viz_dir: Path to output visualization directory
    title:   Title shown in the header
    """
    rag_dir = Path(rag_dir)
    viz_dir = Path(viz_dir)
    viz_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. Load graph ──────────────────────────────────────────────
    graph_file = rag_dir / "graph_chunk_entity_relation.graphml"
    if not graph_file.exists():
        print(f"  ⚠️  Graph file not found: {graph_file}")
        return
    G = nx.read_graphml(str(graph_file))
    degree_dict = dict(G.degree())
    print(f"  ✓ Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # ── 2. Load entity descriptions ────────────────────────────────
    entity_descriptions = {}
    ent_file = rag_dir / "vdb_entities.json"
    if ent_file.exists():
        with open(ent_file) as f:
            ent_data = json.load(f)
        for item in ent_data.get("data", []):
            name = item.get("entity_name", "")
            content = item.get("content", "")
            if name and content:
                lines = content.split("\n")
                desc = "\n".join(lines[1:]).strip() if len(lines) > 1 else content
                entity_descriptions[name] = desc
    print(f"  ✓ Descriptions: {len(entity_descriptions)} entities")

    # ── 3. Infer entity types ──────────────────────────────────────
    node_types = {}
    for node in G.nodes():
        desc = entity_descriptions.get(node, "")
        node_types[node] = infer_entity_type(node, desc)
    type_counts = Counter(node_types.values())
    print(f"  ✓ Types inferred: {dict(type_counts)}")

    # ── 4. Build JSON data ─────────────────────────────────────────
    type_list = list(TYPE_COLORS.keys())
    type_to_group = {t: i + 1 for i, t in enumerate(type_list)}

    nodes = []
    entity_details = {}
    for node in G.nodes():
        etype = node_types.get(node, "Other")
        neighbors = list(G.neighbors(node))
        nodes.append({
            "id": node,
            "label": node[:40],
            "degree": degree_dict.get(node, 0),
            "group": type_to_group.get(etype, len(type_list)),
            "category": etype,
        })
        entity_details[node] = {
            "name": node,
            "description": entity_descriptions.get(node, "No description available."),
            "degree": degree_dict.get(node, 0),
            "category": etype,
            "neighbors": neighbors[:30],
            "neighbor_count": len(neighbors),
        }

    edges = [{"source": s, "target": t} for s, t in G.edges()]

    graph_data = {
        "nodes": nodes,
        "links": edges,
        "type_colors": TYPE_COLORS,
        "type_counts": dict(type_counts),
    }

    with open(viz_dir / "graph_data.json", "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2, ensure_ascii=False)
    with open(viz_dir / "entity_details.json", "w", encoding="utf-8") as f:
        json.dump(entity_details, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Data files written")

    # ── 5. Write HTML ──────────────────────────────────────────────
    type_colors_json = json.dumps(TYPE_COLORS)
    safe_title = title.replace('"', "&quot;")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{safe_title}</title>
<script src="https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;background:#1a1a2e;color:#fff}}
#header{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:12px 20px;display:flex;align-items:center;justify-content:space-between}}
#header h1{{font-size:1.6em}}
#type-bar{{display:flex;flex-wrap:wrap;gap:8px;padding:10px 20px;background:#16213e;border-bottom:1px solid rgba(255,255,255,.1)}}
.type-tag{{padding:5px 12px;border-radius:20px;font-size:13px;cursor:pointer;border:2px solid transparent;transition:all .2s;font-weight:500}}
.type-tag:hover{{opacity:.8}}.type-tag.active{{border-color:#fff}}
.type-tag .count{{opacity:.7;font-size:11px}}
#container{{display:flex;height:calc(100vh - 120px);position:relative}}
#controls{{width:260px;background:#16213e;padding:15px;overflow-y:auto;border-right:1px solid rgba(255,255,255,.1);transition:width .3s,padding .3s,opacity .3s}}
#controls.hidden{{width:0;padding:0;overflow:hidden;opacity:0;border:none}}
.toggle-btn{{position:absolute;top:10px;z-index:100;width:32px;height:32px;border-radius:50%;background:rgba(102,126,234,.8);color:#fff;border:none;cursor:pointer;font-size:16px;display:flex;align-items:center;justify-content:center}}
.toggle-btn:hover{{background:rgba(102,126,234,1)}}
#toggle-left{{left:270px;transition:left .3s}}
#toggle-left.shifted{{left:10px}}
#network{{flex:1;background:#0f0f1e}}
#info{{width:0;background:#16213e;padding:0;overflow-y:auto;overflow-x:hidden;border-left:none;transition:width .3s,padding .3s}}
#info.open{{width:380px;padding:20px;border-left:1px solid rgba(255,255,255,.1)}}
input[type="text"]{{width:100%;padding:10px;border:none;border-radius:5px;background:#0f3460;color:#fff;font-size:14px;margin-bottom:10px}}
input[type="text"]:focus{{outline:2px solid #667eea}}
.ctrl-btn{{width:100%;padding:10px;margin:5px 0;border:none;border-radius:5px;background:#0f3460;color:#fff;cursor:pointer;font-size:13px}}
.ctrl-btn:hover{{background:#1a4a8a}}
.stat-box{{background:#0f3460;padding:12px;margin:8px 0;border-radius:5px}}
.stat-label{{color:#4ecdc4;font-size:11px;text-transform:uppercase}}
.stat-value{{font-size:20px;font-weight:bold;margin-top:3px}}
#entity-name{{font-size:1.4em;margin-bottom:10px;word-wrap:break-word}}
.type-badge{{display:inline-block;padding:4px 12px;border-radius:12px;font-size:12px;font-weight:bold;margin-bottom:15px}}
.desc-box{{background:#0f3460;padding:15px;border-radius:8px;margin:10px 0;border-left:3px solid #667eea;font-size:14px;line-height:1.6}}
.section-title{{color:#4ecdc4;font-size:12px;text-transform:uppercase;margin:15px 0 8px 0;letter-spacing:1px}}
.neighbor-item{{background:rgba(102,126,234,.2);padding:8px 12px;margin:4px 0;border-radius:4px;cursor:pointer;font-size:13px;display:flex;justify-content:space-between;align-items:center}}
.neighbor-item:hover{{background:rgba(102,126,234,.4)}}
.neighbor-type{{font-size:11px;opacity:.7}}
.close-btn{{float:right;background:none;border:none;color:rgba(255,255,255,.5);font-size:20px;cursor:pointer;padding:0 5px}}
.close-btn:hover{{color:#fff}}
</style>
</head>
<body>
<div id="header"><h1>{safe_title}</h1></div>
<div id="type-bar"></div>
<div id="container">
  <div id="controls">
    <input type="text" id="search" placeholder="🔍 Search entity...">
    <button class="ctrl-btn" onclick="resetView()">Reset View</button>
    <button class="ctrl-btn" onclick="fitNetwork()">Fit to Screen</button>
    <div class="stat-box"><div class="stat-label">Nodes</div><div class="stat-value" id="node-count">-</div></div>
    <div class="stat-box"><div class="stat-label">Edges</div><div class="stat-value" id="edge-count">-</div></div>
    <div class="stat-box"><div class="stat-label">Types</div><div class="stat-value" id="type-count">-</div></div>
  </div>
  <button class="toggle-btn" id="toggle-left" onclick="toggleLeft()" title="Toggle sidebar">&#9664;</button>
  <div id="network"></div>
  <div id="info">
    <div id="detail-panel">
      <button class="close-btn" onclick="closeInfo()" title="Close">&times;</button>
      <div id="entity-name"></div>
      <div id="entity-type-badge"></div>
      <div class="section-title">Description</div>
      <div class="desc-box" id="entity-desc"></div>
      <div class="section-title">Statistics</div>
      <div class="stat-box"><div class="stat-label">Connections</div><div class="stat-value" id="entity-degree">-</div></div>
      <div class="section-title" id="neighbors-title">Related Entities</div>
      <div id="neighbors-list"></div>
    </div>
  </div>
</div>
<script>
var network,nodesDS,edgesDS,allNodes,allEdges,entityDetails,graphData;
var activeTypeFilter=null;
var TYPE_COLORS={type_colors_json};

function isLight(h){{var r=parseInt(h.slice(1,3),16),g=parseInt(h.slice(3,5),16),b=parseInt(h.slice(5,7),16);return(r*.299+g*.587+b*.114)>150}}
function toggleLeft(){{var c=document.getElementById("controls"),b=document.getElementById("toggle-left");c.classList.toggle("hidden");b.classList.toggle("shifted");b.innerHTML=c.classList.contains("hidden")?"&#9654;":"&#9664;"}}
function closeInfo(){{document.getElementById("info").classList.remove("open")}}
function openInfo(){{document.getElementById("info").classList.add("open")}}

function init(){{
  Promise.all([fetch("graph_data.json").then(function(r){{return r.json()}}),fetch("entity_details.json").then(function(r){{return r.json()}})]).then(function(res){{
    graphData=res[0];entityDetails=res[1];
    allNodes=graphData.nodes.map(function(n){{return{{id:n.id,label:n.degree>3?n.label:"",group:n.group,value:Math.max(n.degree,1),title:n.id+"\\n"+(n.category||"")+"\\nConnections: "+n.degree,category:n.category,color:{{background:TYPE_COLORS[n.category]||"#636e72",border:"#fff"}}}}}});
    allEdges=graphData.links.map(function(l){{return{{from:l.source,to:l.target}}}});
    document.getElementById("node-count").textContent=allNodes.length;
    document.getElementById("edge-count").textContent=allEdges.length;
    document.getElementById("type-count").textContent=Object.keys(graphData.type_counts).length;
    buildTypeBar(graphData.type_counts);createNetwork();
  }}).catch(function(e){{console.error(e);alert("Load error: "+e.message)}});
}}

function buildTypeBar(tc){{
  var bar=document.getElementById("type-bar");
  var a=document.createElement("div");a.className="type-tag active";a.style.background="rgba(255,255,255,.2)";a.style.color="#fff";a.innerHTML="All <span class='count'>("+allNodes.length+")</span>";a.onclick=function(){{filterByType(null)}};bar.appendChild(a);
  Object.entries(tc).sort(function(a,b){{return b[1]-a[1]}}).forEach(function(e){{
    var t=e[0],c=e[1],tag=document.createElement("div");tag.className="type-tag";tag.dataset.type=t;var col=TYPE_COLORS[t]||"#636e72";tag.style.background=col;tag.style.color=isLight(col)?"#333":"#fff";tag.innerHTML=t.replace(/_/g," ")+" <span class='count'>("+c+")</span>";tag.onclick=function(){{filterByType(t)}};bar.appendChild(tag);
  }});
}}

function filterByType(t){{
  activeTypeFilter=t;
  document.querySelectorAll(".type-tag").forEach(function(tag){{tag.classList.remove("active");if(t===null&&!tag.dataset.type)tag.classList.add("active");if(tag.dataset.type===t)tag.classList.add("active")}});
  if(t===null){{nodesDS.clear();edgesDS.clear();nodesDS.add(allNodes);edgesDS.add(allEdges)}}
  else{{var f=allNodes.filter(function(n){{return n.category===t}});var ids=new Set(f.map(function(n){{return n.id}}));var fe=allEdges.filter(function(e){{return ids.has(e.from)&&ids.has(e.to)}});nodesDS.clear();edgesDS.clear();nodesDS.add(f);edgesDS.add(fe)}}
}}

function createNetwork(){{
  var c=document.getElementById("network");nodesDS=new vis.DataSet(allNodes);edgesDS=new vis.DataSet(allEdges);
  var opt={{nodes:{{shape:"dot",font:{{size:11,color:"#fff",strokeWidth:2,strokeColor:"#000"}},borderWidth:2,scaling:{{min:8,max:40}}}},edges:{{width:1,color:{{color:"rgba(255,255,255,.15)",highlight:"#ffd700"}},smooth:{{type:"continuous"}}}},physics:{{stabilization:{{iterations:150}},barnesHut:{{gravitationalConstant:-20000,springLength:150}}}},interaction:{{hover:true,tooltipDelay:100}}}};
  network=new vis.Network(c,{{nodes:nodesDS,edges:edgesDS}},opt);
  network.on("click",function(p){{if(p.nodes.length>0)showDetail(p.nodes[0])}});
  network.on("stabilizationIterationsDone",function(){{network.setOptions({{physics:false}})}});
  document.getElementById("search").addEventListener("input",function(e){{var q=e.target.value.toLowerCase();if(q.length>=2){{var m=allNodes.filter(function(n){{return n.id.toLowerCase().indexOf(q)>=0}});if(m.length>0){{network.selectNodes([m[0].id]);network.focus(m[0].id,{{scale:1.5,animation:true}});showDetail(m[0].id)}}}}}});
}}

function showDetail(nid){{
  var d=entityDetails[nid];if(!d)return;openInfo();
  document.getElementById("entity-name").textContent=d.name;
  var col=TYPE_COLORS[d.category]||"#636e72";var tc=isLight(col)?"#333":"#fff";
  document.getElementById("entity-type-badge").innerHTML="<span class='type-badge' style='background:"+col+";color:"+tc+"'>"+(d.category||"Other").replace(/_/g," ")+"</span>";
  document.getElementById("entity-desc").textContent=d.description||"No description available.";
  document.getElementById("entity-degree").textContent=d.degree;
  document.getElementById("neighbors-title").textContent="Related Entities ("+d.neighbor_count+")";
  var h="";d.neighbors.forEach(function(n){{var nd=entityDetails[n];var nt=nd?nd.category:"";var nc=TYPE_COLORS[nt]||"#636e72";var si=n.replace(/'/g,"\\\\'");h+="<div class='neighbor-item' onclick=\\"selectNode('"+si+"')\\"><span>"+n+"</span><span class='neighbor-type' style='color:"+nc+"'>"+(nt||"").replace(/_/g," ")+"</span></div>"}});
  document.getElementById("neighbors-list").innerHTML=h;
  var cn=network.getConnectedNodes(nid);network.selectNodes([nid].concat(cn));
}}

function selectNode(nid){{network.selectNodes([nid]);network.focus(nid,{{scale:1.5,animation:true}});showDetail(nid)}}
function resetView(){{activeTypeFilter=null;nodesDS.clear();edgesDS.clear();nodesDS.add(allNodes);edgesDS.add(allEdges);network.unselectAll();document.getElementById("search").value="";closeInfo();document.querySelectorAll(".type-tag").forEach(function(t){{t.classList.remove("active");if(!t.dataset.type)t.classList.add("active")}})}}
function fitNetwork(){{network.fit({{animation:true}})}}
init();
</script>
</body>
</html>"""

    with open(viz_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ HTML viewer written: {viz_dir / 'index.html'}")


# ── CLI ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Generate interactive RAG visualization")
    p.add_argument("rag_dir", help="LightRAG working directory")
    p.add_argument("-o", "--output", default=None, help="Output directory (default: <rag_dir>/../visualization)")
    p.add_argument("-t", "--title", default="Knowledge Graph", help="Page title")
    args = p.parse_args()
    out = args.output or str(Path(args.rag_dir).parent / "visualization")
    generate(args.rag_dir, out, args.title)
