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

    # Initialize graph_nodes_html with a generic fallback message
    graph_nodes_html = "<p>An unexpected issue occurred while preparing graph data.</p>"

    if not html_content or not css_content: # Basic check for HTML/CSS
        st.warning("HTML or CSS content not found in results. Cannot display graph fully.")
        # graph_nodes_html might still be useful if js_content is processed,
        # but the overall display will be broken. For now, we let it proceed.
        # If js_content is also missing, the message below will take precedence.

    if not js_content:
        graph_nodes_html = "<p>JavaScript content for the graph was not found in the AI's response. Unable to render graph.</p>"
    else:
        try:
            graph_data_py = None # Initialize to None
            import re
            import json
            # Regex to find "const graphData = {" up to its corresponding "};"
            match = re.search(r"const\s+graphData\s*=\s*(\{[\s\S]*?\n\}\s*;)", js_content, re.DOTALL)

            if match:
                graph_data_str = match.group(1).strip().rstrip(';')
                # print(f"DEBUG: graph_data_str: {graph_data_str}")
                try:
                    graph_data_py = json.loads(graph_data_str)
                    # print(f"DEBUG: Parsed graphData (Python Dict): {graph_data_py}")
                except json.JSONDecodeError as e:
                    # print(f"DEBUG: Error parsing graphData string with json.loads: {e}")
                    # print(f"DEBUG: Problematic graph_data_str for JSON parsing: {graph_data_str}")
                    graph_nodes_html = "<p>The graph data object found in the JavaScript was improperly formatted (not valid JSON). Unable to render graph.</p>"
            else:
                # print("DEBUG: graphData object not found in js_content.")
                graph_nodes_html = "<p>Could not find the graph data object (graphData) within the JavaScript from the AI. Unable to render graph.</p>"

            if graph_data_py: # Proceed only if graph_data_py was successfully populated
                if 'nodes' in graph_data_py and isinstance(graph_data_py['nodes'], list):
                    if graph_data_py['nodes']:
                        nodes_html_parts = []
                        for node_data in graph_data_py['nodes']:
                            node_id = node_data.get('id', 'Unknown ID')
                            description = node_data.get('description', 'No description available.')
                            import html
                            node_id_safe = html.escape(str(node_id))
                            description_safe = html.escape(description)
                            nodes_html_parts.append(
                                f'<div class="node" data-description="{description_safe}">{node_id_safe}</div>'
                            )
                        graph_nodes_html = "".join(nodes_html_parts)
                    else:
                        graph_nodes_html = "<p>Graph data contains an empty list of nodes.</p>"
                else:
                    graph_nodes_html = "<p>The parsed graph data is missing the expected 'nodes' list or it is not a list. Unable to render graph.</p>"
            # If graph_data_py is None AND no specific error message was set in the try-except for json.loads or match-else block,
            # the graph_nodes_html will retain the message set in those blocks, or the generic one if those were skipped due to js_content being None.
            # This elif condition ensures that if graph_data_py is None (e.g. match was None, or json.loads failed but didn't set graph_nodes_html - which it does now)
            # AND graph_nodes_html hasn't been updated by a more specific error, then we set a fallback.
            # Given the current logic, this specific fallback might be less likely to be hit if js_content existed.
            elif graph_nodes_html == "<p>An unexpected issue occurred while preparing graph data.</p>": # Check if it's still the initial generic fallback
                 graph_nodes_html = "<p>No graph data found or no nodes in data.</p>"

        except Exception as e:
            # This outer exception might catch other issues during js_content processing
            st.error(f"An error occurred while processing JavaScript for the graph: {e}")
            graph_nodes_html = f"<p>An unexpected error occurred during graph data preparation: {e}</p>"


    # --- Display HTML/CSS/JS Graph ---
    # This 'if' now primarily checks if we have the necessary components to attempt rendering.
    # The graph_nodes_html will display specific error messages if js_content processing failed.
    if html_content and css_content: # js_content presence is handled by graph_nodes_html logic
        try:
            # Embed CSS and JavaScript into the HTML
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Recipe Graph</title>
                <style>
                    {css_content}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Recipe Flowchart</h1>
                    <div id="graphDiv" class="graph-placeholder">
                        {graph_nodes_html}
                    </div>
                    <div id="tooltip" class="tooltip" style="opacity:0;"></div>
                </div>
                <script>
                    document.addEventListener('DOMContentLoaded', function() {{
                        const tooltipDiv = document.getElementById('tooltip');
                        const nodes = document.querySelectorAll('.node');

                        if (!tooltipDiv) {{
                            console.error('Tooltip div not found!');
                            return;
                        }}
                        if (nodes.length === 0) {{
                            console.log('No nodes found for tooltips.');
                            // Display message in graphDiv if no nodes rendered by Python
                            const graphDiv = document.getElementById('graphDiv');
                            if(graphDiv && graphDiv.innerHTML.trim() === "" || graphDiv.innerHTML.includes("No graph data found")) {{
                                // graphDiv.textContent = 'No graph nodes were rendered by Python or data was invalid.';
                                // The Python-generated message is already in graph_nodes_html, so no need to overwrite here unless it's empty
                            }}
                            return;
                        }}

                        nodes.forEach(node => {{
                            node.onmouseover = function(event) {{
                                const description = this.getAttribute('data-description');
                                tooltipDiv.innerHTML = description;
                                tooltipDiv.style.opacity = 1;
                                // Position tooltip - adjust as needed
                                tooltipDiv.style.left = (event.pageX + 10) + 'px';
                                tooltipDiv.style.top = (event.pageY + 10) + 'px';
                            }};
                            node.onmouseout = function() {{
                                tooltipDiv.style.opacity = 0;
                            }};
                            node.onmousemove = function(event) {{ // Keep tooltip moving with mouse
                                tooltipDiv.style.left = (event.pageX + 10) + 'px';
                                tooltipDiv.style.top = (event.pageY + 10) + 'px';
                            }};
                        }});
                        console.log(`Tooltip JS initialized for ${{nodes.length}} nodes.`);
                    }});
                </script>
            </body>
            </html>
            """
            st.subheader("Generated Recipe Graph:")
            # print(full_html) # For debugging the full HTML structure if needed
            st.components.v1.html(full_html, height=1200, scrolling=True)

        except Exception as e:
            # This error is for issues during the final HTML assembly or display by Streamlit
            st.error(f"An error occurred while assembling or displaying the HTML graph: {e}")
            # Display the graph_nodes_html error message if assembly fails
            st.markdown(graph_nodes_html, unsafe_allow_html=True)
    elif html_content and not css_content:
        st.warning("CSS content is missing. Graph display may be affected.")
        # Attempt to display with placeholder for graphDiv if js was processed
        # This case is less critical if graph_nodes_html already indicates JS issues.
        placeholder_html = f"""
        <!DOCTYPE html><html><head><meta charset="utf-8"><title>Recipe Graph (CSS Missing)</title></head>
        <body><div class="container"><h1>Recipe Flowchart (CSS Missing)</h1>
        <div id="graphDiv" class="graph-placeholder">{graph_nodes_html}</div>
        </div></body></html>"""
        st.components.v1.html(placeholder_html, height=600, scrolling=True)
    else: # Handles cases where html_content is missing, or other unhandled scenarios.
          # The graph_nodes_html should provide specific errors if JS was the primary issue.
        if not html_content:
            st.warning("HTML content not found in results. Cannot display graph.")
        # If graph_nodes_html has a specific error, display it.
        # Otherwise, show a generic warning if it's still the initial fallback.
        if graph_nodes_html == "<p>An unexpected issue occurred while preparing graph data.</p>":
            st.warning("HTML, CSS, or JavaScript content not found or processed correctly. Cannot display graph.")
        else:
            # Display the specific error from graph_nodes_html processing
            st.markdown(graph_nodes_html, unsafe_allow_html=True)


    # --- Download Buttons ---
    # These should still be offered if the content exists, even if display failed for some reason.
    if html_content:
        st.download_button(
            label="Download HTML",
            data=html_content,
            file_name=f"{st.session_state.recipe_name}_index.html",
            mime="text/html"
        )
    if css_content:
        st.download_button(
            label="Download CSS",
            data=css_content,
            file_name=f"{st.session_state.recipe_name}_style.css",
            mime="text/css"
        )
    if js_content:
        st.download_button(
            label="Download JavaScript",
            data=js_content,
            file_name=f"{st.session_state.recipe_name}_script.js",
            mime="application/javascript"
        )
    # --- End Download Buttons ---

    # --- End Display HTML/CSS/JS Graph ---
