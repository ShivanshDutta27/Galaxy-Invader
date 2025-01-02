import math

import pygame
import os
import time
import random
pygame.font.init()

# Setting Up the Window
WIDTH, HEIGHT = 800, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Invader")

#LOADING IN ALL THE IMAGES         We can do it directly too but its cleaner if we use os.path.join
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))
BOSS_SHIP=pygame.transform.scale(pygame.image.load(os.path.join("assets","pixel_ship_boss.png"),),(100,100))
# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
CYAN_LASER= pygame.image.load(os.path.join("assets","pixel_laser_cyan.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))


# Rules that will be displayed
rules = [
        "Game Rules:",
        "1. Use W, A, S, D to move your ship.",
        "2. Press SPACE to shoot lasers.",
        "3. Destroy enemy ships to prevent them from reaching the bottom.",
        "4. Each enemy ship that reaches the bottom reduces your lives.",
        "5. Avoid enemy lasers to protect your health.",
        "6. If your health or lives drop to zero, it's game over.",
        "7. Survive waves of enemies; each wave gets harder.",
        "                                                  ",
        "Press ESC to return to the Main Menu."
    ]


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

# Abstract class for all Ships , so it wont be directly used but inherited from
class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    # This function is just to check collision with player, for enemies , seperate function in player class
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
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER

        # Masking for Pixel Perfect Collision
        self.mask = pygame.mask.from_surface(self.ship_img)        # Identifies where pixels are and aren't
        self.max_health = health

    def move_lasers(self, vel, objs,isBoss):
        if not isBoss:
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
        else:
            self.cooldown()
            for laser in self.lasers:
                laser.move(vel)
                if laser.off_screen(HEIGHT):
                    self.lasers.remove(laser)
                elif laser.collision(objs):
                    objs.health -= 10
                    if laser in self.lasers:
                        self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

# Boss
class Boss(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = BOSS_SHIP
        self.laser_img = CYAN_LASER

        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.last_move_time = pygame.time.get_ticks()
        self.dir=True

    def move_lasers(self, vel, obj):

        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
    def shoot(self):
        if self.cool_down_counter == 0:
            laser1 = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser1)
            laser2 = Laser(self.x+self.ship_img.get_width() - 20, self.y, self.laser_img)
            self.lasers.append(laser2)
            self.cool_down_counter+=0.5

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

    def move(self):
        if self.y<25:
            self.y+=2

    def move_x(self,vel_x,val):
        if val>0.99:
            self.dir=not self.dir
        if self.dir==True and self.x+self.ship_img.get_width()+ vel_x<WIDTH:
            self.x+=vel_x
        elif self.dir==False and self.x-self.ship_img.get_width()+vel_x>0:
            self.x-=vel_x

# if boss health 0, move randomly
class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

# Main game loop
def main():
    run = True
    FPS = 60
    level = 7
    lives = 5
    main_font = pygame.font.SysFont("JetBrains Mono", 36)
    lost_font = pygame.font.SysFont("Arial", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5
    boss_vel=6
    player = Player(300, 630)
    boss=Boss(WIDTH//2,-150)
    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    

    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)
        # The ordering here makes it so that if they overlap then player will be visible as it is drawn later
        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("Git Gud", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:

        clock.tick(FPS)
        redraw_window()
        # Checking if lost
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        # Spawning enemies
        
        if len(enemies) == 0:
            level += 1
            if(level==8):
                boss_level()
                
            wave_length += round(5*(math.log(level,2)))
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        # if we handle the movement inside this for loop, it wont register multiple clicks at the same time
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
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
        # Negative belocity so that it goes up and not down
        player.move_lasers(-laser_vel, enemies,False)

    pygame.quit()


def game_rules():
    title_font=pygame.font.SysFont("HP Simplified",32)
    rule_font = pygame.font.SysFont("HP Simplified", 27)
    run=True
    while run:
        WIN.blit(BG,(0,0))
        title_label=title_font.render("Game Rules: ",1,"white")
        WIN.blit(title_label,(WIDTH//2-title_label.get_width()//2,10))
        temp=title_label.get_height()
        rule_y=10+title_label.get_height()
        for rule in rules:
            rule_label=rule_font.render(rule,1,"white")
            WIN.blit(rule_label,(10,rule_y))
            rule_y+=temp
        pygame.display.update()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                run=False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    pygame.time.delay(200)
                    main_menu()
    pygame.quit()



def boss_level():
    run = True
    FPS = 60
    x=0
    main_font = pygame.font.SysFont("JetBrains Mono", 36)
    lost_font = pygame.font.SysFont("Arial", 50)
    
    boss=Boss(WIDTH//2-BOSS_SHIP.get_width()//2,-200,200)
    player_vel = 5
    laser_vel = 5
    boss_vel = 6
    player = Player(300, 630)
    clock = pygame.time.Clock()

    lost = False
    lost_count = 0
    win=False
    win_count=0
    def redraw_window():
        WIN.blit(BG, (0, 0))
        
        level_label = main_font.render(f"Boss Level", 1, (255, 0, 0))

        WIN.blit(level_label, (WIDTH//2-level_label.get_width()//2, 0))

        boss.draw(WIN)
        
        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("Come back again(If You Dare)", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))

        pygame.display.update()

    while run:

        clock.tick(FPS)
        redraw_window()
        # Checking if lost
        if player.health <= 0:
            lost = True
            lost_count += 1

        # Check if won
        if boss.health<=0:
            won_text=main_font.render("You are the Goat",1,"white")
            WIN.blit(won_text,(WIDTH//2-won_text.get_width()//2,HEIGHT//2-won_text.get_height()//2))
            pygame.display.update()
            win=True

        if win:
            if win_count > FPS*2:
                run=False
            else:
                win_count+=1
                continue
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        boss.move()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        # if we handle the movement inside this for loop, it wont register multiple clicks at the same time
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:  # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        val=random.random()
        print(val)
        if boss.y>=15 :
            boss.move_x(2,val)


        boss.move_lasers(laser_vel,player)
        if random.randrange(0, 2 * 20) == 1:
            boss.shoot()

        if collide(boss, player):
            lost=True
            continue
        
        player.move_lasers(-laser_vel, boss,True)
        x+=1
    pygame.quit()



    
def main_menu():
    title_font = pygame.font.SysFont("JetBrains Mono", 36)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin", 1, (255,255,255))
        rules_text=title_font.render("Press H for Game Rules",1,(200,200,0))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 320))
        WIN.blit(rules_text, (WIDTH / 2 - rules_text.get_width() / 2, 330+title_label.get_height()))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
        keys=pygame.key.get_pressed()
        if keys[pygame.K_h]:
            game_rules()

    pygame.quit()




main_menu()
