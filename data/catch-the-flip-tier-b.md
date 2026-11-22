# Catch the flip, tier B: heterodyne records

Simulated measurement records of the buffer of a dissipative cat qubit, for the Alice & Bob challenge "Catch the flip" at the PushQuantum Hackathon (Munich, 20–22 November 2026).

Tier B holds the records of a heterodyne detector. They are the records of the challenge: your detector works on them, and the leaderboard scores its test split. Tier A, the click records of a photon counter, is the tutorial dataset `Alice_Bob/catch-the-flip-tier-a`, where a flip can be seen by eye. The statement of the challenge, the tutorials and a template notebook are in the workspace `Alice_Bob/catch-the-flip`.

## Explore the data

The table is the result of the SQL query in the box below it. The dataset is the table `data`: edit the query to filter, count or sort. The query below shows the first 6 of the 400 bins of I and Q; `SELECT * FROM data` shows the full records. The table under the box counts the segments and the flips of each split and cat size (the labels of the test split are hidden).

*Showing the first 10 of 45,000 rows. Increase the table's `page_size` to embed more in the static export.*

| split | segment_id (i32) | nbar (f64) | label (i8) | I_first_6_bins (list[f32]) | Q_first_6_bins (list[f32]) |
|---|---|---|---|---|---|
| train | 0 | 3.0 | 0 | `[1.7978515625, -2.158203125, 0.51318359375, -2.30078125, 0.153076171875, -2.525390625]` | `[1.5830078125, -0.413330078125, 0.3056640625, -0.2236328125, 1.630859375, -0.802734375]` |
| train | 1 | 3.0 | 0 | `[0.286865234375, -1.84375, -2.4296875, 1.6923828125, -2.693359375, -2.6640625]` | `[4.265625, 1.7431640625, -2.345703125, 0.91748046875, 1.9365234375, -0.265625]` |
| train | 2 | 3.5 | 0 | `[-0.70703125, 0.63818359375, 0.59619140625, 2.681640625, 1.1083984375, -0.488037109375]` | `[2.486328125, 1.837890625, 2, 1.47265625, -1.580078125, -0.8857421875]` |
| train | 3 | 3.5 | 0 | `[-0.88037109375, -3.583984375, -1.0859375, -0.320556640625, -0.95849609375, 0.40869140625]` | `[0.80859375, -1.36328125, 0.92431640625, 0.58447265625, -0.11297607421875, -2.87890625]` |
| train | 4 | 3.5 | 0 | `[0.6103515625, -1.96875, 0.289306640625, -0.2222900390625, 2.7109375, -0.7109375]` | `[-0.0172882080078125, 1.4677734375, 1.0380859375, 0.6572265625, 0.2349853515625, -2.8828125]` |
| train | 5 | 2.0 | 0 | `[-2.35546875, -0.402587890625, 0.360107421875, 2.13671875, -2.01171875, 2.53515625]` | `[1.908203125, -1.1025390625, -0.53759765625, -1.310546875, -1.517578125, 0.12261962890625]` |
| train | 6 | 3.5 | 0 | `[-0.85107421875, 2.27734375, 0.257568359375, -0.415283203125, -0.419677734375, -0.587890625]` | `[0.056640625, -1.0517578125, -0.1666259765625, 4.27734375, -1.03515625, -0.89111328125]` |
| train | 7 | 2.0 | 0 | `[-1.8369140625, 0.8037109375, 2.162109375, 0.775390625, 2.541015625, -1.193359375]` | `[-2.03515625, -0.06146240234375, -2.044921875, 0.50244140625, 2.38671875, 0.98681640625]` |
| train | 8 | 3.0 | 0 | `[1.3779296875, -0.7255859375, 4.50390625, -2.28515625, 0.52392578125, -0.1832275390625]` | `[0.50244140625, 1.0595703125, -1.8017578125, -4.79296875, -2.443359375, 0.096923828125]` |
| train | 9 | 2.5 | 0 | `[-4.07421875, -0.181640625, 0.97119140625, -0.493896484375, 2.375, 1.4248046875]` | `[2.45703125, -0.1348876953125, -1.8134765625, 1.314453125, -3.056640625, -0.5849609375]` |

45,000 rows, 6 columns

```sql
SELECT split, segment_id, nbar, label,
       I[1:6] AS I_first_6_bins, Q[1:6] AS Q_first_6_bins
FROM data
```

*Showing the first 10 of 12 rows. Increase the table's `page_size` to embed more in the static export.*

| split | nbar (f64) | segments (i64) | flips (i32) | flip_percent (f64) |
|---|---|---|---|---|
| train | 2.0 | 1,000 | 158 | 15.80 |
| train | 2.5 | 2,000 | 133 | 6.65 |
| train | 3.0 | 4,000 | 121 | 3.03 |
| train | 3.5 | 8,000 | 127 | 1.59 |
| val | 2.0 | 500 | 131 | 26.20 |
| val | 2.5 | 1,000 | 113 | 11.30 |
| val | 3.0 | 2,000 | 168 | 8.40 |
| val | 3.5 | 4,000 | 174 | 4.35 |
| test | 2.0 | 1,500 | None | None |
| test | 2.5 | 3,000 | None | None |

12 rows, 5 columns

## What a row is

A row is one segment, one memory experiment. The cat is prepared in the state +α at t = 0, the output of its buffer is monitored for a duration T_seg = 200, and the cat is read out in the Z basis. Times are in units of 1/κ₂, the inverse of the two-photon dissipation rate. The `label` is 1 when the readout gave −α: the cat has flipped.

The record of a segment holds the two quadratures I and Q of the buffer output, measured by an ideal heterodyne detector (efficiency 1) and averaged over 400 bins of duration 0.5. Convention (dynamiqs): for the measured channel L = sqrt(η/2) (a² − α²), the record is I = ⟨L + L†⟩ + ξ(t), with ξ a white noise of variance 1 per unit time, so each bin carries Gaussian noise of standard deviation sqrt(400/200) = 1.41. Q is the same for the channel iL. The burst of a flip sits under this noise.

**A note on the baseline of I.** The simulation uses a first-order scheme with a fixed time step, which shifts the mean of I in proportion to the step. The training records were simulated with a step of 0.000016: the mean of their I agrees with the master equation of the nominal device within its statistical error (0.001 to 0.002, depending on the cat size). The validation and test records were simulated with a step of 0.0005 and are shifted by about −0.004: do not read physics into a baseline difference of that size. The mean of Q is not affected.

Every split mixes segments of four cat sizes, nbar = 2, 2.5, 3 and 3.5 photons, in the proportions 1 : 2 : 4 : 8 (big cats flip less often, so they get more segments), in random order. The column `nbar` gives the cat size of each segment.

## Splits

Each split is one partition of the dataset.

| split | partition | device | labels | segments | use |
|---|---|---|---|---|---|
| train | 0 | nominal (the one you can simulate) | yes | 15 000 | design and train your detector |
| val | 1 | hidden test device | yes | 7 500 | measure how your detector transfers to the real device |
| test | 2 | hidden test device | no | 22 500 | your submission, scored on the leaderboard |

The hidden device differs from the nominal one in kind, not only in numbers: its buffer is a real resonator of finite bandwidth (two-mode model) and its memory has a small Kerr non-linearity, the same at every cat size. The noise rates and the cat sizes are the nominal ones.

Fraction of flip labels:

| cat size nbar | 2 | 2.5 | 3 | 3.5 |
|---|---|---|---|---|
| nominal device, master equation | 14.6 % | 7.30 % | 3.40 % | 1.51 % |
| train | 15.8 ± 1.2 % | 6.7 ± 0.6 % | 3.0 ± 0.3 % | 1.59 ± 0.14 % |
| val (hidden device) | 26.2 ± 2.0 % | 11.3 ± 1.0 % | 8.4 ± 0.6 % | 4.3 ± 0.3 % |

The errors are binomial. On the test split, the leaderboard score carries a statistical uncertainty of about ±0.015.

## Columns

| column | type | description |
|---|---|---|
| `split` | string | train, val or test |
| `segment_id` | int32 | position of the segment in its split, starting at 0; the segment_id of a submission is the one of the test split |
| `nbar` | float64 | cat size of the segment (mean photon number of the coherent states) |
| `label` | int8 | 1 if the cat has flipped, 0 otherwise; null in the test split |
| `I` | list of 400 float32 | quadrature I of the buffer output, one value per bin |
| `Q` | list of 400 float32 | quadrature Q of the buffer output, one value per bin |

The values of I and Q have the precision of 16-bit floats (a resolution of about 0.001, far below the noise).

## Loading

```python
import pyarrow.compute as pc
from aqora.pyarrow import dataset  # pip install "aqora[pyarrow]"

ds = dataset("Alice_Bob/catch-the-flip-tier-b", "v1.0.0")
train = ds.to_table(filter=pc.field("split") == "train")

nbar = train["nbar"].to_numpy()
labels = train["label"].to_numpy()
I = train["I"].combine_chunks().flatten().to_numpy().reshape(len(train), -1)  # shape (segments, 400)
Q = train["Q"].combine_chunks().flatten().to_numpy().reshape(len(train), -1)
```

With pandas:

```python
pd.read_parquet("aqora://Alice_Bob/catch-the-flip-tier-b/v1.0.0", filters=[("split", "==", "train")])
```

The three splits take 150 MB in memory as arrays: load one split at a time. In the workspace of the challenge, `catchtheflip.records.load_aqora("B", "train")` returns the split as a dictionary of NumPy arrays (`nbar`, `labels`, `I`, `Q`, `meta`), with I and Q as 16-bit floats.

## Submission format

A CSV file with a header and one row per segment of the test split, in the order of `segment_id`:

```csv
segment_id,score,decision
0,0.12,0
1,3.41,1
...
```

`score` is any real number, where higher means more suspicious. The leaderboard discards the 30 % of the segments with the highest scores, all cat sizes together, and reports the flip suppression, 1 − rho70, where rho70 is the fraction of flips among the segments that are kept divided by the fraction of flips among all segments.

`decision` is 0 or 1 (1 = discard) and marks the segments that you yourself would discard.

To get your score, save the file from the template notebook of the workspace, then sign in on the live leaderboard and press Submit. The leaderboard shows the score with two decimals. A team may submit as often as it likes, and its final submission is one file: the last one it submitted before the deadline.

## Make your own data

The script `scripts/generate_dataset.py` of the workspace produces labelled data of the nominal device at any cat size and with any seed. The test split cannot be regenerated: its seed and the parameters of its device are private.
