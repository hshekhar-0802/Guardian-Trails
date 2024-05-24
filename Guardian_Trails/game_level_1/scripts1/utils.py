
import os

import pygame

BASE_IMG_PATH = 'game_level_1/data/images/'

def load_image(path):
    #print (BASE_IMG_PATH + path)
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

def display_text(screen, text, pos, font, color=(255, 255, 255)):
    img = font.render(text, True, color)
    screen.blit(img, pos)

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
       # print (BASE_IMG_PATH + path + '/' + img_name)
        if img_name.endswith('.png') or img_name.endswith('.gif'):
            images.append(load_image(path + '/' + img_name))
    return images


class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0
        
    
    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    def update(self):
         
        
        if self.loop:

            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True
    
    def img(self):
        return self.images[int(self.frame / self.img_duration)]
  
