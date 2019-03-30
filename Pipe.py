import pygame


class Pipe(pygame.sprite.Sprite):

    pipe_width = 128

    def __init__(self, center, height, width):
        pygame.sprite.Sprite.__init__(self)

        self.center = center
        self.gap = 150
        self.scored = False
        ubody_height = self.center - round(self.gap/2) - 32
        lbody_height = height - self.center - round(self.gap/2) - 32


        self.ubody_image = pygame.image.load(r"./pipe_body_image.png").convert()
        self.ubody_image = pygame.transform.scale(self.ubody_image, (self.pipe_width, ubody_height))
        self.lbody_image = pygame.image.load(r"./pipe_body_image.png").convert()
        self.lbody_image = pygame.transform.scale(self.lbody_image, (self.pipe_width, lbody_height))

        self.uhead_image = pygame.image.load(r"./pipe_head_image.png").convert()
        self.lhead_image = pygame.image.load(r"./pipe_head_image.png").convert()

        self.ubody_image.set_colorkey((255, 255, 255))
        self.lbody_image.set_colorkey((255, 255, 255))
        self.uhead_image.set_colorkey((255, 255, 255))
        self.lhead_image.set_colorkey((255, 255, 255))

        self.ubody_mask = pygame.mask.from_surface(self.ubody_image)
        self.lbody_mask = pygame.mask.from_surface(self.lbody_image)
        self.uhead_mask = pygame.mask.from_surface(self.uhead_image)
        self.lhead_mask = pygame.mask.from_surface(self.lhead_image)

        self.rect = self.ubody_image.get_rect()
        self.mask = self.ubody_mask
        self.x_velocity = -8
        self.top_left = [width+100, 0]

    def check_for_collision(self, bird):
        x = self.top_left[0]
        y = self.top_left[1]
        self.rect = self.ubody_image.get_rect()
        self.rect.topleft = self.top_left
        self.mask = self.ubody_mask
        if pygame.sprite.collide_rect(bird, self):
            if pygame.sprite.collide_mask(bird, self):
                print('Collision Detected!')
                return True

        self.top_left[1] = self.center + round(self.gap/2) + 32
        self.rect = self.lbody_image.get_rect()
        self.rect.topleft = self.top_left
        self.mask = self.lbody_mask
        if pygame.sprite.collide_rect(bird, self):
            if pygame.sprite.collide_mask(bird, self):
                print('Collision Detected!')
                return True

        self.top_left[0] = x - 16
        self.top_left[1] = self.center - round(self.gap/2) - 32
        self.rect = self.uhead_image.get_rect()
        self.rect.topleft = self.top_left
        self.mask = self.uhead_mask
        if pygame.sprite.collide_rect(bird, self):
            if pygame.sprite.collide_mask(bird, self):
                print('Collision Detected!')
                return True

        self.top_left[1] = self.center + round(self.gap/2)
        self.rect = self.lhead_image.get_rect()
        self.rect.topleft = self.top_left
        self.mask = self.lhead_mask
        if pygame.sprite.collide_rect(bird, self):
            if pygame.sprite.collide_mask(bird, self):
                print('Collision Detected!')
                return True
        self.top_left[0] = x
        self.top_left[1] = y
        return False

    def move(self):
        self.top_left[0] += self.x_velocity
        self.rect.topleft = self.top_left

    def draw(self, screen):
        x = self.top_left[0]
        y = self.top_left[1]
        screen.blit(self.ubody_image, self.top_left)

        self.top_left[1] = self.center + round(self.gap/2) + 32
        screen.blit(self.lbody_image, self.top_left)

        self.top_left[0] = x - 16
        self.top_left[1] = self.center - round(self.gap/2) - 32
        screen.blit(self.uhead_image, self.top_left)

        self.top_left[1] = self.center + round(self.gap/2)
        screen.blit(self.lhead_image, self.top_left)
        self.top_left[0] = x
        self.top_left[1] = y