---
title: "Predicate Docstring"
icon: "material/file-document"
---

# Predicate Docstring

To document predicates in ASP, use a single block comment per predicate with the following format:

```txt
%* <predicate>
.................
<description>
Args:
    <parameter_1_name> (<optional_parameter_1_type>): <parameter_1_description>
    <parameter_2_name> (<optional_parameter_2_type>): <parameter_2_description>
*%
```

### Example

!!! example

    ```txt
    %* sudoku(X,Y,V)
    .................
    Represents a Sudoku board. The value of the cell at position (X, Y) is V.
    Args:
        X (int): The row index of the cell.
        Y (int): The column index of the cell.
        V (int): The value assigned to the cell.

    *%
    ```

All text within the block comment will be rendered in markdown. You can leverage any feature supported by mkdocs-material to enhance its presentation.

!!! tip

    If you prefer not to include these comments directly in your code, you can create a separate `.lp` file containing all the comments and include it in your encoding.
