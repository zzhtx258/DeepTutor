## S1: Identify the Most Extensively Described Step in Dataset Construction

In the dataset construction process for BioKaLMA, three core steps are sequentially executed: **Person Selection**, **Name Disambiguation**, and **Evolutionary Question Generation** [rag-1]. To determine which step is most extensively described, we compare the depth and technical detail afforded to each phase.

Person Selection involves identifying relevant individuals from a source corpus, typically based on predefined criteria such as prominence or relevance to a domain. This step is described concisely, focusing on filtering heuristics rather than algorithmic complexity [rag-1]. Name Disambiguation follows, resolving ambiguities in entity references (e.g., distinguishing between multiple individuals with the same name), which requires matching algorithms and contextual analysis—but remains relatively compact in its exposition [rag-1].

In contrast, **Evolutionary Question Generation** is described in significantly greater depth. This step is iterative and algorithmically sophisticated, leveraging large language models (LLMs) to generate and refine questions over multiple rounds [rag-1]. It employs a composite scoring function that evaluates generated questions along two key dimensions: *specificity* (how precisely the question targets a unique fact) and *coherence* (how logically and linguistically sound the question is) [rag-1]. Furthermore, the process incorporates detailed templates for prompt engineering, feedback loops for question refinement, and mechanisms for diversity preservation across generations—all of which contribute to its extensive documentation [rag-1].

The richness of this description stems from its hybrid nature: it combines elements of automated generation, human-in-the-loop evaluation, and multi-objective optimization—making it not only the most complex but also the most thoroughly articulated phase in the entire pipeline.

### Summary
Among the three steps in BioKaLMA’s dataset construction, **Evolutionary Question Generation** is unequivocally the most extensively described, due to its iterative LLM-driven design, multi-criteria scoring mechanism, and intricate templating system [rag-1].

---

## Citations

- **[rag-1]** [RAG (Naive)] Stage: analysis | Source: 2310.05634v2.pdf
  - Query Content:
    `dataset construction steps description length comparison`
  - Citation Content:
    ```
    In the dataset construction process for BioKaLMA, the Evolutionary Question Generation step is the most extensively described, followed by Name Disambiguation, and then Person Selection. This is due to its iterative, algorithmically complex design involving LLMs, a composite scoring function based on specificity and coherence metrics, and detailed templates for question generation, making it the longest and most technically detailed phase.
    ```