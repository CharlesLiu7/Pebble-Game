# -*- coding: UTF-8 -*-
__author__ = 'Charles'
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

logger = logging.getLogger(__name__)


def findPebble(v, _v, seen, path, pebble):
    """find pebble function in paper
    :param v: current site/node
    :param _v: current bond/edge (v, _v)
    :param seen: sites/nodes checked, default value is False
    :param path: the path to reallocate pebbles
    :param pebble: current pebble allocation
    :return: True representative found free pebble, False is not
    """
    seen[v] = True
    path[v] = -1  # -1 means the end of path
    if pebble[v][0] is None:
        return True
    if pebble[v][1] is None:
        return True
    x = pebble[v][0]
    if (not seen[x] and x != _v):  # cannot allocate pebble from `_v`
        path[v] = x
        found = findPebble(x, _v, seen, path, pebble)
        if found:
            return True
    y = pebble[v][1]
    if (not seen[y] and y != _v):
        path[v] = y
        found = findPebble(y, _v, seen, path, pebble)
        if found:
            return True
    return False


def rearrangePebble(v, _v, path, pebble):
    """rearrange pebble function in paper
    :param v: current site/node
    :param _v: current bond/edge (v, _v)
    :param path: the path to reallocate pebbles
    :param pebble: current pebble allocation
    """
    # if current site/node has free pebble, just allocate it.
    if path[v] == -1:
        if pebble[v][0] is None:
            tmp = (_v, pebble[v][1])
            pebble[v] = tmp
        elif pebble[v][1] is None:
            tmp = (pebble[v][0], _v)
            pebble[v] = tmp
        else:
            logger.error('Error in rearrangePebble: loc 0, it cannot happen.')
        return
    v_copy = v  # the copy of the first site/node
    # 1. rearrange pebble allocation according to the path.
    while (path[v] != -1):
        w = path[v]
        if path[w] == -1:
            if pebble[w][0] is None:
                tmp = (v, pebble[w][1])
                pebble[w] = tmp
            elif pebble[w][1] is None:
                tmp = (pebble[w][0], v)
                pebble[w] = tmp
            else:
                logger.error(
                    'Error in rearrangePebble: loc 1, it cannot happen.')
        else:
            _w = path[w]
            if pebble[w][0] == _w:
                tmp = (v, pebble[w][1])
                pebble[w] = tmp
            elif pebble[w][1] == _w:
                tmp = (pebble[w][0], v)
                pebble[w] = tmp
            else:
                logger.error(
                    'Error in rearrangePebble: loc 2, it cannot happen.')
        v = w
    # 2. rearrange the first site/node's pebble.
    if pebble[v_copy][0] == path[v_copy]:
        tmp = (_v, pebble[v_copy][1])
        pebble[v_copy] = tmp
    elif pebble[v_copy][1] == path[v_copy]:
        tmp = (pebble[v_copy][0], _v)
        pebble[v_copy] = tmp
    else:
        logger.error('Error in rearrangePebble: loc 3, it cannot happen.')


# 算法测试阶段

def pebbleGame(G):
    """pebble game allocation algorithm
    :param G: the graph G with adjacency table structure, each edge appears one time.
    :return:
        1. for each site/node, determine if it is in a rigid sub-graph
        2. The final allocation of each pebble
        3. redundant bonds/edges
    """
    # initialization
    pebble = [(None, None) for _ in G]  # default pebble allocation
    # var for determining if a site/node is in a rigid component
    rigid_node = [False for _ in G]
    redundant = []  # redundant bonds/edges

    for i, j in enumerate(G):
        for v in j:
            logger.info('Phase testing edge ({0}, {1})'.format(i, v))
            pebble_cpy = json.loads(json.dumps(pebble))  # try G_4e allocation
            flag = True  # whether a bond/edge is independent
            seen = [False for _ in G]
            for times in range(4):
                path = [-1 for _ in G]
                if (findPebble(i, v, seen, path, pebble_cpy)):
                    rearrangePebble(i, v, path, pebble_cpy)
                    path = [-1 for _ in G]
                elif (findPebble(v, i, seen, path, pebble_cpy)):
                    rearrangePebble(v, i, path, pebble_cpy)
                    path = [-1 for _ in G]
                else:
                    flag = False
                    if times < 3:
                        logger.error(
                            'Error in pebbleGame: loc 0, it cannot happen.')
                    elif times == 3:
                        # if current edge is redundant, then sites/nodes in `seen` are in a rigid set already
                        redundant.append((i, v))
                        for x, y in enumerate(seen):
                            if y:
                                rigid_node[x] = True
            if flag:
                # if G_4e is possible, and e=2v-3，then the current sub-graph is rigid
                if sum(seen) != 2:  # not 2
                    num_edge = 0
                    for seen_index, seen_i in enumerate(seen):
                        if seen_i:
                            for p_i in pebble_cpy[seen_index]:
                                if p_i is not None:
                                    num_edge += 1
                    if num_edge == 2 * sum(seen):
                        for x, y in enumerate(seen):
                            if y:
                                rigid_node[x] = True
                # now the current bond/edge is independent, allocate one pebble for it
                seen = [False for _ in G]
                path = [-1 for _ in G]
                if (findPebble(i, v, seen, path, pebble)):
                    rearrangePebble(i, v, path, pebble)
                elif (findPebble(v, i, seen, path, pebble)):
                    rearrangePebble(v, i, path, pebble)
                else:
                    logger.error(
                        'Error in pebbleGame: loc 1, it cannot happen.')
    return rigid_node, pebble, redundant


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
    G = [{1, 2, 3}, {2, 5}, {5}, {4, 6}, {5, 6}, {6}, {7}, {}]
    print(pebbleGame(G))
