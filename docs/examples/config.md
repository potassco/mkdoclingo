---
icon: material/motorbike
---

# Product Configuration

Documentation generated automatically, showcasing the use of `mkdoclingo` for a large project
where the documentation of predicates is in a separate file.

!!! tip

    Use the :material-file-eye-outline: icon in the top right to see the source code for this page.


::: examples/config/encoding-base-clingo.lp
    handler: asp
    options:
        source: true
        glossary:
            include_undocumented: false
            include_references: false
        predicate_table:
            include_undocumented: false
        start_level: 2
