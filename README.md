# Substitute Text and Repeat (STAR)
STAR is a tool which parses input text marked with substitution and repetition commands to produce a formatted output.

The purpose of this tool is to make it quicker and easier to create simple texts that have repetitive elements.

## Example

If we give STAR the following input:
```
Let's roll some dice!
I have 2 dice, so the results I could get are as follows:

<RPT* `i = 1` | `i <= 6` | `i = i + 1` | '\n'>
	<RPT* `j = 1` | `j <= 6` | `j = j + 1` | ', '>
		<SUB* 'result' => f'({i}, {j})', 'sum' => f'{i + j}'>
result -> sum
		<*SUB>
	<*RPT>
<*RPT>

Let's give them a roll!
<RPT* `once = True; import random; roll = (random.randint(1,6), random.randint(1,6))` | `once` | `once = False` | ''>
	<SUB* 'roll' => f'{roll}', 'sum' => f'{roll[0] + roll[1]}'>
roll -> sum
	<*SUB>
<*RPT>
```

Then STAR will produce the following output (or something similar anyways, the random roll may be different between executions)
```
Let's roll some dice!
I have 2 dice, so the results I could get are as follows:

(1, 1) -> 2, (1, 2) -> 3, (1, 3) -> 4, (1, 4) -> 5, (1, 5) -> 6, (1, 6) -> 7
(2, 1) -> 3, (2, 2) -> 4, (2, 3) -> 5, (2, 4) -> 6, (2, 5) -> 7, (2, 6) -> 8
(3, 1) -> 4, (3, 2) -> 5, (3, 3) -> 6, (3, 4) -> 7, (3, 5) -> 8, (3, 6) -> 9
(4, 1) -> 5, (4, 2) -> 6, (4, 3) -> 7, (4, 4) -> 8, (4, 5) -> 9, (4, 6) -> 10
(5, 1) -> 6, (5, 2) -> 7, (5, 3) -> 8, (5, 4) -> 9, (5, 5) -> 10, (5, 6) -> 11
(6, 1) -> 7, (6, 2) -> 8, (6, 3) -> 9, (6, 4) -> 10, (6, 5) -> 11, (6, 6) -> 12

Let's give them a roll!
(1, 1) -> 2


```

For more examples, see the Examples directory in this git repo.

## How to Use STAR

STAR runs with python3. It specifically uses features of python 3.9.0.

STAR uses parsy for its parsing. It was developed with parsy-1.4.0 in particular. You can install parsy with pip:
```sh
pip install parsy
```

STAR reads from stdin and prints to stdout. To pass it input, pipe the input to the process.
```sh
cat example.txt | python3 star.py
```