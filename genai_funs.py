import base64
import logging
from google import genai
from google.genai import types

def re_write_recipe(project_id, recipe, input_type, si_text):
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location="us-central1",
    )

    print("runnung the re-writing agent")
    

    if input_type == "txt":
        recipe_text = recipe
        text = types.Part.from_text(text=recipe_text)
        parts = [text]

    if input_type == "youtube":
        video1 = types.Part.from_uri(
            file_uri=recipe,
            mime_type="video/*",
        )
        text = types.Part.from_text(text="here is a video of the recipe:")
        parts = [text, video1]

    model = "gemini-2.0-pro-exp-02-05"
    contents = [types.Content(role="user", parts=parts)]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.2,
        top_p=1,
        seed=0,
        max_output_tokens=8048,
        response_modalities=["TEXT"],
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"
            ),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ],
        system_instruction=[types.Part.from_text(text=si_text)],
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    print("The re-written recipe is:")
    print(response.text)

    return response.text


def generate_graph(project_id, recipe, si_text):
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location="us-central1",
    )
    print("running the graph generation agent")

    
    text = types.Part.from_text(text=recipe)
    parts = [text]
    model = "gemini-2.0-pro-exp-02-05"
    contents = [types.Content(role="user", parts=parts)]
    tools = [types.Tool(google_search=types.GoogleSearch())]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.2,
        top_p=1,
        seed=0,
        max_output_tokens=8048,
        response_modalities=["TEXT"],
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"
            ),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ],
        tools=tools,
        system_instruction=[types.Part.from_text(text=si_text)],
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    print("finished the first graph generation agent")

    return response.text


def improve_graph(project_id, recipe, graph_code, si_text):
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location="us-central1",
    )

    print("running the graph improvement agent")

    
    graph_code = types.Part.from_text(
        text="Here  is the python code that represents the recipe: \n"
        + graph_code
        + "\n"
    )
    recipe = types.Part.from_text(
        text="Here is the recipe you are capturing in graph format : \n" + recipe + "\n"
    )
    parts = [recipe, graph_code]

    model = "gemini-2.0-pro-exp-02-05"
    contents = [types.Content(role="user", parts=parts)]
    tools = [types.Tool(google_search=types.GoogleSearch())]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.2,
        top_p=1,
        seed=0,
        max_output_tokens=8048,
        response_modalities=["TEXT"],
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"
            ),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ],
        tools=tools,
        system_instruction=[types.Part.from_text(text=si_text)],
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    print("finished the graph improvement agent")

    return response.text
