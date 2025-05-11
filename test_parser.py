import unittest
from parser import parse_code_string

class TestCodeParser(unittest.TestCase):

    def test_parse_valid_string(self):
        sample_input = """
```html filename="index.html"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Webpage</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>Hello, World!</h1>
    <p>This is a sample HTML page.</p>
    <script src="script.js"></script>
</body>
</html>
```

```css filename="style.css"
body {
    font-family: sans-serif;
    margin: 0;
    background-color: #f0f0f0;
}

h1 {
    color: #333;
    text-align: center;
    padding: 1em 0;
}
```

```javascript filename="script.js"
document.addEventListener('DOMContentLoaded', () => {
    const heading = document.querySelector('h1');
    heading.addEventListener('click', () => {
        alert('Heading clicked!');
    });
});
```
"""
        parsed_content = parse_code_string(sample_input)
        self.assertIsInstance(parsed_content, dict)
        self.assertIn("index.html", parsed_content)
        self.assertTrue(parsed_content["index.html"].startswith("<!DOCTYPE html>"))
        self.assertTrue(parsed_content["index.html"].endswith("</html>"))
        self.assertIn("style.css", parsed_content)
        self.assertTrue(parsed_content["style.css"].startswith("body {"))
        self.assertTrue(parsed_content["style.css"].endswith("}"))
        self.assertIn("script.js", parsed_content)
        self.assertTrue(parsed_content["script.js"].startswith("document.addEventListener"))
        self.assertTrue(parsed_content["script.js"].endswith("});"))

    def test_parse_empty_string(self):
        parsed_content = parse_code_string("")
        self.assertEqual(parsed_content["index.html"], "")
        self.assertEqual(parsed_content["style.css"], "")
        self.assertEqual(parsed_content["script.js"], "")

    def test_parse_missing_css_block(self):
        input_missing_css = """
```html filename="index.html"
<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
</head>
<body>
    <p>No CSS here.</p>
</body>
</html>
```

```javascript filename="script.js"
console.log("No CSS block test");
```
"""
        parsed_content = parse_code_string(input_missing_css)
        self.assertTrue(parsed_content["index.html"].startswith("<!DOCTYPE html>"))
        self.assertTrue(parsed_content["script.js"].startswith("console.log"))
        self.assertEqual(parsed_content["style.css"], "")

if __name__ == '__main__':
    unittest.main()
