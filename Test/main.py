import pgzero
from pygame import Rect
from pygame.image import load # importing load function to load the tileset
import random as rand

class Character:
    def __init__(self, hp, attack, pos):
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.pos = pos
        self.attacked = False

    def attack(self, target, attack, precision):
        d20 = rand.randint(1, 20)
        dammage = rand.randint(1, 6) + attack

        if d20 == 1 or d20 + precision < 9:
            dammage = 0
            print(f'{self.__class__.__name__} missed! (rolled {d20})')
        elif d20 == 20:
            dammage *= 2
            target.hp -= dammage
            print(f'{self.__class__.__name__} landed a critic! (rolled {d20})')
        else:
            print(f'{self.__class__.__name__} rolled {d20} and caused {dammage} dammage!')
        
        target.hp -= dammage
        return None

    def hp_bar_draw(self):
        screen.draw.filled_rect(Rect((self.pos[0]-25, self.pos[1]-40), (50, 5)), 'red')
        screen.draw.filled_rect(Rect((self.pos[0]-25, self.pos[1]-40), (50 * self.hp / self.max_hp, 5)), 'green')

class Knight(Character):
    def __init__(self, step, hp, attack, pos):
        self.name = 'Knight'
        self.step = step
        self.precision = 4
        self.attack_range = 2
        super().__init__(hp, attack, pos)
        self.mov_sprites = {'w': [f'knight/walk_up/{i}' for i in range(1,5)],
                            's': [f'knight/walk_down/{i}' for i in range(1,5)],
                            'a': [f'knight/walk_left/{i}' for i in range(1,3)],
                            'd': [f'knight/walk_right/{i}' for i in range(1,3)]}
        
        self.attack_sprites = {'a': [f'knight/attack/left{i}' for i in range(1,4)],
                               'w': [f'knight/attack/back{i}' for i in range(1,4)],
                               'd': [f'knight/attack/right{i}' for i in range(1,4)],
                               's': [f'knight/attack/front{i}' for i in range(1,4)]}
        
        self.idle_sprites = {'left': ['knight/idle_left/1'],
                             'up': ['knight/idle_up/1', 'knight/idle_up/2'],
                             'right': ['knight/idle_right/1'],
                             'down': ['knight/idle_down/1', 'knight/idle_down/2']}
        self.last_pressed = 's'
        self.idle_index = 0
        self.mov_index = 0
        self.idle_frame_count = 0
        self.mov_frame_count = 0
        self.regen_frame_count = 0
        self.attack_frame_count = 0
        self.switch_delay = 15 # 30 frames = 0.5 sec
        self.knight = Actor('knight/idle_down/1')
        self.knight.pos = (WIDTH//2, HEIGHT//2)

    def move(self, enemies):

        if self.hp > 0:
            moved = False
            idle_sprites = self.idle_sprites['down']

            original_position = (self.knight.x, self.knight.y)

            if keyboard.a:
                new_x = self.knight.x - self.step
                new_y = self.knight.y
                mov_sprites = self.mov_sprites['a']
                moved = True
                self.last_pressed = 'a'
            elif keyboard.d:
                new_x = self.knight.x + self.step
                new_y = self.knight.y
                mov_sprites = self.mov_sprites['d']
                moved = True
                self.last_pressed = 'd'
            elif keyboard.w:
                new_x = self.knight.x
                new_y = self.knight.y - self.step
                mov_sprites = self.mov_sprites['w']
                moved = True
                self.last_pressed = 'w'
            elif keyboard.s:
                new_x = self.knight.x
                new_y = self.knight.y + self.step
                mov_sprites = self.mov_sprites['s']
                moved = True
                self.last_pressed = 's'
            elif keyboard.RETURN or self.attack_frame_count != 0:
                self.attack_frame_count += 1

                if self.attack_frame_count < 10:
                    self.knight.image = self.attack_sprites[self.last_pressed][0]
                    self.attacked = False
                elif self.attack_frame_count < 15:
                    self.knight.image = self.attack_sprites[self.last_pressed][1]
                elif self.attack_frame_count < 20:
                    self.knight.image = self.attack_sprites[self.last_pressed][2]
                    for enemy in enemies:
                        distance_to_enemy = ((self.knight.x - enemy.devil.x)**2 + (self.knight.y - enemy.devil.y)**2)**0.5
                        hit = False
                        if self.last_pressed == 'w' and enemy.devil.y < self.knight.y and distance_to_enemy <= self.attack_range:
                            hit = True
                        elif self.last_pressed == 's' and enemy.devil.y > self.knight.y and distance_to_enemy <= self.attack_range:
                            hit = True
                        elif self.last_pressed == 'a' and enemy.devil.x < self.knight.x and distance_to_enemy <= self.attack_range:
                            hit = True
                        elif self.last_pressed == 'd' and enemy.devil.x > self.knight.x and distance_to_enemy <= self.attack_range:
                            hit = True

                        if hit and not self.attacked:
                            super().attack(enemy, self.attack, self.precision)
                            self.attacked = True
                
                        if enemy.hp <= 0:
                            self.hp = min(self.hp + enemy.max_hp * .05, self.max_hp)

                else:
                    self.attack_frame_count = 0
                return
            self.attack_frame_count = 0

            self.regen_frame_count += 1
            if self.regen_frame_count == 60:
                self.regen_frame_count = 0
                self.hp = min(self.hp * 1.005, self.max_hp)

            match(self.last_pressed):
                case 'w':
                    idle_sprites = self.idle_sprites['up']
                case 'a':
                    idle_sprites = self.idle_sprites['left']
                case 'd':
                    idle_sprites = self.idle_sprites['right']

            if not moved or not level.can_move_to(new_x, new_y):
                moved = False
                self.knight.x = original_position[0]
                self.knight.y = original_position[1]
                self.idle_frame_count += 1
                if self.idle_frame_count > self.switch_delay:
                    self.idle_index = (self.idle_index + 1) % len(idle_sprites)
                    self.knight.image = idle_sprites[self.idle_index]
                    self.idle_frame_count = 0
            else:
                self.mov_frame_count += 1
                self.knight.x = new_x
                self.knight.y = new_y
                if self.mov_frame_count > self.switch_delay:
                    self.mov_index = (self.mov_index + 1) % len(mov_sprites)
                    self.knight.image = mov_sprites[self.mov_index]
                    self.mov_frame_count = 0
        else:
            self.knight.image = 'knight/dead'
 
    def draw(self):
        self.knight.draw()

class Devil(Character):
    def __init__(self, step, hp, attack, pos):
        self.step = step
        self.attack_frame_count = 0
        self.attack_frame_index = 0
        self.is_alive = True
        self.precision = 2
        self.last_pressed = 's'
        self.mov_frame_count = 0
        self.idle_frame_count = 0
        self.idle_index = 0
        self.mov_index = 0
        self.switch_delay = 15
        super().__init__(hp=hp, attack=attack, pos=pos)
        self.devil = Actor('enemy/devil/1')
        self.devil.pos = pos
        self.mov_sprites = {'w': [f'enemy/devil/{i}' for i in range(5,9)],
                            'a': [f'enemy/devil/{i}' for i in range(5,9)],
                            's': [f'enemy/devil/{i}' for i in range(5,9)],
                            'd': [f'enemy/devil/{i}' for i in range(5,9)]}
        
        self.attack_sprites = [f'enemy/devil/{i}' for i in [2, 3, 1, 4, 1, 2]]
        self.attack_frame_delay = [10, 20, 30, 50, 55, 60]
        
        self.idle_sprites = {'up': ['enemy/devil/1'],
                             'left': ['enemy/devil/1'],
                             'right': ['enemy/devil/1'],
                             'down': ['enemy/devil/1']}

    def move(self, target, map):
        if self.hp > 0:
            moved = False
            idle_sprites = self.idle_sprites['down']

            original_position = (self.devil.x, self.devil.y)
            distance = [target[i] - original_position[i] for i in range(len(target))]

            if (distance[0]**2 + distance[1]**2)**0.5 <= 2 or self.attack_frame_count != 0:

                self.attack_frame_count += 1

                if self.attack_frame_count < self.attack_frame_delay[self.attack_frame_index]:
                    self.devil.image = self.attack_sprites[self.attack_frame_index]
                    if self.attack_frame_index == 4 and (distance[0]**2 + distance[1]**2)**0.5 <= 2 and not self.attacked:
                        super().attack(main_char, self.attack, self.precision)
                        self.attacked = True
                    return

                elif self.attack_frame_index < len(self.attack_frame_delay)-1:
                    self.attack_frame_index += 1
                    return
                self.attacked = False


            elif abs(distance[0]) > abs(distance[1]):
                direction = distance[0] / abs(distance[0])
                new_x = self.devil.x + direction * self.step
                new_y = self.devil.y
                mov_sprites = self.mov_sprites['a']
                moved = True
                self.last_pressed = 's'
            else:
                direction = distance[1] / abs(distance[1])
                new_y = self.devil.y + direction * self.step
                new_x = self.devil.x
                mov_sprites = self.mov_sprites['s']
                moved = True
                self.last_pressed = 'a'

            self.attack_frame_index = 0
            self.attack_frame_count = 0

            match(self.last_pressed):
                case 'w':
                    idle_sprites = self.idle_sprites['up']
                case 'a':
                    idle_sprites = self.idle_sprites['left']
                case 'd':
                    idle_sprites = self.idle_sprites['right']

            if not moved or not map.can_move_to(new_x, new_y):
                moved = False
                self.devil.x = original_position[0]
                self.devil.y = original_position[1]
                self.idle_frame_count += 1
                if self.idle_frame_count > self.switch_delay:
                    self.idle_index = (self.idle_index + 1) % len(idle_sprites)
                    self.devil.image = idle_sprites[self.idle_index]
                    self.idle_frame_count = 0
            else:
                self.mov_frame_count += 1
                self.devil.x = new_x
                self.devil.y = new_y
                if self.mov_frame_count > self.switch_delay:
                    self.mov_index = (self.mov_index + 1) % len(mov_sprites)
                    self.devil.image = mov_sprites[self.mov_index]
                    self.mov_frame_count = 0
        else:
            pass

    def draw(self):
        self.devil.draw()

    def can_move_to(self, x, y):
        pass

class Map:
    def __init__(self):
        self.tileset = load("images/Tiled_files/walls_floor.png")
        self.tile_size = 16 # try 8, 16, 32
        self.tiles = {0: self.get_tile(14, 12), # floor
                      1: self.get_tile(4, 6), # wall facing up
                      2: self.get_tile(4, 5), # down left corner
                      3: self.get_tile(3, 5), # wall left
                      4: self.get_tile(2, 5), # wall left 2 
                      5: self.get_tile(1, 5), # upper left corner
                      6: self.get_tile(1, 6), # wall facing down
                      7: self.get_tile(1, 7), # upper right corner
                      8: self.get_tile(2, 7), # wall right
                      9: self.get_tile(3, 7), # wall right 2
                      10: self.get_tile(4, 7), # down right corner
                      11: self.get_tile(4, 2), # wall facing down (bottom part)
                      12: self.get_tile(4, 3), # wall right to up curve (bottom part)
                      13: self.get_tile(1, 1),
                      14: self.get_tile(3, 1),
                      15: self.get_tile(1, 4),
                      16: self.get_tile(3, 4)} 
        
        self.dungeon_map = [[5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7],
                            [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
                            [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9],
                            [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
                            [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9],
                            [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
                            [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9],
                            [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
                            [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9],
                            [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
                            [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9],
                            [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
                            [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9],
                            [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
                            [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9],
                            [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
                            [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9],
                            [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
                            [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 10]]

    def get_tile(self, row, col):
        rect = Rect(col*self.tile_size, row*self.tile_size, self.tile_size, self.tile_size)
        tile = self.tileset.subsurface(rect).copy()
        return tile
    
    def draw_map(self):
        for y, row in enumerate(self.dungeon_map):
            for x, tile_id in enumerate(row):
                tile = self.tiles[tile_id]
                screen.blit(tile, (x*self.tile_size, y*self.tile_size))
    
    def can_move_to(self, new_x, new_y):
        new_x //= self.tile_size
        new_y //= self.tile_size
        return self.dungeon_map[int(new_y)][int(new_x)] == 0

class Menu:
    def __init__(self):
        self.menu_items = ['Start Game', 'Volume', 'Quit']
        self.selected_item = 0
        self.volume = 0.25
        self.frame_count = 0
        sounds.game_intro.play(-1)
        sounds.game_intro.set_volume(self.volume)

    
    def draw_menu(self):
        screen.draw.text(2*'=' + ' Enter The Dungeon ' + 2*'=', (10, 30), fontsize=45, color='yellow')
        
        for i, item in enumerate(self.menu_items):
            color = 'red' if i == self.selected_item else 'white'
            text = item
            if item == 'Volume':
                text = f'Volume: {round(self.volume*100)}%'
            screen.draw.text(text, (50, 100+i*20), fontsize=30, color=color)
        screen.draw.text('Use WASD to move and ENTER to choose', (0, HEIGHT-10), fontsize=15, color='blue')
    
    def change_option(self):
        self.frame_count += 1 # just to make option change smoother

        if self.frame_count == 10:
            self.frame_count = 0
            if keyboard.w:
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)
            elif keyboard.s:
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)

        if self.frame_count >= 1: # volume change rate can be higher
            if self.selected_item == 1: # i.e. if selected item = volume
                if keyboard.a:
                    self.volume = max(0, self.volume-0.01)

                elif keyboard.d:
                    self.volume = min(1, self.volume+0.01)

                sounds.game_intro.set_volume(self.volume)
        
        if keyboard.RETURN:
            if self.selected_item == 0: # i.e. if selected item = start
                sounds.game_intro.stop()
                sounds.in_game.play(-1)
                sounds.in_game.set_volume(self.volume)
                return True
            elif self.selected_item == 2: # i.e. if selected item = quit
                exit()
        return False

WIDTH = 400
HEIGHT = 300

main_char = Knight(step=3, hp=100, attack=5, pos=(WIDTH//2, HEIGHT//2))
level = Map()
main_menu = Menu()

game_started = False
devil_spawn = rand.randint(1, 10) * 60
devil_spawn_count = 0
devils= []

def draw():
    screen.clear()

    if not game_started:
        main_menu.draw_menu()
    elif main_char.hp > 0:
        level.draw_map()
        main_char.draw()
        main_char.hp_bar_draw()

        for devil in devils:
            devil.draw()
    else:
        screen.clear()
        screen.fill((0, 0, 0))
        screen.draw.text("YOU DIED",
                            center=(WIDTH//2, HEIGHT//2),
                            fontsize=100,
                            color="red",
                            owidth=1.5, ocolor="black")
        for devil in devils:
            devils.remove(devil)
        main_char.knight.image = 'knight/dead'
        main_char.draw()
        main_char.knight.pos = (WIDTH//2, HEIGHT*3/4)
        sounds.in_game.stop()
        sounds.dark_souls_you_died.play()
        sounds.dark_souls_you_died.set_volume(main_menu.volume)
        



def update():
    global game_started, devil_spawn_count, devil_spawn
    
    if not game_started:
        game_started = main_menu.change_option()
    else:
        if main_char.hp > 0:
            main_char.move(devils)
            if devil_spawn_count == devil_spawn:
                for i in range(rand.randint(1, 4)):
                    new_devil = Devil(step=rand.randint(1, 3), hp=rand.randint(5, 10), attack=rand.randint(1, 3), pos=(rand.randint(20, 380),rand.randint(20, 280)))
                    new_devil.draw()
                    devils.append(new_devil)
                devil_spawn = rand.randint(5, 10) * 60
                devil_spawn_count = 0
            else:
                devil_spawn_count += 1

            for devil in devils:
                if devil.hp <= 0:
                    devils.remove(devil)
                    pass
                devil.move((main_char.knight.x, main_char.knight.y), level)

