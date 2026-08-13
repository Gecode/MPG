SEND+MORE=MONEY
trace<Int>::init(id:0) slack: 100.00% (72 values)
trace<Int>::prune(id:0): [0] = [1..9] - {0} by post()
trace<Int>::prune(id:0): [4] = [1..9] - {0} by post()
trace<Int>::prune(id:0): [0] = 9 - {1..8} by propagator(id:2)
  ...
trace<Int>::fix(id:0) slack: 33.33% - 66.67%
  ...
trace<Int>::done(id:0) slack: 0%
        {9, 5, 6, 7, 1, 0, 8, 2}
trace<Int>::prune(id:0): [1] = [6..7] - {5} by brancher(id:1)
  ...
