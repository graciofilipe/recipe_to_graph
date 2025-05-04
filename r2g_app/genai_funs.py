import logging
import os
from typing import List, Optional, Dict, Any, Literal
from google import genai
from google.genai import types

DEFAULT_VERTEX_PROJECT_ID = os.getenv("PROJECT_ID")
DEFAULT_VERTEX_LOCATION = "us-central1"
DEFAULT_MODEL_NAME = "gemini-2.5-pro-exp-03-25"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_TOP_P = 1.0
DEFAULT_MAX_TOKENS = 8048

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def _get_genai_client(
    project_id: Optional[str] = DEFAULT_VERTEX_PROJECT_ID,
    location: str = DEFAULT_VERTEX_LOCATION
) -> genai.Client:
    """
    Initializes and returns the Generative AI client for Vertex AI.

    Args:
        project_id: Google Cloud project ID. Defaults to env variable 'PROJECT_ID'.
        location: Google Cloud location for the Vertex AI endpoint.

    Returns:
        An initialized genai.Client instance.

    Raises:
        ValueError: If project_id is not provided or found.
        Exception: If client initialization fails for other reasons.
    """
    if not project_id:
        logger.error("Vertex AI Project ID not provided or found in environment variables.")
        raise ValueError("Vertex AI Project ID is required.")
    try:
        client = genai.Client(vertexai=True, project=project_id, location=location)
        logger.info(f"Initialized GenAI client for project '{project_id}' in '{location}'.")
        return client
    except Exception as e:
        logger.exception(f"Failed to initialize GenAI client: {e}")
        raise

def _build_generate_content_config(
    system_instruction_text: Optional[str] = None,
    tools: Optional[List[types.Tool]] = None,
    temperature: Optional[float] = None,
    top_p: float = DEFAULT_TOP_P,
    max_output_tokens: int = DEFAULT_MAX_TOKENS,
) -> types.GenerateContentConfig:
    """
    Builds the GenerateContentConfig object for the API call.

    Args:
        system_instruction_text: The system prompt text, if any.
        tools: A list of tools (e.g., GoogleSearch) for the model, if any.
        temperature: Controls randomness (lower is more deterministic).
        top_p: Controls diversity via nucleus sampling.
        max_output_tokens: Maximum number of tokens to generate.

    Returns:
        A configured types.GenerateContentConfig object.
    """
    safety_settings = [
        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
        types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
        types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
    ]

    config_kwargs: Dict[str, Any] = {
        "temperature": temperature if temperature is not None else DEFAULT_TEMPERATURE,
        "top_p": top_p,
        "max_output_tokens": max_output_tokens,
        "safety_settings": safety_settings,
        "candidate_count": 1
    }
    if system_instruction_text:
        config_kwargs["system_instruction"] = [types.Part.from_text(text=system_instruction_text)]
    if tools:
        config_kwargs["tools"] = tools
    config_kwargs["thinking_config"] = types.ThinkingConfig(include_thoughts=True)

    return types.GenerateContentConfig(**config_kwargs)

def _call_generate_content(
    client: genai.Client,
    model_name: str,
    contents: List[types.Content],
    config: types.GenerateContentConfig
) -> str:
    """
    Calls the generate_content API, handles errors, and returns the text response.

    Args:
        client: The initialized genai.Client.
        model_name: The name of the model to use.
        contents: The list of content parts (user input).
        config: The generation configuration.

    Returns:
        The text part of the model's response.

    Raises:
        RuntimeError: If the API call fails or returns an empty response.
        Exception: For other unexpected errors during the API call.
    """
    try:
        logger.debug(f"Calling model '{model_name}' with config: {config}")
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config,
        )
        if not hasattr(response, 'text') or not response.text:
             logger.warning(f"GenAI response for model '{model_name}' was empty or lacked text.")
             raise RuntimeError("Received empty response from AI model.")
        logger.debug(f"Received response text (length {len(response.text)}) from model '{model_name}'.")
        return response.text
    except Exception as e:
        logger.exception(f"GenAI API call to model '{model_name}' failed: {e}")
        raise RuntimeError(f"GenAI API call failed: {e}") from e

def draft_to_recipe(
    recipe_draft: str,
    system_instruction: str,
    project_id: Optional[str] = DEFAULT_VERTEX_PROJECT_ID,
    location: str = DEFAULT_VERTEX_LOCATION,
    model_name: str = DEFAULT_MODEL_NAME,
    temperature: Optional[float] = None
) -> str:
    """
    Transforms a recipe draft into a standardized recipe using a GenAI model.

    Args:
        recipe_draft: The raw text draft of the recipe.
        system_instruction: The system prompt guiding the AI's behavior.
        project_id: Google Cloud project ID for Vertex AI. Defaults to env variable.
        location: Google Cloud location for Vertex AI endpoint.
        model_name: The specific GenAI model to use.

    Returns:
        The standardized recipe text generated by the AI.

    Raises:
        ValueError: If project_id is not provided.
        RuntimeError: If the API call fails or returns an empty response.
    """
    logger.info("Running the draft-to-recipe agent...")
    client = _get_genai_client(project_id, location)

    text_part = types.Part.from_text(text=recipe_draft)
    contents = [types.Content(role="user", parts=[text_part])]
    tools = [types.Tool(google_search=types.GoogleSearch())]
    config = _build_generate_content_config(
        system_instruction_text=system_instruction,
        tools=tools,
        temperature=temperature
    )

    response_text = _call_generate_content(client, model_name, contents, config)

    logger.info("Finished the draft-to-recipe agent.")
    return response_text

def re_write_recipe(
    recipe_input: str,
    input_type: Literal["txt", "youtube"],
    system_instruction: str,
    project_id: Optional[str] = DEFAULT_VERTEX_PROJECT_ID,
    location: str = DEFAULT_VERTEX_LOCATION,
    model_name: str = DEFAULT_MODEL_NAME,
    temperature: Optional[float] = None
) -> str:
    """
    Rewrites a recipe from text or a YouTube video URI into a standardized format.

    Args:
        recipe_input: The recipe text or the accessible video URI (e.g., GCS).
        input_type: The type of input provided: "txt" or "youtube".
        system_instruction: The system prompt guiding the AI's behavior.
        project_id: Google Cloud project ID for Vertex AI. Defaults to env variable.
        location: Google Cloud location for Vertex AI endpoint.
        model_name: The specific GenAI model to use.

    Returns:
        The rewritten, standardized recipe text.

    Raises:
        ValueError: If project_id is not provided or input_type is invalid.
        RuntimeError: If the API call fails or returns an empty response.
    """
    logger.info(f"Running the re-writing agent for input type: {input_type}...")
    client = _get_genai_client(project_id, location)

    parts: List[types.Part] = []
    if input_type == "txt":
        parts.append(types.Part.from_text(text=recipe_input))
    elif input_type == "youtube":
        logger.info(f"Processing video URI: {recipe_input}")
        try:
            video_part = types.Part.from_uri(
                file_uri=recipe_input,
                mime_type="video/*",
            )
            text_part = types.Part.from_text(
                text="Generate a standardized recipe from the following video:"
            )
            parts = [text_part, video_part]
        except Exception as e:
            logger.exception(f"Failed to create Part from URI '{recipe_input}': {e}")
            raise ValueError(f"Could not process video URI '{recipe_input}'. Ensure it's accessible (e.g., a GCS URI).") from e
    else:
        logger.error(f"Invalid input_type provided: '{input_type}'")
        raise ValueError(f"Invalid input_type: '{input_type}'. Must be 'txt' or 'youtube'.")

    contents = [types.Content(role="user", parts=parts)]
    config = _build_generate_content_config(
        system_instruction_text=system_instruction,
        temperature=temperature
    )

    response_text = _call_generate_content(client, model_name, contents, config)

    logger.info("Finished the re-writing agent.")
    return response_text

def generate_graph(
    standardised_recipe: str,
    system_instruction: str,
    project_id: Optional[str] = DEFAULT_VERTEX_PROJECT_ID,
    location: str = DEFAULT_VERTEX_LOCATION,
    model_name: str = DEFAULT_MODEL_NAME,
    temperature: Optional[float] = None
) -> str:
    """
    Generates initial Graphviz Python code from a standardized recipe.

    Args:
        standardized_recipe: The recipe text in a standardized format.
        system_instruction: The system prompt guiding the AI's behavior.
        project_id: Google Cloud project ID for Vertex AI. Defaults to env variable.
        location: Google Cloud location for Vertex AI endpoint.
        model_name: The specific GenAI model to use.

    Returns:
        The generated Python code string for Graphviz.

    Raises:
        ValueError: If project_id is not provided.
        RuntimeError: If the API call fails or returns an empty response.
    """
    logger.info("Running the graph generation agent...")
    client = _get_genai_client(project_id, location)

    text_part = types.Part.from_text(text=standardised_recipe)
    contents = [types.Content(role="user", parts=[text_part])]
    tools = [types.Tool(google_search=types.GoogleSearch())]
    config = _build_generate_content_config(
        system_instruction_text=system_instruction,
        tools=tools,
        temperature=temperature
    )

    response_text = _call_generate_content(client, model_name, contents, config)

    logger.info("Finished the graph generation agent.")
    return response_text

def improve_graph(
    standardised_recipe: str,
    graph_code: str,
    system_instruction: str,
    project_id: Optional[str] = DEFAULT_VERTEX_PROJECT_ID,
    location: str = DEFAULT_VERTEX_LOCATION,
    model_name: str = DEFAULT_MODEL_NAME,
    temperature: Optional[float] = None
) -> str:
    """
    Improves existing Graphviz Python code based on the recipe and instructions.

    Args:
        standardised_recipe: The recipe text for context.
        graph_code: The initial Python Graphviz code to be improved.
        system_instruction: The system prompt guiding the AI's behavior.
        project_id: Google Cloud project ID for Vertex AI. Defaults to env variable.
        location: Google Cloud location for Vertex AI endpoint.
        model_name: The specific GenAI model to use.

    Returns:
        The improved Python code string for Graphviz.

    Raises:
        ValueError: If project_id is not provided.
        RuntimeError: If the API call fails or returns an empty response.
    """
    logger.info("Running the graph improvement agent...")
    client = _get_genai_client(project_id, location)

    recipe_part = types.Part.from_text(
        text=f"## Standardized Recipe Context:\n\n{standardised_recipe}\n\n"
    )
    graph_code_part = types.Part.from_text(
        text=f"## Current Graphviz Python Code to Improve:\n\n```python\n{graph_code}\n```\n\n"
        + "Improve the above Python code based on the recipe context and the system instructions."
    )
    contents = [types.Content(role="user", parts=[recipe_part, graph_code_part])]
    tools = [types.Tool(google_search=types.GoogleSearch())]
    config = _build_generate_content_config(
        system_instruction_text=system_instruction,
        tools=tools,
        temperature=temperature
    )

    response_text = _call_generate_content(client, model_name, contents, config)

    logger.info("Finished the graph improvement agent.")
    return response_text