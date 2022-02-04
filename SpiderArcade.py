# Created: 30/01/2022
# By Matheus Matsumoto

import pygame
import random
import math
import sys
pygame.font.init()

# Objects:

class Player(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("sprites/spider_player.png")

        self.screen_rect = screen.get_rect()
        self.rect = self.image.get_rect()

        self.rect.centerx = self.screen_rect.centerx
        self.rect.centery = self.screen_rect.centery

        self.position_x = self.rect.centerx 
        self.position_y = self.rect.centery 

        self.move_x = 0
        self.move_y = 0
        self.speed = 2.5
        self.power = 1

        self.health = 398
        self.health_color_g = 255
        self.health_color_r = 0


class Projectile(object):

    def __init__(self,x,y,radius,color, aim_x, aim_y):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vel = 8
        self.aim_x = aim_x
        self.aim_y = aim_y

        self.angle = math.atan2(-(aim_x - x), (aim_y - y)) + 1.52
    
    def draw(self,win):
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)


class SmallEnemy(pygame.sprite.Sprite):
    
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("sprites/small_enemy.png") 

        self.screen_rect = screen.get_rect()
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.health = 2
        self.vel = 0.75

class Boss_1(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("sprites/boss_1.png")

        self.rect = self.image.get_rect()

        self.x = 448
        self.y = -200

        self.health = 90


# Setup:

pygame.init()
main = True
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1024, 768))
pygame.display.set_caption("Spider Arcade")
icon = pygame.image.load("sprites/spider.png")
pygame.display.set_icon(icon)
background = pygame.image.load("sprites/background.jpg")
player_hud = pygame.image.load("sprites/player_hud.png")
main_font = pygame.font.SysFont("comicsans", 30)
smaller_main_font = pygame.font.SysFont("comicsans", 25)
tiny_font = pygame.font.SysFont("comicsans", 15)
boss_icon = pygame.image.load("sprites/boss_icon.png")
boss_bar = pygame.image.load("sprites/boss_bar.png")
reload_bar = pygame.image.load("sprites/reload_bar.png")
gameover_bar = pygame.image.load("sprites/game_over_bar.png")
controls_square = pygame.image.load("sprites/controls.png")
win_bar = pygame.image.load("sprites/win_bar.png")

correction_angle = 90
num_wave = 0
ammo = 8
ammo_max = ammo
player_bullets = []
enemy_bullets = []
small_enemies = []
num_small_enemies = len(small_enemies)
boss_level = False
moving_up = False
moving_down = False
moving_left = False
moving_right = False

player = Player()
first_boss = Boss_1()

# Functions


def generate_small_enemies():
    for i in range(num_small_enemies):
        random_x = random.randrange(-64,1056)
        if random_x >= 0 and random_x <= 1024 and random_x % 2 == 1:
            random_y = -64
        elif random_x >= 0 and random_x <= 1024 and random_x % 2 == 0:
            random_y = 832
        elif random_x < 0 or random_x > 1024:
            random_y = random.randrange(-64, 832)
        small_enemies.append(SmallEnemy(random_x, random_y))

def reset_player_stats():
    player.health = 398
    player.power = 1
    player.speed = 2.5
    player.health_color_g = 255
    player.health_color_r = 0
    player.position_x = screen.get_rect().centerx
    player.position_y = screen.get_rect().centery


# Main Loop:

while main:

    ammo_label = smaller_main_font.render(f"AMMO: {ammo} / {ammo_max}", 1, (0, 0, 0))
    wave_label = smaller_main_font.render(f"WAVE: {num_wave}", 1, (0, 0, 0))
    health_label = smaller_main_font.render(f"HEALTH: ", 1, (0, 0, 0))
    gameover_label = main_font.render(f"GAME OVER", 1, (0, 0, 0))
    reload_label = tiny_font.render(f"RELOAD : R", 1, (0, 0, 0))

    clock.tick(60)

    screen.blit(background, (0,0))

    # Show controls box
    if num_wave < 2:
        screen.blit(controls_square, (10, 150))

    # First 9 waves
    if len(small_enemies) == 0 and num_wave < 9:
        num_small_enemies += 1
        num_wave += 1
        generate_small_enemies()
    

    # First boss --------------------------------------------------------------------------------------------------------------
    if len(small_enemies) == 0 and num_wave == 9:
        boss_level = True

        # Entrance
        entrance = True
        if first_boss.y <= 100 and len(small_enemies) == 0:
            first_boss.y += 1
            if first_boss.y == 100:
                entrance = False
        
        # Movement
        if first_boss.x == 448 and first_boss.y == 100:
            moving_right = True
        
        if first_boss.x == 808 and first_boss.y >= 100:
            moving_down = True
            moving_right = False

        if first_boss.x == 808 and first_boss.y >= 460:
            moving_down = False
            moving_left = True
        
        if first_boss.x == 216 and first_boss.y >= 460:
            moving_left = False
            moving_up = True
        
        if first_boss.x == 216 and first_boss.y == 100:
            moving_right = True
            moving_up = False
        
        if moving_up:
            first_boss.y -= 2
        
        if moving_down:
            first_boss.y += 2
        
        if moving_right:
            first_boss.x += 2
        
        if moving_left:
            first_boss.x -= 2
        
        # Touching player
        if first_boss.x <= player.position_x and first_boss.x >= player.position_x - 64 and first_boss.y <= player.position_y and first_boss.y >= player.position_y - 64:
            player.health -= 5
        
        # Shooting bullets
        start_time = pygame.time.get_ticks()
        if start_time%600 >= 0 and start_time%600 < 25:

            # up
            enemy_bullets.append(Projectile(first_boss.x+64, 
                                            first_boss.y,
                                            10, (250,0,0),
                                            first_boss.x+64,
                                            first_boss.y-64))
            
            # down
            enemy_bullets.append(Projectile(first_boss.x+64, 
                                            first_boss.y+110,
                                            10, (250,0,0),
                                            first_boss.x+64,
                                            first_boss.y+200))
            
            # right
            enemy_bullets.append(Projectile(first_boss.x+110, 
                                            first_boss.y+64,
                                            10, (250,0,0),
                                            first_boss.x+120,
                                            first_boss.y+65))
            
            # left 
            enemy_bullets.append(Projectile(first_boss.x, 
                                            first_boss.y+64,
                                            10, (250,0,0),
                                            first_boss.x-64,
                                            first_boss.y+64))

            # top right
            enemy_bullets.append(Projectile(first_boss.x+128, 
                                            first_boss.y,
                                            10, (250,0,0),
                                            first_boss.x+190,
                                            first_boss.y-64))
            
            # top left
            enemy_bullets.append(Projectile(first_boss.x, 
                                            first_boss.y,
                                            10, (250,0,0),
                                            first_boss.x-64,
                                            first_boss.y-64))
            
            # bottom right
            enemy_bullets.append(Projectile(first_boss.x+128, 
                                            first_boss.y+128,
                                            10, (250,0,0),
                                            first_boss.x+180,
                                            first_boss.y+180))
            
            # bottom left
            enemy_bullets.append(Projectile(first_boss.x, 
                                            first_boss.y+128,
                                            8, (250,0,0),
                                            first_boss.x-64,
                                            first_boss.y+190))

        # Boss death
        if first_boss.health <= 0:
            num_wave += 1
            boss_level = False
            moving_right, moving_left, moving_down, moving_up = False, False, False, False
            screen.blit(win_bar, (384,352))
            pygame.display.update()
            pygame.time.wait(5000)
            pygame.quit()
            main = False

        screen.blit(first_boss.image, (first_boss.x, first_boss.y))
    
    # -------------------------------------------------------------------------------------------------------------------------
        

    # Commands ----------------------------------------------------------------------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            try:
                sys.exit()
            finally:
                main = False

        # Commands to move
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                player.move_x = -player.speed
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                player.move_x = player.speed
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                player.move_y = -player.speed
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                player.move_y = player.speed
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                player.move_x = 0
            elif event.key == pygame.K_UP or event.key == pygame.K_w or event.key == pygame.K_DOWN or event.key == pygame.K_s:
                player.move_y = 0

        # Command to shoot
        if event.type == pygame.MOUSEBUTTONDOWN:
            if len(player_bullets) < ammo_max and ammo != 0:
                aim_x, aim_y = pygame.mouse.get_pos()
                player_bullets.append(Projectile(player.position_x, player.position_y, 5, (255,255,255), aim_x, aim_y))
                ammo -= 1
        
        # Command to reload
        if event.type == pygame.KEYDOWN and ammo < ammo_max:
            if event.key == pygame.K_r:
                 ammo = ammo_max
    
    # -------------------------------------------------------------------------------------------------------------------------    
    
    # Mouse positioning
    mouse_x, mouse_y = pygame.mouse.get_pos()
    d_x, d_y = mouse_x - player.position_x, mouse_y - player.position_y
    angle = math.degrees(math.atan2(-d_y, d_x)) - correction_angle

    # Player position changes according to movement
    player.position_x += player.move_x
    player.position_y += player.move_y

    # Boundaries
    if player.position_x > 1000:
        player.position_x = 1000
    
    if player.position_x < 24:
        player.position_x = 24
    
    if player.position_y > 744:
        player.position_y = 744
    
    if player.position_y < 24:
        player.position_y = 24

    # Player rotation according to mouse positioning
    rot_image = pygame.transform.rotate(player.image, angle)
    rot_image_rect = rot_image.get_rect(center = (player.position_x, player.position_y))


    # Player bullets ----------------------------------------------------------------------------------------------------------

    # Bullet boundaries
    for bullet in player_bullets:
        if bullet.x < 1024 and bullet.x > 0 and bullet.y < 768 and bullet.y > 0:
            bullet.x += math.cos(bullet.angle)*bullet.vel
            bullet.y += math.sin(bullet.angle)*bullet.vel
            bullet.draw(screen)
            
        else:
            player_bullets.pop(player_bullets.index(bullet))
        
        # Hitting small enemies
        for enemy in small_enemies:
            if bullet.x >= enemy.x and bullet.x <= enemy.x + 64 and bullet.y >= enemy.y and bullet.y <=  enemy.y + 64:
                enemy.health -= player.power
                if enemy.health == 0:
                    small_enemies.pop(small_enemies.index(enemy))
                player_bullets.remove(bullet)
        
        # Hitting boss
        if bullet.x >= first_boss.x and bullet.x <= first_boss.x + 128 and bullet.y >= first_boss.y and bullet.y <=  first_boss.y + 128:
            first_boss.health -= player.power
            player_bullets.remove(bullet)

    # -------------------------------------------------------------------------------------------------------------------------
    

    # Boss bullets: -----------------------------------------------------------------------------------------------------------
    
    # Bullet boundaries
    for b_bullet in enemy_bullets:
        if b_bullet.x < 1024 and b_bullet.x > 0 and b_bullet.y < 768 and b_bullet.y > 0:
            b_bullet.x += math.cos(b_bullet.angle)*b_bullet.vel
            b_bullet.y += math.sin(b_bullet.angle)*b_bullet.vel
            b_bullet.draw(screen)
        
        else:
            enemy_bullets.pop(enemy_bullets.index(b_bullet))
        
        # Hitting player
        if b_bullet.x >= player.position_x and b_bullet.x <= player.position_x+64 and b_bullet.y >= player.position_y and b_bullet.y <= player.position_y + 64:
            player.health -= 5
        
        if player.health <= 0:
            enemy_bullets.clear()
    
    # -------------------------------------------------------------------------------------------------------------------------
    

    # Small enemies -----------------------------------------------------------------------------------------------------------
    for e1 in range(len(small_enemies)):
        
        # Chase player
        if small_enemies[e1].x - player.position_x+32 > 0:
            small_enemies[e1].x -= small_enemies[e1].vel
        else:
            small_enemies[e1].x += small_enemies[e1].vel
        
        if small_enemies[e1].y - player.position_y+32 > 0:
            small_enemies[e1].y -= small_enemies[e1].vel
        else:
            small_enemies[e1].y += small_enemies[e1].vel
        
        # Do not overlap
        for e2 in range(len(small_enemies)):
            if e1 != e2:
                d_enemiesx, d_enemiesy = small_enemies[e1].x - small_enemies[e2].x, small_enemies[e1].y - small_enemies[e2].y
                
                if max(d_enemiesx, -d_enemiesx) < 80 and max(d_enemiesy, -d_enemiesy) < 80:

                    if small_enemies[e1].y >= small_enemies[e2].y and player.position_y >= small_enemies[e1].y:
                        small_enemies[e2].vel = -1.25
                        small_enemies[e1].vel = 1.25

                    if small_enemies[e1].y >= small_enemies[e2].y and player.position_y < small_enemies[e1].y:
                        small_enemies[e2].vel = 1.25
                        small_enemies[e1].vel = -1.25
                    
                    if small_enemies[e1].y < small_enemies[e2].y and player.position_y >= small_enemies[e1].y:
                        small_enemies[e2].vel = 1.25
                        small_enemies[e1].vel = -1.25

                    if small_enemies[e1].y < small_enemies[e2].y and player.position_y < small_enemies[e1].y:
                        small_enemies[e2].vel = -1.25
                        small_enemies[e1].vel = 1.25
                    
                    if small_enemies[e1].x >= small_enemies[e2].x and player.position_x >= small_enemies[e1].x:
                        small_enemies[e2].vel = -1.25
                        small_enemies[e1].vel = 1.25
                    
                    if small_enemies[e1].x >= small_enemies[e2].x and player.position_x < small_enemies[e1].x:
                        small_enemies[e2].vel = 1.25
                        small_enemies[e1].vel = -1.25
                    
                    if small_enemies[e1].x < small_enemies[e2].x and player.position_x >= small_enemies[e1].x:
                        small_enemies[e2].vel = 1.25
                        small_enemies[e1].vel = -1.25
                    
                    if small_enemies[e1].x < small_enemies[e2].x and player.position_x < small_enemies[e1].x:
                        small_enemies[e2].vel = -1.25
                        small_enemies[e1].vel = 1.25
                    
                else:
                    small_enemies[e1].vel = 0.75
        
        # Hitting player
        if small_enemies[e1].x <= player.position_x and small_enemies[e1].x >= player.position_x - 64 and small_enemies[e1].y <= player.position_y and small_enemies[e1].y >= player.position_y - 64:
            player.health -= 1
            if player.health_color_g > 0 and player.health_color_r < 255:
                player.health_color_g -= 1
                player.health_color_r += 1
                
        screen.blit(small_enemies[e1].image, (small_enemies[e1].x, small_enemies[e1].y))
        if small_enemies[e1].health > 0: 
            pygame.draw.rect(screen, (255, 0, 0), (small_enemies[e1].x, small_enemies[e1].y+5, small_enemies[e1].health*32, 4))
    
    # -------------------------------------------------------------------------------------------------------------------------

    # Shows the rotating image of the player
    screen.blit(rot_image, rot_image_rect.topleft)

    # Shows reload text
    if ammo == 0:
        screen.blit(reload_bar, (player.position_x-48, player.position_y-70))
        screen.blit(reload_label, (player.position_x-42, player.position_y-70))
    
    # Player's health goes to 0
    if player.health <= 0:
        screen.blit(gameover_bar, (384, 352))
        pygame.display.update()
        pygame.time.wait(5000)
        reset_player_stats()
        ammo = 8
        ammo_max = ammo
        num_wave = 0
        num_small_enemies = 0
        small_enemies.clear()
        boss_level = False
        first_boss.health = 90
        first_boss.x = 448
        first_boss.y = -200
        moving_down, moving_left, moving_up, moving_right = False, False, False, False

    # HUD ---------------------------------------------------------------------------------------------------------------------
    screen.blit(player_hud, (10, 10))
    pygame.draw.rect(screen, (player.health_color_r, player.health_color_g, 0), (135, 87, player.health/3, 15))
    screen.blit(ammo_label, (20, 45))
    screen.blit(wave_label, (20, 15))
    screen.blit(health_label, (20, 75))

    # Boss health bar
    if boss_level == True and num_wave == 9:
        screen.blit(boss_icon, (224, 694))
        screen.blit(boss_bar, (288, 694))
        if len(small_enemies) == 0 and num_wave == 9:
            pygame.draw.rect(screen, (255, 0, 0), (298, 710, first_boss.health*5.42, 32))
    pygame.display.update()
    # -------------------------------------------------------------------------------------------------------------------------
