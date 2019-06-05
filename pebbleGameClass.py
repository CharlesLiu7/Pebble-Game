#! /usr/bin/python
# -*- coding: utf-8 -*-

import json
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format=''.join(['[%(asctime)s] ',
                    '%(message)s']),
    datefmt='%m-%d %T',
    stream=sys.stdout,
)


class pebbleGame:
    def __init__(self, edge_set, node_num):
        """
        init
        :param edge_set: input graph defined by edge set
        :param node_num: number of nodes, consideration for some nodes without one edge connected
        """
        self.__node_num = node_num
        self.__edges = edge_set
        # initialization
        self.pebble = [[None, None] for _ in range(
            self.__node_num)]  # default pebble allocation
        self.rigid_node = [False for _ in
                           range(self.__node_num)]  # var for determining if a site/node is in a rigid component
        self.redundant = []  # redundant bonds/edges
        self.__logger = logging.getLogger(__name__)

    def runGame(self):
        """pebble game allocation algorithm
        :param G: the graph G with adjacency table structure, each edge appears one time.
        :return:
            1. for each site/node, determine if it is in a rigid sub-graph
            2. The final allocation of each pebble
            3. redundant bonds/edges
        """
        for i, v in self.__edges:
            self.__logger.info('Phase testing edge ({0}, {1})'.format(i, v))
            pebble_cpy = json.loads(json.dumps(
                self.pebble))  # try G_4e allocation
            flag = True  # whether a bond/edge is independent
            self.__seen = [False for _ in range(self.__node_num)]
            for times in range(4):  # try G_4e
                self.__path = [-1 for _ in range(self.__node_num)]
                if (self.__findPebble(i, v, pebble_cpy)):
                    self.__rearrangePebble(i, v, pebble_cpy)
                elif (self.__findPebble(v, i, pebble_cpy)):
                    self.__rearrangePebble(v, i, pebble_cpy)
                else:
                    flag = False
                    if times < 3:
                        self.__logger.error(
                            'Error in pebbleGame: loc 0, it cannot happen.')
                    elif times == 3:
                        # if current edge is redundant, then sites/nodes in `seen` are in a rigid set already
                        self.redundant.append((i, v))
                        for x, y in enumerate(self.__seen):
                            if y:
                                self.rigid_node[x] = True
            if flag:
                # if G_4e is possible, and e=2v-3，then the current sub-graph is rigid
                if sum(self.__seen) != 2:  # not 2
                    num_edge = 0
                    for seen_index, seen_i in enumerate(self.__seen):
                        if seen_i:
                            for p_i in pebble_cpy[seen_index]:
                                if p_i is not None:
                                    num_edge += 1
                    if num_edge == 2 * sum(self.__seen):
                        for x, y in enumerate(self.__seen):
                            if y:
                                self.rigid_node[x] = True
                # now the current bond/edge is independent, allocate one pebble for it
                self.__seen = [False for _ in range(self.__node_num)]
                self.__path = [-1 for _ in range(self.__node_num)]
                if (self.__findPebble(i, v, self.pebble)):
                    self.__rearrangePebble(i, v, self.pebble)
                elif (self.__findPebble(v, i, self.pebble)):
                    self.__rearrangePebble(v, i, self.pebble)
                else:
                    self.__logger.error(
                        'Error in pebbleGame: loc 1, it cannot happen.')
        return self.rigid_node, self.pebble, self.redundant

    def __findPebble(self, v, _v, pebble):
        """find pebble function in paper
        :param v: current site/node
        :param _v: current bond/edge (v, _v)
        :param pebble: current pebble allocation
        :return: True representative found free pebble, False is not
        """
        self.__seen[v] = True
        self.__path[v] = -1  # -1 means the end of path
        if pebble[v][0] is None:
            return True
        if pebble[v][1] is None:
            return True
        x = pebble[v][0]
        if (not self.__seen[x] and x != _v):  # cannot allocate pebble from `_v`
            self.__path[v] = x
            found = self.__findPebble(x, _v, pebble)
            if found:
                return True
        y = pebble[v][1]
        if (not self.__seen[y] and y != _v):
            self.__path[v] = y
            found = self.__findPebble(y, _v, pebble)
            if found:
                return True
        return False

    def __rearrangePebble(self, v, _v, pebble):
        """rearrange pebble function in paper
        :param v: current site/node
        :param _v: current bond/edge (v, _v)
        :param pebble: current pebble allocation
        """
        # if current site/node has free pebble, just allocate it.
        if self.__path[v] == -1:
            if pebble[v][0] is None:
                tmp = (_v, pebble[v][1])
                pebble[v] = tmp
            elif pebble[v][1] is None:
                tmp = (pebble[v][0], _v)
                pebble[v] = tmp
            else:
                self.__logger.error(
                    'Error in rearrangePebble: loc 0, it cannot happen.')
            return
        v_copy = v  # the copy of the first site/node
        # 1. rearrange pebble allocation according to the path.
        while (self.__path[v] != -1):
            w = self.__path[v]
            if self.__path[w] == -1:
                if pebble[w][0] is None:
                    tmp = (v, pebble[w][1])
                    pebble[w] = tmp
                elif pebble[w][1] is None:
                    tmp = (pebble[w][0], v)
                    pebble[w] = tmp
                else:
                    self.__logger.error(
                        'Error in rearrangePebble: loc 1, it cannot happen.')
            else:
                _w = self.__path[w]
                if pebble[w][0] == _w:
                    tmp = (v, pebble[w][1])
                    pebble[w] = tmp
                elif pebble[w][1] == _w:
                    tmp = (pebble[w][0], v)
                    pebble[w] = tmp
                else:
                    self.__logger.error(
                        'Error in rearrangePebble: loc 2, it cannot happen.')
            v = w
        # 2. rearrange the first site/node's pebble.
        if pebble[v_copy][0] == self.__path[v_copy]:
            tmp = (_v, pebble[v_copy][1])
            pebble[v_copy] = tmp
        elif pebble[v_copy][1] == self.__path[v_copy]:
            tmp = (pebble[v_copy][0], _v)
            pebble[v_copy] = tmp
        else:
            self.__logger.error(
                'Error in rearrangePebble: loc 3, it cannot happen.')


if __name__ == '__main__':
    """
    0 -> 1, 2, 3
    1 -> 2, 5
    2 -> 5
    3 -> 4, 6
    4 -> 5, 6
    5 -> 6
    6 -> 7
    7 ->
    """
    edge_set = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 5), (2, 5), (3, 4),
                (3, 6), (4, 5), (4, 6), (5, 6), (6, 7)]
    g = pebbleGame(edge_set, 8)
    print(g.runGame())
