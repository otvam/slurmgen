import string
import json

t = string.Template('${village} folk send to $cause.')

a = {"village": "fdsf", "cause": "none"}

str = t.substitute(a)

print(str)

with open("example/job_tmpl.json", "r") as fid:
    tmpl = string.Template(fid.read())
    data = tmpl.substitute(a)
    data = json.loads(data)

print(data)