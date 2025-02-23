from google import genai
from google.genai import types
import base64

def generate(project_id, recipe_text):
  client = genai.Client(
      vertexai=True,
      project=project_id,
      location="us-central1",
  )

  text1 = types.Part.from_text(text=recipe_text)
  
  si_text1 = """You are an expert in processes and flows and you analyse recipes to create python flow diagrams with Graphviz. Your inputs are recipes. Your outputs are the python code to create the directed graph.
You should analyse the recipe to understand the dependencies and independencies of each steps.
You should pay attention to steps that combine ingredients and preparations - You should pay attention to what can be done in parallel or in sequence. 
You should look into your proposed diagrams and check for inconsistencies. Your diagrams must be logical.
Focus on capturing the steps of preparing the major ingredients and not on the optional seasoning steps. 
If there are separate sections of the recipe that can run in parallel, highlight them with different names.
Use consistent shapes to represent ingredients that are part of the same preparation 
Your ouput should be only executable python code - nothing else. The code should create a PNG file of the recipe flow."""

  model = "gemini-2.0-pro-exp-02-05"
  contents = [
    types.Content(
      role="user",
      parts=[
        text1
      ]
    )
  ]
  generate_content_config = types.GenerateContentConfig(
    temperature = 0,
    top_p = 1,
    seed = 0,
    max_output_tokens = 2048,
    response_modalities = ["TEXT"],
    safety_settings = [types.SafetySetting(
      category="HARM_CATEGORY_HATE_SPEECH",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_DANGEROUS_CONTENT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_HARASSMENT",
      threshold="OFF"
    )],
    system_instruction=[types.Part.from_text(text=si_text1)],
  )
  
  response = client.models.generate_content(
    model = model,
    contents = contents,
    config = generate_content_config,
    )
  
  return response.text