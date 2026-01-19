# --- imports (all at top) ---
import os
from pathlib import Path
import neo4j
from dotenv import load_dotenv
from PyPDF2 import PdfWriter, PdfReader

from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
from neo4j_graphrag.experimental.components.text_splitters.fixed_size_splitter import FixedSizeSplitter
from neo4j_graphrag.indexes import create_vector_index

# --- config/constants (defined early, in order) ---
INPUT_FOLDER = "papers"
PDF_FOLDER = "processed_papers"

os.makedirs(PDF_FOLDER, exist_ok=True)

# Replace simple label lists with rich schema + patterns
NODE_TYPES = [
    {
        "label": "Paper",
        "description": "A scientific paper (article, preprint, or conference paper).",
        "properties": [
            {"name": "title", "type": "STRING", "required": True},
            {"name": "doi", "type": "STRING", "required": True},
            {"name": "year", "type": "INTEGER"},
        ],
    },
    {
        "label": "Author",
        "description": "A person who authored a paper.",
        "properties": [
            {"name": "name", "type": "STRING", "required": True},
        ],
    },
    {
        "label": "Institution",
        "description": "An organization/affiliation associated with an author.",
        "properties": [
            {"name": "name", "type": "STRING", "required": True},
        ],
    },
    {
        "label": "Journal",
        "description": "Journal or conference venue where a paper was published/presented.",
        "properties": [
            {"name": "name", "type": "STRING", "required": True},
        ],
    },
    {
        "label": "Topic",
        "description": "A research area or keyword mentioned in or describing a paper.",
        "properties": [
            {"name": "name", "type": "STRING", "required": True},
        ],
    },
]

RELATIONSHIP_TYPES = [
    {
        "label": "WRITTEN_BY",
        "description": "Connects a Paper to an Author who wrote it. (Paper -> Author)",
    },
    {
        "label": "FROM",
        "description": "Connects an Author to an Institution affiliation. (Author -> Institution)",
    },
    {
        "label": "PUBLISHED_IN",
        "description": "Connects a Paper to its venue (Journal/Conference). (Paper -> Journal)",
    },
    {
        "label": "MENTIONS",
        "description": "Connects a Paper to a Topic it is about or mentions. (Paper -> Topic)",
    },
    {
        "label": "SIMILAR_TO",
        "description": "Connects two Papers that are semantically similar. (Paper -> Paper)",
        # Optional later if you want to store the similarity score:
        # "properties": [{"name": "score", "type": "FLOAT"}],
    },
]

PATTERNS = [
    ("Paper", "WRITTEN_BY", "Author"),
    ("Author", "FROM", "Institution"),
    ("Paper", "PUBLISHED_IN", "Journal"),
    ("Paper", "MENTIONS", "Topic"),
    ("Paper", "SIMILAR_TO", "Paper"),
]


prompt_template = """
You are an information extraction system. Your task is to extract a property graph from scientific paper text. 
The Paper entity is the main focus, and you should extract related entities and relationships as specified.
Each document contains only one scientific paper. The paper can have multiple authors, with different institutions.
et al. is not an author name, so ignore it. Usually the title of the paper is at the start of the document.

Extract:
1) Entities as nodes with a specific type (label)
2) Relationships between nodes with a direction from start node to end node

Strict rules:
- Use ONLY the node labels and relationship types provided in the schema below.
- Respect relationship direction and allowed source/target node types.
- Assign a unique string ID to each node, and reuse it in relationships.
- Do NOT invent facts. If a property is not present, set it to null (or omit it if unsure).
- Prefer fewer, higher-confidence nodes over many uncertain ones.
- De-duplicate nodes:
  - Paper: prefer DOI match; otherwise exact (or near-exact) title match.
  - Author/Institution/Journal/Topic: normalize by name (case-insensitive).
- Output MUST be a single valid JSON object. No markdown, no commentary.

Return JSON in exactly this format:
{{
  "nodes": [
    {{"id": "0", "label": "Paper", "properties": {{"title": "...", "doi": "...", "year": 2024}}}}
  ],
  "relationships": [
    {{"type": "WRITTEN_BY", "start_node_id": "0", "end_node_id": "1", "properties": {{"details": "..."}}}}
  ]
}}

Relationship guidance (intended graph):
- Paper -[:WRITTEN_BY]-> Author
- Author -[:FROM]-> Institution
- Paper -[:PUBLISHED_IN]-> Journal
- Paper -[:MENTIONS]-> Topic
- Paper -[:SIMILAR_TO]-> Paper (ONLY if the text explicitly indicates similarity; otherwise do not create it)

Allowed schema (use only these):
{schema}

Examples:
{examples}

Input text:
{text}
"""

# --- env (load then read) ---
load_dotenv(".env", override=True)
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


# --- graph/llm components (in dependency order) ---
driver = neo4j.GraphDatabase.driver(
    NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)


llm = OpenAILLM(
    model_name="gpt-4o-mini",
    model_params={"response_format": {"type": "json_object"}, "temperature": 0},
)

embedder = OpenAIEmbeddings()



kg_builder_pdf = SimpleKGPipeline(
    llm=llm,
    driver=driver,
    text_splitter=FixedSizeSplitter(chunk_size=800, chunk_overlap=100),
    embedder=embedder,
    schema={
        "node_types": NODE_TYPES,
        "relationship_types": RELATIONSHIP_TYPES,
    },
    prompt_template=prompt_template,
    from_pdf=True, 
)

pdf_file_paths = list(Path(PDF_FOLDER).glob("*.pdf"))
for path in pdf_file_paths[0:3]:
    print(f"Processing : {path}")
    pdf_result = await kg_builder_pdf.run_async(file_path=path)
    print(f"Result: {pdf_result}")


# --- indexing + similarity links ---
# Creates/ensures a Neo4j VECTOR INDEX named "paper_embeddings" over (:Chunk).embedding (size=1536)
# so retrievers can do cosine nearest-neighbor search for relevant chunks.

create_vector_index(
    driver,
    name="paper_embeddings",
    label="Chunk",
    embedding_property="embedding",
    dimensions=1536,
    similarity_fn="cosine",
)

SIMILARITY_THRESHOLD = 0.75
SIMILARITY_TOP_K = 25

# Find similar papers by querying the vector index for each chunk, then linking their parent papers.
# Assumes KG builder creates (Paper)-[:FROM_CHUNK]->(Chunk) (as used in your VectorCypherRetriever query).
with driver.session() as session:
    stats = session.run(
        """
        // sanity checks
        MATCH (c:Chunk)
        WITH count(c) AS chunks, count(CASE WHEN c.embedding IS NOT NULL THEN 1 END) AS chunks_with_emb
        MATCH (p:Paper)
        WITH chunks, chunks_with_emb, count(p) AS papers
        MATCH (p:Paper)-[:FROM_CHUNK]->(c:Chunk)
        WITH chunks, chunks_with_emb, papers, count(DISTINCT p) AS papers_with_chunks
        RETURN chunks, chunks_with_emb, papers, papers_with_chunks
        """
    ).single()
    print(f"Chunks={stats['chunks']}, withEmbedding={stats['chunks_with_emb']}, Papers={stats['papers']}, PapersWithChunks={stats['papers_with_chunks']}")

with driver.session() as session:
    res = session.run(
        """
        MATCH (p1:Paper)-[:FROM_CHUNK]->(c1:Chunk)
        WHERE c1.embedding IS NOT NULL
        CALL db.index.vector.queryNodes($index_name, $top_k, c1.embedding)
        YIELD node AS c2, score
        WHERE c2 <> c1 AND score >= $th
        MATCH (p2:Paper)-[:FROM_CHUNK]->(c2:Chunk)
        WHERE p1 <> p2

        // aggregate to one score per paper-pair (best chunk match)
        WITH p1, p2, max(score) AS score
        WITH
          CASE WHEN elementId(p1) < elementId(p2) THEN p1 ELSE p2 END AS a,
          CASE WHEN elementId(p1) < elementId(p2) THEN p2 ELSE p1 END AS b,
          score
        MERGE (a)-[r:SIMILAR_TO]->(b)
        SET r.score = CASE WHEN r.score IS NULL OR r.score < score THEN score ELSE r.score END
        RETURN count(r) AS paper_pairs_linked
        """,
        index_name="paper_embeddings",
        top_k=SIMILARITY_TOP_K,
        th=SIMILARITY_THRESHOLD,
    ).single()
    print(f"SIMILAR_TO paper pairs linked: {res['paper_pairs_linked']}")

with driver.session() as session:
    rows = session.run(
                """
                MATCH ()-[r]->()
                RETURN DISTINCT type(r) AS relationshipType
                ORDER BY relationshipType
                """
            ).data()


## --- Retrieval of information

from neo4j_graphrag.retrievers import VectorCypherRetriever

vc_retriever = VectorCypherRetriever(
    driver,
    index_name="paper_embeddings",
    embedder=embedder,
    retrieval_query="""
//1) Go out 2-3 hops in the entity graph and get relationships
WITH node AS chunk
MATCH (chunk)<-[:FROM_CHUNK]-()-[relList:!FROM_CHUNK]-{1,2}()
UNWIND relList AS rel

//2) collect relationships and text chunks
WITH collect(DISTINCT chunk) AS chunks, 
  collect(DISTINCT rel) AS rels

//3) format and return context
RETURN '=== text ===\n' + apoc.text.join([c in chunks | c.text], '\n---\n') + '\n\n=== kg_rels ===\n' +
  apoc.text.join([r in rels | startNode(r).name + ' - ' + type(r) + '(' + coalesce(r.details, '') + ')' +  ' -> ' + endNode(r).name ], '\n---\n') AS info
"""
)

from neo4j_graphrag.llm import OpenAILLM as LLM
from neo4j_graphrag.generation import RagTemplate
from neo4j_graphrag.generation.graphrag import GraphRAG

llm = LLM(model_name="gpt-4o",  model_params={"temperature": 0.0})

rag_template = RagTemplate(template='''Answer the Question using the following Context. Only respond with information mentioned in the Context. Do not inject any speculative information not mentioned. 

# Question:
{query_text}
 
# Context:
{context}

# Answer:
''', expected_inputs=['query_text', 'context'])

vc_rag = GraphRAG(llm=llm, retriever=vc_retriever, prompt_template=rag_template)

q = "Which papers mention Conterfactual learning and who are their authors?"
print(f"Vector + Cypher Response: \n{vc_rag.search(q, retriever_config={'top_k':5}).answer}")

def split_pdf(file, output_folder):
    """Extract the first two pages from a PDF and save to output folder."""
    
    with open(file, "rb") as pdf_file:
        input_pdf = PdfReader(pdf_file)
        
        # Check if PDF has at least one page
        if len(input_pdf.pages) == 0:
            print(f"Warning: {file} has no pages")
            return
        
        output = PdfWriter()
        
        # Add first page
        output.add_page(input_pdf.pages[0])
        
        # Add second page if it exists
        if len(input_pdf.pages) > 1:
            output.add_page(input_pdf.pages[1])
        
        output_path = Path(output_folder) / file.name
        with open(output_path, "wb") as output_stream:
            output.write(output_stream)
                
    

# --- process PDFs ---

for pdf_file in Path(INPUT_FOLDER).glob("*.pdf"):
    print(f"Splitting PDF: {pdf_file}")
    split_pdf(pdf_file, PDF_FOLDER)

