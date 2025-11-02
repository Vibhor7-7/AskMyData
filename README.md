
# AskMyData


## **RAG Pipeline Step by Step:**


### 1. File upload & initial parsing
User uploads a file via the frontend.

Backend receives the file and determines its type (CSV, JSON, iCal).

Parser routines normalize the file into a consistent tabular/record format (rows with named fields).

### 2. Chunking / conversion to text snippets
Convert each record (or logical group of records) into one or more human-readable text chunks

Decide chunk size and granularity: one chunk per row is simple and reliable for tabular data; longer narrative files can be split into paragraphs or rolling windows

Attach metadata to each chunk: original row id, file id, date, numeric fields, and any tags useful for filtering.

### Create Embeddings 
For each chunk, create an embedding vector that represents its semantic content.

Use the chosen embedding model (via Ollama) and keep track of vector dimensionality.

Normalize or cast embeddings to the format required by Chroma.

### Store Embeddings in Chroma 
Initialize a Chroma collection dedicated to the user/session or dataset.

Add documents to the collection with:
    the chunk text

    its embedding

    metadata (file id, row id, dates, categories)

    a unique document id


### Receive user query and decide intent
User types a question in the chatbox.

Before retrieval, perform a light analysis of the prompt to detect intent:

Is this an information retrieval question? (e.g., “How many meetings did I have?”)

Is this a visualization request? (keywords: “plot”, “chart”, “show”, “display by”, “histogram”)

Is it an instruction to modify data? (disallow or warn)

Tag the query with the detected intent and decide whether to include a visualization step later.

### Embed Question and retrieve context from Chroma 
Create an embedding for the user’s question with the same embedding model/approach used for the chunks. 

Query Chroma with the question embedding to retrieve top-K nearest chunks according to similarity.

Retrieve both chunk text and metadata for the top results.

### Construct the prompt for the LLM (grounding + question)

Build a prompt that places retrieved context before the user question. A typical prompt contains:

Short instruction: how the model should behave (be concise, use only provided facts, output JSON if needed, etc.)


### Ask Ollama (LLM) to generate an answer

Send the constructed prompt to the Ollama model.

The model returns a grounded answer. Depending on instruction, it may:

Provide a direct numeric/text answer (e.g., “Total rent: $900”)

Provide a short plan or instructions for a visualization (e.g., “Plot monthly totals with month on x-axis and sum(amount) on y-axis”)

Include both explanation and a suggested chart type

Capture model output and any structured tokens (JSON output, chart spec, or simple instructions).


### Post-process & verify (optional but recommended)

If the model returns a factual/aggregated number, optionally verify by running an exact Pandas query on the parsed dataset to ensure the number matches the data. Use the metadata and filters used during retrieval for exact computation. If there is a mismatch, prefer the computed result and annotate that verification was used. For anything numeric or actionable, return both model reasoning and the verified number (transparency).


### Generate visualizations (if requested)

If the user asked for a chart or the LLM returned chart instructions, translate that into a concrete plotting step:
Map LLM chart instructions to a plotting function (Matplotlib for static / PNG or Plotly for interactive). Use the verified DataFrame queries (e.g., groupby + aggregation) to build the dataset for charting.

Create the visualization:
For static images: render a Matplotlib figure, save to PNG, and return a URL or base64 content. For interactive charts: build a Plotly figure and either return serialized JSON for client-side rendering or an HTML fragment. Attach chart metadata (type, axes, legend) and alt text for accessibility.



### Build the final response to the frontend

Compose a response object that includes:

The textual answer Verification status and (optional) the raw data query used to compute numeric answers Any retrieved context snippets (if you want to show source lines) A visualization payload: image URL/base64 or Plotly JSON/HTML. Helpful metadata (file id, timestamp, etc.) Return the response over the API.  The frontend then: Renders text in the chat UI, Renders images or Plotly charts, Shows source/context snippets if desired


