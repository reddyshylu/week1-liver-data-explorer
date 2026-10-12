import io
import unittest
from pathlib import Path
from liver_data import read_liver


class LiverDataTests(unittest.TestCase):
    def test_bundled_dataset(self):
        frame = read_liver(Path(__file__).resolve().parents[1] / 'data' / 'hcvdat0.csv')
        self.assertEqual(len(frame), 615)
        self.assertEqual(frame['ALP'].isna().sum(), 18)
        self.assertEqual(frame['Category'].value_counts()['Blood Donor'], 533)
        self.assertEqual(len(frame.columns), 13)

    def test_wrong_dataset_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Missing required columns'):
            read_liver(io.StringIO('symbol,shares\nABC,1\n'))

    def test_invalid_measurement_rejected(self):
        source = Path(__file__).resolve().parents[1] / 'data' / 'hcvdat0.csv'
        frame = read_liver(source)
        frame['ALT'] = frame['ALT'].astype(object)
        frame.loc[0, 'ALT'] = 'invalid'
        with self.assertRaisesRegex(ValueError, 'ALT'):
            read_liver(io.StringIO(frame.to_csv(index=False)))


if __name__ == '__main__':
    unittest.main()
