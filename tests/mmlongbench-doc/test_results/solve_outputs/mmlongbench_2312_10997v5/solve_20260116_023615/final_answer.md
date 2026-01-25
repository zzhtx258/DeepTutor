## Concise Answer

PKG

---

## Detailed Answer

## S1: Identification of the Method for Integrating Knowledge via Directive Fine-Tuning in White-Box Models

The method that integrates knowledge into white-box models through directive fine-tuning is **PKG (Parametric Knowledge Guiding)** [rag-1]. This approach operates by substituting the retriever module within a model architecture to directly generate contextually relevant documents based on input queries. By doing so, PKG enables the structured or external knowledge to be injected into the model in a targeted and instruction-aligned manner.

Directive fine-tuning, as implemented in PKG, allows for precise adaptation of specific model components — particularly the retriever — to conform with task-specific directives. This modularity is especially advantageous in white-box models, where internal structures are transparent and accessible, facilitating controlled and interpretable knowledge integration.

In essence, PKG transforms the retrieval process from a black-box operation into a parametric, trainable component that can be fine-tuned according to explicit instructions, thereby enhancing both performance and interpretability in knowledge-intensive tasks.

This method is distinct from general fine-tuning or retrieval-augmented generation (RAG) approaches because it explicitly targets the retriever module for parametric adaptation under directive guidance, making it uniquely suited for white-box architectures where component-level control is required [rag-1].

### Summary
PKG (Parametric Knowledge Guiding) is the identified method that enables knowledge integration into white-box models via directive fine-tuning, primarily through substitution and adaptation of the retriever module to align with task-specific instructions.

---

## Citations

- **[rag-1]** [RAG (Hybrid)] Stage: analysis | Source: Raw Search Result, Raw Search Result
  - Query Content:
    ```
    What methods integrate knowledge into white-box models via directive fine-tuning?
    ```
  - Citation Content:
    ```
    The method that integrates knowledge into white-box models via directive fine-tuning is PKG (Parametric Knowledge Guiding). It substitutes the retriever module to directly generate relevant documents based on queries, enabling structured or external knowledge integration. This directive fine-tuning allows targeted adaptation of model components—especially the retriever—to align with task-specific instructions, making it suitable for white-box models where modularity supports precise knowledge injection.
    ```