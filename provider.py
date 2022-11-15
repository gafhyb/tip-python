#!/Users/virgile/.venvs/tip/bin/python

import json
import sys
import urllib.parse
import re

import unicodedata


def jwt_payload(content):
    import jwt

    return jwt.decode(
        content, options={"verify_signature": False}, algorithms=["HS256"]
    )


def jwt_header(content):
    import jwt

    return jwt.get_unverified_header(content)


def to_date(content):
    from datetime import datetime

    return datetime.fromtimestamp(int(content)).strftime("%d/%m/%Y %H:%M:%S")


def main(orig):
    # open('/tmp/tip.txt','w').write(input)
    input = unicodedata.normalize("NFC", orig)
    text = input if len(input) < 1000 else "Too long too display"
    items = [
        {"type": "text", "value": f"Input {text}"},
    ]
    encoded = urllib.parse.quote_plus(f"{input}")

    def find():
        is_search = True
        patterns = [
            {
                "pattern": "^[a-zA-Z0-9.-]{3,16}$",
                "type": "url",
                "label": "Authiris {match}",
                "generated": "https://authiris.unistra.fr/authiris/bin/cptedit?uti={match}",
            },
            {
                "pattern": "^[\w]+$",
                "type": "url",
                "label": "Wikitionnaire {match}",
                "generated": "https://fr.wiktionary.org/w/index.php?search={encoded}",
            },
            {
                "pattern": "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                "type": "url",
                "label": "Open {match}",
                "generated": "{match}",
                "search": False,
            },
            {
                "pattern": "^[\w ]+$",
                "type": "url",
                "label": "Wikipedia {match}",
                "generated": "https://fr.wikipedia.org/w/index.php?title={encoded}",
            },
            {
                "pattern": "^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$",
                "type": "text",
                "label": "JWT",
                "actions": ["jwt_header", "jwt_payload"],
                "search": False,
            },
            {
                "pattern": "^[1-9][0-9]{6,9}$",
                "type": "text",
                "label": "Timestamp",
                "actions": ["to_date"],
                "search": False,
            },
        ]
        for pattern in patterns:
            matches = re.findall(pattern["pattern"], input)
            if len(matches) > 0:
                for m in matches:
                    is_search &= "search" not in pattern or (
                        "search" in pattern and pattern["search"]
                    )
                    m_encoded = urllib.parse.quote_plus(f"{m}")
                    data = {
                        "type": pattern["type"],
                        "label": pattern["label"].format(match=m, encoded=m_encoded),
                    }
                    if "generated" in pattern:
                        data["value"] = pattern["generated"].format(
                            match=m, encoded=m_encoded
                        )
                    elif "actions" in pattern:
                        data["value"] = (
                            json.dumps(
                                [
                                    getattr(sys.modules[__name__], action)(m)
                                    for action in pattern["actions"]
                                ]
                            )
                            if len(pattern["actions"]) > 1
                            else getattr(sys.modules[__name__], pattern["actions"][0])(
                                m
                            )
                        )
                    items.append(data)
        return is_search

    if find():
        items.append(
            {
                "type": "url",
                "label": f"Google {input}",
                "value": f"https://google.com/search?q={encoded}",
            }
        )

    print(json.dumps(items))


if __name__ == "__main__":
    main(sys.argv[1])
