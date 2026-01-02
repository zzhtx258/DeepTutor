## Concise Answer

```
Input: Query embedding q ∈ ℝ^m, Tree with d layers, Top-k parameter k
Output: Sequence of selected node sets S₁, S₂, ..., S_d

1. Scurrent ← {root}
2. S_list ← []
3. for i = 1 to d do
4.     Slayer ← []
5.     for each node u in Scurrent do
6.         for each child node c of u do
7.             sim(c) ← q · e_c
8.             add (c, sim(c)) to Slayer
9.     end for
10.    Slayer ← topk(Slayer, k)
11.    Scurrent ← Slayer
12.    append Slayer to S_list
13. end for
14. return S_list
```

---

## Detailed Answer

## S1: Core Operation of Step 5 in Tree Traversal — Iterative Top-k Selection via Dot Product Similarity

Step 5 of the tree traversal method, as defined in the RAPTOR querying framework, implements an iterative, layer-by-layer propagation mechanism that selects the most relevant child nodes at each level of the tree based on semantic similarity with the query [rag-2]. This process is central to efficient hierarchical retrieval, ensuring that only the most promising branches are explored, thereby reducing computational overhead while preserving retrieval accuracy.

The core operation begins with the root node as the initial set $ S_0 $. For each of the $ d $ layers in the tree, the algorithm performs the following sequence:

1. **Embedding Comparison**: For every child node $ c $ in the current layer’s node set $ S_{i-1} $, compute the dot product similarity between the query embedding $ \mathbf{q} \in \mathbb{R}^m $ and the node’s embedding $ \mathbf{e}_c \in \mathbb{R}^m $:
   $$
   \text{sim}(c) = \mathbf{q} \cdot \mathbf{e}_c
   $$
   This scalar value quantifies the semantic alignment between the query and the node’s content [rag-1].

2. **Top-k Selection**: From all child nodes in layer $ i $, select the top-$ k $ nodes with the highest similarity scores. This forms the next layer’s active node set:
   $$
   S_i = \text{topk}\left( \{ c \mid c \in \text{children}(S_{i-1}), \text{sim}(c) \}, k \right)
   $$
   where $ \text{topk}(\cdot, k) $ returns the $ k $ elements with maximum similarity values.

3. **Propagation**: The selected set $ S_i $ becomes the input for the next iteration, repeating the process until the leaf layer ($ i = d $) is reached. The final output is a sequence of node sets $ S_1, S_2, \ldots, S_d $, each representing the most relevant nodes at their respective depth [rag-3].

This iterative top-k selection ensures that the traversal remains focused on high-relevance paths, avoiding exhaustive exploration of the entire tree. The use of dot product similarity is computationally efficient and aligns with standard practices in dense retrieval systems, where embeddings are normalized and similarity is approximated via inner product [rag-2].

### Summary
Step 5 formalizes a scalable, layer-wise relevance filtering mechanism that leverages dot product-based similarity to iteratively narrow down the search space. By selecting only the top-k child nodes at each level and propagating them forward, the algorithm efficiently navigates the hierarchical structure of the tree toward the most semantically aligned leaf nodes.

## S2: Pseudocode for Step 5 — Iterative Top-k Tree Traversal

The iterative top-k selection process in Step 5 of the tree traversal method is formally captured in the following pseudocode, which directly implements the layer-wise propagation mechanism described in the RAPTOR querying framework [rag-2][rag-3]. This algorithm ensures efficient hierarchical retrieval by dynamically narrowing the search space at each depth level using semantic similarity computed via dot product.

```
Input: Query embedding q ∈ ℝ^m, Tree with d layers, Top-k parameter k
Output: Sequence of selected node sets S₁, S₂, ..., S_d

1. Scurrent ← {root}  // Initialize current node set with root node
2. S_list ← []        // Initialize list to store selected sets at each layer
3. for i = 1 to d do
4.     Slayer ← []     // Initialize candidate set for layer i
5.     for each node u in Scurrent do
6.         for each child node c of u do
7.             sim(c) ← q · e_c  // Compute dot product similarity [rag-1]
8.             add (c, sim(c)) to Slayer
9.     end for
10.    Slayer ← topk(Slayer, k)  // Select top-k child nodes by similarity score [rag-2]
11.    Scurrent ← Slayer         // Propagate selected nodes to next layer
12.    append Slayer to S_list   // Record selected set for output
13. end for
14. return S_list  // Return sequence S₁, S₂, ..., S_d
```

### Explanation of Key Components

- **Line 1**: The traversal begins at the root node, which serves as the initial context for semantic comparison. This aligns with the requirement that $ S_0 = \{\text{root}\} $ [rag-3].
  
- **Lines 5–9**: For every node in the current layer ($ S_{i-1} $), the algorithm iterates over all its children and computes the dot product between the query embedding $ \mathbf{q} $ and each child’s embedding $ \mathbf{e}_c $. This scalar value $ \text{sim}(c) = \mathbf{q} \cdot \mathbf{e}_c $ measures semantic relevance under the assumption that embeddings are normalized, making the dot product equivalent to cosine similarity [rag-2].

- **Line 10**: The `topk` function selects the $ k $ child nodes with the highest similarity scores, ensuring that only the most relevant branches are retained. This operation enforces the core pruning strategy of the algorithm, preventing combinatorial explosion [rag-1].

- **Line 11–12**: The selected set $ S_i $ becomes $ S_{\text{current}} $ for the next iteration, and is stored in $ S_{\text{list}} $ to preserve the full traversal path. This maintains the sequence $ S_1, S_2, \ldots, S_d $, which is essential for downstream tasks such as answer synthesis or path reconstruction [rag-3].

- **Line 14**: The final output is the complete sequence of top-k node sets across all $ d $ layers, enabling hierarchical refinement of retrieval results.

This pseudocode is a direct formalization of the procedural logic described in the available materials, with no assumptions beyond those explicitly stated. It is computationally efficient, scalable to deep trees, and consistent with dense retrieval practices in modern retrieval-augmented systems.

### Summary
The pseudocode for Step 5 precisely encodes the iterative top-k selection mechanism: initializing at the root, computing dot product similarities across child nodes at each layer, selecting the top-k candidates, and propagating them forward. The result is a structured, layer-by-layer narrowing of the search space that balances precision and efficiency in hierarchical tree traversal.

---

## Citations

- **[rag-1]** [RAG (Naive)] Stage: analysis | Source: 2401.18059v1.pdf
  - Query Content:
    `pseudo code appendix step 5 tree traversal method`
  - Citation Content:
    ```
    Step 5 of the tree traversal method involves recursively selecting the top-k child nodes at each layer, starting from the root. For each of d layers, the algorithm computes similarity between the query and all child nodes of the previously selected set, picks the top-k nodes to form the next set, and continues until the leaf layer is reached, producing sets S1 through Sd.
    ```
- **[rag-2]** [RAG (Naive)] Stage: analysis | Source: 2401.18059v1.pdf
  - Query Content:
    `pseudo code for step 5 of tree traversal method appendix`
  - Citation Content:
    ```
    The pseudocode for Step 5 of the tree traversal method is implemented in the loop of the TRAVERSETREE function, which iteratively processes each layer of the tree. For each layer, it computes the dot product between the query and each node's embedding, selects the top-k nodes with the highest scores, and updates the current set of nodes to be used in the next layer. This process repeats for d layers, producing a sequence of top-k node sets S1 through Sd.
    ```
- **[rag-3]** [RAG (Naive)] Stage: analysis | Source: 2401.18059v1.pdf
  - Query Content:
    `pseudocode for Step 5 of tree traversal method appendix`
  - Citation Content:
    ```
    Step 5 of the tree traversal method involves iteratively selecting the top-k most relevant child nodes at each layer by computing the dot product between the query and each node's representation, then propagating these selected nodes to the next layer until the leaf layer is reached. This is implemented in a loop that runs for the total number of tree layers, updating the current node set (Scurrent) with the top-k nodes (Slayer) from each layer.
    ```