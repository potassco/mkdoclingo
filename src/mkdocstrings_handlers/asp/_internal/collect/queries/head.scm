; -----------------------------------------------------------------------------
; This gathers the provided and needed predicates in the head of a statement
; -----------------------------------------------------------------------------

(head/literal) @provided

(disjunction
    (literal) @provided
)

(conditional_literal
    (literal) @provided
    (condition
        (literal) @needed
    )?
)

(head_aggregate
  (head_aggregate_elements
    (head_aggregate_element
            (literal) @needed
            (condition
                (literal) @needed
            )?
        )
  )
)

(head/set_aggregate
    (set_aggregate_elements
        (set_aggregate_element
            (literal) @provided
            (condition
                (literal) @needed
            )?
        )
    )
)
