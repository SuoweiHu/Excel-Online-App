"""
读取Json文件
"""
import json

class JSON: 
    PATH = "src/json/"
    def save(text, path):
        s = json.dumps(text, indent=4, ensure_ascii=False)
        with open(path, "w+") as f:
            f.write(s)
            f.close()
        f.close()

    def read(path):
        with open(path, 'r') as f:
            data = json.load(f)
            f.close()
            return data