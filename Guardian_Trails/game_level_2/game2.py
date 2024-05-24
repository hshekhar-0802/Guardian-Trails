
import sys
import math
import random

import pygame
from pyvidplayer2 import Video
from game_level_2.scripts2.utils import load_image, load_images, Animation, display_text
from game_level_2.scripts2.entities import PhysicsEntity, Player, Animal, Skeleton
from game_level_2.scripts2.tilemap import Tilemap
from game_level_2.scripts2.clouds import Clouds
from game_level_2.scripts2.particle import Particle


GREEN = (0, 255, 0)
RED = (255, 0, 0)


class Game:
    
    def __init__(self):
        pygame.init()
        
        pygame.display.set_caption('rainforest')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()
        
        self.movement = [False, False]
        
        

        self.sounds = {
            'bgm': pygame.mixer.Sound('game_level_2/data/audios/rainforest.mp3'),
            'sword': pygame.mixer.Sound('game_level_2/data/audios/not_level_specific/attack.wav'),
            'run': pygame.mixer.Sound('game_level_2/data/audios/not_level_specific/running.mp3'),
            'jump': pygame.mixer.Sound('game_level_2/data/audios/not_level_specific/jump.mp3'),
            'death': pygame.mixer.Sound('game_level_2/data/audios/not_level_specific/death.mp3'),
            'skeleton_death': pygame.mixer.Sound('game_level_2/data/audios/not_level_specific/skeleton_death.mp3'),
            'skeleton_attack': pygame.mixer.Sound('game_level_2/data/audios/not_level_specific/skeleton_attack.mp3'),
            'defend': pygame.mixer.Sound('game_level_2/data/audios/not_level_specific/defend.mp3'),
            'heal': pygame.mixer.Sound('game_level_2/data/audios/not_level_specific/heal.mp3'),
            'hit': pygame.mixer.Sound('game_level_2/data/audios/not_level_specific/hit.mp3'),
            'skeleton_running': pygame.mixer.Sound('game_level_2/data/audios/not_level_specific/skeleton_running.mp3'),
            'player_hit': pygame.mixer.Sound('game_level_2/data/audios/not_level_specific/player_hit.mp3'),

        }
        self.sounds['bgm'].set_volume(0.1)
        self.sounds['run'].set_volume(0.5)
        self.sounds['jump'].set_volume(0.6)
        self.sounds['death'].set_volume(1.0)
        self.sounds['skeleton_death'].set_volume(0.5)
        self.sounds['skeleton_attack'].set_volume(0.5)
        self.sounds['defend'].set_volume(0.3)
        self.sounds['heal'].set_volume(0.5)
        self.sounds['sword'].set_volume(0.3)
        self.sounds['hit'].set_volume(0.2)
        self.sounds['skeleton_running'].set_volume(1.0)
        self.sounds['player_hit'].set_volume(0.2)

        self.assets = {
            'level_complete':Video('game_level_2/data/level_complete_scene.mp4'),
            'level_lost': Video('game_level_2/data/level_lost_scene.mp4'),
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'background': load_images('background'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=5),
            'player/run': Animation(load_images('entities/player/run'),img_dur=5),
            'player/attack': Animation(load_images('entities/player/attack'),img_dur=6, loop=False),
            'player/fall': Animation(load_images('entities/player/fall'), img_dur=5),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/death': Animation(load_images('entities/player/death'), img_dur=5, loop=False),
            'player/defend': Animation(load_images('entities/player/defend')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/heal': Animation(load_images('entities/player/heal'), img_dur=5),
            'player/crouch': Animation(load_images('entities/player/crouch')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'animal/idle': Animation(load_images('entities/animal/deer/idle'), img_dur=5),
            'animal/run': Animation(load_images('entities/animal/deer/run'), img_dur=5),
            'skeleton/walk': Animation(load_images('entities/enemies/skeleton/walk'), img_dur=5),
            'skeleton/idle': Animation(load_images('entities/enemies/skeleton/idle'), img_dur=10),
            'skeleton/attack': Animation(load_images('entities/enemies/skeleton/attack'), img_dur=7, loop=False),
            'skeleton/arrow': load_image('entities/enemies/skeleton/arrow.png') ,
            'skeleton/death': Animation(load_images('entities/enemies/skeleton/death'), img_dur=5, loop=False),
            'alert': load_image('entities/enemies/skeleton/alert.png'),
            


        }
        
        
        
        
        self.player = Player(self, (100, 50), (17, 33))
        
        self.tilemap = Tilemap(self, tile_size=32)
        self.tilemap.load('game_level_2/data/mapnew.json')
        
        self.leaf_spawners = []
        #for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
        #    self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
        self.animals = []
        self.max_animals = 0
        self.max_skeletons = 0
        self.skeletons = []  
        for spawner in self.tilemap.extract([('spawners', 0),('spawners',2),('spawners',1)]):
            if spawner['variant']==0:
                self.player.pos = spawner['pos']
            elif spawner['variant']==2:
                self.animals.append(Animal(self, spawner['pos'], (40, 25)))
            else:
                self.skeletons.append(Skeleton(self, spawner['pos'], (28, 33)))

        self.max_animals = len(self.animals)
        self.max_skeletons = len(self.skeletons)
        self.particles = []
        self.arrows = []
        self.scroll = [0, 0]
        self.helped_animals = 0
        self.myfont = pygame.font.SysFont('Comic Sans MS', 35, bold=True)
        self.lost = False
        self.win = False
        self.is_running_sound_playing = False
        self.skeleton_sounds = {}
        for skeleton in self.skeletons:
            self.skeleton_sounds[skeleton] = False


        
    def run(self):
        ans = escape()
        if ans == 1:
            return 
        self.sounds['bgm'].play(-1)
        while True:
            if len(self.animals)<6:
                self.lost = True
            #if player falls out of screen then player dies
            if self.player.rect().y > 1000:
                self.lost = True    
                
            
            if len(self.skeletons) == 0 and not self.lost:
                self.win = True
                
                

            if self.lost:
                while(self.assets['level_lost'].active):
                    (self.assets['level_lost']).draw(self.screen,(0,0))
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                    pygame.display.update()
                
                self.sounds['bgm'].stop()
                return 
            if self.win:
                while(self.assets['level_complete'].active):
                    (self.assets['level_complete']).draw(self.screen,(0,0))
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            
                    pygame.display.update()
                
                self.sounds['bgm'].stop()
                return

            


            self.draw_background_with_parallax()
            
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))
            
            
            
            self.tilemap.render(self.display, offset=render_scroll)
            for animal in self.animals:
                animal.update(self.tilemap, (0, 0))
                animal.render(self.display, offset=render_scroll)
            for skeleton in self.skeletons:
                skeleton.update(self.tilemap, (0, 0))
                skeleton.render(self.display, offset=render_scroll)

            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)
            
            for arrow in self.arrows.copy():
                arrow[0][0]+=arrow[1]
                arrow[2]+=1
                arrow_img = self.assets['skeleton/arrow']
                self.display.blit(arrow_img,(arrow[0][0] - arrow_img.get_width() // 2 - render_scroll[0], arrow[0][1] - arrow_img.get_height() // 2 - render_scroll[1]))
                if self.tilemap.solid_check(arrow[0]) :
                    if arrow in self.arrows:
                        self.arrows.remove(arrow)
                elif arrow[2]>360:
                    if arrow in self.arrows:
                        self.arrows.remove(arrow)
                    

                
                for animal in self.animals:
                    if animal.rect().colliderect(pygame.Rect(arrow[0][0] - 5, arrow[0][1] - 5, 10, 10)):
                        #if animal is within player's view play hit sound 
                        if abs(self.player.rect().centerx - animal.rect().centerx)<150:
                            self.sounds['hit'].play(0)
                        
                            
                        animal.health -= 10
                        if arrow in self.arrows:
                            self.arrows.remove(arrow)
                        if animal.health<=0:
                            if animal in self.animals:
                                self.animals.remove(animal)
                
                
            
            
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.player.attack()
                        
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_SPACE:
                        self.player.jump(0)
                    if event.key == pygame.K_d:
                        self.sounds['defend'].play()
                        self.player.defending = True
                    if event.key == pygame.K_h:
                        self.sounds['heal'].play(-1)
                        self.player.healing = True
                    if event.key == pygame.K_j :
                        self.player.big_jump = True
                    if event.key == pygame.K_ESCAPE:
                        self.sounds['bgm'].stop()   
                        ans = escape()
                        if ans == 1:
                            return 
                        self.sounds['bgm'].play(-1)
                        
                    
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        
                        self.movement[1] = False
                    if event.key == pygame.K_d:
                        self.player.defending = False
                    if event.key == pygame.K_h:
                        self.sounds['heal'].stop()
                        self.player.healing = False
                    if event.key == pygame.K_j:
                        self.player.big_jump = False
         
            if self.player.last_movement[0]!=0 and self.player.air_time<5 and not self.is_running_sound_playing:
                self.sounds['run'].play(-1)
                
                self.is_running_sound_playing = True
            else:
                if self.player.last_movement[0]==0 or self.player.air_time>=5:
                    self.sounds['run'].stop()
                    self.is_running_sound_playing = False


            for skeleton in self.skeletons:
                if abs(self.player.rect().centerx - skeleton.rect().centerx)<150:
                    if not self.skeleton_sounds[skeleton] and skeleton.last_movement[0]!=0:
                        self.sounds['skeleton_running'].play(-1)
                        self.skeleton_sounds[skeleton] = True
                    elif skeleton.last_movement[0]==0:
                        self.sounds['skeleton_running'].stop()
                        self.skeleton_sounds[skeleton] = False
                


            enemy_logo=pygame.image.load('game_level_2/data/images/logo/enemy.png')
            animal_logo=pygame.image.load('game_level_2/data/images/logo/animal.png')
            heal_logo=pygame.image.load('game_level_2/data/images/logo/heal.png')
            animals_label=self.myfont.render(':' + str(len(self.animals)) + '/'+ str(self.max_animals),True,(255,255,255))
            skeletons_label=self.myfont.render(':' + str(len(self.skeletons)) + '/'+ str(self.max_skeletons),True,(255,255,255))
            helped_animals_label=self.myfont.render(':' + str(self.helped_animals) + '/' + str(self.max_animals),True,(255,255,255))
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            self.screen.blit(animals_label,(50,1))
            self.screen.blit(skeletons_label,(405,1))
            self.screen.blit(helped_animals_label,(740,1))
            self.screen.blit(enemy_logo,(380,10))
            self.screen.blit(animal_logo,(0,10))
            self.screen.blit(heal_logo,(710,10))
            pygame.display.update()
            self.clock.tick(60)

    def draw_background_with_parallax(self):
        bg_width = self.assets['background'][0].get_width()
        for x in range(0,20):
            speed = 0.2
            counter = 0
            for img in self.assets['background']:
                self.display.blit(img, (x*bg_width - (self.scroll[0]+67.99914951943938)*speed, counter))
                counter+=20
                speed+=0.1


def escape():
    img = pygame.image.load('game_level_2/data/escape.png')
    screen = pygame.display.set_mode((1092, 720))
    escape_audio = pygame.mixer.Sound('audios/mystery.mp3')
    escape_audio.set_volume(0.1)
    screen.blit(img, (0, 0))
    while True:
        pygame.display.update()
        escape_audio.play()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    escape_audio.stop()
                    return 0
                if event.key == pygame.K_RETURN:
                    escape_audio.stop()
                    return 1


            

