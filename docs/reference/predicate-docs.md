---
title: "Predicate Docstring"
icon: "material/file-document"
---

# Predicate Docstring

To document predicates in ASP, use a single block comment per predicate with the following format:

```txt
%*! <predicate(arg1,arg2,...)>

<description>

Args:
    - <arg_1_name>: <arg_1_description>
    - <arg_2_name>: <arg_2_description>
*%
```


### Example

!!! example

    ```txt
        %*! sudoku(X,Y,V)

        Describes a sudoku board. The value of cell (X,Y) is V.

        Args:
            - X: the row of the cell
            - Y: the column of the cell
            - V: the value of the cell
        *%
    ```

!!! tip "Markdown support"

    All text within the block comment will be rendered in markdown. You can leverage any feature supported by mkdocs-material to enhance its presentation.

!!! warning "Single block comment"

    Each predicate docstring should be in a single block comment for it to be recognized correctly.

!!! warning "Tuples not supported"

    Using tuples in the predicate is not supported, e.g., `sudoku((X,Y),V)`.
    Instead, use a single argument and make the description clear in the arguments, e.g., `sudoku(Pos,V)` where `Pos` represents the position `(X,Y)`.


!!! tip "Separate documentation file"

    If you prefer not to include these comments directly in your code, you can create a separate `.lp` file containing all the comments and include it in your encoding.
