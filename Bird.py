import pygame


class Bird(pygame.sprite.Sprite):


    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.bird_image = pygame.image.load(r"./bird_image2.png").convert()
        self.bird_image.set_colorkey((255, 255, 255))
        self.mask = pygame.mask.from_surface(self.bird_image)
        self.rect = self.bird_image.get_rect()
        self.top_left = [100, 100]
        self.rect.topleft = self.top_left
        self.y_velocity = .1
        self.acceleration = 3
        self.max_speed = -20

    def flap(self):
        self.y_velocity = self.max_speed

    def move(self):
        self.top_left[1] += self.y_velocity
        self.y_velocity += self.acceleration
        self.rect.topleft = self.top_left

    def draw(self, screen):
        screen.blit(self.bird_image, self.top_left)