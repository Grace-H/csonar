# main.py - Captain Sonar Radio Operator
# Track other team's moves to narrow location and recommend weapons usage

class Path:
    '''One possible path the other team may have taken. May have parent paths'''
    def __init__(self, i, j):
        self.past_coords = [(i, j)]
        self.parents = [self]
        self.mines = []
        self.i = i
        self.j = j

    def set_parent(self, parent, mp):
        self.parents = parent.parents
        self.parents.append(self)
        for i, j in parent.past_coords:
            mp.move_path(i, j, self)
            self.past_coords.append((i, j))

    def goto(self, i, j):
        self.i = i
        self.j = j
        self.past_coords.append((i, j))

    def kill(self, mp):
        for i, j in self.past_coords:
            mp.remove_path(i, j, self)



class Cell:
    '''Map cell'''
    def __init__(self, island=False):
        self.island = island
        self.breadcrumbs = []  # paths that may have crosses this coordinate

    def add_breadcrumb(self, path):
        self.breadcrumbs.append(path)

    def del_breadcrumb(self, path):
        self.breadcrumbs.remove(path)

    def test_path(self, path):
        if not self.island and path not in self.breadcrumbs:
            return True
        return False

    def __str__(self):
        if self.island:
            return 'O'
        return '.'


class Sonar:
    '''Grid used to track the other team's location. Paths leave breadcrumbs of
    where they may have been'''
    def __init__(self, map_file):
        self.mp = []
        self.load_map(map_file)
        self.xlen = len(self.mp)
        self.ylen = len(self.mp[0])

    def load_map(self, map_file):
        mf = open(map_file, "r")
        lines = mf.readlines()
        mf.close()
        for l in lines:
            row = []
            for c in l:
                if c == '.' or c == 'O':
                    row.append(Cell(c == 'O'))
            self.mp.append(row)

    def test_path(self, i, j, path):
        '''Whether a path could enter this cell. Called before moving'''
        if i < 0 or j < 0 or i >= self.xlen or j >= self.ylen:
            return False
        return self.mp[i][j].test_path(path)

    def move_path(self, i, j, path):
        if i < 0 or j < 0 or i >= self.xlen or j >= self.ylen:
            return
        self.mp[i][j].add_breadcrumb(path)

    def remove_path(self, i, j, path):
        if i < 0 or j < 0 or i >= self.xlen or j >= self.ylen:
            return
        self.mp[i][j].del_breadcrumb(path)

    def gen_template(self):
        return [[str(c) for c in row] for row in self.mp]

class Control:
    def __init__(self, map_file):
        self.paths = []
        self.mp = Sonar(map_file)
        for i in range(self.mp.ylen):
            for j in range(self.mp.xlen):
                path = Path(i, j)
                if self.mp.test_path(i, j, path):
                    self.paths.append(path)
                    self.mp.move_path(i, j, path)

    def handle_go(self):
        trans_ij = { "N": lambda i, j: (i - 1, j),
                    "E": lambda i, j: (i, j + 1),
                    "S": lambda i, j: (i + 1, j),
                    "W": lambda i, j: (i, j - 1) }

        card = input("Direction? ").upper()
        if card not in trans_ij:
            return

        transpose = trans_ij[card]
        old_paths = []
        print(str(len(self.paths)))
        for path in self.paths:
            (newi, newj) = transpose(path.i, path.j)
            if self.mp.test_path(newi, newj, path):
                self.mp.move_path(newi, newj, path)
                path.goto(newi, newj)
            else:
                path.kill(self.mp)
                old_paths.append(path)

        for path in old_paths:
            self.paths.remove(path)

    def handle_silence(self):
        new_paths = []
        for path in self.paths:
            for i in range(path.i - 4, path.i + 5):
                if self.mp.test_path(i, path.j, path):
                    new_path = Path(i, path.j)
                    new_path.set_parent(path, self.mp)
                    self.mp.move_path(i, path.j, new_path)
                    new_paths.append(new_path)
            for j in range(path.j - 4, path.j + 5):
                if self.mp.test_path(path.i, j, path):
                    new_path = Path(path.i, j)
                    new_path.set_parent(path, self.mp)
                    self.mp.move_path(path.i, j, new_path)
                    new_paths.append(new_path)
        for path in new_paths:
            self.paths.append(path)

    def print_map(self):
        template = self.mp.gen_template()
        for path in self.paths:
            template[path.i][path.j] = 'x'
        print("     A   B   C   D   E   F   G   H   I   J   K   L   M   N   O")
        print("  -|-------------------|-------------------|------------------")
        for i, row in enumerate(template):
            to_print = ""
            if len(str(i + 1)) < 2:
                to_print += ' '
            to_print += str(i + 1) + " | "
            to_print += "   ".join(row)
            print(to_print)
            if (i + 1) % 5 == 0:
                print("  -| -- -- -- -- -- -- | -- -- -- -- -- -- | -- -- -- -- -- --")
            else:
                print("   |                   |                   |                 ")

    def game_loop(self):
        while(True):
            print()
            self.print_map()
            print()
            print("Commands: (g)o, (s)ilence, (t)orpedo, (m)ine, (q)uit")
            cmd = input("> ").upper()
            if len(cmd) < 1:
                continue
            if cmd[0] == 'G':
                self.handle_go()
            if cmd[0] == 'S':
                self.handle_silence()
            elif cmd[0] == 'Q':
                return


if __name__ == '__main__':
    ctrl = Control('map.txt')
    ctrl.game_loop()




