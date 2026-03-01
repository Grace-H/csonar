# main.py - Captain Sonar Radio Operator
# Track other team's moves to narrow location and recommend weapons usage

from copy import deepcopy

class Path:
    '''One possible path the other team may have taken. May have parent paths'''
    def __init__(self, i, j, mp):
        self.parents = [self]
        self.past_coords = []
        self.mines = []
        self.mp = mp
        self.valid = True
        self.goto(i, j)

    def set_parent(self, parent):
        self.parents = parent.parents
        self.parents.append(self)
        self.mines = deepcopy(parent.mines)
        for i, j in parent.past_coords:
            self.mp.move_path(i, j, self)
            self.past_coords.append((i, j))

    def goto(self, i, j):
        if not self.mp.test_path(i, j, self):
            self.valid = False
        elif self.valid:
            self.i = i
            self.j = j
            self.past_coords.append((i, j))
            self.mp.move_path(i, j, self)
        return self.valid

    def kill(self):
        for i, j in self.past_coords:
            self.mp.remove_path(i, j, self)

    def add_mine(self):
        self.mines.append((self.i, self.j))

    def plot_self(self, template):
        template[self.i][self.j] = 'x'

    def plot_mines(self, template):
        for mi, mj in self.mines:
            template[mi][mj] = 'm'

    def sector(self):
        return self.i // (self.mp.ylen // 3) * 3 + self.j // (self.mp.xlen // 3)
    

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
                path = Path(i, j, self.mp)
                if path.valid:
                    self.paths.append(path)
                else:
                    path.kill()

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
        for path in self.paths:
            (newi, newj) = transpose(path.i, path.j)
            path.goto(newi, newj)
            if not path.valid:
                path.kill()
                old_paths.append(path)

        for path in old_paths:
            self.paths.remove(path)

    def handle_silence(self):
        new_paths = []
        for path in self.paths:
            print(path.i, ",", path.j)
            for i in range(path.i - 4, path.i):
                new_path = Path(path.i, path.j, self.mp)
                new_path.set_parent(path)
                for newi in range(path.i - 1, i - 1, -1):
                    new_path.goto(newi, path.j)
                    print("went to: ", newi, path.j, new_path.valid)
                if new_path.valid:
                    new_paths.append(new_path)
                else:
                    new_path.kill()
            for i in range(path.i + 1, path.i + 5):
                new_path = Path(path.i, path.j, self.mp)
                new_path.set_parent(path)
                for newi in range(path.i + 1, i + 1, 1):
                    new_path.goto(newi, path.j)
                    print("went to: ", newi, path.j, new_path.valid)
                if new_path.valid:
                    new_paths.append(new_path)
                else:
                    new_path.kill()

            for j in range(path.j - 4, path.j):
                new_path = Path(path.i, path.j, self.mp)
                new_path.set_parent(path)
                for newj in range(path.j - 1, j - 1, -1):
                    new_path.goto(path.i, newj)
                    print("went to: ", path.i, newj, new_path.valid)
                if new_path.valid:
                    new_paths.append(new_path)
                else:
                    new_path.kill()
            for j in range(path.j + 1, path.j + 5):
                new_path = Path(path.i, path.j, self.mp)
                new_path.set_parent(path)
                for newj in range(path.j + 1, j + 1, 1):
                    new_path.goto(path.i, newj)
                    print("went to: ", path.i, newj, new_path.valid)
                if new_path.valid:
                    new_paths.append(new_path)
                else:
                    new_path.kill()

        for path in new_paths:
            self.paths.append(path)

    def handle_mine(self):
        for path in self.paths:
            path.add_mine()

    def handle_report(self):
        print("### Mine report")
        self.print_mines()

        print("\n### Sub report")
        print("Total possible sub locations: ", len(self.paths))
        if len(self.paths):
            row_cnts = [0 for i in range(self.mp.ylen)]
            col_cnts = [0 for i in range(self.mp.xlen)]
            sec_cnts = [0 for i in range(9)]
            for path in self.paths:
                row_cnts[path.i] += 1
                col_cnts[path.j] += 1
                sec_cnts[path.sector()] += 1

            forty = []
            seventy = []
            hundred = []
            row_dist = "\tDistribution: "
            for i, r in enumerate(row_cnts):
                row_dist += str(i + 1) + ": " + str(r) + ", "
                if r / len(self.paths) == 1:
                    hundred.append("Row " + str(i + 1))
                elif r / len(self.paths) > 0.7:
                    seventy.append("Row " + str(i + 1))
                elif r / len(self.paths) > 0.4:
                    forty.append("Row " + str(i + 1))

            col_dist = "\tDistribution: "
            for j, c in enumerate(col_cnts):
                col_dist += chr(ord('A') + j) + ": " + str(c) + ", "
                if c / len(self.paths) == 1:
                    hundred.append("Column " + chr(ord('A') + j))
                elif c / len(self.paths) > 0.7:
                    seventy.append("Column " + chr(ord('A') + j))
                elif c / len(self.paths) > 0.4:
                    forty.append("Column " + chr(ord('A') + j))

            sec_dist = "\tDistribution: "
            for i, s in enumerate(sec_cnts):
                sec_dist += str(i + 1) + ": " + str(s) + ", "
                if s / len(self.paths) == 1:
                    hundred.append("Sector " + str(i + 1))
                elif s / len(self.paths) > 0.7:
                    seventy.append("Sector " + str(i + 1))
                elif s / len(self.paths) > 0.4:
                    forty.append("Sector " + str(i + 1))
                
            print("Possible rows: ", sum(1 for r in row_cnts if r > 0))
            print(row_dist)
            print("Possible columns: ", sum(1 for c in col_cnts if c > 0))
            print(col_dist)
            print("Possible sectors: ", sum(1 for s in sec_cnts if s > 0))
            print(sec_dist)

            print("High prob locations:")
            if len(forty) or len(seventy) or len(hundred):
                if len(forty):
                    print("\t>40%")
                    for f in forty:
                        print("\t\t", f)
                if len(seventy):
                    print("\t>70%")
                    for s in seventy:
                        print("\t\t", s)
                if len(hundred):
                    print("\t100%")
                    for h in hundred:
                        print("\t\t", h)
            else:
                print("\tNone")

    def print_template(self, template):
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

    def print_paths(self):
        template = self.mp.gen_template()
        for path in self.paths:
            template[path.i][path.j] = 'x'
        self.print_template(template)

    def print_mines(self):
        template = self.mp.gen_template()
        for path in self.paths:
            path.plot_mines(template)
        self.print_template(template)

    def game_loop(self):
        while(True):
            print()
            self.print_paths()
            print()
            print("Commands: (g)o, (s)ilence, (t)orpedo, (m)ine, (r)eport, (q)uit")
            cmd = input("> ").upper()
            if len(cmd) < 1:
                continue
            if cmd[0] == 'G':
                self.handle_go()
            elif cmd[0] == 'M':
                self.handle_mine()
            elif cmd[0] == 'R':
                self.handle_report()
            elif cmd[0] == 'S':
                self.handle_silence()
            elif cmd[0] == 'Q':
                return


if __name__ == '__main__':
    ctrl = Control('map.txt')
    ctrl.game_loop()

