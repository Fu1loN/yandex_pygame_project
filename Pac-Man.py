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
        global decorations, points, level_map
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
        global running

        self.rect = self.rect.move(self.x_move, self.y_move)
        if pygame.sprite.spritecollideany(self, decorations):
            self.rect = self.rect.move(-self.x_move, -self.y_move)
        if self.ate_big_coin:
            self.ate_clock += 0.2
            if self.ate_clock >= 11:
                self.ate_big_coin = False
                self.ate_clock = 0
                bashful.unscare()
                speedy.unscare()
                shadow.unscare()
                pockey.unscare()
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
                print('dead')
                running = False
            else:
                c = pygame.sprite.spritecollide(self, ghosts, False)
                for ghost in c:
                    if ghost.eatable:
                        board.score += 0#Сколько??
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
        self.x, self.y = x, y
        self.way = []
        self.level_map = level_map
        self.image = pygame.Surface((2 * 15 - 4, 2 * 15 - 4), pygame.SRCALPHA,
                                    32)
        self.rect = pygame.Rect((self.x + 1) * 30, (self.y + 1) * 30, 30, 30)

        self.speed = 5
        self.lspeed = 5
        self.ticks = 0
        self.updates = 0
        self.eatable = False
        self.fear = False

    def update_target(self):
        if self.fear:
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
            elif x == self.x and y == self.y and self.fear and not self.eatable:
                self.unscare()

            else:
                self.rect = self.rect.move(self.speed, 0)
                self.x, self.y = board.find_cell(
                    (self.rect.x + 1, self.rect.y + 15))

        except IndexError:
            pass

    def ate(self):
        self.eatable = False
        # поменять спрайт
        self.speed, self.lspeed = 10, self.speed


    def scaring(self):
        # поменять спрайт
        self.fear = True
        self.eatable = True

    def unscare(self):
        self.speed = self.lspeed
        self.fear = False
        self.eatable = False
        # поменять спрайт


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
        shadow = pygame.sprite.Group()
        sprite = pygame.sprite.Sprite()
        sprite.image = board.load_image("shadow.jpg")
        sprite.rect = sprite.image.get_rect()
        shadow.add(sprite)
        shadow.draw(self.image)


class Speedy(Ghost):
    def __init__(self, x, y, level_map):
        super().__init__(x, y, level_map)
        self.image = pygame.Surface((2 * 15 - 4, 2 * 15 - 4), pygame.SRCALPHA,
                                    32)
        pygame.draw.circle(self.image, pygame.Color("pink"), (13, 13), 13)

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
        self.image = pygame.Surface((2 * 15 - 4, 2 * 15 - 4), pygame.SRCALPHA,
                                    32)
        pygame.draw.circle(self.image, pygame.Color("lightblue"), (13, 13), 13)

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
        self.image = pygame.Surface((2 * 15 - 4, 2 * 15 - 4), pygame.SRCALPHA,
                                    32)
        pygame.draw.circle(self.image, pygame.Color("orange"), (13, 13), 13)

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

    soundpoint = pygame.mixer.Sound('images/point.mp3')
    soundpoint.set_volume(0.05)
    menu_text = ['Pac-Man', '1 level']
    font = pygame.font.Font(None, 30)
    text_coord = 100
    width, height = 500, 500
    size = width, height
    screen_menu = pygame.display.set_mode(size)
    string_rendered = font.render(menu_text[0], 5, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    text_coord += 50
    intro_rect.top = text_coord
    intro_rect.x = 50
    text_coord += intro_rect.height
    screen_menu.blit(string_rendered, intro_rect)
    for line in menu_text[1:]:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen_menu.blit(string_rendered, intro_rect)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                running = False
        pygame.display.flip()

    file_level = 1
    if file_level == 1:
        file_name = 'level1.txt'
        f = open(file_name, 'rt', encoding="utf-8")
        level = [[one for one in f.readline().replace('\n', '')] for _ in
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
        '''ghost_type = 0
        ghost_color = ['red', 'pink', 'blue', 'orange']'''
        placed = 0

        shadow = Shadow(get_ghost_coord(board.level, 1)[0],
                        get_ghost_coord(board.level, 1)[1], level_map)
        speedy = Speedy(get_ghost_coord(board.level, 2)[0],
                        get_ghost_coord(board.level, 2)[1], level_map)
        bashful = Bashful(get_ghost_coord(board.level, 3)[0],
                          get_ghost_coord(board.level, 3)[1], level_map)
        pockey = Pockey(get_ghost_coord(board.level, 4)[0],
                        get_ghost_coord(board.level, 4)[1], level_map)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                '''if event.type == pygame.MOUSEBUTTONDOWN:
                    print(board.find_cell(event.pos))'''
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
        pygame.quit()
