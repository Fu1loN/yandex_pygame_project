import pygame
import os
import sys
from PIL import Image


def get_pacman_cord(level):
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == '*':
                return [j, i]


def get_ghost_coord(level, turn):
    global ghost_type
    which_position = 0
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == '@':
                which_position += 1
                if which_position == turn:
                    return [j, i]


class Board:
    def __init__(self, level):
        self.level = level
        self.cell_size = 30
        self.width = len(self.level[0])
        self.height = len(self.level)
        self.left = 25
        self.top = 25
        self.score = 0

    def render(self, screen):
        global decorations, points, level_map, running
        decorations = pygame.sprite.Group()
        points = pygame.sprite.Group()
        for i in range(len(self.level)):
            for j in range(len(self.level[i])):
                if self.level[i][j] == '#':
                    sprite = pygame.sprite.Sprite()
                    sprite.image = self.load_image("wall.jpg")
                    sprite.rect = sprite.image.get_rect()
                    sprite.rect.x = 25 + j * 30
                    sprite.rect.y = 25 + i * 30
                    decorations.add(sprite)
                    level_map[i][j] = -1
                elif self.level[i][j] == '-':
                    sprite = pygame.sprite.Sprite()
                    sprite.image = self.load_image("door.jpg")
                    sprite.rect = sprite.image.get_rect()
                    sprite.rect.x = 25 + j * 30
                    sprite.rect.y = 25 + i * 30
                    decorations.add(sprite)
                elif self.level[i][j] == '.':
                    sprite = pygame.sprite.Sprite()
                    sprite.image = self.load_image("small_point.jpg")
                    sprite.rect = sprite.image.get_rect()
                    sprite.rect.x = 32 + j * 30
                    sprite.rect.y = 32 + i * 30
                    sprite.cords = (j, i)
                    points.add(sprite)
                elif self.level[i][j] == ',':
                    sprite = pygame.sprite.Sprite()
                    sprite.image = self.load_image("big_point.jpg")
                    sprite.rect = sprite.image.get_rect()
                    sprite.rect.x = 27 + j * 30
                    sprite.rect.y = 27 + i * 30
                    sprite.cords = (j, i)
                    points.add(sprite)
        if len(points) == 0:
            running = False
        decorations.draw(screen_play)
        points.draw(screen_play)

    def find_cell(self, pos):
        x, y = pos
        x -= self.left
        y -= self.top
        rlx, rly = x // self.cell_size, y // self.cell_size
        if rlx > self.width or self.height < rly or rlx < 0 or rly < 0:
            return None
        else:
            return rlx, rly

    def load_image(self, name, colorkey=None):
        fullname = os.path.join('images', name)
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        if colorkey is not None:
            image = image.convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        return image


class PacMan(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites)
        self.imagl = board.load_image('pacmanleft.png')
        self.imagr = board.load_image('pacmanright.png')
        self.imagt = board.load_image('pacmantop.png')
        self.imagb = board.load_image('pacmanbot.png', colorkey=-1)
        self.image = self.imagl
        x, y = pos
        x += 1
        y += 1
        self.rect = pygame.Rect(x, y, 28, 28)
        self.x_move = 0
        self.y_move = 0
        self.ate_big_coin = False
        self.ate_clock = 0

    def update(self, *args):
        global running, died
        self.rect = self.rect.move(self.x_move, self.y_move)
        if pygame.sprite.spritecollideany(self, decorations):
            self.rect = self.rect.move(-self.x_move, -self.y_move)
        if self.ate_big_coin:
            self.ate_clock += 0.2
            if self.ate_clock >= 11:
                self.ate_big_coin = False
                self.ate_clock = 0
                shadow.unscare()
                bashful.unscare()
                pockey.unscare()
                speedy.unscare()
        c = pygame.sprite.spritecollide(self, points, True)
        for i in c:
            x, y = i.cords
            if board.level[y][x] == ',':
                board.score += 50
                self.ate_big_coin = True
                self.ate_clock = 0
                bashful.scaring()
                speedy.scaring()
                shadow.scaring()
                pockey.scaring()
            else:
                board.score += 10
                soundpoint.stop()
                soundpoint.play()
            board.level[y][x] = ' '
        if pygame.sprite.spritecollideany(self,
                                          ghosts):
            if not self.ate_big_coin:
                died = True
                running = False
            else:
                c = pygame.sprite.spritecollide(self, ghosts, False)
                for ghost in c:
                    if ghost.eatable:
                        board.score += 200
                        ghost.ate()

    def change_way(self, ev):
        x, y = self.x_move, self.y_move
        if ev.key == pygame.K_LEFT:
            imag = self.imagl
            self.x_move, self.y_move = -10, 0
        if ev.key == pygame.K_UP:
            imag = self.imagt
            self.x_move, self.y_move = 0, -10
        if ev.key == pygame.K_RIGHT:
            imag = self.imagr
            self.x_move, self.y_move = 10, 0
        if ev.key == pygame.K_DOWN:
            imag = self.imagb
            self.x_move, self.y_move = 0, 10
        self.rect = self.rect.move(self.x_move, self.y_move)
        if pygame.sprite.spritecollideany(self, decorations):
            self.rect = self.rect.move(-self.x_move, -self.y_move)
            self.x_move, self.y_move = x, y
        else:
            self.image = imag
            self.rect = self.rect.move(-self.x_move, -self.y_move)


class Ghost(pygame.sprite.Sprite):
    def __init__(self, x, y, level_map):
        super().__init__(all_sprites)
        ghosts.add(self)
        self.eyesim = board.load_image('eyes.jpg')
        self.fearim = board.load_image('fear.png')
        self.x, self.y = x, y
        self.way = []
        self.level_map = level_map
        self.rect = pygame.Rect((self.x + 1) * 30, (self.y + 1) * 30, 30, 30)

        self.speed = 5
        self.lspeed = 5
        self.ticks = 0
        self.updates = 0
        self.eatable = False
        self.fear = False

    def update_target(self):
        if pacman.ate_big_coin:
            target_x, target_y = 12, 11
        else:
            target_x, target_y = self.get_target()
        map_way = [[one for one in line] for line in self.level_map]
        map_way = self.obhod(map_way, self.x, self.y, 1)
        self.make_way(map_way, target_x, target_y)
        x, y = self.way[-2][0], self.way[-2][1]
        self.target = (x, y)

    def update(self, *args):
        global running
        try:
            self.ticks %= 30
            if self.ticks < self.speed:
                self.update_target()
            self.ticks += self.speed
            x, y = self.target
            if x == self.x and self.y > y:
                self.rect = self.rect.move(0, -self.speed)
                self.x, self.y = board.find_cell(
                    (self.rect.x + 15, self.rect.y + 29))
            elif x == self.x and self.y < y:
                self.rect = self.rect.move(0, self.speed)
                self.x, self.y = board.find_cell(
                    (self.rect.x + 15, self.rect.y + 1))
            elif x < self.x and self.y == y:
                self.rect = self.rect.move(-self.speed, 0)
                self.x, self.y = board.find_cell(
                    (self.rect.x + 29, self.rect.y + 15))
            elif self.get_target()[0] == self.x and self.get_target()[
                1] == self.y and pacman.ate_big_coin:
                print('w')
                print(self.speed)
                x_move = 0
                y_move = 0

                self.rect = self.rect.move(x_move, y_move)
                self.x, self.y = 12, 11
            else:
                self.rect = self.rect.move(self.speed, 0)
                self.x, self.y = board.find_cell(
                    (self.rect.x + 1, self.rect.y + 15))
        except IndexError:
            pass

    def ate(self):
        self.eatable = False
        self.speed, self.lspeed = 10, self.speed
        self.image = self.eyesim

    def scaring(self):
        # поменять спрайт
        self.image = self.fearim
        self.fear = True
        self.eatable = True

    def unscare(self):
        self.speed = self.lspeed
        self.fear = False
        self.eatable = False
        self.image = self.std

    def obhod(self, lab, x, y, cur):
        lab[y][x] = cur
        for xp, yp in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            xr = x + xp
            yr = y + yp
            try:
                if 0 <= xr and 0 <= yr:
                    if lab[yr][xr] == 0 or (
                            lab[yr][xr] != -1 and lab[yr][xr] > cur):
                        self.obhod(lab, xr, yr, cur + 1)
                else:
                    continue
            except IndexError:
                continue
        return lab

    def make_way(self, lab, x, y):
        t = lab[y][x]
        self.way.append((x, y))
        if t == 1:
            return 1
        for xp, yp in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            xr = x + xp
            yr = y + yp
            try:
                if 0 <= xr and 0 <= yr:
                    if lab[yr][xr] == t - 1:
                        self.make_way(lab, xr, yr)
                        continue
                else:
                    continue
            except IndexError:
                continue

    def get_target(self):
        return board.find_cell((pacman.rect.x + 15, pacman.rect.y + 15))


class Shadow(Ghost):
    def get_target(self):
        return board.find_cell((pacman.rect.x + 15, pacman.rect.y + 15))

    def __init__(self, x, y, level_map):
        super().__init__(x, y, level_map)
        self.std = board.load_image("shadow.jpg")
        self.image = self.std



class Speedy(Ghost):
    def __init__(self, x, y, level_map):
        super().__init__(x, y, level_map)
        self.std = board.load_image('speedy.png')
        self.image = self.std

    def get_target(self):
        xm, ym = pacman.x_move, pacman.y_move
        if ym == 0:
            for i in range(4):
                x = xm // 10 * 30 * (4 - i) + pacman.rect.x + 15
                y = pacman.rect.y + 15
                z = board.find_cell((x, y))
                if z is None:
                    continue
                else:
                    x, y = z
                    if board.level[y][x] == '#':
                        continue
                    return z
                    break
        else:
            for i in range(4):
                x = pacman.rect.x + 15
                y = ym // 10 * 30 * (4 - i) + pacman.rect.y + 15
                z = board.find_cell((x, y))
                if z is None:
                    continue
                else:
                    x, y = z
                    if board.level[y][x] == '#':
                        continue
                    return z
                    break
        return super().get_target()


class Bashful(Ghost):
    def __init__(self, x, y, level_map):
        super().__init__(x, y, level_map)
        self.std = board.load_image('bashful.png')
        self.image = self.std

    def get_target(self):
        xm, ym = pacman.x_move, pacman.y_move
        if ym == 0:
            for i in range(2):
                x = (xm // 10 * 30 * (2 - i) + pacman.rect.x + 15) * 2
                y = (pacman.rect.y + 15) * 2
                z = board.find_cell((x, y))
                if z is None:
                    continue
                else:
                    x, y = z
                    if board.level[y][x] == '#':
                        continue
                    return z
                    break
        else:
            for i in range(2):
                x = (pacman.rect.x + 15) * 2
                y = (ym // 10 * 30 * (2 - i) + pacman.rect.y + 15) * 2
                z = board.find_cell((x, y))
                if z is None:
                    continue
                else:
                    x, y = z
                    if board.level[y][x] == '#':
                        continue
                    return z
                    break
        return super().get_target()


class Pockey(Ghost):
    def __init__(self, x, y, level_map):
        super().__init__(x, y, level_map)

        self.std = board.load_image('pockey.png')
        self.image = self.std

    def get_target(self):
        x, y = Ghost.get_target(self)
        map_way = [[one for one in line] for line in self.level_map]
        map_way = self.obhod(map_way, self.x, self.y, 1)
        self.make_way(map_way, x, y)
        if len(self.way) > 16:
            self.way = []
            return (x, y)
        else:
            self.way = []
            return (4, 20)


if __name__ == '__main__':
    if not os.path.exists('images'):
        os.mkdir('images')
    if not os.path.exists('images/door.jpg'):
        im = Image.new("RGB", (30, 10))
        pixels = im.load()
        for i in range(30):
            for j in range(10):
                pixels[i, j] = 132, 68, 33
        im.save("images/door.jpg")
    if not os.path.exists('images/big_point.jpg'):
        im = Image.new("RGB", (28, 28))
        pixels = im.load()
        for i in range(28):
            for j in range(28):
                pixels[i, j] = 190, 162, 63
        im.save("images/big_point.jpg")
    if not os.path.exists('images/small_point.jpg'):
        im = Image.new("RGB", (15, 15))
        pixels = im.load()
        for i in range(15):
            for j in range(15):
                r, g, b = pixels[i, j]
                pixels[i, j] = 231, 217, 128
        im.save("images/small_point.jpg")
    if not os.path.exists('images/wall.jpg'):
        im = Image.new("RGB", (30, 30))
        pixels = im.load()
        for i in range(30):
            for j in range(30):
                pixels[i, j] = 68, 150, 226
        im.save("images/wall.jpg")
    if not os.path.exists('images/shadow.jpg'):
        im = Image.new("RGB", (22, 25))
        pixels = im.load()
        for i in range(22):
            for j in range(25):
                pixels[i, j] = 248, 4, 4
        im.save("images/shadow.jpg")
    pygame.init()
    operating = True
    while operating:
        soundpoint = pygame.mixer.Sound('images/point.mp3')
        soundpoint.set_volume(0.05)
        menu_text = ['Pac-Man', '1 level', '2 level', '3 level', 'help',
                     'exit']
        font = pygame.font.Font('19888.ttf', 70)
        text_coord = 5
        width, height = 500, 400
        size = width, height
        screen_menu = pygame.display.set_mode(size)
        string_rendered = font.render(menu_text[0], 5, (248, 235, 49))
        intro_rect = string_rendered.get_rect()
        text_coord += 50
        intro_rect.top = text_coord
        intro_rect.x = 125
        text_coord += intro_rect.height
        screen_menu.blit(string_rendered, intro_rect)

        font = pygame.font.Font('19888.ttf', 32)
        string_rendered = font.render((' ' * 2).join(menu_text[1:4]), 1,
                                      (248, 235, 49))
        intro_rect = string_rendered.get_rect()
        text_coord += 70
        intro_rect.top = text_coord
        intro_rect.x = 30
        text_coord += intro_rect.height
        screen_menu.blit(string_rendered, intro_rect)

        string_rendered = font.render((' ' * 15).join(menu_text[4:]), 1,
                                      (248, 235, 49))
        intro_rect = string_rendered.get_rect()
        text_coord += 100
        intro_rect.top = text_coord
        intro_rect.x = 40
        text_coord += intro_rect.height
        screen_menu.blit(string_rendered, intro_rect)

        running = True
        while running and operating:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    operating = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x = event.pos[0]
                    y = event.pos[1]
                    if x >= 380 and x <= 450 and y >= 335 and y <= 350:
                        operating = False
                    elif x >= 30 and x <= 150 and y >= 195 and y <= 218:
                        file_level = 1
                        running = False
                    elif x >= 190 and x <= 314 and y >= 195 and y <= 218:
                        file_level = 2
                        running = False
                    elif x >= 352 and x <= 475 and y >= 195 and y <= 218:
                        file_level = 3
                        running = False
            pygame.display.flip()
        if file_level == 1:
            file_name = 'level1.txt'
            if not os.path.exists(file_name):
                level = ['############################',
                         '#............##............#',
                         '#,#####.####.##.#####.####,#',
                         '#.#####.####.##.#####.####.#',
                         '#.#####.####.##.#####.####.#',
                         '#..........................#',
                         '##.####.############.####.##',
                         '#..........................#',
                         '#.#####.#### ## ####.#####.#',
                         '#.......#.# *    #.#.......#',
                         '#.##.##.#.###--###.#.##.##.#',
                         '#.##.##.#.##@@@@##.#.##.##.#',
                         '#.##.##.#.########.#.##.##.#',
                         '#.##.##..............##.##.#',
                         '#.##.##.############.##.##.#',
                         '#............##............#',
                         '#,##.##.####.##.####.##.##,#',
                         '#.##.##.####.##.####.##.##.#',
                         '#..........................#',
                         '#.#####.####.##.#####.####.#',
                         '#..........................#',
                         '############################', ]
            else:
                f = open(file_name, 'rt', encoding="utf-8")
                level = [[one for one in f.readline().replace('\n', '')] for _
                         in
                         range(22)]
                f.close()
        elif file_level == 2:
            file_name = 'level2.txt'
            if not os.path.exists(file_name):
                level = ['############################'
                         '#............##............#',
                         '#.#.#.#.#.##.##.##.##.####.#',
                         '#.#.,...#.##.##.##.##.####.#',
                         '#.#####.####.##.##.##.####.#',
                         '#...#..................#.,.#',
                         '##.#.##..###.##.##.#.#.##.##',
                         '#..........................#',
                         '#.#####.#### ## ####.#####.#',
                         '#.....#... *      .........#',
                         '##.#.##.#.###--###..#.#.#.##',
                         '##.#.##.#.##@@@@##..#.#.#.##',
                         '##.#,##.#.########..#.#.#.##',
                         '##.#.##.............#.#.#.##',
                         '##.#.##.##.########.#.#.#.##',
                         '#.....#......##.....###....#',
                         '#.#.#.#.####.##.##.#.###,#.#',
                         '###.#.#.####.##.##.#.#.#.#.#',
                         '#.#.#.#..............#.###.#',
                         '#.#.#.#.####.##.#####..###.#',
                         '#..........................#',
                         '############################']
            else:
                f = open(file_name, 'rt', encoding="utf-8")
                level = [[one for one in f.readline().replace('\n', '')] for _
                         in
                         range(22)]
                f.close()
        elif file_level == 3:
            file_name = 'level3.txt'
            if not os.path.exists(file_name):
                level = ['############################',
                         '#......#...................#',
                         '#.#.#.#.#.##.##.##.##.##.#.#',
                         '###.,...#.##.##..#.#...#####',
                         '#.#.#.#.####.##.##.##.##.#.#',
                         '#...#..................#.,.#',
                         '##.#.##..###.##.##.#.#.##.##',
                         '#............##............#',
                         '#.#####.#### ## ##########.#',
                         '#.....#.#. *      ..#......#',
                         '#.##.##.#.###--###..#.#.#.##',
                         '##...##.#..#@@@@#...#.#.#.##',
                         '####.##.#.########..#.#.#.##',
                         '##,..##.................#.##',
                         '#.##.##.##.#####.##.#.#.#.##',
                         '#.....#......##.....###....#',
                         '#.#.#.#.####.##.##.#.###,#.#',
                         '###.#.#.####.##.##.#.#.#.#.#',
                         '#.#.#.#..............#.....#',
                         '#.#.#.#.#.##.##.#.###..###.#',
                         '#.....#.............#....#.#',
                         '############################']
            else:
                f = open(file_name, 'rt', encoding="utf-8")
                level = [[one for one in f.readline().replace('\n', '')] for _
                         in
                         range(22)]
                f.close()
        board = Board(level)
        width, height = 32 * len(level[0]), 32 * len(level)
        size = width, height
        screen_play = pygame.display.set_mode(size)
        running = True
        all_sprites = pygame.sprite.Group()
        clock = pygame.time.Clock()
        pacman = PacMan(map(lambda x: board.left + board.cell_size * x,
                            get_pacman_cord(level)))
        points = pygame.sprite.Group()
        decorations = pygame.sprite.Group()
        ghosts = pygame.sprite.Group()
        level_map = [[0 for one in range(len(level[0]))] for _ in
                     range(len(level))]
        placed = 0
        died = False
        shadow = Shadow(get_ghost_coord(board.level, 1)[0],
                        get_ghost_coord(board.level, 1)[1], level_map)
        speedy = Speedy(get_ghost_coord(board.level, 2)[0],
                        get_ghost_coord(board.level, 2)[1], level_map)
        bashful = Bashful(get_ghost_coord(board.level, 3)[0],
                          get_ghost_coord(board.level, 3)[1], level_map)
        pockey = Pockey(get_ghost_coord(board.level, 4)[0],
                        get_ghost_coord(board.level, 4)[1], level_map)
        while running and operating:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    operating = False
                if event.type == pygame.KEYDOWN:
                    pacman.change_way(event)
            screen_play.fill((0, 0, 0))
            if board.score > 0:
                shadow.update()
            if board.score > 300:
                speedy.update()
            if board.score > 450:
                pockey.update()
            if board.score > 600:
                bashful.update()
            pacman.update()
            board.render(screen_play)
            all_sprites.draw(screen_play)
            pygame.display.flip()
            clock.tick(30)

        width, height = 500, 350
        size = width, height
        screen_result = pygame.display.set_mode(size)
        score = "Your score: " + str(board.score)
        if died:
            menu_text = ["You've lost!", score, 'menu', 'exit']
            font = pygame.font.Font('19888.ttf', 70)
            text_coord = 5
            size = width, height
            string_rendered = font.render(menu_text[0], 5, (248, 235, 49))
            intro_rect = string_rendered.get_rect()
            text_coord += 50
            intro_rect.top = text_coord
            intro_rect.x = 25
            text_coord += intro_rect.height
            screen_result.blit(string_rendered, intro_rect)
        else:
            menu_text = ["You won!", score, 'menu', 'exit']
            font = pygame.font.Font('19888.ttf', 70)
            text_coord = 5
            string_rendered = font.render(menu_text[0], 5, (248, 235, 49))
            intro_rect = string_rendered.get_rect()
            text_coord += 50
            intro_rect.top = text_coord
            intro_rect.x = 110
            text_coord += intro_rect.height
            screen_result.blit(string_rendered, intro_rect)

        font = pygame.font.Font('19888.ttf', 32)
        string_rendered = font.render(menu_text[1], 1,
                                      (248, 235, 49))
        intro_rect = string_rendered.get_rect()
        text_coord += 50
        intro_rect.top = text_coord
        intro_rect.x = 130
        text_coord += intro_rect.height
        screen_result.blit(string_rendered, intro_rect)

        string_rendered = font.render((' ' * 15).join(menu_text[2:]), 1,
                                      (248, 235, 49))
        intro_rect = string_rendered.get_rect()
        text_coord += 60
        intro_rect.top = text_coord
        intro_rect.x = 50
        text_coord += intro_rect.height
        screen_result.blit(string_rendered, intro_rect)

        running = True
        while running and operating:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    operating = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x = event.pos[0]
                    y = event.pos[1]
                    if x >= 392 and x <= 460 and y >= 272 and y <= 290:
                        operating = False
                    elif x >= 45 and x <= 120 and y >= 275 and y <= 290:
                        running = False
            pygame.display.flip()
    pygame.quit()
