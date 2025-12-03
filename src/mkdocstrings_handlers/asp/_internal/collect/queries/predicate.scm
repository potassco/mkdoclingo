; -----------------------------------------------------------------------------
; This contains the queries to capture literals in ASP code.
;
; It's used to get the negation, identifier, and terms of literals.
; -----------------------------------------------------------------------------

; Normal literal occurrence
(literal
    (default_negation)? @negation

    (symbolic_atom
        (identifier) @identifier
        (terms
            (_) @term
        )?
    )
)

; Literal occuring directly in a body
(body_literal
    (default_negation)? @negation

    (symbolic_atom
        (identifier) @identifier
        (terms
            (_) @term
        )?
    )
)
