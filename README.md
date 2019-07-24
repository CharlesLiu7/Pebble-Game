# Pebble Game for Two-Dimensional Rigidity Percolation

This repo is a naive code implement of paper ["An Algorithm for Two-Dimensional Rigidity Percolation: The Pebble Game"](https://pdfs.semanticscholar.org/4783/4fa63ceb304a0516d5d19f04992f12616f6a.pdf), mainly implements two functions, which are `Find_Pebble` and `Rearrange_Pebbles` in the paper.

The code is implemented strictly according to the algorithm provided in the paper. It is recommended to use [`pebbleGameClass.py`](./pebbleGameClass.py), the initial input is edges of a graph. If you need to input the adjacency table of a graph, you can refer to [`pebbleGame.py`](./pebbleGame.py).

TODO:
- [ ] Undo the `rearrange pebbles` process but not copy the whole graph

MIT License
