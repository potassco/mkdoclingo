---
icon: "material/rocket-launch"
---

# Quick Start Guide


Consider the following sudoku encoding.

```clingo
    #const dim = 3.
    val(1..dim*dim).
    pos(X,Y) :- val(X), val(Y).

    subgrid(X,Y,(((X-1)/dim)*dim+((Y-1)/dim))) :- pos(X,Y).

    1 { sudoku(X,Y,V) : val(V) } 1 :- pos(X,Y).

    :- sudoku(X,Y,V), sudoku(X',Y,V), X != X'.
    :- sudoku(X,Y,V), sudoku(X,Y',V), Y != Y'.
    :- sudoku(X,Y,V), sudoku(X',Y',V), subgrid(X,Y,S), subgrid(X',Y',S), (X,Y)!=(X',Y').

    sudoku(X,Y,V) :- initial(X,Y,V).

    #show .
    #show sudoku/3.
```

First you have to include the encoding in your mkdocs documentation using the `::: <path-to-file>` syntax provided by *mkdoclingo*. You must specify the `handler: asp` to indicate that it is an ASP encoding. You can also pass options to customize the rendering of the documentation. For example, to enable the glossary, predicate table and dependency graph, you can use the following configuration:

```markdown
::: examples/sudoku/encoding.lp
    handler: asp
    options:
        glossary: true
        predicate_table: true
        dependency_graph: true
        encodings: true
        start_level: 1
```

More details about the available options can be found in [`reference`](../../reference).


In this guide we will go step by step to showcase the features, the rendered documentation can be found in [`examples/sudoku`](../../examples/sudoku).
To include the file anywhere in your mkdocs documentation, you can use the following syntax:


**Markdown docs**

First we can add a title for the encoding by adding a comment at the top of the file using a markdown header. This will be shown as a markdown title in the documentation for the encodings.

```clingo
    %# Sudoku Puzzle

    #const dim = 3.
    val(1..dim*dim).
    pos(X,Y) :- val(X), val(Y).

    ...
```

Other comments in the encoding will be rendered as markdown text in the documentation of the encoding as shown in [`reference/sections/encodings`](../../reference/sections/encodings). Double comments `%%` and comments that are valid clingo code will be ignored.

**Predicate docs**

We can add documentation for a predicate using a block comment like the following. The placement of the comment does not matter as long as it is included in the encoding (even using `#include` statements), and inside a single block comment starting with `%*!`.

```clingo
    %*! sudoku(X,Y,V)

    Describes a sudoku board. The value of cell (X,Y) is V.

    Args:
        - X: the row of the cell
        - Y: the column of the cell
        - V: the value of the cell
    *%
```

This will generate a section in the predicate documentation for the predicate `sudoku/3` with the description and arguments rendered in markdown. It will also generate an entry in the predicate summary table at the start.
For the full format, please refer to [`reference/predicate-docs`](../../reference/predicate-docs).

**Predicate types**

Automatically, *mkdoclingo* will identify input and output predicates based on their usage in the encoding. In this case, `initial/3` will be marked as an input predicate  since it is not in the encoding, and `sudoku/3` as an output predicate in the predicate documentation since it is shown. This is rendered in the [`reference/sections/glossary`](../../reference/sections/glossary), the [`reference/sections/dependency-graph`](../../reference/sections/dependency-graph) and the [`reference/sections/predicate-table`](../../reference/sections/predicate-table).
