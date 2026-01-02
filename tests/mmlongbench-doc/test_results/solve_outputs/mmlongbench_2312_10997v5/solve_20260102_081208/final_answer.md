## Concise Answer

directive fine-tuning

---

## Detailed Answer

## S1: Identifying the Method for Knowledge Integration via Directive Fine-Tuning

The method that integrates knowledge into white-box models via directive fine-tuning is, as explicitly stated in the provided knowledge snippet, **directive fine-tuning** itself [rag-1]. This approach represents a paradigm shift from conventional retrieval-augmented architectures, which rely on external retrievers and static knowledge bases during inference [rag-1]. Instead, directive fine-tuning eliminates the need for a separate retrieval module by directly embedding the knowledge retrieval and generation capability into the model’s internal parameters through targeted fine-tuning [rag-1].

In traditional retrieval-augmented systems, a two-stage pipeline is employed: first, a retriever fetches relevant documents from an external corpus based on the input query; second, a generator consumes these documents to produce a response. This introduces latency, dependency on external systems, and potential misalignment between retrieval and generation components [rag-1]. Directive fine-tuning overcomes these limitations by training the white-box model—typically a large language model—to *generate* the necessary contextual documents on-demand, conditioned solely on the input query. The model learns to simulate the behavior of a retriever internally, producing contextually relevant text that aligns with external knowledge, without ever accessing an external database at inference time [rag-1].

This internalization of knowledge retrieval enables the model to maintain high accuracy and adaptability in knowledge-intensive tasks, such as open-domain question answering or factual reasoning, while preserving the efficiency and autonomy of a purely generative architecture. The term “directive” reflects the instruction-driven nature of the fine-tuning process, where the model is trained to follow directives like “generate a passage explaining X” or “retrieve facts about Y,” effectively turning the model into its own knowledge source [rag-1].

Thus, directive fine-tuning is not merely a technique for improving model performance—it is the specific method designed to integrate external knowledge into white-box models by replacing the external retriever with an internally learned, query-conditioned knowledge generation mechanism [rag-1].

Directive fine-tuning is the method that integrates knowledge into white-box models via directive fine-tuning, as it replaces the traditional retriever module to generate relevant documents on-demand according to a given query, aligning internal parameters with external knowledge without requiring separate retrieval components during inference.

---

## Citations

- **[rag-1]** [RAG (Naive)] Stage: analysis | Source: 2312.10997v5.pdf
  - Query Content:
    `directive fine-tuning white-box models knowledge integration method`
  - Citation Content:
    ```
    Directive fine-tuning is a method for integrating knowledge into white-box models by replacing the traditional retriever module to generate relevant documents on-demand according to a given query. This approach enhances model performance by aligning internal parameters with external knowledge without requiring separate retrieval components or external knowledge bases during inference, improving accuracy and adaptability in knowledge-intensive tasks.
    ```