## Concise Answer

Iterative Retrieval, Recursive Retrieval, and Adaptive Retrieval

---

## Detailed Answer

## S1: Identification of Subsections in "AUGMENTATION PROCESS IN RAG"

The section titled *AUGMENTATION PROCESS IN RAG* is explicitly defined in the provided knowledge base as encompassing three distinct subsections, each representing a strategic approach to enhancing retrieval quality in Retrieval-Augmented Generation (RAG) systems beyond single-pass retrieval [rag-1]. These subsections are:

1. **Iterative Retrieval**: This method employs a feedback loop between the retrieval and generation components, allowing the system to refine the context used for generation through multiple rounds of querying and re-evaluation. This iterative refinement improves relevance by correcting initial retrieval errors or omissions [rag-1].

2. **Recursive Retrieval**: Designed for complex, multi-faceted queries, Recursive Retrieval decomposes the original question into a hierarchy of sub-problems. Each sub-problem is addressed sequentially through targeted retrieval and reasoning, enabling the system to build a structured, step-by-step solution path [rag-1].

3. **Adaptive Retrieval**: This dynamic approach autonomously determines whether additional retrieval is necessary during generation, based on confidence signals such as reflection tokens or uncertainty metrics. It avoids unnecessary retrievals while ensuring sufficient context is gathered when the model’s output confidence is low [rag-1].

These three mechanisms—Iterative, Recursive, and Adaptive Retrieval—constitute the core architectural subdivisions of the augmentation process in RAG, each addressing different dimensions of retrieval inefficiency: sequential refinement, hierarchical decomposition, and real-time decision-making.

The extraction of these subsections is directly supported by the raw excerpt and summary from [rag-1], which consistently and unambiguously lists these three components as the defining elements of the section. No other subsections are mentioned or implied in the available material.

In summary, the section "AUGMENTATION PROCESS IN RAG" includes exactly three subsections: Iterative Retrieval, Recursive Retrieval, and Adaptive Retrieval.

---

## Citations

- **[rag-1]** [RAG (Naive)] Stage: analysis | Source: 2312.10997v5.pdf
  - Query Content:
    `AUGMENTATION PROCESS IN RAG subsections`
  - Citation Content:
    ```
    The section 'AUGMENTATION PROCESS IN RAG' includes three subsections: Iterative Retrieval, Recursive Retrieval, and Adaptive Retrieval. Iterative Retrieval uses a feedback loop between retrieval and generation to refine context. Recursive Retrieval breaks complex queries into hierarchical sub-problems using step-by-step reasoning. Adaptive Retrieval enables the system to autonomously decide when to retrieve new information based on generation confidence, using mechanisms like reflection tokens.
    ```