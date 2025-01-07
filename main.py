import math

import pygame
import os
import time
import random
pygame.font.init()
pygame.mixer.init()

pygame.mixer.music.load("assets/space-120280.mp3")
pygame.mixer.music.play(-1, 0.0)  # -1 means loop indefinitely; 0.0 means start from the beginning
pygame.mixer.music.set_volume(0.1)


# Setting Up the Window
WIDTH, HEIGHT = 800, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Invader")

#LOADING IN ALL THE IMAGES         We can do it directly too but its cleaner if we use os.path.join
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player player
YELLOW_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png")),(90,80))
BOSS_SHIP=pygame.transform.scale(pygame.image.load(os.path.join("assets","pixel_ship_boss.png"),),(100,100))
# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
CYAN_LASER= pygame.image.load(os.path.join("assets","pixel_laser_cyan.png"))

#Power Ups
HEALTH3=pygame.transform.scale(pygame.image.load(os.path.join("assets", "health_power.png")),(25,25))
FIRE=pygame.transform.scale(pygame.image.load(os.path.join("assets","bullet.png")),(40,40))

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
        "8. Collect power-ups to gain special abilities",
        "                                                  ",
        "Press ESC to return to the Main Menu."
    ]

player_laser_sound=pygame.mixer.Sound("assets/laser-hit.mp3")
player_laser_sound.set_volume(0.1)

enemy_laser_sound=pygame.mixer.Sound("assets/enemy-laser.mp3")
enemy_laser_sound.set_volume(0.1)

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

class PowerUp:

    MAP = {
        "health": HEALTH3,
        "fire_rate": FIRE
    }

    def __init__(self, x, y, type):

        self.x = x
        self.y = y
        self.type = type
        self.img = self.MAP[type]
        self.mask = pygame.mask.from_surface(self.img)  # For pixel-perfect collision

    def draw(self, window):

        window.blit(self.img, (self.x, self.y))

    def move(self, speed):

        self.y += speed

    def get_height(self):
        return self.img.get_height()


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

    def move_lasers(self, vel, obj,isLow):

        self.cooldown()
        for laser in self.lasers:
            if isLow:
                vel=8
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
    def shoot(self,isLow):

        if self.cool_down_counter == 0:
            laser1 = Laser(self.x-25, self.y, self.laser_img)
            self.lasers.append(laser1)
            laser2 = Laser(self.x+self.ship_img.get_width() - 25, self.y, self.laser_img)
            self.lasers.append(laser2)
            if(isLow):
                laser3=Laser(self.x+25,self.y,self.laser_img)
                self.lasers.append(laser3)
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

    powers=[]
    enemies = []
    wave_length = 6
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5
    boss_vel=6
    player = Player(300, 630)
    boss=Boss(WIDTH//2,-150)
    clock = pygame.time.Clock()

    lost = False
    lost_count = 0
    fire_rate_bool=False
    power_counter=1

    

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

        for power in powers:
            power.draw(WIN)

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
                result_component(WIN, main_font, level-1)
                run = False
            else:
                continue

        # Spawning enemies
        if len(enemies) == 0:
            level += 1
            if(level==8):
                boss_level()

            wave_length += round(5*(math.log(level,4)))
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-2000, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

            for i in range(round(math.log10(wave_length)+1)):
                power=PowerUp(random.randrange(50, WIDTH-100), random.randrange(-2000, -800), random.choice(["health","fire_rate"]))
                powers.append(power)

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
            player_laser_sound.play()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
                if enemy.x>0 and enemy.y>0:
                    enemy_laser_sound.play()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)


        for power in powers[:]:
            power.move(enemy_vel)

            if collide(power, player):
                if power.type=="health" and player.health<=90:
                    player.health+=10
                else:
                    fire_rate_bool=True
                powers.remove(power)
            elif power.y + power.get_height() > HEIGHT:
                powers.remove(power)

        if fire_rate_bool:
            if power_counter < 650:
                player.COOLDOWN = 18
                power_counter += 1

            else:
                power_counter = 0
                fire_rate_bool=False
                player.COOLDOWN = 30



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
    counter=40
    boss=Boss(WIDTH//2-BOSS_SHIP.get_width()//2,-200,360)
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
                result_component(WIN, main_font, 7)
                run=False
            else:
                win_count+=1
                continue
        if lost:
            if lost_count > FPS * 3:
                result_component(WIN,main_font,7)
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

        if boss.y>=15 :
            boss.move_x(2,val)
        if boss.health<0.5*boss.max_health:
            boss.move_lasers(laser_vel,player,True)
        else:
            boss.move_lasers(laser_vel, player, False)
        if boss.health<0.5*boss.max_health:
            counter=15
        if random.randrange(1, counter) == 1:
            if boss.health<0.5*boss.max_health:
                boss.shoot(True)
            else:
                boss.shoot(False)

        if collide(boss, player):
            player.health=0


        
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

def result_component(screen, font, level,main_file="leaderboard.txt"):

    def load():
        try:
            with open(main_file, "r") as file:
                return [line.strip().split(" ", 1) for line in file.readlines()]
        except FileNotFoundError:
            return []

    def save(leaderboard):
        with open(main_file, "w") as file:
            for name, score in leaderboard:
                file.write(f"{name} {score}\n")

    def update(name, level_cleared):

        leaderboard = load()
        leaderboard.append((name, str(level_cleared)))  # Ensure level_cleared is a string
        leaderboard = sorted(
            leaderboard, key=lambda x: int(x[1]) if x[1].isdigit() else 8, reverse=True
        )[:10]
        save(leaderboard)

    def show_message(message, delay=2000):
        screen.fill((0, 0, 0))
        msg_surface = font.render(message, True, pygame.Color('yellow'))
        screen.blit(msg_surface, (WIDTH//2 - msg_surface.get_width() // 2, HEIGHT//2))
        pygame.display.update()
        pygame.time.delay(delay)

    def get_player_name():
        input_box = pygame.Rect(300, 400, 400, 50)
        color_active = pygame.Color('dodgerblue2')
        color_inactive = pygame.Color('lightskyblue3')
        color = color_inactive
        active = False
        text = ""
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    active = input_box.collidepoint(event.pos)
                    color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN and active:
                    if event.key == pygame.K_RETURN:
                        return text.strip()[:15]
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

            screen.fill((0, 0, 0))
            prompt = font.render("Enter your name:", True, pygame.Color('white'))
            screen.blit(prompt, (input_box.x, input_box.y - 40))
            pygame.draw.rect(screen, color, input_box, 2)
            text_surface = font.render(text, True, pygame.Color('white'))
            screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))
            input_box.w = max(400, text_surface.get_width() + 10)
            pygame.display.flip()
            clock.tick(30)

    def display_leaderboard():
        leaderboard = load()
        screen.fill((0, 0, 0))
        title = font.render("Top 10 Scores", True, pygame.Color('green'))
        screen.blit(title, (WIDTH//2 - title.get_width() // 2, 20))

        y_offset = 120
        for idx, (name, level) in enumerate(leaderboard):
            text = font.render(f"{idx + 1}. {name:<10} {level}", True, pygame.Color('white'))
            screen.blit(text, (200, y_offset))
            y_offset += 50

        pygame.display.update()
        pygame.time.delay(5000)

    # Main logic for result_component
    leaderboard = load()

    if len(leaderboard) < 10 or int(level) > int(leaderboard[-1][1] if leaderboard[-1][1].isdigit() else 0):
        show_message("You made it to the Top 10!")
        player_name = get_player_name()
        if player_name:
            update(player_name, level)
            show_message("Leaderboard updated!")
        else:
            show_message("Name entry canceled. Leaderboard not updated.")
    else:
        show_message("You did not qualify for the Top 10.")

    display_leaderboard()



# Add homing lasers for boss, Shield Mechanics for boss, Gravity Wells, Teleportation
main_menu()
