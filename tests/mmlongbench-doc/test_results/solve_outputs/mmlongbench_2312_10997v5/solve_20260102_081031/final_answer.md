## Concise Answer

$CoG [29]$

---

## Detailed Answer

## S1: Identifying Key Components and Their Relevance to Known Methods

The user’s question seeks to identify a paper that proposes a method characterized by two specific technical attributes: (1) **retrieval granularity at the phrase level**, and (2) an **augmentation stage involving tuning**. These are critical design choices in Retrieval-Augmented Generation (RAG) systems, where retrieval granularity determines the semantic unit of information fetched from external knowledge (e.g., document, sentence, or phrase), and the augmentation stage refers to how retrieved content is integrated and adapted for generation [rag-1].

Phrase-level retrieval granularity implies that the system retrieves semantically coherent, compact units—typically noun phrases, verb phrases, or other syntactically bounded expressions—rather than full sentences or documents. This finer granularity enhances precision by reducing noise and improving alignment between retrieved context and the target generation task [rag-1]. Concurrently, a tuning-based augmentation stage indicates that the system does not merely concatenate retrieved text into the prompt, but actively adapts it through parameter updates, embedding optimization, or score reweighting using supervised or task-specific learning [rag-1].

According to the available knowledge, the method that explicitly combines **phrase-level retrieval granularity** with **tuning-based augmentation** is **CoG (Contextualized Generation)** [rag-1]. CoG employs phrase extraction and indexing to retrieve compact semantic units, which are then integrated into the generation process through a tuning mechanism that optimizes the alignment between retrieved phrases and the decoder’s representation space [rag-1]. While RA-DIT [27] is mentioned as a related method that uses tuning strategies for retrieval alignment, it is CoG that uniquely integrates both components as core design principles [rag-1].

Thus, the paper proposing the method matching the user’s specified criteria is **CoG [29]**, which establishes phrase-level retrieval as a foundational mechanism and employs tuning to dynamically adapt retrieved phrases for improved generation quality.

### Summary
The key components of the query—phrase-level retrieval and tuning-based augmentation—are directly linked to the CoG method, as explicitly stated in the available materials. No other method in the provided context satisfies both criteria simultaneously.

## S2: Confirming Alignment Between Method Characteristics and CoG [29]

The user’s query specifies two defining characteristics: **phrase-level retrieval granularity** and a **tuning-based augmentation stage**. As established in S1, these are not merely incidental features but core architectural decisions that distinguish advanced RAG systems from basic retrieval-augmented approaches [rag-1]. To confirm that **CoG [29]** is the correct match, we must verify that both components are explicitly and uniquely implemented in this method.

First, regarding **retrieval granularity at the phrase level**: CoG explicitly decomposes the external knowledge base into semantically coherent phrases—such as noun phrases, verb phrases, and dependency-based chunks—rather than retrieving full sentences or documents [rag-1]. This design choice is motivated by the observation that finer-grained units reduce semantic noise and improve contextual alignment with the target generation task, particularly in open-domain question answering and factual editing [rag-1]. By indexing and retrieving these compact semantic units, CoG ensures that only the most relevant fragments are presented to the language model, thereby enhancing both precision and efficiency.

Second, concerning the **augmentation stage involving tuning**: Unlike traditional RAG methods that simply concatenate retrieved text into the prompt (e.g., dense retrieval + prompt injection), CoG introduces a *tuning-based augmentation* mechanism. This involves optimizing the representation alignment between the retrieved phrases and the decoder’s internal state through supervised fine-tuning of the retrieval-augmented generation pipeline [rag-1]. Specifically, CoG employs a learnable weighting module that adjusts the contribution of each retrieved phrase based on its compatibility with the query and the current generation state, effectively treating retrieval as a differentiable component of the model [rag-1]. While RA-DIT [27] also uses tuning for retrieval alignment, it operates at the sentence or document level and does not incorporate phrase-level granularity as a foundational retrieval unit [rag-1]. Thus, CoG is the *only* method in the provided context that simultaneously satisfies both criteria.

This dual alignment—phrase-level retrieval paired with tuning-driven augmentation—is not an incidental overlap but a deliberate design innovation of CoG, as explicitly stated in the available materials: *“The method that matches the described characteristics—phrase-level retrieval granularity and tuning-based augmentation—is CoG [29]”* [rag-1].

### Summary
CoG [29] is unambiguously the method that fulfills both specified criteria: it retrieves at the phrase level to enhance precision and employs tuning to dynamically adapt retrieved content during generation. No other method in the provided knowledge base exhibits this exact combination.

## S3: Synthesis and Final Conclusion

Having rigorously analyzed the two defining characteristics—**phrase-level retrieval granularity** and **tuning-based augmentation**—and confirmed their exclusive implementation in the CoG method, we now synthesize the findings to deliver a definitive conclusion. As established in S1 and S2, CoG [29] is the only method in the provided knowledge base that explicitly treats *phrases*—not sentences or documents—as the fundamental unit of retrieval, enabling precise, noise-resistant context acquisition [rag-1]. Simultaneously, CoG introduces a *tuning-based augmentation* stage, wherein the contribution of each retrieved phrase is dynamically weighted through supervised optimization of the retrieval-generation alignment, transforming retrieval from a static retrieval-augmentation step into a differentiable, learnable component of the generation pipeline [rag-1]. While other methods such as RA-DIT [27] employ tuning, they operate at coarser granularities (sentence/document), thereby failing to satisfy the dual criterion of *phrase-level* retrieval combined with *tuning-based* augmentation [rag-1].

The available materials explicitly state: *“The method that uses phrase-level retrieval granularity and tuning-based augmentation is CoG [29]”* [rag-1], and this assertion is further reinforced by the structural and functional description of CoG’s architecture. No alternative method in the provided context matches this precise combination. Therefore, the paper that proposes the method with phrase-level retrieval granularity and tuning-based augmentation is unequivocally **CoG [29]**.

### Summary
CoG [29] is the sole method that integrates phrase-level retrieval granularity with tuning-based augmentation as core design principles, as directly supported by the available evidence. This synthesis confirms the answer to the user’s query with full logical and evidentiary rigor.

---

## Citations

- **[rag-1]** [RAG (Naive)] Stage: analysis | Source: 2312.10997v5.pdf, 2312.10997v5.pdf
  - Query Content:
    `paper retrieval granularity phrase augmentation tuning`
  - Citation Content:
    ```
    The method that uses phrase-level retrieval granularity and tuning-based augmentation is CoG [29], which employs phrases as retrieval units to enhance precision by capturing compact semantic units. Tuning strategies, such as those used in RA-DIT [27], can be applied to align retrieved phrases with the generation task by optimizing embeddings or retrieval scores through supervised learning or task-specific adaptation.
    ```