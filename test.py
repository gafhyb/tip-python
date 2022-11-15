import sys
import unittest
import provider
from io import StringIO
from contextlib import redirect_stdout
import json


class TestTips(unittest.TestCase):
    def _result(self, content):
        f = StringIO()
        with redirect_stdout(f):
            provider.main(content)
        return {i["label"]: i for i in json.loads(f.getvalue()) if "label" in i}

    def _common_ok(self, content, key, value):
        result = self._result(content)
        self.assertIn(key, result)
        self.assertEqual(value, result[key]["value"])

    def _common_ko(self, content, key):
        result = self._result(content)
        self.assertNotIn(key, result)

    def test_authiris_ok(self):
        self._common_ok(
            "toto",
            "Authiris toto",
            "https://authiris.unistra.fr/authiris/bin/cptedit?uti=toto",
        )

    def test_authiris_ko(self):
        self._common_ko("héhé", "Authiris héhé")

    def test_wikitionnaire_ok(self):
        self._common_ok(
            "héhé",
            "Wikitionnaire héhé",
            "https://fr.wiktionary.org/w/index.php?search=h%C3%A9h%C3%A9",
        )

    def test_wikitionnaire_ko(self):
        self._common_ko("expression régulière", "Wikitionnaire expression régulière")

    def test_wikipedia(self):
        self._common_ok(
            "expression régulière",
            "Wikipedia expression régulière",
            "https://fr.wikipedia.org/w/index.php?title=expression+r%C3%A9guli%C3%A8re",
        )

    def test_url(self):
        self._common_ok(
            'toto<a href="https://www.unistra.fr">Unistra</a>tutu titi',
            "Open https://www.unistra.fr",
            "https://www.unistra.fr",
        )

    def test_timestamp(self):
        self._common_ok("1587476268", "Timestamp", "21/04/2020 15:37:48")

    def test_jwt(self):
        self._common_ok(
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzb21lIjoicGF5bG9hZCJ9.Joh1R2dYzkRvDkqv3sygm5YyK8Gi4ShZqbhK2gxcs2U",
            "JWT",
            '[{"typ": "JWT", "alg": "HS256"}, {"some": "payload"}]',
        )


if __name__ == "__main__":
    unittest.main()
