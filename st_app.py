import os
import streamlit as st
# Updated import to use the new functions
from r2g_app.main import process_text, text_to_graph
import re # Import re for GCS link validation/parsing (optional but good practice)

PROJECT_ID = os.getenv("PROJECT_ID")
print('PROJECT ID IS: ', PROJECT_ID)

# Helper function to create clickable GCS links (optional)
def create_gcs_link(uri):
    if uri and uri.startswith("gs://"):
        # Simple conversion for console link - more robust parsing might be needed
        # depending on exact GCS URI format variations if used for direct browser access
        return f"https://console.cloud.google.com/storage/browser/{uri[5:]}"
    return None

st.title("Recipe Processor")

recipe_draft = st.text_area("Recipe Draft", height=300, placeholder="Paste your recipe draft here...")
recipe_name = st.text_input("Recipe Name", placeholder="e.g., chocolate_chip_cookies")
gcs_bucket_name = st.text_input("GCS Bucket Name", placeholder="your-gcs-bucket-name")

process_button = st.button("Process Recipe")

if process_button:
    # --- Input Validation ---
    if not recipe_draft:
        st.error("Recipe Draft cannot be empty.")
    elif not recipe_name:
        st.error("Recipe Name cannot be empty.")
    elif not gcs_bucket_name:
        st.error("GCS Bucket Name cannot be empty.")
    else:
        # --- Process Recipe ---
        try:
            # 1. Process text first
            with st.spinner("Processing recipe text..."):
                standardised_recipe_text = process_text(
                    recipe_draft_text=recipe_draft,
                    project_id=PROJECT_ID
                )

            # Display the standardized text
            st.subheader("Standardized Recipe:")
            st.text_area("Recipe Text", value=standardised_recipe_text, height=300, disabled=True, key="standardized_text_display") # Added key for potential future use

            # 2. Generate graph and upload artifacts
            with st.spinner("Generating graph and uploading results..."):
                results = text_to_graph(
                    standardised_recipe=standardised_recipe_text,
                    recipe_name=recipe_name,
                    gcs_bucket_name=gcs_bucket_name,
                    project_id=PROJECT_ID
                )

            # --- Display Success ---
            st.success("Recipe processed and graph generated successfully!") # Updated success message

            recipe_uri = results.get("recipe_uri")
            graph_uri = results.get("graph_uri")

                if recipe_uri:
                    recipe_link = create_gcs_link(recipe_uri)
                    if recipe_link:
                         st.markdown(f"**Standardized Recipe:** [View in GCS Console]({recipe_link}) (`{recipe_uri}`)")
                    else:
                         st.markdown(f"**Standardized Recipe:** `{recipe_uri}`") # Fallback if link creation fails
                else:
                    st.warning("Standardized recipe GCS URI not found in results.")

                if graph_uri:
                    graph_link = create_gcs_link(graph_uri)
                    if graph_link:
                        st.markdown(f"**Recipe Graph PDF:** [View in GCS Console]({graph_link}) (`{graph_uri}`)")
                    else:
                        st.markdown(f"**Recipe Graph PDF:** `{graph_uri}`") # Fallback if link creation fails
                else:
                    st.warning("Recipe graph GCS URI not found in results.")


            except (ValueError, RuntimeError, Exception) as e:
                # --- Display Error ---
                st.error(f"An error occurred: {e}") # This single block catches errors from both functions

            # --- End Process Recipe ---
