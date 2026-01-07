%# Sudoku Puzzle
%   Uses the well known [puzzle](https://en.wikipedia.org/wiki/Sudoku)
%

#const dim = 3.
val(1..dim*dim).
pos(X,Y) :- val(X), val(Y).

%*! sudoku(X,Y,V)

Describes a sudoku board. The value of cell (X,Y) is V.

Args:
    - X: the row of the cell
    - Y: the column of the cell
    - V: the value of the cell
*%

%*! initial(X,Y,V)

Describes initial values of the sudoku board. The value of cell (X,Y) is V.

Args:
    - X: the row of the cell
    - Y: the column of the cell
    - V: the value of the cell
*%

%*! pos(X,Y)

Describes a cell (X,Y) in the sudoku board.

Args:
    - X: the row of the cell
    - Y: the column of the cell
*%

%*! val(V)

Describes a possible value V for a cell.

Args:
    - V: the value
*%


subgrid(X,Y,(((X-1)/dim)*dim+((Y-1)/dim))) :- pos(X,Y).

% A choice rule for each cell
1 { sudoku(X,Y,V) : val(V) } 1 :- pos(X,Y).

%## Constraints
:- sudoku(X,Y,V), sudoku(X',Y,V), X != X'.
:- sudoku(X,Y,V), sudoku(X,Y',V), Y != Y'.
:- sudoku(X,Y,V), sudoku(X',Y',V), subgrid(X,Y,S), subgrid(X',Y',S), (X,Y)!=(X',Y').

sudoku(X,Y,V) :- initial(X,Y,V).

%## Shows

#show .
#show sudoku/3.
