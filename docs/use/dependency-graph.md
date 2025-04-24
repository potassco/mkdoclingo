---
icon: "material/graphql"
---


Generates a dependency graph between predicates. Input predicates are shown purple and shown predicates in green.

!!! example

    === "Usage"

        ```
        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                dependency_graph: true
                start_level: 3
        ```

    === "Output"

        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                dependency_graph: true
                start_level: 3



## Configuration options

- `ignore-undocumented` TODO
- `ignore-hidden` This would make it not be connected TODO
- `ignore-includes` Boolean indication that the included files should not considered TODO
