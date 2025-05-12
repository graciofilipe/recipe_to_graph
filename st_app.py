import os
import streamlit as st
import base64 # Import base64 for PDF embedding
import datetime # Import datetime to generate date string
# Updated import to use the new functions
from r2g_app.main import process_text, text_to_graph
from r2g_app.main import revise_recipe
import re # Import re for GCS link validation/parsing (optional but good practice)

st.set_page_config(layout="wide") # Set page layout to wide

# Initialize session state variables
if "standardized_recipe_text" not in st.session_state:
    st.session_state.standardized_recipe_text = ""
if "user_feedback" not in st.session_state:
    st.session_state.user_feedback = ""
if "recipe_approved" not in st.session_state:
    st.session_state.recipe_approved = False
if "original_recipe_draft" not in st.session_state:
    st.session_state.original_recipe_draft = ""
if "graph_results" not in st.session_state:
    st.session_state.graph_results = None
if "processing_error" not in st.session_state:
    st.session_state.processing_error = None
if 'recipe_name' not in st.session_state:
    st.session_state.recipe_name = ""
if 'gcs_bucket_name' not in st.session_state:
    st.session_state.gcs_bucket_name = ""

PROJECT_ID = os.getenv("PROJECT_ID")
# print('PROJECT ID IS: ', PROJECT_ID) # Optional: Comment out or remove print statements for cleaner logs


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

# --- Display Processing Errors ---
if st.session_state.processing_error:
    st.error(st.session_state.processing_error)

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
        st.session_state.original_recipe_draft = recipe_draft # Store original draft
        st.session_state.recipe_name = recipe_name # Store recipe name
        st.session_state.gcs_bucket_name = gcs_bucket_name # Store bucket name
        st.session_state.processing_error = None # Clear previous errors

        try:
            with st.spinner("Processing recipe text..."):
                processed_text = process_text(
                    recipe_draft_text=recipe_draft,
                    project_id=PROJECT_ID
                )
            # --- Success ---
            st.session_state.standardized_recipe_text = processed_text
            st.session_state.recipe_approved = False # Reset approval on new processing
            st.session_state.graph_results = None # Clear previous results
            st.session_state.user_feedback = "" # Clear previous feedback
            st.info("Recipe processed. Please review the standardized text below and approve or provide feedback.") # Inform user

        except (ValueError, RuntimeError, Exception) as e:
            # --- Error Handling ---
            error_message = f"An error occurred during recipe processing: {e}"
            st.session_state.processing_error = error_message
            st.session_state.standardized_recipe_text = "" # Clear stale data
            st.session_state.recipe_approved = False
            st.session_state.graph_results = None
            st.error(error_message) # Display error in the main area

        # --- End Process Recipe (text only) ---
        # Graph generation and display logic is removed from here and will be handled later based on session state.


# --- Review and Approval Section ---
if st.session_state.standardized_recipe_text and not st.session_state.recipe_approved:
    st.subheader("Review Standardized Recipe:")
    st.text_area("Standardized Recipe Text", value=st.session_state.standardized_recipe_text, height=300, disabled=True, key="standardized_recipe_display")

    approve_button = st.button("Generate Graph")

    st.subheader("Request Changes (Optional):")
    # Add value parameter to bind the text area to the user_feedback state
    st.text_area("Describe desired changes:", value=st.session_state.user_feedback, key="user_feedback_input", height=150)
    submit_changes_button = st.button("Submit Changes")

    # --- Handle Button Clicks ---
    if approve_button:
        st.session_state.recipe_approved = True
        st.session_state.user_feedback = "" # Clear feedback state, but not the input field directly
        # Remove: st.session_state.user_feedback_input = ""
        st.session_state.processing_error = None
        st.rerun()

    if submit_changes_button:
        feedback_text = st.session_state.user_feedback_input
        if feedback_text and feedback_text.strip():
            st.session_state.user_feedback = feedback_text.strip()
            st.session_state.processing_error = None # Clear previous errors
            try:
                with st.spinner("Revising recipe based on feedback..."):
                    revised_recipe_text = revise_recipe(
                        original_draft=st.session_state.original_recipe_draft,
                        current_standardised_recipe=st.session_state.standardized_recipe_text,
                        user_feedback=st.session_state.user_feedback,
                        project_id=PROJECT_ID # Pass PROJECT_ID
                    )
                # --- Revision Success ---
                st.session_state.standardized_recipe_text = revised_recipe_text
                st.session_state.user_feedback = "" # Clear feedback state, input field will clear via rerun + value binding
                # Remove: st.session_state.user_feedback_input = ""
                st.rerun() # Refresh to show revised recipe
            except Exception as e:
                # --- Revision Error ---
                st.session_state.processing_error = f"Failed to revise recipe: {e}"
                st.session_state.user_feedback = "" # Clear feedback state, but keep input
                st.rerun() # Refresh to show error
        else:
            st.warning("Please enter your requested changes before submitting.")


# --- Graph Generation Trigger ---
# This block runs only when the recipe is approved but graph results are not yet generated
if st.session_state.recipe_approved and not st.session_state.graph_results:
    # Check if required inputs are available (safety check)
    if not st.session_state.recipe_name or not st.session_state.gcs_bucket_name:
        st.session_state.processing_error = "Recipe Name or GCS Bucket Name is missing. Please re-enter details and process again."
        st.session_state.recipe_approved = False # Reset approval status
        st.rerun()
    else:
        try:
            with st.spinner("Generating graph and uploading results..."):
                # Use stored recipe name and bucket name
                results = text_to_graph(
                    standardised_recipe=st.session_state.standardized_recipe_text,
                    recipe_name=st.session_state.recipe_name,
                    gcs_bucket_name=st.session_state.gcs_bucket_name,
                    project_id=PROJECT_ID
                )
            st.session_state.graph_results = results
            st.session_state.processing_error = None # Clear any previous errors
            st.rerun() # Rerun to display results

        except Exception as e:
            st.session_state.processing_error = f"Failed to generate graph: {e}"
            st.session_state.recipe_approved = False # Reset approval status
            st.session_state.graph_results = None # Clear potentially partial results
            st.rerun() # Rerun to display error


# --- Display Final Results Section ---
# This block now only displays results if they exist (generated by the block above)
if st.session_state.recipe_approved and st.session_state.graph_results:
    st.success("Recipe approved and graph generated successfully!")

    results = st.session_state.graph_results # Get results from session state
    recipe_uri = results.get("recipe_uri")
    html_uri = results.get("html_uri") # Added
    css_uri = results.get("css_uri")    # Added
    js_uri = results.get("js_uri")      # Added

    if recipe_uri:
        recipe_link = create_gcs_link(recipe_uri)
        if recipe_link:
            st.markdown(f"**Standardized Recipe:** [View in GCS Console]({recipe_link}) (`{recipe_uri}`)")
        else:
            st.markdown(f"**Standardized Recipe:** `{recipe_uri}`") # Fallback if link creation fails
    else:
        st.warning("Standardized recipe GCS URI not found in results.")

    if html_uri:
        html_link = create_gcs_link(html_uri)
        if html_link:
            st.markdown(f"**Recipe Graph HTML:** [View in GCS Console]({html_link}) (`{html_uri}`)")
        else:
            st.markdown(f"**Recipe Graph HTML:** `{html_uri}`")
    else:
        st.warning("Recipe graph HTML URI not found in results.")

    if css_uri:
        css_link = create_gcs_link(css_uri)
        if css_link:
            st.markdown(f"**Recipe Graph CSS:** [View in GCS Console]({css_link}) (`{css_uri}`)")
        else:
            st.markdown(f"**Recipe Graph CSS:** `{css_uri}`")
    else:
        # This is not a warning as CSS might be embedded or not always separate
        st.info("Recipe graph CSS URI not found in results (it might be embedded in HTML).")

    if js_uri:
        js_link = create_gcs_link(js_uri)
        if js_link:
            st.markdown(f"**Recipe Graph JS:** [View in GCS Console]({js_link}) (`{js_uri}`)")
        else:
            st.markdown(f"**Recipe Graph JS:** `{js_uri}`")
    else:
        # This is not a warning as JS might be embedded or not always separate
        st.info("Recipe graph JS URI not found in results (it might be embedded in HTML).")


    # --- Display HTML/CSS/JS Graph ---
    html_content = results.get("html_content")
    css_content = results.get("css_content")
    js_content = results.get("js_content")
    # print(f"DEBUG: js_content: {js_content}")

    # --- Add Download Buttons ---
    if html_content:
        st.download_button(
            label="Download HTML",
            data=html_content,
            file_name="index.html",
            mime="text/html"
        )
    if css_content:
        st.download_button(
            label="Download CSS",
            data=css_content,
            file_name="style.css",
            mime="text/css"
        )
    if js_content:
        st.download_button(
            label="Download JS",
            data=js_content,
            file_name="script.js",
            mime="application/javascript"
        )
