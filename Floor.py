import pygame


class Floor(pygame.sprite.Sprite):


    def __init__(self, height):
        pygame.sprite.Sprite.__init__(self)
        self.floor_image = pygame.image.load(r"./floor_image.png").convert()
        self.floor_image.set_colorkey((255, 255, 255))
        self.mask = pygame.mask.from_surface(self.floor_image)
        self.rect = self.floor_image.get_rect()
        self.top_left = [0, height - 100]
        self.rect.topleft = self.top_left


    def draw(self, screen):
        screen.blit(self.floor_image, self.top_left)