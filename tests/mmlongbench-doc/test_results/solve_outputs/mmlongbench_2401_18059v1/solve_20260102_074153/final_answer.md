## Concise Answer

intermediate and root layers

---

## Detailed Answer

## S1: Identification of RAPTOR-Retrieved Nodes for Both Questions

RAPTOR (Recursive Abstraction and Progressive Tree-based Organization for Retrieval) employs a hierarchical tree structure to organize and retrieve information at multiple levels of abstraction [rag-1]. Unlike Dense Passage Retrieval (DPR), which retrieves granular, leaf-level text fragments (e.g., “glass slipper fits” or “fairy godmother appears”), RAPTOR leverages synthesized summaries from higher layers of the tree to answer thematic, high-level questions [rag-1].

In Figure 4, for both questions — *“What is the central theme of the story?”* and *“How did Cinderella find a happy ending?”* — RAPTOR retrieves nodes from the **intermediate** and **root layers** of its hierarchical structure, as these are the only layers highlighted in bright yellow [rag-1]. These layers contain abstracted, semantically enriched summaries that encapsulate broader narrative patterns and causal relationships. Specifically, the retrieved nodes include synthesized concepts such as *“courage, resilience, transformation”*, which collectively capture the thematic essence and narrative arc underlying Cinderella’s journey [rag-1].

The selection of these higher-layer nodes is intentional: they subsume the granular details found in DPR’s leaf nodes, enabling efficient and contextually coherent answers to abstract queries without requiring direct matching to surface-level text. This demonstrates RAPTOR’s core advantage — hierarchical abstraction allows a single, high-level node to answer multiple related questions by encoding shared semantic content.

Thus, the nodes retrieved by RAPTOR for both questions are precisely those in the intermediate and root layers, visually distinguished by bright yellow highlighting in Figure 4, and semantically characterized by their synthesized thematic summaries.

### Summary
RAPTOR retrieves the same set of high-level, synthesized nodes — specifically those in the intermediate and root layers — for both thematic questions, as these nodes encode the overarching narrative themes common to both inquiries.

---

## Citations

- **[rag-1]** [RAG (Naive)] Stage: analysis | Source: 2401.18059v1.pdf
  - Query Content:
    `RAPTOR retrieved nodes Figure 4`
  - Citation Content:
    ```
    In Figure 4, RAPTOR retrieves nodes from the intermediate and root layers of its hierarchical tree structure, which are highlighted in bright yellow. These nodes contain synthesized summaries such as 'courage, resilience, transformation' that capture broad narrative themes and causal relationships for both questions: 'What is the central theme of the story?' and 'How did Cinderella find a happy ending?'. These higher-layer nodes encompass the information retrieved by DPR, which consists of isolated leaf nodes with granular plot details like 'glass slipper fits' or 'fairy godmother appears'.
    ```