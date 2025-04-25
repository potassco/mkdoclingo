---
icon: "material/file-code"
---

Generates a section with one section for each file included in the root file.

Each section will include the encoding where comments are rendered as markdown.
This means that any markdown code can be rendered, including sections, admonitions, code, etc.


!!! note "Commented clingo code"

    If a comment can be interpreted by clingo as a valid statement, it will be ignored.

    === "Encoding"

        ```clingo

        % Will skip the next comment since it is parsable
        % a:-b.
        %% This is also skipped since it is a comment in clingo
        c:-d,e.
        % The next line prints a line separator
        %----------------------
        % The following lines will not be printed and can use in the encodings to separate sections
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        %%=================================
        %%---------------------------------
        ```

    === "Output"

        Will skip the next comment
        ```clingo
            c:-d,e.
        ```

        The next line prints a line separator

        ----------------------

        The following lines will not be printed and can use in the encodings as separator

For each encoding, a section in the table of content will be created.


!!! example

    === "Usage"

        ```
        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                encodings:
                    source: true
                start_level: 3
        ```

        Notice the use of `start_level` passed for rendering headers and the TOC.

    === "Output"

        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                encodings:
                    source: true
                start_level: 3

## Configuration options

- `source` Boolean indicating if the source code is included. By default source code is not included.
- `include-git-links` Boolean indicating if github links should be added. By default git links are included. (TODO)
- `ignore-includes` Boolean indication that the included files should not be rendered. By default all included files are rendered. (TODO)
