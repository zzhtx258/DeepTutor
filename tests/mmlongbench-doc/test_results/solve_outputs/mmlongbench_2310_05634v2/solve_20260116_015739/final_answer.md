## Concise Answer

Evolutionary Question Generation

---

## Detailed Answer

## S1: Comparative Analysis of Description Detail Across Dataset Construction Steps

In the context of the BioKaLMA dataset construction pipeline, the process is structured into three core iterative stages: **Person Selection**, **Name Disambiguation**, and **Evolutionary Question Generation** [rag-1]. While all steps are essential to the pipeline’s integrity, a qualitative comparison of their descriptive elaboration reveals that **Evolutionary Question Generation** is described with significantly greater depth and technical specificity than the other two.

This step involves not only the generation of questions but also an iterative refinement mechanism powered by Large Language Models (LLMs). It employs a composite scoring function, denoted as $Score_r$, which balances two key dimensions: *informativeness* and *readability* [rag-1]. The process may undergo up to five iterations to optimize question quality, culminating in the production of a **Minimum Knowledge Set** intended for downstream evaluation purposes. Furthermore, this phase references supplementary materials — specifically Appendix E — indicating additional algorithmic or implementation details beyond the main text [rag-1].

In contrast, the descriptions of **Person Selection** and **Name Disambiguation** are comparatively concise, lacking explicit mention of scoring functions, iteration counts, or cross-references to appendices. This suggests that while these steps are foundational, they are presented at a higher level of abstraction without the same degree of procedural or evaluative granularity.

Thus, based on the available documentation, **Evolutionary Question Generation** stands out as the most thoroughly described step in the dataset construction pipeline, both in terms of conceptual scope and technical exposition.

### Summary
The Evolutionary Question Generation step is the most verbose and technically detailed among the three stages of the BioKaLMA dataset construction pipeline, featuring algorithmic components, scoring metrics, iteration limits, and external references — making it the step that takes the most words to describe.

---

## Citations

- **[rag-1]** [RAG (Hybrid)] Stage: analysis | Source: Appendix A, Appendix C, Appendix E, Table 1, Human Evaluation Scores for BioKaLMA Dataset Questions (table)
  - Query Content:
    ```
    What are the steps involved in dataset construction and how are they described in detail?
    ```
  - Citation Content:
    ```
    Among the three steps in the BioKaLMA dataset construction pipeline — Person Selection, Name Disambiguation, and Evolutionary Question Generation — the third step, Evolutionary Question Generation, is described in the most detail. It involves iterative knowledge injection using LLMs, a composite scoring function (Score_r) balancing informativeness and readability, up to five iterations, and produces a Minimum Knowledge Set for evaluation. This step includes algorithmic details, scoring components, and references to appendices (Appendix E), making it the most verbose and technically elaborated phase.
    ```