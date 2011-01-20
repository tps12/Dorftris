from heapq import *

class PathManager:
    """
    Class dealing with finding adjacent spaces and paths.
    """
    def __init__(self, space):
        """
        Construct a path manager for the provided 3D space.
        """
        self.space = space
        self.dim = self.space.get_dimensions()
        
    def adjacent_xy(self, loc):
        """
        Get adjacent hex locations in an XY plane.
        """
        (x,y) = loc
        dy = ((x & 1) << 1) - 1 # -1 or +1 for even and odd x, respectively
        return set([(x,y)
                    for (x,y) in
                    [(x,y-1),(x,y+1),(x-1,y),(x+1,y),(x-1,y+dy),(x+1,y+dy)]
                    if 0 <= x < self.dim[0] and 0 <= y < self.dim[1]])

    def adjacent(self, loc):
        """
        Get adajacent hex locations in 3D space.
        """
        a = [(x,y,loc[2]) for (x,y) in self.adjacent_xy((loc[0],loc[1]))]
        if loc[2] > 0:
            a += [(loc[0],loc[1],loc[2]-1)]
        if loc[2] < self.dim[2]-1:
            a += [(loc[0],loc[1],loc[2]+1)]
        return a

    def within_radius(self, loc, r):
        """
        Get hex locations within r steps of the location specified.
        """
        if r == 0:
            return set([loc])
        else:
            adj = self.within_radius(loc, r-1)
            for space in adj:
                adj = adj.union(set([(x,y,space[2])
                                     for (x,y) in
                                     self.adjacent_xy((space[0],space[1]))]))
            return adj

    def radius_include(self, loc, loc_p):
        """
        Get hex locations within minimum steps of the specified location to
        include the specified perimeter location.
        """
        r = 0
        while True:
            adj = self.within_radius(loc, r)
            if loc_p in adj:
                return adj
            r += 1

    def open_adjacent(self, loc):
        """
        Get spaces available to move to from a location.

        A space is open for movement if it's not filled with anything,
        is supported by a floor, and is either on the same Z level or
        is one Z level away without an obstacle in the way (you can't step
        up if there's a roof directly overhead, and you can't step down
        if there's a wall in front of you).
        
        """
        return set([(x,y,z)
                    for (x,y) in self.adjacent_xy((loc[0],loc[1]))
                    for z in range(max(1,loc[2]-1), min(self.dim[2],loc[2]+2))
                    if self.space[(x,y,z)].is_passable() # free
                    and not self.space[(x,y,z-1)].is_passable() and # has floor
                    (z == loc[2] or
                     (z > loc[2] and # step down
                      self.space[(loc[0],loc[1],z)].is_passable()) or # space above
                     (z < loc[2] # step up
                      and self.space[(x,y,z+1)].is_passable()))]) # space above

    def distance_xy(self, a, b):
        """
        Get the number of spaces to traverse between two XY locations.
        """
        d = 0
        while True:
            (dx,dy) = [b[i] - a[i] for i in range(2)]
            
            # base case, straight line along x or y
            if dx == 0 or dy == 0:
                return d + abs(dx + dy)

            # move diagonally: advance y if moving south and x is odd
            #                  or moving north and x is even
            a = (a[0] + dx/abs(dx),
                 a[1] + dy/abs(dy) if (dy>0)==a[0]&1 else a[1])
            d = d + 1

    def heuristic(self, a, b):
        return self.distance_xy(a, b)

    def find_path(self, a, b):
        """
        Use A* to get the list of spaces to traverse to reach b from a.

        XY distance (number of moves) is used as a heuristic: since moving
        between Z levels doesn't carry any additional cost, walls and cliffs
        are just like obstacles.
        
        """
        for p in (a,b):
            for i in range(3):
                if p[i] < 0 or p[i] >= self.dim[i]:
                    raise IndexError

        class Node(object):
            def __init__(self, node, g, h, parent):
                self.node = node
                self.g = g
                self.h = h
                self.f = self.g + self.h
                self.parent = parent

            def __cmp__(self, other):
                return (cmp(self.f, other.f) or
                        cmp(self.h, other.h) or
                        cmp(self.node, other.node))
        
        o = []
        heappush(o, Node(a, 0, self.heuristic(a,b), None))
        visited = {o[0].node:o[0]}
        loops = 0
        while len(o):
            cur = o[0]
            if cur.node == b:
                break

            heappop(o)

            for n in self.open_adjacent(cur.node):
                g = cur.g + 1 + (n[2] - cur.node[2])/10.0

                try:
                    e = visited[n]
                except KeyError:
                    e = Node(n, float('inf'), 0, None)
                    visited[n] = e

                if g < e.g:                    
                    n_o = next((node for node in o
                                if node.node == n), None)
                    if n_o is None:
                        heappush(o, e)

                    e.g = g
                    e.h = self.heuristic(n, b)
                    e.f = g + e.h
                    e.parent = cur
                    
            loops += 1
        else:
            return None

        if loops > self.dim[0] * self.dim[1]:
            import pdb
            pdb.set_trace()

        res = []
        p = o[0]
        while p:
            res.append(p.node)
            p = p.parent
        res.reverse()
        return res[1:]
