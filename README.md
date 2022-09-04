# Substitute Text and Repeat (STAR)
STAR is a tool which parses input text marked with substitution and repetition commands to produce a formatted output.

The purpose of this tool is to make it quicker and easier to create simple texts that have repetitive elements.

## Example

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