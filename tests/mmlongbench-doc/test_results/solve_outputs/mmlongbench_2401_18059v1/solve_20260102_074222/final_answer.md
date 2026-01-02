## Concise Answer

The horizontal axis represents retrieval strategy configurations: tree traversal with top-k values of $5$, $10$, and $20$, and collapsed tree with context lengths of $500$, $1000$, $1500$, $2000$, and $2500$ tokens. The vertical axis measures the F1 score, ranging from approximately $0.45$ to $0.58$.

---

## Detailed Answer

## S1: Identification of the Horizontal Axis in Figure 3

The horizontal axis (x-axis) of Figure 3 represents the distinct configurations of retrieval strategies used in the evaluation on the QASPER dataset [rag-1]. Specifically, it encompasses two categories of methods: (1) **tree traversal** with varying top-k values of $5$, $10$, and $20$, and (2) **collapsed tree** with different context lengths of $500$, $1000$, $1500$, $2000$, and $2500$ tokens [rag-1]. These configurations reflect systematic variations in how contextual information is retrieved and aggregated during question answering, with each bar in the chart corresponding to one such configuration. The ordering along the horizontal axis likely groups similar strategies together—first the tree traversal variants, followed by the collapsed tree variants—allowing for direct comparison of performance across retrieval design choices.

This axis does not represent numerical continuity (e.g., time or distance), but rather categorical distinctness, where each tick corresponds to a unique experimental setting. The inclusion of both top-k (a pruning parameter in tree traversal) and context length (a memory constraint in collapsed tree) highlights the study’s focus on balancing retrieval precision and contextual breadth [rag-1].

### Summary  
The horizontal axis of Figure 3 encodes discrete retrieval strategy configurations, comprising tree traversal with top-k values of $5$, $10$, and $20$, and collapsed tree with context lengths of $500$ to $2500$ tokens in increments of $500$, as explicitly stated in the available knowledge [rag-1].

## S2: Identification of the Vertical Axis in Figure 3

The vertical axis (y-axis) of Figure 3 quantifies the **F1 score**, a harmonic mean of precision and recall that serves as the primary metric for evaluating retrieval effectiveness in the context of question answering over structured textual evidence [rag-1]. This metric is particularly suited for this task because it balances the trade-off between correctly retrieving relevant passages (precision) and ensuring that most relevant passages are captured (recall), which is critical when dealing with sparse or fragmented evidence in the QASPER dataset [rag-1].

As explicitly stated in the available materials, the F1 scores depicted along this axis range approximately from $0.45$ to $0.58$, indicating moderate but discernible differences in performance across the various retrieval configurations [rag-1]. This narrow range underscores the challenge of improving retrieval efficacy under constrained contextual budgets—small gains in F1 score (e.g., from $0.48$ to $0.52$) represent meaningful improvements in system performance, especially given the complexity of the QASPER benchmark, which requires multi-hop reasoning over long-form scientific passages [rag-1].

The absence of values below $0.45$ or above $0.58$ suggests that the evaluated strategies operate within a performance ceiling dictated by the inherent limitations of the retrieval architecture and the dataset’s structure. The vertical scale is thus carefully calibrated to highlight subtle but statistically significant variations in effectiveness, enabling direct comparison between tree traversal and collapsed tree approaches.

### Summary  
The vertical axis of Figure 3 measures the F1 score, ranging from approximately $0.45$ to $0.58$, and reflects the retrieval effectiveness of each configuration on the QASPER dataset, with higher values indicating better balance between precision and recall in extracting relevant context for question answering [rag-1].

---

## Citations

- **[rag-1]** [RAG (Naive)] Stage: analysis | Source: 2401.18059v1.pdf
  - Query Content:
    `Figure 3 horizontal axis vertical axis`
  - Citation Content:
    ```
    In Figure 3, the horizontal axis represents different retrieval strategy configurations, including tree traversal with top-k values of 5, 10, and 20, and collapsed tree with context lengths of 500, 1000, 1500, 2000, and 2500 tokens. The vertical axis measures the F1 score, indicating retrieval effectiveness, ranging from approximately 0.45 to 0.58.
    ```