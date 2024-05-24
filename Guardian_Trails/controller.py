from pyvidplayer2 import Video
import pygame
import os
from button import Button
from game_level_1 import scripts1,game
from game_level_2 import game2, scripts2
from game_level_3 import game3, scripts3
import sys


pygame.init()
WIDTH = 1092
HEIGHT = 720
FPS = 60



opening_scene = Video('videos/opening_scene.mp4')
#opening_scene.play()


def ultimate():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    while True:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                opening_scene.close()
                main_menu()
                return
            
        opening_scene.draw(screen, (0, 0))
        pygame.display.update()
        pygame.time.Clock().tick(FPS)

def main_menu():
    screen_width = 1092
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Menu")  

    background = pygame.image.load(os.path.join('data','main_menu','images', 'background.jpeg'))
    background = pygame.transform.scale(background, (screen_width, screen_height))

    #load logo image
    logo = pygame.image.load(os.path.join('data','main_menu','images', 'logo.png'))
    logo = pygame.transform.scale(logo, (int(logo.get_width()*0.35), int(logo.get_height()*0.35)))

    move_audio = pygame.mixer.Sound(os.path.join('data','main_menu', 'audio', 'move.wav'))
    select_audio = pygame.mixer.Sound(os.path.join('data','main_menu', 'audio', 'select.wav'))
    move_audio.set_volume(0.2)
    select_audio.set_volume(0.2)

    button_images = []
    button_images.append(pygame.image.load(os.path.join('data', 'button_images', 'rainforest1.png')))
    button_images.append(pygame.image.load(os.path.join('data', 'button_images', 'desert1.png')))
    button_images.append(pygame.image.load(os.path.join('data', 'button_images', 'snow1.png')))
    button_images.append(pygame.image.load(os.path.join('data', 'button_images', 'quit1.png')))
    

    button_images_selected = []

    button_images_selected.append(pygame.image.load(os.path.join('data', 'button_images', 'rainforest2.png')))
    button_images_selected.append(pygame.image.load(os.path.join('data', 'button_images', 'desert2.png')))
    button_images_selected.append(pygame.image.load(os.path.join('data', 'button_images', 'snow2.png')))
    button_images_selected.append(pygame.image.load(os.path.join('data', 'button_images', 'quit2.png')))
    button_scale = 0.5

    adjustments = [50, 32,67,23]
    button_texts = ["Rainforest","Desert","Snowy Mountains", "Quit"]
    buttons = [] 
    for i in range(4):
        button = Button(screen_width/2 - button_images[i].get_width()*button_scale/2 - adjustments[i], screen_height/2 + i*100 - 60 , button_images[i], button_scale, button_texts[i])
        buttons.append(button)

    #initialize font
    font = pygame.font.Font(None, 36)
    main_menu_audio = pygame.mixer.Sound(os.path.join('audios','main_menu.mp3'))
    main_menu_audio.set_volume(0.1)
    #initialize variables
    selected = 0
    running = True

    #main loop
    while running:
        screen.blit(background, (0, 0))
        screen.blit(logo, (screen_width/2 - logo.get_width()/2 + 2, 0))
        
        main_menu_audio.play()

        #display buttons
        for i in range(4):
            if i == selected:
                buttons[i].image = button_images_selected[i]
            else:
                buttons[i].image = button_images[i]
            buttons[i].draw(screen)
        
        pygame.display.flip()

        #event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    move_audio.play()
                    selected = (selected - 1) % 4
                if event.key == pygame.K_DOWN:
                    move_audio.play()
                    selected = (selected + 1) % 4
                if event.key == pygame.K_RETURN:
                    select_audio.play()
                    if selected == 0:
                        main_menu_audio.stop()
                        run_game_1()
                        main_menu_audio.play()
                        
                    
                    elif selected == 1:
                        main_menu_audio.stop()
                        run_game_2()
                        main_menu_audio.play()
                        
                    elif selected == 2:
                        main_menu_audio.stop()
                        run_game_3()
                        main_menu_audio.play()
                    else:
                        pygame.quit()
                        sys.exit()

def run_game_1():
    mission_scene = Video('videos/mission1.mp4')
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    running = True
    while mission_scene.active and running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                running = False
                
        if not running:
            mission_scene.close()
            break 
        else:   
            mission_scene.draw(screen, (0, 0))
            pygame.display.update()
            pygame.time.Clock().tick(FPS)
    game.Game().run()


def run_game_2():
    mission_scene = Video('videos/mission2.mp4')
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    running = True
    while mission_scene.active and running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                running = False
                
        if not running:
            mission_scene.close()
            break 
        else:   
            mission_scene.draw(screen, (0, 0))
            pygame.display.update()
            pygame.time.Clock().tick(FPS)
    game2.Game().run()


def run_game_3():
    mission_scene = Video('videos/mission3.mp4')
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    running = True
    while mission_scene.active and running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                running = False
                
        if not running:
            mission_scene.close()
            break 
        else:   
            mission_scene.draw(screen, (0, 0))
            pygame.display.update()
            pygame.time.Clock().tick(FPS)
    game3.Game().run()
    
ultimate()


            

        