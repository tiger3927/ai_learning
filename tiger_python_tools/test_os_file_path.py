import os

lst = os.listdir(os.getcwd() + "\\views")
files = [c for c in lst if os.path.isfile(os.getcwd() + "\\views\\"+c) and c.endswith(".html")]
print(files)

