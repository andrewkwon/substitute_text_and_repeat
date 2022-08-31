Good resource on parsers:
https://tomassetti.me/parsing-in-python/

What the input should look like:
```
<SUB* "where_we_are" => "World">
Hello where_we_are!
<*SUB>
Here is some pure unprocessed text.

There are three things that matter in the world:
<SUB* "thing_1" => "eggs", "thing_2" => "muffins", "thing_3" => "local radio">
	thing_1,
	thing_2,
	and thing_3.
<*SUB>

<RPT* i = 1; i < 4; i = i + 1; "\n">
	<SUB* "$i" => {i:02d}>
I have now said "cat" $i time(s).
		<RPT* j = 0; j < i; j = j + 1; " ">
meow
		<*RPT>
	<*SUB>
<*RPT>
```

The input will be used to generate python code which will create the output.

What the output of this example would look like:
```
Hello World!
Here is some pure unprocessed text.

There are three things that matter in the world:
	eggs,
	muffins,
	and local radio.

I have now said "cat" 1 time(s).
meow
I have now said "cat" 2 time(s).
meow meow
I have now said "cat" 3 time(s).
meow meow meow
```

So my idea is:
Parse the input with to create a string of python code
Execute that code to create the output

Parsy looks good for this application
https://parsy.readthedocs.io/en/latest/index.html