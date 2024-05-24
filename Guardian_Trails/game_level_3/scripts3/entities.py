import pygame
import random
import sys
import time 


start = time.perf_counter()

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.max_health = 100
        self.health = 100
        self.health_bar_height = 2
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.health_bar_width = self.size[0]
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')
        
        self.last_movement = [0, 0]
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
        
    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
        
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            

            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True

                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                 
                self.pos[1] = entity_rect.y
                
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
            
        self.last_movement = movement
        
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
            
        self.animation.update()
        
        
        
        
    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        health_ratio = self.health / self.max_health
        health_bar_length = int(self.health_bar_width * health_ratio)
        health_bar_rect = pygame.Rect(self.pos[0] - offset[0], self.pos[1] - offset[1] - self.health_bar_height-8, health_bar_length, self.health_bar_height)
        pygame.draw.rect(surf, (0, 255, 0), health_bar_rect)  # Green part of the health bar
        pygame.draw.rect(surf, (255, 0, 0), (health_bar_rect.right, health_bar_rect.y, self.health_bar_width - health_bar_length, self.health_bar_height))

        

class Animal (PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'animal', pos, size) 
        self.walking = 0

    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            
            if tilemap.solid_check((self.rect().centerx + (-40 if self.flip else 70), self.pos[1]+self.size[1] + 10)):
                
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                    self.walking = 0
                else:
                    movement = (movement[0] + (-0.5 if self.flip else  0.5), movement[1])
            else :
                self.flip = not self.flip
                self.walking = 0
            self.walking -= 1
            if self.walking==-1:
                self.walking = 0
        elif random.random() < 0.005:
            self.walking = random.randint(50, 150)
        
        super().update(tilemap, movement=movement)

        if movement[0]!=0:
            self.set_action('run')
        else:
            self.set_action('idle')
        

class Skeleton (PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'skeleton', pos, size) 
        self.walking = 0
        self.attacking = False
        self.arrow_release_time = 0
        self.attack_counter = 5
        self.attack_counter_refill = 180
        self.is_dead = False
        self.is_attack_sound_playing = False

    def update(self, tilemap, movement=(0, 0)):
        
        if self.attack_counter == 0:
            self.attack_counter_refill-=1
            if self.attack_counter_refill == 0:
                self.attack_counter = 5
                self.attack_counter_refill = 180
        if self.action == 'death' and self.animation.done:
            if self in self.game.skeletons:
                self.game.skeletons.remove(self)
            super().update(tilemap, movement=movement)
            return
        elif self.action == 'death':                
            super().update(tilemap, movement=movement)
            return 
        if abs(self.game.player.pos[1] - self.pos[1]) < 5 and abs(self.game.player.pos[0] - self.pos[0]) < 200:
            if self.game.player.pos[0] < self.pos[0]:
                self.flip = True    
            else:
                self.flip = False

            self.attacking = True
                
            alert_img = self.game.assets['alert']
            self.game.display.blit(alert_img, (self.pos[0] - self.game.scroll[0] + self.size[0] // 2 - alert_img.get_width() // 2 + 5, self.pos[1] - self.game.scroll[1] - alert_img.get_height() ))
        elif self.walking:
            if tilemap.solid_check((self.rect().centerx + (-40 if self.flip else 70), self.pos[1]+self.size[1] + 10)):
                    
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                    self.walking = 0
                else:
                    movement = (movement[0] + (-0.5 if self.flip else  0.5), movement[1])
            else :
                self.flip = not self.flip
                self.walking = 0
            self.walking -= 1
            if self.walking==-1:
                self.walking = 0
        elif random.random() < 0.01:
            self.walking = random.randint(150, 250)
        elif random.random() < 0.01:
               self.attacking = True
        
        

        
        super().update(tilemap, movement=movement)
        
        if self.attacking and self.attack_counter > 0:
            
            
                
            self.arrow_release_time += 1
            if self.arrow_release_time >= 60:
                self.arrow_release_time = 0
                self.attack_counter -= 1
                
                if self.flip :
                    self.game.arrows.append([[self.rect().centerx - 10, self.rect().centery - 3],-2,0])
                else:
                    self.game.arrows.append([[self.rect().centerx + 10, self.rect().centery - 3], 2,0])
                self.is_attack_sound_playing = False
                
            self.set_action('attack')
            if self.animation.done:
                self.set_action('idle')
                self.attacking = False
                
                self.arrow_release_time = 0
        elif movement[0]!=0:
                self.set_action('walk')
        else:
                self.set_action('idle') 

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)

        

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.attacking = False 
        self.jumping = False
        self.has_hit_enemy = False
        self.defending = False
        self.healing = False
        self.big_jump_counter = 0
        self.big_jump = False
        self.healed_animals = []
        self.is_really_healing = False
        
        
        
    
    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)
        

        if self.action == 'death' and self.animation.done:
            self.game.lost = True
            
            return
        elif self.action == 'death':
            return
        
        
        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1
        is_wall_slide = False
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            is_wall_slide = True

        
        if self.big_jump  and self.air_time <= 4:
            self.set_action('crouch')
            self.big_jump_counter =min(100,self.big_jump_counter+0.25)
            if self.big_jump_counter >= 100 :
                self.big_jump_counter = 0
                self.set_action('idle')
                self.jump(1)
                
            return 
        else:
            self.big_jump_counter = max(self.big_jump_counter-0.1,0)


        if self.healing:
            
            self.set_action('heal')
            self.velocity[0] = 0

        is_healing_animal = False

        for animal in self.game.animals:
            if self.rect().colliderect(animal.rect()) and self.healing:
                animal.health += 0.2
                is_healing_animal = True
                
                if animal.health > animal.max_health:
                    if animal not in self.healed_animals:
                        self.healed_animals.append(animal)
                        self.game.helped_animals += 1
                        
                    animal.health = animal.max_health
                else:
                    self.health+=0.1
                    self.health = min(self.health, self.max_health)
                break
        
        self.is_really_healing = is_healing_animal   
         
        if self.defending:
            
            self.set_action('defend')
            self.velocity[0] = 0
            
            
        
        for arrow in self.game.arrows: 
            if self.pos[0]>arrow[0][0]:
                off1 = 6
                off2 = 0
            else:
                off1 = 0
                off2 = 12
            wrong_side_defend = False
            if self.flip and self.pos[0] < arrow[0][0]:
                wrong_side_defend = True
            elif not self.flip and self.pos[0] > arrow[0][0]:
                wrong_side_defend = True

            if self.rect().colliderect(pygame.Rect(arrow[0][0], arrow[0][1], 20, 6)) and ((not self.defending) or wrong_side_defend) :
                self.health -= 10
                if arrow in self.game.arrows:
                    self.game.arrows.remove(arrow)
                if self.health >0:
                    self.game.sounds['player_hit'].play()
                if self.health <= 0:
                    self.game.sounds['death'].play()
                    self.set_action('death')
                    self.health = 0
                    return
                break
            elif self.rect().colliderect(pygame.Rect(arrow[0][0] - off2 , arrow[0][1],20 - off1, 6)) and self.defending and not wrong_side_defend:
                if arrow in self.game.arrows:
                    self.game.arrows.remove(arrow)
                break

        # hit the enemy
        if self.healing:
            return
        
        if self.attacking:
            if self.flip:
                off1 = 0
                off2 = 0
            else:
                off1 = 0
                off2 = 37
            player_rect = pygame.Rect(self.pos[0] - off1 , self.pos[1], self.size[0] + off2 , self.size[1])
            for skeleton in self.game.skeletons:
                if player_rect.colliderect(skeleton.rect()):
                    
                    if not self.has_hit_enemy:
                        self.has_hit_enemy = True
                        
                        skeleton.health -= 20
                        if skeleton.health <= 0:
                            if not skeleton.is_dead:
                                self.game.sounds['skeleton_death'].play()
                            skeleton.is_dead = True
                            skeleton.set_action('death')
                        break
        if self.defending:
            self.attacking = False
            return 

        if self.attacking:
            self.set_action('attack')
            if self.animation.done:
                self.attacking = False
                self.has_hit_enemy = False
            
        if is_wall_slide and not self.attacking and not self.defending:
            self.set_action('wall_slide')
        
        if (not self.wall_slide) and (not self.attacking) and (not self.defending):
            if self.air_time > 4:
                if self.velocity[1] > 0:
                    self.set_action('fall')
                else:
                    self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
                
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.3, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)
            
    def jump(self,jumptype=0):
        
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.game.sounds['jump'].play()
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.game.sounds['jump'].play()
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
                
        elif self.jumps:
            if jumptype == 0:
                self.velocity[1] = -3
            else:
                self.velocity[1] = -6
            self.game.sounds['jump'].play()
            self.jumps -= 1
            self.air_time = 5
            return True
    
    def attack(self):
        if not self.attacking:
            self.game.sounds['sword'].play()
        self.attacking = True
    
    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        health_ratio = self.health / self.max_health
        health_bar_length = int(self.health_bar_width * health_ratio)
        #print((self.pos[0] - offset[0], self.pos[1] - offset[1] - self.health_bar_height-8))
        health_bar_rect = pygame.Rect(250,30, health_bar_length*3, self.health_bar_height*3)
        pygame.draw.rect(surf, (0, 255, 0), health_bar_rect)  # Green part of the health bar
        pygame.draw.rect(surf, (255, 0, 0), (health_bar_rect.right, health_bar_rect.y, (self.health_bar_width - health_bar_length)*3, (self.health_bar_height)*3))
        if self.big_jump:
            big_jump_ratio = self.big_jump_counter/100
            jump_bar_length = int(self.health_bar_width * big_jump_ratio)
            jump_bar_rect = pygame.Rect(10,30, jump_bar_length*3, self.health_bar_height*3)
            pygame.draw.rect(surf, (0, 255, 0), jump_bar_rect)  # Green part of the health bar
            pygame.draw.rect(surf, (255, 0, 0), (jump_bar_rect.right, jump_bar_rect.y, (self.health_bar_width - jump_bar_length)*3, (self.health_bar_height)*3))

        
    def set_action(self, action):
        if action != self.action:
            if action == 'heal' and self.is_really_healing:
                self.game.sounds['heal'].play(-1)

            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()


        
    

