%*
Finds the hypothetical model using abduction and the distance defined by the user

*%
%*
#_abduced(T,A)

Uses the concept of abduction to find the hypothetical model

#parameters
- T : type of abduction `add` or `rm`
- A : atom that has been abduced

*%
%*
#_abducible(T,A)

Abducible atoms full

#parameters
- T : type of abduction `add` or `rm`
- A : atom that can be abduced

*%
%*
#_distance(N,D,L)
    Distance between the real and hypothetical model.

#parameters
- N : Identifier for the distance, each identifier will yield one penalization
- D : Penalization value
- L : Level of the distance. Higher levels will be prioritized

*%
%*
#_query(T,A)
    Query that should hold in the hypothetical model

#parameters
- T : type of query `include` or `exclude`
- A : atom that the user wants to include or exclude

*%
%*
#_model(T,A)
    Atoms that are part of the model

#parameters
- T : type of model `real` or `hypothetical`
- A : atom that is part of the model

*%

#defined _abduced/2.
#defined _model/2.
#defined _distance/3.

:- _query(exclude,Atom), _model(hypothetical,Atom).
:- _query(include,Atom), not _model(hypothetical,Atom).

%*
#world(W).
#parameters
- W : W is a world; either `real` or `hypothetical`
*%
world(real;hypothetical).
{_abduced(X,Atom)} :- _abducible(X,Atom).

%--------------------------------------------------
%## Constraints

% - (C1) No sense to remove something that is not in input
:- not _model(real,Atom), _abduced(rm,Atom).
% - (C2) + (C4) No sense to both remove and add something
:- _abduced(add,Atom), _abduced(rm,Atom).
% - (C3) No sense to add something that is already in input
:- _model(real,Atom), _abduced(add,Atom).

_model(hypothetical,Atom) :- _abduced(add, Atom).

%--------------------------------------------------
%## Distance

:~ _distance(N,D,L). [D@L,N]

% Default distance
% _distance((Atom,h), 1, 0) :- _model(hypothetical, Atom), not _model(real, Atom).
% _distance((Atom,r), 1, 0) :- _model(real, Atom), not _model(hypothetical, Atom).
