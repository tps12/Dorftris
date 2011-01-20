import unittest

from pathing import PathManager

class SingleSpace:
    def __init__(self, value):
        self.value = value

    def is_passable(self):
        return not self.value

class Space:
    def __init__(self, dim):
        self.a = [[[0
                    for z in range(dim[2])]
                   for y in range(dim[1])]
                  for x in range(dim[0])]

    def __getitem__(self, loc):
        return SingleSpace(self.a[loc[0]][loc[1]][loc[2]])

    def __setitem__(self, loc, value):
        self.a[loc[0]][loc[1]][loc[2]] = value

    def get_dimensions(self):
        return (len(self.a),len(self.a[0]),len(self.a[0][0]))

class PathManagerTestCase(unittest.TestCase):
    def test_new(self):
        PathManager(Space((4,4,3)))

    def test_adjacent_even_x(self):
        p = PathManager(Space((4,4,3)))
        t = (2,1)
        a = set([      (2,0),
                (1,0),      (3,0),
                (1,1),      (3,1),
                       (2,2)])
        self.assertEqual(p.adjacent_xy(t), a)

    def test_adjacent_odd_x(self):
        p = PathManager(Space((4,4,3)))
        t = (1,1)
        a = set([      (1,0),
                (0,1),      (2,1),
                (0,2),      (2,2),
                       (1,2)])
        self.assertEqual(p.adjacent_xy(t), a)

    def test_adjacent_edge(self):
        p = PathManager(Space((4,4,3)))
        t = (0,1)
        a = set([(0,0),
                      (1,0),
                      (1,1),
                (0,2)])
        self.assertEqual(p.adjacent_xy(t), a)

    def test_adjacent_corner(self):
        p = PathManager(Space((4,4,3)))
        t = (3,3)
        a = set([      (3,2),
                (2,3)])
        self.assertEqual(p.adjacent_xy(t), a)

    def test_open_adjacent(self):
        s = Space((4,4,3))
        for x in range(4):
            for y in range(4):
                s[(x,y,0)] = 1
        s[(1,0,1)] = s[(1,0,2)] = 1
        s[(2,2,1)] = s[(2,2,2)] = 1
        p = PathManager(s)
        t = (2,1,1)
        a = set([       (2,0,1),
                                (3,0,1),
                (1,1,1),        (3,1,1)])
        self.assertEqual(p.open_adjacent(t), a)

    def test_open_adjacent_step_up(self):
        s = Space((4,4,3))
        for x in range(4):
            for y in range(4):
                s[(x,y,0)] = 1
        s[(1,0,1)] = 1
        s[(2,2,1)] = 1
        p = PathManager(s)
        t = (2,1,1)
        a = set([        (2,0,1),
                 (1,0,2),        (3,0,1),
                 (1,1,1),        (3,1,1),
                         (2,2,2)])
        self.assertEqual(p.open_adjacent(t), a)

    def test_open_adjacent_step_down(self):
        s = Space((4,4,3))
        for x in range(4):
            for y in range(4):
                s[(x,y,0)] = 1
                s[(x,y,1)] = 1
        s[(1,0,1)] = 0
        s[(2,2,1)] = 0
        p = PathManager(s)
        t = (2,1,2)
        a = set([        (2,0,2),
                 (1,0,1),        (3,0,2),
                 (1,1,2),        (3,1,2),
                         (2,2,1)])
        self.assertEqual(p.open_adjacent(t), a)

    def test_open_adjacent_step_up_blocked(self):
        s = Space((4,4,3))
        for x in range(4):
            for y in range(4):
                s[(x,y,0)] = 1
        s[(1,0,1)] = 1
        s[(2,2,1)] = 1
        s[(2,1,2)] = 1
        p = PathManager(s)
        t = (2,1,1)
        a = set([        (2,0,1),
                                 (3,0,1),
                 (1,1,1),        (3,1,1)])
        self.assertEqual(p.open_adjacent(t), a)

    def test_open_adjacent_step_down_blocked(self):
        s = Space((4,4,3))
        for x in range(4):
            for y in range(4):
                s[(x,y,0)] = 1
                s[(x,y,1)] = 1
        s[(1,0,1)] = 0
        s[(1,0,2)] = 1
        s[(2,2,1)] = 0
        p = PathManager(s)
        t = (2,1,2)
        a = set([        (2,0,2),
                                 (3,0,2),
                 (1,1,2),        (3,1,2),
                         (2,2,1)])
        self.assertEqual(p.open_adjacent(t), a)

    def test_distance_x(self):
        p = PathManager(Space((4,4,3)))
        self.assertEqual(p.distance_xy((0,0),(3,0)), 3)

    def test_distance_x_2(self):
        p = PathManager(Space((4,4,3)))
        self.assertEqual(p.distance_xy((1,1),(2,2)), 1)

    def test_distance_x_3(self):
        p = PathManager(Space((4,4,3)))
        self.assertEqual(p.distance_xy((2,1),(3,1)), 1)

    def test_distance_y(self):
        p = PathManager(Space((4,4,3)))
        self.assertEqual(p.distance_xy((1,0),(1,2)), 2)

    def test_distance_x_y(self):
        p = PathManager(Space((4,4,3)))
        self.assertEqual(p.distance_xy((0,0),(3,2)), 4)

    def test_distance_x_y_2(self):
        p = PathManager(Space((4,4,3)))
        self.assertEqual(p.distance_xy((0,0),(2,3)), 4)

    def test_distance_x_y_3(self):
        p = PathManager(Space((8,8,3)))
        self.assertEqual(p.distance_xy((5,5),(1,2)), 5)

    def test_distance_x_y_4(self):
        p = PathManager(Space((8,8,3)))
        self.assertEqual(p.distance_xy((1,0),(5,5)), 7)

    def test_find_path(self):
        s = Space((6,6,3))
        p = PathManager(s)
        for x in range(6):
            for y in range(6):
                s[(x,y,0)] = 1
        self.assertEqual(len(p.find_path((1,2,1),(4,5,1))), 4)

    def test_find_path_3d(self):
        s = Space((3,2,3))
        p = PathManager(s)
        for x in range(3):
            for y in range(2):
                s[(x,y,0)] = 1
        s[(1,0,1)] = 1
        e = [(1,0,2),(0,0,1)]
        self.assertEqual(p.find_path((2,0,1),(0,0,1)), e)

    def test_find_path_3d_wall(self):
        s = Space((3,3,4))
        p = PathManager(s)
        for x in range(3):
            for y in range(3):
                s[(x,y,0)] = 1
        s[(1,0,1)] = 1
        s[(1,0,2)] = 1
        s[(1,1,1)] = 1
        e = [(2,1,1),(1,1,2),(0,1,1),(0,0,1)]
        self.assertEqual(p.find_path((2,0,1),(0,0,1)), e)

    def test_no_path(self):
        s = Space((3,2,3))
        p = PathManager(s)
        for x in range(3):
            for y in range(2):
                s[(x,y,0)] = 1
        s[(1,0,1)] = 1
        s[(1,0,2)] = 1
        s[(1,1,1)] = 1
        s[(1,1,2)] = 1
        self.assertEqual(p.find_path((2,0,1),(0,0,1)), None)

    def test_find_path_prefer_flat(self):
        s = Space((4,2,4))
        p = PathManager(s)
        for x in range(4):
            for y in range(2):
                s[(x,y,0)] = 1
        # two paths, via 2,0,1 or 2,1,1: find the preferred path for flat
        f = p.find_path((1,0,1),(3,0,1))
        not_f0 = (2,0,1) if f[0] == (2,1,1) else (2,1,1)
        # turn into a hill
        s[f[0]] = 1
        # should path around it
        h = p.find_path((1,0,1),(3,0,1))
        self.assertEqual(h[0], not_f0)
        # block new path entirely
        s[h[0]] = 1
        s[(h[0][0],h[0][1],h[0][2]+1)] = 1
        # should be back to first, one step up
        f[0] = (f[0][0], f[0][1], f[0][2]+1)
        self.assertEqual(p.find_path((1,0,1),(3,0,1)), f)

    def test_find_path_out_of_limits(self):
        s = Space((48,32,8))
        p = PathManager(s)
        for x in range(48):
            for y in range(32):
                s[(x,y,6)] = 1
        s[(31,27,7)] = 1
        try:
            p.find_path((31,28,7),(31,27,8))
            self.fail('Expected IndexError')
        except IndexError:
            pass

    def test_find_path_inside_block(self):
        s = Space((3,2,3))
        p = PathManager(s)
        for x in range(3):
            for y in range(2):
                s[(x,y,0)] = 1
        s[(1,0,2)] = 1
        self.assertEqual(p.find_path((2,0,1),(1,0,2)), None)

    def test_get_radius_0(self):
        s = Space((6,6,3))
        p = PathManager(s)
        for x in range(6):
            for y in range(6):
                s[(x,y,0)] = 1
        self.assertEqual(p.within_radius((2,2,0),0), set([(2,2,0)]))

    def test_get_radius_1(self):
        s = Space((6,6,3))
        p = PathManager(s)
        for x in range(6):
            for y in range(6):
                s[(x,y,0)] = 1
        self.assertEqual(p.within_radius((2,2,0),1),
                         set([(2,1,0),(3,1,0),(3,2,0),(2,3,0),(1,2,0),
                              (1,1,0),(2,2,0)]))
        
    def test_get_radius_2(self):
        s = Space((6,6,3))
        p = PathManager(s)
        for x in range(6):
            for y in range(6):
                s[(x,y,0)] = 1
        self.assertEqual(p.within_radius((2,2,0),2),
                         set([(2,1,0),(3,1,0),(3,2,0),(2,3,0),(1,2,0),
                              (1,1,0),(2,2,0),(2,0,0),(3,0,0),(4,1,0),
                              (4,2,0),(4,3,0),(3,3,0),(2,4,0),(1,3,0),
                              (0,3,0),(0,2,0),(0,1,0),(1,0,0)]))

    def test_get_radius_include_0(self):
        s = Space((6,6,3))
        p = PathManager(s)
        for x in range(6):
            for y in range(6):
                s[(x,y,0)] = 1
        self.assertEqual(p.radius_include((2,2,0),(2,2,0)), set([(2,2,0)]))

    def test_get_radius_include_1(self):
        s = Space((6,6,3))
        p = PathManager(s)
        for x in range(6):
            for y in range(6):
                s[(x,y,0)] = 1
        self.assertEqual(p.radius_include((2,2,0),(3,2,0)),
                         set([(2,1,0),(3,1,0),(3,2,0),(2,3,0),(1,2,0),
                              (1,1,0),(2,2,0)]))
        
    def test_get_radius_include_2(self):
        s = Space((6,6,3))
        p = PathManager(s)
        for x in range(6):
            for y in range(6):
                s[(x,y,0)] = 1
        self.assertEqual(p.radius_include((2,2,0),(1,0,0)),
                         set([(2,1,0),(3,1,0),(3,2,0),(2,3,0),(1,2,0),
                              (1,1,0),(2,2,0),(2,0,0),(3,0,0),(4,1,0),
                              (4,2,0),(4,3,0),(3,3,0),(2,4,0),(1,3,0),
                              (0,3,0),(0,2,0),(0,1,0),(1,0,0)]))

if __name__ == '__main__':
    unittest.main()
