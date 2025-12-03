; -----------------------------------------------------------------------------
; PROVIDED
; -----------------------------------------------------------------------------
; Single literal in head
(head/literal) @provided

; Single literal in disjunction
(disjunction
    (literal) @provided
)

; Literal in head of conditional literal
(conditional_literal
    (literal) @provided
)

; -----------------------------------------------------------------------------
; NEEDED
; -----------------------------------------------------------------------------
(conditional_literal
  (condition
    (literal) @needed
  )
)

(head_aggregate
  (head_aggregate_elements
    (_) @needed
  )
)
