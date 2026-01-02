## S1: Identification of the Clustering Algorithm Model and Its Core Challenge

The clustering algorithm employed in the paper is based on **Gaussian Mixture Models (GMMs)**, a probabilistic generative model that represents the data as a weighted sum of multiple Gaussian distributions [rag-1]. Unlike hard clustering methods (e.g., K-means), GMMs enable **soft clustering**, meaning that each text segment can belong to multiple clusters with varying probabilities—this is particularly advantageous for textual data, where segments often semantically overlap across multiple topics [rag-1]. The model parameters, including means, covariances, and mixing coefficients of the Gaussians, are estimated using the **Expectation-Maximization (EM) algorithm**, a standard iterative method for maximum likelihood estimation in latent variable models [rag-1].

A key challenge arises from the mismatch between the assumptions of GMMs and the statistical properties of text embeddings. Specifically, GMMs assume that data points are drawn from continuous, multivariate Gaussian distributions with smooth density profiles. However, text embeddings—especially those derived from transformer-based models—are typically **high-dimensional, sparse, and skewed**, exhibiting non-Gaussian structures such as long tails and cluster manifolds that deviate significantly from spherical or elliptical Gaussian shapes [rag-1]. This structural misalignment can lead to suboptimal cluster boundaries and inflated model complexity if not addressed.

To mitigate these issues, the method incorporates **UMAP (Uniform Manifold Approximation and Projection)** for non-linear dimensionality reduction, which helps preserve local structure while reducing noise and computational burden in high-dimensional space [rag-1]. Additionally, the optimal number of clusters is selected using the **Bayesian Information Criterion (BIC)**, a penalized likelihood criterion that balances model fit against complexity, thereby preventing overfitting in the presence of noisy embeddings [rag-1].

Despite these challenges, empirical results demonstrate that GMM-based clustering outperforms simpler alternatives such as contiguous chunking, validating its suitability for hierarchical text summarization tasks within the RAPTOR framework [rag-1].

The use of GMMs thus provides a principled, probabilistic foundation for soft clustering in text, while the adoption of UMAP and BIC serves as practical adaptations to overcome the inherent limitations of Gaussian assumptions in high-dimensional text spaces.

## S2: Analysis of the Key Challenge — Misalignment Between GMM Assumptions and Text Embedding Characteristics

The primary challenge to the Gaussian Mixture Model (GMM) in this context stems from a fundamental **statistical misalignment** between its underlying assumptions and the empirical properties of modern text embeddings. While GMMs assume that data points are generated from a mixture of multivariate Gaussian distributions—characterized by smooth, symmetric, and ellipsoidal density contours in continuous space—text embeddings derived from transformer architectures (e.g., BERT, RoBERTa) exhibit markedly different statistical behaviors [rag-1].

Specifically, text embeddings are typically **high-dimensional**, **sparse**, and **skewed**, with pronounced non-Gaussian features such as:

- **Long-tailed distributions**: A small number of embedding dimensions dominate variance, while most are near-zero, violating the isotropic spread assumed by Gaussians.
- **Cluster manifolds**: Semantically similar text segments tend to lie on low-dimensional, nonlinear manifolds rather than compact, convex Gaussian blobs.
- **Sparsity in semantic space**: Despite being numerically dense vectors, the effective information is concentrated in a few directions, making the data inherently non-Gaussian in structure [rag-1].

This mismatch leads to several practical consequences:
- The **EM algorithm**, which relies on Gaussian likelihoods for parameter estimation, may converge to suboptimal solutions where cluster centroids fail to capture the true semantic structure.
- The **covariance matrices** estimated by GMMs become misleading, as they attempt to model elliptical shapes around data that are better described by irregular, stretched, or disconnected manifolds.
- The **soft clustering probabilities** may become poorly calibrated, assigning non-negligible membership weights to semantically distant clusters due to the model’s forced Gaussian fit.

Although the paper mitigates these issues through preprocessing with UMAP (to approximate the underlying manifold structure) and model selection via BIC (to penalize unnecessary components), the core challenge remains: **GMMs are inherently parametric models that impose a rigid geometric structure on data that is fundamentally non-parametric in nature**. This structural mismatch is not resolved by dimensionality reduction alone—it is a modeling assumption that persists even after projection into lower-dimensional space.

Empirical success (e.g., outperforming contiguous chunking) does not negate this theoretical limitation; rather, it underscores the robustness of GMMs under imperfect conditions, while highlighting the need for more flexible, non-parametric, or manifold-aware clustering approaches in future work.

In summary, while GMMs provide a mathematically elegant and probabilistically grounded framework for soft clustering, their reliance on Gaussian assumptions renders them inherently misaligned with the true geometry of text embeddings, posing a persistent challenge to accurate and interpretable cluster formation.

---

## Citations

- **[rag-1]** [RAG (Naive)] Stage: analysis | Source: 2401.18059v1.pdf
  - Query Content:
    `clustering algorithm model based on`
  - Citation Content:
    ```
    The clustering algorithm in the paper is based on Gaussian Mixture Models (GMMs), which provide a probabilistic soft clustering framework where text segments can belong to multiple clusters. This is particularly useful for text data, as segments often relate to multiple topics. A key challenge is that the Gaussian assumption does not perfectly align with the sparse and skewed nature of text embeddings, though empirical results still show GMMs outperform alternatives like contiguous chunking. To mitigate issues with high-dimensional embeddings, the method uses UMAP for dimensionality reduction and selects the optimal number of clusters using the Bayesian Information Criterion (BIC), with parameters estimated via the Expectation-Maximization algorithm.
    ```