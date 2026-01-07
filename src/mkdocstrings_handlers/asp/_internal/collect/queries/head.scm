; -----------------------------------------------------------------------------
; This gathers the provided and needed predicates in the head of a statement
; -----------------------------------------------------------------------------

(head/literal
    (symbolic_atom)
) @provided

(disjunction
    (literal
        (symbolic_atom)
    ) @provided
)

(conditional_literal
    (literal
        (symbolic_atom)
    ) @provided
    (condition
        (literal
            (symbolic_atom)
        ) @needed
    )?
)

(head_aggregate
  (head_aggregate_elements
    (head_aggregate_element
            (literal
                (symbolic_atom)
            ) @provided
            (condition
                (literal
                    (symbolic_atom)
                ) @needed
            )?
        )
  )
)

(head/set_aggregate
    (set_aggregate_elements
        (set_aggregate_element
            (literal
                (symbolic_atom)
            ) @provided
            (condition
                (literal
                    (symbolic_atom)
                ) @needed
            )?
        )
    )
)
