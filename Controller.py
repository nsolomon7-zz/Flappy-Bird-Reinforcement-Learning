import pygame, random, csv, os
from Bird import Bird
from Floor import Floor
from Pipe import Pipe
from Supervised_Player import Supervised_Player
size = [512, 768]
bg_color = (22, 150, 200)
record_data = False
computer_playing = False
play_with_pipes = True
class Controller(object):

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(size)
        self.score_text = pygame.font.SysFont('Comic Sans', 32)
        if computer_playing:
            self.computer_player = Supervised_Player('./player_data.csv')
        self.bird = Bird()
        self.floor = Floor(size[1])
        self.pipes = []
        self.lay_pipe()
        self.playing_game = True
        self.play_game()

    def play_game(self):

        collision = False
        time_since_pipe = 1
        score = 0

        if not computer_playing and record_data:
            try:
                #os.remove("./player_data.csv")
                pass
            except:
                pass
            self.data_to_write = []

        while(self.playing_game):
            if not computer_playing:
                if not record_data:
                    self.read_keyboard_input()
                else:
                    self.record_data_to_csv()
            else:
                self.read_computer_input()
            if not collision:
                self.bird.move()
                self.draw_everything(score)
            else:
                self.playing_game = False
            collision = self.check_for_collision()
            if play_with_pipes:
                self.update_pipes()
            if time_since_pipe % 62 == 0 and play_with_pipes:
                time_since_pipe = 1
                self.lay_pipe()
            pygame.display.update()
            pygame.event.pump()
            pygame.time.Clock().tick(30)
            time_since_pipe += 1
            score = self.increment_score(score)

        if record_data:
            self.record_data_to_csv()
        self.display_score()
        self.quit_game()

    def get_stimuli(self):
        #bird's y position, bird's y velocity, next pipe's center, next pipe's distance
        stimuli = [self.bird.top_left[1], self.bird.y_velocity, 300, size[0]]
        for p in self.pipes:
            if p.top_left[0] >= self.bird.top_left[0] - p.pipe_width:
                stimuli[2] = p.center
                stimuli[3] = p.top_left[0]
        return stimuli

    def record_data_to_csv(self):
        if self.playing_game:
            self.data_to_write.append([self.read_keyboard_input()] + self.get_stimuli())
        else:
            with open('player_data.csv', mode='a', newline='') as csv_file:
                d_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for d in self.data_to_write:
                    d_writer.writerow(d)


    def increment_score(self, score):
        for p in self.pipes:
            if p.top_left[0] < self.bird.top_left[0] - p.pipe_width and not p.scored:
                p.scored = True
                score += 1
        return score
    def display_score(self):
        pass
    	
    def quit_game(self):
        pygame.quit()

    def read_keyboard_input(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.bird.flap()
                    return "SPACE"
                elif event.key == pygame.K_ESCAPE:
                    self.playing_game = False
        return "NO_INPUT"

    def read_computer_input(self):
        s = [self.get_stimuli()]
        action = self.computer_player.make_decision(s)
        print(action)
        if action == "SPACE":
            self.bird.flap()

    def check_for_collision(self):
        if pygame.sprite.collide_rect(self.bird, self.floor):
            if pygame.sprite.collide_mask(self.bird, self.floor):
                print('Collision Detected!')
                return True
        for p in self.pipes:
            if p.top_left[0] < size[0]:
                if p.check_for_collision(self.bird,pixel_collision=False):
                    print('Collision Detected!')
                    return True
        return False

    def update_pipes(self):
        for p in self.pipes:
            if p.top_left[0] < -200:
                self.pipes.remove(p)
                break
        for p in self.pipes:
            p.move()

    def lay_pipe(self):
        p = Pipe(random.randint(round(256), round(size[1]-256)), size[1], size[0])
        self.pipes.append(p)

    def draw_everything(self, score):
        self.draw_background()
        self.draw_bird()
        self.draw_pipe()
        self.draw_floor()
        self.draw_score(score)

    def draw_score(self, score):
        t = self.score_text.render("%s" % score, False, (255, 255, 255))
        self.screen.blit(t, (round(size[0]/2), 100))


    def draw_bird(self):
        self.bird.draw(self.screen)

    def draw_background(self):
        self.screen.fill(bg_color)

    def draw_pipe(self):
        for p in self.pipes:
            p.draw(self.screen)

    def draw_floor(self):
        self.floor.draw(self.screen)


if __name__ == "__main__":
    Controller()