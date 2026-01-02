## Concise Answer

$WikidataMapMakingWorkshop.ipynb$

---

## Detailed Answer

## S1: Identify the Jupyter Notebook for Interactive Map Creation in Module 3

Module 3 of the workshop “From Wikidata to Interactive Off-Wiki Maps in Three Steps” employs the Jupyter Notebook titled **`WikidataMapMakingWorkshop.ipynb`** to demonstrate the end-to-end process of creating an interactive map [rag-1]. This notebook serves as the primary instructional tool, guiding learners through a structured workflow that begins with querying georeferenced data from Wikidata using SPARQL, followed by data processing with `pandas` and `geopandas`, and culminating in interactive visualization using the `ipyleaflet` library [rag-1].

The notebook specifically extracts information about public libraries in the Netherlands, including their geographic coordinates, and renders them as point markers on a map. Notably, it implements cluster markers to manage visual density in areas with multiple libraries, enhancing usability and interpretability. The map is centered on Bergen, North Holland, with a distinct red marker identifying the Schoorl public library at coordinates ($52.08, 5.33$) [rag-1]. Additionally, the workflow generates a standalone HTML output, `NetherlandsPublicLibrariesHeatmap.html`, which provides a heatmap representation of library density across Dutch municipalities, further extending the analytical utility of the notebook [rag-1].

The choice of `ipyleaflet`—a Python interface to the Leaflet JavaScript library—enables dynamic, browser-based interactivity directly within the Jupyter environment, making it ideal for educational and exploratory data analysis tasks [rag-1]. This notebook thus exemplifies how open data from Wikidata can be transformed into geospatial insights using standard Python data science tools.

In summary, the `WikidataMapMakingWorkshop.ipynb` notebook is the designated example in Module 3 for teaching interactive map creation, integrating data retrieval, processing, and visualization into a single, reproducible workflow.

---

## Citations

- **[rag-1]** [RAG (Naive)] Stage: analysis | Source: 52b3137455e7ca4df65021a200aef724.pdf
  - Query Content:
    `module 3 example notebook interactive map`
  - Citation Content:
    ```
    Module 3 uses the Jupyter Notebook titled 'WikidataMapMakingWorkshop.ipynb' to demonstrate how to create an interactive map. The notebook extracts georeferenced data about public libraries in the Netherlands from Wikidata using SPARQL, processes it with pandas and geopandas, and visualizes it using the ipyleaflet library. The resulting interactive map displays point markers for library locations, with cluster markers for high-density areas, and is centered on Bergen, North Holland, showing a red marker for the Schoorl public library at coordinates (52.08, 5.33). The workflow also produces a standalone HTML file named 'NetherlandsPublicLibrariesHeatmap.html' that shows a heatmap of library density across Dutch municipalities.
    ```