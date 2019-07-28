import re

import requests

sources = [
    ("open-sans-font.css",
     "https://fonts.googleapis.com/css?family=Open+Sans:400,300,600,400bold&subset=cyrillic,latin"),
    ("pt-sans-font.css",
     "https://fonts.googleapis.com/css?family=PT+Sans:400,700,400italic,700italic&subset=cyrillic,latin"),
]

for fname, floc in sources:
    css_content = requests.get(floc).content.decode()
    new_css_content = []
    regexp = "url\((https:\/\/fonts\.gstatic\.com\/.*\.ttf)\)"

    for line in css_content.split('\n'):
        m = re.search(regexp, line)
        if m:
            with open(m.group(1).split('/')[-1], 'wb') as ofile:
                ofile.write(requests.get(m.group(1)).content)
            new_fname = '/static/google/' + m.group(1).split('/')[-1]
            line = line.replace(m.group(1), new_fname)
        new_css_content.append(line)

    with open(fname, 'w') as ofile:
        ofile.write('\n'.join(new_css_content))
