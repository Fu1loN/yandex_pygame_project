import pygame
import os
import sys

def get_pacman_cord(level):
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == '*':
                return [j, i]


class Board:
    def __init__(self, level):
        self.level = level
        self.cell_size = 30
        self.width = len(self.level[0])
        self.height = len(self.level)
        self.left = 25
        self.top = 25

    def render(self, screen):
        global decorations, points
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
                    points.add(sprite)
                elif self.level[i][j] == ',':
                    sprite = pygame.sprite.Sprite()
                    sprite.image = self.load_image("big_point.jpg")
                    sprite.rect = sprite.image.get_rect()
                    sprite.rect.x = 27 + j * 30
                    sprite.rect.y = 27 + i * 30
                    points.add(sprite)
        decorations.draw(screen_play)
        points.draw(screen_play)

    def find_cell(self, pos):
        '''когда пакмен будет находиться на клетке с точкой,то сюда будут передоваться его координаты, чтобы определить положение клетки и по ней удалить её из self.level'''
        x, y = pos[0], pos[1]
        for i in range(len(self.level)):
            for j in range(len(self.level[i])):
                if x > 25 + j * 30 and x < 25 + (j + 1) * 30 and \
                        y > 25 + i * 30 and y < 25 + (i + 1) * 30:
                    return i, j

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
        self.image = pygame.Surface((2 * 15 - 4, 2 * 15 - 4),
                                    pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("yellow"),
                           (13, 13), 13)
        x, y = pos
        x += 1
        y += 1
        self.rect = pygame.Rect(x, y, 28, 28)
        self.x_move = 0
        self.y_move = 0

    def update(self, *args):
        self.rect = self.rect.move(self.x_move, self.y_move)
        if pygame.sprite.spritecollideany(self, decorations):
            self.rect = self.rect.move(-self.x_move, -self.y_move)

    def change_way(self, ev):
        x, y = self.x_move, self.y_move
        if ev.scancode == 80:
            self.x_move, self.y_move = -5, 0
        if ev.scancode == 82:
            self.x_move, self.y_move = 0, -5
        if ev.scancode == 79:
            self.x_move, self.y_move = 5, 0
        if ev.scancode == 81:
            self.x_move, self.y_move = 0, 5
        self.rect = self.rect.move(self.x_move, self.y_move)
        if pygame.sprite.spritecollideany(self, decorations):
            self.rect = self.rect.move(-self.x_move, -self.y_move)
            self.x_move, self.y_move = x, y
        else:
            self.rect = self.rect.move(-self.x_move, -self.y_move)



if __name__ == '__main__':
    pygame.init()
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
    all_sprites = pygame.sprite.Group()
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
    try:
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
        pacman = PacMan(map(lambda x: board.left + board.cell_size * x, get_pacman_cord(level)))

        points = pygame.sprite.Group()
        decorations = pygame.sprite.Group()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    print(board.find_cell(event.pos))
                if event.type == pygame.KEYDOWN:
                    pacman.change_way(event)

            screen_play.fill((0, 0, 0))
            pacman.update()
            board.render(screen_play)
            all_sprites.draw(screen_play)
            pygame.display.flip()
            clock.tick(30)
        pygame.quit()
    except FileNotFoundError:
        print('Файл с уровнем не найден')
