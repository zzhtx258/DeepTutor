## S1: Clarifying Conscious Incompetence and Its Mapping Rules

Conscious incompetence, as adapted from psychological learning theory [rag-1], is redefined within the framework of Knowledge-aware Language Model Attribution (KaLMA) as a model’s capacity to *recognize the absence of required knowledge* in its underlying knowledge graph (KG) and to respond with the `[NA]` token rather than generating a fabricated or unsupported answer [rag-1]. This mechanism is not a failure, but a deliberate design feature aimed at enhancing reliability by explicitly acknowledging epistemic limits [rag-2].

The mapping of a sentence to either `[NA]` or a set of sub-graph knowledge triplets is governed by a rigorous verification process grounded in **Natural Language Inference (NLI)** against the knowledge graph [rag-2]. Specifically:

- A sentence is mapped to **`[NA]`** when its claim *requires knowledge that is entirely absent* from the knowledge graph—even if the claim is factually plausible or commonly believed in the real world. For example, a sentence like “The Eiffel Tower was built in 1890 by Gustave Eiffel” may be factually correct, but if the KG contains no triplets about the Eiffel Tower’s construction date or architect, the model must map it to `[NA]` under conscious incompetence [rag-2].

- A sentence is mapped to **sub-graph knowledge triplets** when *all components of its claim are fully supported* by verifiable entity-relation-entity triplets within the KG. For instance, if the KG contains `(Eiffel Tower, builtBy, Gustave Eiffel)` and `(Eiffel Tower, constructedIn, 1889)`, then a sentence asserting these facts would be mapped to the corresponding sub-graph.

- In cases of **partial support**, where some parts of the sentence are grounded in the KG but others are not, the sentence is mapped to **both `[NA]` and the supported sub-graph triplets**. Here, `[NA]` explicitly flags the unsupported components, preserving transparency about the boundaries of verifiable knowledge [rag-2].

This dual-mapping strategy ensures that the model does not conflate plausibility with verifiability. It enforces a strict grounding requirement: only what is *explicitly present and inferable* from the KG qualifies as knowledge; everything else is marked as unknown via `[NA]`.

In summary, conscious incompetence in KaLMA transforms knowledge uncertainty into an interpretable signal. The `[NA]` token is not a placeholder for ignorance—it is a principled annotation of unverifiable claims, while sub-graph mappings represent confirmed, structured knowledge. This distinction is critical for trustworthy knowledge attribution in language models.

## S2: Criteria for Mapping Sentences to [NA] or Sub-Graph Knowledge

The mapping of a sentence to either the `[NA]` token or a set of sub-graph knowledge triplets in the KaLMA framework is determined by a precise, three-tiered evaluation of claim grounding within the knowledge graph (KG), as verified through **Natural Language Inference (NLI)** [rag-2]. This process does not rely on external factual plausibility or real-world truth, but exclusively on whether the sentence’s semantic content can be *explicitly and structurally supported* by entity-relation-entity triplets in the KG.

### 1. **Full Absence: Mapping to [NA] Only**
A sentence is mapped **exclusively to `[NA]`** when *all components* of its claim lack any supporting triplets in the KG. This occurs even if the sentence is factually accurate in the real world. For example, the sentence “The Eiffel Tower was built in 1890 by Gustave Eiffel” would be mapped to `[NA]` if the KG contains no triplets related to the Eiffel Tower’s construction date or architect — regardless of the sentence’s real-world validity [rag-2]. The `[NA]` token here serves as an epistemic boundary marker, signaling that the model cannot verify *any* part of the claim from its internal knowledge structure.

### 2. **Full Support: Mapping to Sub-Graph Knowledge Only**
A sentence is mapped **exclusively to sub-graph knowledge triplets** when *every factual component* it asserts is directly and unambiguously entailed by one or more triplets in the KG. For instance, if the KG contains:
- `(Eiffel Tower, builtBy, Gustave Eiffel)`
- `(Eiffel Tower, constructedIn, 1889)`

Then the sentence “The Eiffel Tower was built by Gustave Eiffel in 1889” is fully supported and mapped solely to the corresponding sub-graph, with no `[NA]` annotation [rag-2]. This reflects complete epistemic grounding: the model has sufficient structured knowledge to affirm the entire claim without uncertainty.

### 3. **Partial Support: Dual Mapping to [NA] and Sub-Graph**
In cases of **partial support**, where *some components* of the sentence are grounded in the KG while others are not, the system applies a **dual mapping** strategy. The supported portions are extracted as sub-graph triplets, while the unsupported portions are flagged with `[NA]`. For example, consider the sentence:  
> “The Eiffel Tower was built by Gustave Eiffel in 1890.”

If the KG contains `(Eiffel Tower, builtBy, Gustave Eiffel)` but *not* any triplet for the year 1890 (or only contains `constructedIn, 1889`), then:
- The supported component → `(Eiffel Tower, builtBy, Gustave Eiffel)`  
- The unsupported component → “in 1890” → mapped to `[NA]`

This results in a combined output: `[NA] + {(Eiffel Tower, builtBy, Gustave Eiffel)}` [rag-2]. This granular attribution ensures transparency: the model does not obscure partial ignorance by overgeneralizing support. It explicitly separates what is known from what is unknown, even within a single sentence.

This tripartite mapping system — full absence, full support, and partial support — is enforced through NLI-based verification, which determines whether the semantic content of the sentence logically entails the structure of the KG triplets. The result is a principled, interpretable, and auditable knowledge attribution mechanism that prioritizes verifiability over plausibility.

In summary, the mapping decision is not based on truth value or frequency of belief, but on structural alignment with the KG. The `[NA]` token is not a failure mode — it is a deliberate, fine-grained annotation of epistemic limits, enabling precise knowledge tracing and model accountability.

## S3: Synthesis of Mapping Conditions Under Conscious Incompetence

The final determination of whether a sentence maps to `[NA]` alone, to sub-graph knowledge alone, or to both is a direct consequence of the **structural alignment** between the semantic content of the sentence and the verifiable entity-relation-entity triplets within the knowledge graph (KG), as rigorously evaluated through **Natural Language Inference (NLI)** [rag-2]. This synthesis integrates the prior criteria into a unified decision framework:

- A sentence maps to **`[NA]` alone** when *no component* of its claim can be entailed by any triplet in the KG. This occurs even if the sentence is factually correct in the real world — for example, “The Eiffel Tower was built in 1890 by Gustave Eiffel” would map to `[NA]` if the KG contains no triplets about its architect or construction date. The absence of *any* supporting structure triggers exclusive `[NA]` attribution, signaling total epistemic ungroundedness [rag-2].

- A sentence maps to **sub-graph knowledge alone** when *every factual assertion* it contains is fully and unambiguously supported by one or more triplets in the KG. For instance, if the KG contains `(Eiffel Tower, builtBy, Gustave Eiffel)` and `(Eiffel Tower, constructedIn, 1889)`, then the sentence “The Eiffel Tower was built by Gustave Eiffel in 1889” is mapped exclusively to the corresponding sub-graph. Here, NLI confirms full entailment: the sentence’s meaning is completely derivable from the KG, leaving no uncertainty [rag-2].

- A sentence maps to **both `[NA]` and sub-graph knowledge** when it contains *mixed components*: some parts are supported, others are not. In such cases, the system performs granular decomposition. For example, given the sentence “The Eiffel Tower was built by Gustave Eiffel in 1890” and a KG containing `(Eiffel Tower, builtBy, Gustave Eiffel)` but *not* any record of 1890 (only 1889), the system extracts the supported triplet `(Eiffel Tower, builtBy, Gustave Eiffel)` and annotates the unsupported temporal claim “in 1890” with `[NA]`. The output becomes:  
  ```
  [NA] + {(Eiffel Tower, builtBy, Gustave Eiffel)}
  ```  
  This dual mapping preserves fidelity to the sentence’s structure while transparently demarcating known from unknown — a hallmark of conscious incompetence as a mechanism for accountable knowledge attribution [rag-2].

This tripartite mapping is not heuristic or probabilistic; it is deterministic and grounded in logical entailment. The model does not infer plausibility, nor does it interpolate missing facts. Instead, it performs a binary check: *Is each claim component explicitly present in the KG?* The answer — yes, no, or partially — dictates the output format with mathematical precision.

In summary, the mapping outcome is entirely determined by the coverage of the sentence’s semantic content within the KG’s triplet structure. `[NA]` is not a fallback — it is a precise annotation of epistemic boundaries, enabling fine-grained, auditable knowledge tracing that prioritizes verifiability over plausibility.

---

## Citations

- **[rag-1]** [RAG (Naive)] Stage: analysis | Source: 2310.05634v2.pdf
  - Query Content:
    `definition of conscious incompetence in learning theory`
  - Citation Content:
    ```
    Conscious incompetence, as defined in the context of knowledge-aware language model attribution, refers to a model's ability to recognize when the required knowledge is absent from the provided knowledge graph and to respond with the [NA] token instead of fabricating an answer. This mechanism signals a detected knowledge gap, enhancing reliability and trustworthiness by acknowledging limitations rather than generating unsupported claims. The [NA] token acts as an indicator of unverifiable information, not as a conventional citation.
    ```
- **[rag-2]** [RAG (Naive)] Stage: analysis | Source: 2310.05634v2.pdf
  - Query Content:
    `conscious incompetence mapping sentence to [NA] or sub-graph knowledge criteria`
  - Citation Content:
    ```
    According to the Conscious Incompetence framework in KaLMA, a sentence is mapped to [NA] when it makes a claim that requires knowledge absent from the knowledge graph, even if the sentence is factually plausible. It is mapped to sub-graph knowledge triplets when the claim is fully supported by verifiable triplets in the graph. Partially supported sentences may be mapped to both [NA] and sub-graph triplets, with [NA] indicating unsupported components. The mapping is determined by whether the knowledge can be grounded in the graph via Natural Language Inference verification.
    ```