import pygame
import shutil
import os
import random
from datetime import datetime
pygame.font.init()      #Иициализация шрифта

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

SPACE_SHIP_WIDTH, SPACE_SHIP_HEIGHT = 55, 40

    # Корабли
RED_SPACESHIP = pygame.image.load(os.path.join("assets", "red_ship.png"))
GREEN_SPACESHIP = pygame.image.load(os.path.join("assets", "green_ship.png"))
BLUE_SPACESHIP = pygame.image.load(os.path.join("assets", "blue_ship.png"))

    # Игрок
PLAYER_SPACESHIP = pygame.image.load(os.path.join("assets", "player_ship.png"))

    # Лазеры
RED_LASER = pygame.image.load(os.path.join("assets", "red_laser.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "green_laser.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "blue_laser.png"))
PlAYER_LASER = pygame.image.load(os.path.join("assets", "player_laser.png"))

    # Фон
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "BG.png")), (WIDTH, HEIGHT))


class Laser:
    def __init__(self, x, y, pic):
        self.x = x              #Определение атрибутов лазера, ссылки на объект класса
        self.y = y
        self.pic = pic
        self.mask = pygame.mask.from_surface(self.pic)

    def draw(self, window):
        window.blit(self.pic, (self.x, self.y))             #добавление на экран лазера

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=50):
        self.x = x                  #Определение атрибутов кораблей, ссылки на объект класса
        self.y = y
        self.health = health
        self.ship_pic = None
        self.laser_pic = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_pic, (self.x, self.y))     #выводит на экран игрока
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)

            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_pic)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_pic.get_width()

    def get_height(self):
        return self.ship_pic.get_height()


class Player(Ship):
    def __init__(self, x, y, health=50):
        super().__init__(x, y, health)
        self.ship_pic = PLAYER_SPACESHIP
        self.laser_pic = PlAYER_LASER
        self.mask = pygame.mask.from_surface(self.ship_pic)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)

                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_pic.get_height() + 10, self.ship_pic.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_pic.get_height() + 10, self.ship_pic.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACESHIP, RED_LASER),
                "green": (GREEN_SPACESHIP, GREEN_LASER),
                "blue": (BLUE_SPACESHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_pic, self.laser_pic = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_pic)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_pic)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y

    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 2
    font = pygame.font.SysFont("Arial", 30)
    lost_font = pygame.font.SysFont("Arial", 60)


    score = 0
    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 3
    laser_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))

        lives_text = font.render(f"Жизни: {lives}", 1, (255,255,255))
        level_text = font.render(f"Уровень: {level}", 1, (255,255,255))
        score_text = font.render(f"Счет: {score}", 1, (255,255,255))
        VEL_text = font.render(f"Скорость: {player_vel}", 1, (255,255,255))
        VEL_laser_text = font.render(f"Скорость лазера: {laser_vel}", 1, (255, 255, 255))

        WIN.blit(VEL_laser_text, (10, 100))
        WIN.blit(VEL_text, (10, 70))
        WIN.blit(lives_text, (10, 40))
        WIN.blit(score_text, (10, 10))
        WIN.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:

            lost_label = lost_font.render(f"Поражение!: {score}", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)

        redraw_window()


        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        if lost != True:
            score += 1
        if lost:

            c = str(datetime.now().time())
            sc = str(score)
            f = open("table2.html", mode="r")
            fstr = f.read()
            #print(fstr)
            fstr = fstr.replace('</tbody></table>', "<tr><td>"+c+"</td><td>"+sc+"</td></tr>"+"</tbody></table>", 1)
            f.close()

            f = open("table2.html", mode="w")

            f.write(fstr)




        if len(enemies) == 0:
            level += 1
            a = random.randrange(0, 100)
            if a > 40 or level > 1:
                player_vel += 1
            if a > 50 or level > 1:
                laser_vel += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(40, WIDTH-100), random.randrange(-1200, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()# фиксирование нажатий
        if keys[pygame.K_a] and player.x - player_vel > 0: # влево
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # вправо
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # вверх
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: #вниз
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1

                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("Arial", 60)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        shutil.copy2('C:/Users/User/PycharmProjects/pythonProject4/table2.html',
                     'C:/Users/User/PycharmProjects/pythonProject4Serv/templates/table2.html')

        title_label = title_font.render("Нажмите кнопку мыши...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
