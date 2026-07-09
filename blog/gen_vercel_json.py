import difflib
import json

with open("old.txt") as o, open("new.txt") as n:
    old = o.readlines()
    new = n.readlines()

redirects = []
for url in old:
    m = difflib.get_close_matches(url, new, n=1, cutoff=0.3)
    redirects.append(
        {"source": url.rstrip(), "destination": m[0].rstrip(), "permanent": True}
    )
redirects.append(
    {"source": "/(.*)", "destination": "https://13m0n4de.pages.dev/", "permanent": True}
)

vercel = {"$schema": "https://openapi.vercel.sh/vercel.json", "redirects": redirects}

print(json.dumps(vercel))
