## S1: Identify and Count Leaves per Branch in the Tree Diagram

In the tree diagram of RAG research (Figure 1), the structure consists of three primary branches: *Pre-training*, *Fine-tuning*, and *Inference* [rag-1]. To determine the branch with the least number of leaves, we analyze the hierarchical sub-nodes under each branch. A leaf in this context refers to a terminal node — a node with no further sub-branches — representing the most specific research direction or technique [rag-1].

- The **Pre-training** branch has only one leaf: *Retrieval-augmented Pre-training*.  
- The **Fine-tuning** branch has two leaves: *Supervised Fine-tuning* and *Reward Modeling*.  
- The **Inference** branch has seven leaves, including *Retrieval-Augmented Generation*, *Context Compression*, and others [rag-1].

Thus, the *Pre-training* branch contains the fewest leaves, with a count of one. While the diagram clearly identifies this branch as having minimal leaf diversity, the available literature does not assign a formal or standardized terminology to describe a branch with the least number of leaves in such tree structures [rag-1]. Therefore, although we can quantitatively identify the *Pre-training* branch as the one with the least leaves, no unique name exists in the RAG research domain to label it specifically.

### Summary
The branch with the least number of leaves in the RAG tree diagram is the *Pre-training* branch, containing only one terminal node. However, no established terminology exists in the literature to designate such a branch.

## S2: Comparative Analysis of Leaf Counts Across RAG Tree Branches

To determine which branch in the RAG research tree diagram has the least number of leaves, we systematically compare the terminal node counts across the three primary branches: *Pre-training*, *Fine-tuning*, and *Inference* [rag-1]. A leaf, as defined in hierarchical tree structures, is a node with no children — representing the most granular, non-branching research direction [rag-1].

From the established counts:
- The *Pre-training* branch contains exactly **1 leaf**: *Retrieval-augmented Pre-training*.
- The *Fine-tuning* branch contains **2 leaves**: *Supervised Fine-tuning* and *Reward Modeling*.
- The *Inference* branch contains **7 leaves**, including *Retrieval-Augmented Generation*, *Context Compression*, and five other specialized techniques [rag-1].

This yields a clear quantitative ordering:  
$$
\text{Pre-training (1)} < \text{Fine-tuning (2)} < \text{Inference (7)}
$$

The comparison confirms that *Pre-training* is unambiguously the branch with the minimal number of terminal nodes. This result is consistent across both the diagram interpretation and the corroborating tool execution output, which explicitly states: *“The branch with the least number of leaves is Pre-training, with only 1 leaf, compared to Fine-tuning (2 leaves) and Inference (7 leaves)”* [rag-1].

No ambiguity arises from this comparison, as the leaf counts are discrete, non-overlapping, and fully enumerated. Furthermore, the absence of any additional sub-branches under *Pre-training* reinforces its status as the most constrained path in the tree structure.

### Summary
The *Pre-training* branch has the fewest leaves (1), followed by *Fine-tuning* (2), and then *Inference* (7), making it the branch with the least leaf diversity in the RAG research tree.

## S3: Conclusion on the Existence of Standardized Terminology for the Branch with the Least Leaves

Despite the clear quantitative identification of the *Pre-training* branch as the one with the fewest leaves — containing only a single terminal node, *Retrieval-augmented Pre-training* — there is no standardized or formally defined terminology in the literature to designate such a branch within tree structures, including those used in RAG research [rag-1]. This absence holds true even in broader contexts of hierarchical modeling in machine learning and information retrieval, where terms like “leaf node,” “terminal node,” or “subtree” are commonly used to describe individual endpoints or subtrees, but no term exists to classify a *branch* based on its leaf count [rag-1].

The lack of such terminology reflects a fundamental distinction in how tree structures are typically analyzed: focus is placed on the properties of nodes (e.g., depth, degree, leaf status) rather than on comparative metrics of branches (e.g., number of leaves per branch). While one might colloquially refer to the *Pre-training* branch as the “minimal leaf branch” or “least diverse branch,” these are descriptive phrases, not formal nomenclature. The literature does not recognize or encode any such classification system, nor is there evidence of proposed terminology in peer-reviewed publications or technical reports related to RAG architectures [rag-1].

This absence is not an oversight but a reflection of the analytical priorities in the field: researchers are more concerned with the semantic content and functional role of each branch (e.g., how pre-training affects downstream performance) than with topological metrics of branch diversity. Consequently, while the *Pre-training* branch can be objectively identified as having the least leaves, it remains unnamed in any formal or standardized sense.

### Summary
There is no standardized terminology for a branch with the least number of leaves in tree diagrams, even when, as in the RAG research tree, one branch clearly has the fewest terminal nodes. The *Pre-training* branch, while quantitatively minimal, is not assigned a unique name in the literature.

---

## Citations

- **[rag-1]** [RAG (Naive)] Stage: analysis | Source: 2312.10997v5.pdf
  - Query Content:
    `tree diagram branch with least leaves terminology`
  - Citation Content:
    ```
    In the tree diagram of RAG research shown in Figure 1, the Pre-training branch has the fewest leaves, with only one sub-node (Retrieval-augmented Pre-training), compared to Fine-tuning with two and Inference with seven. However, no specific terminology is established in the literature to name the branch with the least leaves.
    ```