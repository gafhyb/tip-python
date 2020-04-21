import sys
import unittest
import provider
from io import StringIO
from contextlib import redirect_stdout
import json


class TestTips(unittest.TestCase):
    def _common(self, content):
        f = StringIO()
        with redirect_stdout(f):
            provider.main(content)
        return json.loads(f.getvalue())

    def test_authiris_ok(self):
        result = self._common('toto')
        self.assertIn('Authiris toto', [i['label'] for i in result if 'label' in i])
        self.assertEqual('https://authiris.unistra.fr/authiris/bin/cptedit?uti=toto',
                         {i['label']: i for i in result if 'label' in i}['Authiris toto']['value'])

    def test_authiris_ko(self):
        result = self._common('héhé')
        self.assertNotIn('Authiris toto', [i['label'] for i in result if 'label' in i])

    def test_wikitionnaire_ok(self):
        result = self._common('héhé')
        self.assertIn('Wikitionnaire héhé', [i['label'] for i in result if 'label' in i])
        self.assertEqual('https://fr.wiktionary.org/w/index.php?search=h%C3%A9h%C3%A9',
                         {i['label']: i for i in result if 'label' in i}['Wikitionnaire héhé']['value'])

    def test_wikitionnaire_ko(self):
        result = self._common('expression régulière')
        self.assertNotIn('Wikitionnaire expression régulière', [i['label'] for i in result if 'label' in i])

    def test_wikipedia(self):
        result = self._common('expression régulière')
        self.assertIn('Wikipedia expression régulière', [i['label'] for i in result if 'label' in i])
        self.assertEqual('https://fr.wikipedia.org/w/index.php?title=expression+r%C3%A9guli%C3%A8re',
                         {i['label']: i for i in result if 'label' in i}['Wikipedia expression régulière']['value'])

    def test_url(self):
        result = self._common('toto<a href="https://www.unistra.fr">Unistra</a>tutu titi')
        self.assertIn('Open https://www.unistra.fr', [i['label'] for i in result if 'label' in i])
        self.assertEqual('https://www.unistra.fr',
                         {i['label']: i for i in result if 'label' in i}['Open https://www.unistra.fr']['value'])

    def test_timestamp(self):
        result = self._common('1587476268')
        self.assertIn('Timestamp', [i['label'] for i in result if 'label' in i])
        self.assertEqual('21/04/2020 15:37:48',
                         {i['label']: i for i in result if 'label' in i}['Timestamp']['value'])

    def test_jwt(self):
        result = self._common(
            'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzb21lIjoicGF5bG9hZCJ9.Joh1R2dYzkRvDkqv3sygm5YyK8Gi4ShZqbhK2gxcs2U')
        self.assertIn('JWT', [i['label'] for i in result if 'label' in i])
        self.assertEqual('[{"typ": "JWT", "alg": "HS256"}, {"some": "payload"}]',
                         {i['label']: i for i in result if 'label' in i}['JWT']['value'])


if __name__ == '__main__':
    unittest.main()
