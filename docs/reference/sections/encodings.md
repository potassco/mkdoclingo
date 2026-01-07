---
icon: "material/file-code"
---

Generates a section with one section for each file included in the root file.

Each section will include the encoding where comments are rendered as markdown.
This means that any markdown code can be rendered, including sections, admonitions, code, etc.


!!! note "Commented clingo code"

    If a comment can be interpreted by clingo as a valid statement, it will be ignored.

    === ":material-palette-outline: Output"

        Will skip the next comment
        ```clingo
            c:-d,e.
        ```

        The next line prints a line separator

        ----------------------

        The following lines will not be printed and can use in the encodings as separator

    === ":material-code-block-tags: Usage"

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

!!! warning "Markdown headers"

    When using `#` for markdown headers, make sure there is no trailing space between the clingo comment `%` and the `#`.

    ```clingo

        % # Incorrect title
        %# Correct title
    ```



For each encoding, a section in the table of content will be created.


!!! example

    === ":material-palette-outline: Output"

        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                encodings:
                    source: true
                start_level: 3

    === ":material-code-block-tags: Usage"

        ```
        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                encodings:
                    source: true
                start_level: 3
        ```

        Notice the use of `start_level` passed for rendering headers and the TOC.


## Configuration options



The option `encodings` can be further customized with the following options:

- `source` Boolean indicating if the source code is included. Default to True.
- `git_link` Boolean indicating if github links should be added in the encoding title. Default to False.


!!! example



    === ":material-palette-outline: Output"

        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                encodings:
                    git_link: true
                    source: false
                start_level: 3

    === ":material-code-block-tags: Usage"

        ```
        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                encodings:
                    git_link: true
                    source: false
                start_level: 3
        ```
