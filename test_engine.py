import json, unittest
from pathlib import Path
from engine import analyze
class ContractTests(unittest.TestCase):
    def test_expected_outcomes(self):
        for case in json.loads(Path(__file__).with_name('cases.json').read_text()):
            with self.subTest(input=case['input']):
                self.assertEqual(analyze(case['input']),case['expected'])
    def test_does_not_mutate_input(self):
        data=json.loads(Path(__file__).with_name('sample.json').read_text())
        before=json.dumps(data,sort_keys=True)
        analyze(data)
        self.assertEqual(before,json.dumps(data,sort_keys=True))
if __name__ == '__main__': unittest.main()
