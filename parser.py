import re

def parse_code_string(code_string: str):
  """
  Parses a string of code to extract HTML, CSS, and JavaScript content.
  """
  html_regex = re.compile(r'```html filename="index\.html"(.*?)```', re.DOTALL)
  css_regex = re.compile(r'```css filename="style\.css"(.*?)```', re.DOTALL)
  js_regex = re.compile(r'```javascript filename="script\.js"(.*?)```', re.DOTALL)

  html_match = html_regex.search(code_string)
  css_match = css_regex.search(code_string)
  js_match = js_regex.search(code_string)

  html_content = html_match.group(1).strip() if html_match else ""
  css_content = css_match.group(1).strip() if css_match else ""
  js_content = js_match.group(1).strip() if js_match else ""

  return {
    "index.html": html_content,
    "style.css": css_content,
    "script.js": js_content,
  }

import os

def save_files(parsed_content: dict, output_directory: str = "."):
  """
  Saves the parsed code content into files.
  """
  os.makedirs(output_directory, exist_ok=True)
  for filename, content in parsed_content.items():
    filepath = os.path.join(output_directory, filename)
    with open(filepath, "w", encoding="utf-8") as f:
      f.write(content)
    print(f"Saving {filename} to {filepath}")
