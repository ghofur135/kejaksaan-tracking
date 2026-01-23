
extra_css = """
/* Editable Text Cells */
.editable {
    cursor: text;
    transition: background-color 0.2s;
}

.editable:hover {
    background-color: #f1f5f9;
    border-radius: 4px;
    outline: 1px dashed #cbd5e1;
}
"""

path = "d:/my-project/kejaksaan-app2/static/css/style.css"

with open(path, 'r') as f:
    content = f.read()

# Clean up the messy end if exists
if ".editable:hover {" in content and "background-color" not in content.split(".editable:hover {")[-1]:
    # It's the broken ending
    content = content.rsplit(".editable:hover {", 1)[0]
    # Remove stray braces
    content = content.rstrip().rstrip('}')

# Append new
with open(path, 'w') as f:
    f.write(content + extra_css)

print("CSS Fixed")
