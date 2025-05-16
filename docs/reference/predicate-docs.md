---
title: "Predicate Docstring"
icon: "material/file-document"
---

# Predicate Docstring

To document predicates in ASP, use a single block comment per predicate with the following format:

```txt
%*
#<predicate>.
<description>
#parameters
- <parameter_1_name>: <parameter_1_description>
- <parameter_2_name>: <parameter_2_description>
*%
```

### Example

!!! example

    ```txt
    %*
    #sudoku(X,Y,V).
    Represents a Sudoku board. The value of the cell at position (X, Y) is V.
    #parameters
    - X: The row index of the cell.
    - Y: The column index of the cell.
    - V: The value assigned to the cell.

    *%
    ```

All text within the block comment will be rendered in markdown. You can leverage any feature supported by mkdocs-material to enhance its presentation.

!!! tip

    If you prefer not to include these comments directly in your code, you can create a separate `.lp` file containing all the comments and include it in your encoding.
