import json

class EliotJSONEncoder(json.JSONEncoder):
    def default(self, o): ...
