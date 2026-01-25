## Concise Answer

{16, 17, 18, 19}

---

## Detailed Answer

## S1: Identification of Common Nodes Retrieved by RAPTOR in Figure 4

In the context of RAPTOR’s tree-based retrieval mechanism as illustrated in **Figure 4**, the system dynamically selects nodes based on the semantic and structural demands of each query. For the two distinct questions posed — one thematic (“What is the central theme of the story?”) and one multi-hop — RAPTOR retrieves overlapping intermediate nodes while diverging in higher-level node inclusion.

Specifically, for **both questions**, RAPTOR retrieves the following intermediate nodes:  
**Node 16, Node 17, Node 18, and Node 19** [rag-1].

These nodes represent shared contextual or narrative segments that are relevant to answering either question. However, for the multi-hop question (Question 2), RAPTOR additionally retrieves **root summary node 25**, which provides broader summarization context not required for the thematic question [rag-1]. This divergence highlights RAPTOR’s adaptive retrieval strategy: it minimizes redundancy by selecting only the necessary nodes for each query type, while preserving common ground through shared intermediate nodes.

Thus, the set of nodes retrieved for *both* questions is precisely:  
$$
\{16, 17, 18, 19\}
$$

This result is consistent across both the summarized explanation and the raw textual confirmation provided in the available materials [rag-1].

### Summary
RAPTOR retrieves nodes 16, 17, 18, and 19 for both questions in Figure 4, forming the core shared retrieval set. The additional retrieval of node 25 for the multi-hop question underscores RAPTOR’s ability to scale retrieval depth according to query complexity.

---

## Citations

- **[rag-1]** [RAG (Hybrid)] Stage: analysis | Source: Figure 4, RAPTOR_Tree_Retrieval_Diagram_Figure_4, Question 1, Question 2, Intermediate Nodes
  - Query Content:
    `Which nodes are retrieved by RAPTOR for both questions in Figure 4?`
  - Citation Content:
    ```
    In Figure 4, RAPTOR retrieves intermediate nodes 16, 17, 18, and 19 for both questions. For Question 1 (thematic), it selects only these intermediate nodes. For Question 2 (multi-hop), it additionally retrieves root summary node 25. Thus, the common nodes retrieved for both questions are 16, 17, 18, and 19.
    ```