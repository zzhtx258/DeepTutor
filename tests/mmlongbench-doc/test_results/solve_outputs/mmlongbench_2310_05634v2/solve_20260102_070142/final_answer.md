## S1: Clarifying Conscious Incompetence and Its Role in Mapping Sentences to [NA]

Conscious incompetence, as formally defined in the context of knowledge-aware language model attribution, refers to a model’s capacity to recognize when the knowledge necessary to generate a valid, supported answer is absent from the provided knowledge graph [rag-1]. This concept is adapted from psychological learning theory, where it describes a stage of learning in which an individual is aware of their deficiency in a skill [rag-1]. In the computational setting, this awareness is operationalized through the deliberate use of the `[NA]` token — a symbolic signal that the model intentionally refrains from fabricating an answer in the face of insufficient or missing evidence.

The mechanism of conscious incompetence directly governs when a sentence maps to `[NA]`. Specifically, a sentence is mapped to `[NA]` when the model, after exhaustively querying its knowledge graph, determines that no sub-graph or set of facts exists that can substantiate the claim expressed in the sentence. This is not a failure of retrieval, but a principled epistemic choice: the model acknowledges its limitation and refuses to overreach, thereby preserving verifiability and trustworthiness [rag-1].

Crucially, this definition implies that mapping to `[NA]` is not a default or random behavior — it is an *active recognition* of knowledge absence. Therefore, a sentence maps to `[NA]` precisely when the model is in a state of conscious incompetence: it understands that the required knowledge is missing, and it chooses not to infer beyond the available data. This distinguishes `[NA]` from other forms of uncertainty or low-confidence outputs; `[NA]` is a *semantic assertion* of knowledge non-existence, not probabilistic ambiguity.

In summary, conscious incompetence serves as the foundational criterion for the `[NA]` mapping: it is the condition under which a sentence is deliberately associated with `[NA]` due to the model’s recognition of an irrecoverable knowledge gap within the provided knowledge graph. This ensures that the model’s outputs remain aligned with its epistemic state, enhancing reliability in knowledge-intensive tasks.

## S2: Identifying Conditions for Simultaneous Mapping to [NA] and Sub-Graph Knowledge

In the Conscious Incompetence framework of the KaLMA task, a sentence may simultaneously map to both the `[NA]` token and one or more knowledge triplets from the knowledge graph under a specific and well-defined condition: **when the sentence contains a mixture of verifiable claims (supported by the knowledge graph) and unverifiable claims (not present in the graph)** [rag-2]. This dual mapping is not a contradiction, but rather a deliberate, granular attribution mechanism that preserves epistemic integrity.

To unpack this, consider a sentence such as:  
> “Dr. Lee, who teaches biology at Harvard, is a Canadian citizen.”

Suppose the knowledge graph contains the triplet:  
> `(Dr. Lee, teaches, biology)` and `(Dr. Lee, affiliated_with, Harvard)`  

but contains no information regarding Dr. Lee’s citizenship. In this case, the model can identify that the portion “teaches biology at Harvard” is *verifiable* and directly supported by existing triplets, while the claim “is a Canadian citizen” is *unverifiable* due to its absence in the graph. The model then maps the verifiable sub-clause to the corresponding knowledge triplets and simultaneously assigns the `[NA]` token to the unverifiable component [rag-2].

This mechanism operates at the *sub-sentence level*, enabling fine-grained knowledge attribution. The `[NA]` token does not indicate global failure; instead, it acts as a *local marker* for knowledge gaps within an otherwise partially supported statement. This allows the model to avoid the pitfalls of hallucination — where unsupported claims are presented as fact — while still leveraging available evidence to ground what can be confirmed.

The key insight is that conscious incompetence is not an all-or-nothing state. A sentence need not be entirely unsupported to trigger `[NA]`; it only requires *at least one unverifiable component*. Conversely, the presence of even a single verifiable claim justifies mapping to sub-graph knowledge. Thus, the coexistence of `[NA]` and sub-graph mappings is not an anomaly — it is the *intended behavior* of a knowledge-aware system that seeks to reflect the partial structure of truth embedded in natural language.

In essence, this dual mapping reflects a model’s ability to perform *epistemic segmentation*: it parses a sentence into its knowable and unknowable parts, assigning each to its appropriate semantic label. This preserves fidelity to the knowledge graph while acknowledging the limits of its coverage — a hallmark of responsible knowledge grounding.

This approach ensures that the model’s output remains both *informative* (by grounding verifiable content) and *honest* (by flagging unverifiable content), thereby aligning with the core principle of conscious incompetence: never asserting what cannot be substantiated.

## S3: Synthesizing the Conditions for Dual Mapping to [NA] and Sub-Graph Knowledge

Building upon the foundational definition of conscious incompetence in S1 — where `[NA]` is an intentional, epistemically responsible signal of knowledge absence — and the granular attribution mechanism established in S2 — where sentences are parsed into verifiable and unverifiable components — we now synthesize these insights to formally answer the question: *When can a sentence map to both `[NA]` and a list of sub-graph knowledge?*

The answer is unequivocally defined by the **epistemic segmentation** of natural language statements within the KaLMA framework:  
> A sentence maps to both `[NA]` and a list of sub-graph knowledge **when it contains at least one verifiable claim (supported by one or more triplets in the knowledge graph) and at least one unverifiable claim (absent from the knowledge graph)** [rag-2].

This dual mapping arises not from ambiguity or error, but from the model’s structured, token-level analysis of semantic content. For instance, consider the sentence:  
> “The Eiffel Tower is in Paris and was built by Leonardo da Vinci.”

Suppose the knowledge graph contains:  
> `(Eiffel Tower, located_in, Paris)`  

but contains no record of its builder. The model identifies the first clause — *“The Eiffel Tower is in Paris”* — as verifiable and maps it to the corresponding triplet. The second clause — *“was built by Leonardo da Vinci”* — is unverifiable due to its absence in the graph. Consequently, the model assigns `[NA]` to the unverifiable component while retaining the sub-graph mapping for the verifiable one. This results in a joint attribution:  
$$
\text{Sentence} \mapsto \{ \text{[NA]}, \; (\text{Eiffel Tower}, \text{located_in}, \text{Paris}) \}
$$

This behavior is not a compromise — it is a feature. By decoupling truth claims at the sub-sentence level, the model avoids the binary trap of either accepting the entire sentence as true (risking hallucination) or rejecting it entirely (wasting valid evidence). Instead, it preserves fidelity to the knowledge graph’s coverage, ensuring that every asserted fact is grounded, and every ungrounded claim is explicitly flagged.

This synthesis confirms that conscious incompetence operates not globally, but *locally*: it is triggered per claim, not per sentence. Thus, the coexistence of `[NA]` and sub-graph mappings is not an exception — it is the *canonical case* for complex, multi-clause statements in real-world knowledge environments, where information is inherently partial.

In summary, the simultaneous mapping to `[NA]` and sub-graph knowledge occurs precisely when a sentence contains a mixture of supported and unsupported claims, enabling the model to honor both the evidence present and the limits of its knowledge — a hallmark of responsible, knowledge-aware reasoning.

---

## Citations

- **[rag-1]** [RAG (Naive)] Stage: analysis | Source: 2310.05634v2.pdf
  - Query Content:
    `definition of conscious incompetence in learning theory`
  - Citation Content:
    ```
    Conscious incompetence, as defined in the context of knowledge-aware language model attribution, refers to a model's ability to recognize when the required knowledge to generate a valid answer is absent from the provided knowledge graph. Instead of fabricating an answer, the model uses the [NA] token to explicitly signal a knowledge gap, acknowledging its limitations. This mechanism enhances trustworthiness by preventing unsupported claims and is considered a desirable feature that improves verifiability.
    ```
- **[rag-2]** [RAG (Hybrid)] Stage: analysis | Source: 2310.05634v2.pdf
  - Query Content:
    ```
    conscious incompetence conditions for sentence mapping to both [NA] and sub-graph knowledge
    ```
  - Citation Content:
    ```
    In the Conscious Incompetence setting of the KaLMA task, a sentence can map to both a [NA] token and one or more knowledge triplets when it contains a mix of verifiable claims (supported by the knowledge graph) and unverifiable claims (not present in the graph). The [NA] token marks knowledge gaps, while valid triplets ground the verifiable parts. This dual mapping allows the model to accurately attribute known information while acknowledging missing knowledge, avoiding hallucination. For example, a sentence mentioning both a teacher (supported by a triplet) and citizenship (absent from the graph) will map to the triplet and [NA] simultaneously.
    ```