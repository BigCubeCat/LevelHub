"""
Generate clear maze
"""
from random import randrange, shuffle
import flask
from flask import render_template, send_file
from forms import MazeGeneratorForm
import os

blueprint = flask.Blueprint('maze_api', __name__,
                            template_folder='templates')


class MapGenerator:
    def __init__(self, width: int, height: int):
        self.width, self.height = width, height
        self.map = []
        self.generate()

    def replaces(self, string, list_replaces):
        for el in list_replaces:
            string = string.replace(el[0], el[1])
        return string

    def generate(self):
        self.visited = [[0] * self.width + [1] for _ in range(self.height)] + [
            [1] * (self.width + 1)]
        self.vertical = [["|  "] * self.width + ['|'] for _ in range(self.height)] + [[]]
        self.horizontal = [["+--"] * self.width + ['+'] for _ in range(self.height + 1)]
        self.walk(randrange(self.width), randrange(self.height))
        self.horizontal = [''.join([i.replace('+  ',
                                              "00").replace("  ",
                                                            "0").replace("+",
                                                                         "1").replace("--", "1")
                                    for i in j]) for j in self.horizontal]
        self.horizontal = [[int(i) for i in list(j)] for j in self.horizontal]
        self.vertical = [
            [int(j) for j in list(
                self.replaces(''.join(i), [('|  ', "10"), ('  |', "01"), (' ', "0"), ('|', "1")]))]
            for i in self.vertical
        ]
        for row1, row2 in zip(self.horizontal, self.vertical):
            self.map.append(row1)
            self.map.append(row2)

    def walk(self, x, y):
        self.visited[y][x] = 1
        sosedi = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
        shuffle(sosedi)
        for (xx, yy) in sosedi:
            if self.visited[yy][xx]:
                continue
            if xx == x:
                self.horizontal[max(y, yy)][x] = "+  "
            if yy == y:
                self.vertical[y][max(x, xx)] = "   "
            self.walk(xx, yy)

    def create_file(self, filename):
        data = []
        for i in range(self.width):
            for j in range(self.height):
                data.append(f"0: {j};0;{i}")
                if self.map[j][i] == 1:
                    continue
                elif self.map[j][i] == 100:
                    data.append(f"1: {i};1;{j}")
                else:
                    data.append(f"{int(self.map[j][i])}: {i};1;{j}")
        data = '{\n' + '\n'.join(data) + '\n}'
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(data)


@blueprint.route('/maze_generator', methods=["POST", "GET"])
def generator_page():
    form = MazeGeneratorForm()
    if form.validate_on_submit():
        maze = MapGenerator(width=form.width.data, height=form.height.data)
        filename = os.path.abspath('tmp/generated_maze.level')
        maze.create_file(filename)
        return send_file(filename, as_attachment=True)
    return render_template('maze_generator.html', form=form)
