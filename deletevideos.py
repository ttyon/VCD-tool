import os

if os.path.exists("./videos"):
    for file in os.scandir("./videos"):
        file = str(file.path).replace("\\", "/")
        if not file in "README.md":
            os.remove(file)
