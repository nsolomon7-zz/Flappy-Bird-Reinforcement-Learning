import pygame, random, csv, os
from Bird import Bird
from Floor import Floor
from Pipe import Pipe
from Neat_O_Player import Neat_O_Player
import numpy as np
size = [512, 768]
bg_color = (22, 150, 200)
computer_playing = True
play_with_pipes = True


class Controller(object):

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(size)
        self.score_text = pygame.font.SysFont('Comic Sans', 32)
        self.birds = []
        self.networks = []
        if computer_playing:
            self.computer_player = Neat_O_Player()
            for i in range(self.computer_player.num_per_gen):
                self.birds.append(Bird())
            self.networks = self.computer_player.increment_gen()
            self.scores = [0]*self.computer_player.num_per_gen
        else:
            self.birds = [Bird()]
        self.num_alive = len(self.birds)
        self.frame_score = 0
        self.floor = Floor(size[1])
        self.pipes = []
        self.lay_pipe()
        self.playing_game = True
        self.play_game()

    def play_game(self):

        time_since_pipe = 1
        score = 0
        collisions = [False] * len(self.birds)

        if not computer_playing:
            try:
                #os.remove("./player_data.csv")
                pass
            except:
                pass
            self.data_to_write = []
        while(self.playing_game):
            if not computer_playing:
                self.read_keyboard_input(self.birds[0])
            else:
                for i in range(len(self.birds)):
                    if self.birds[i].alive:
                        self.read_computer_input(self.birds[i], self.networks[i])

            count = 0
            for b in self.birds:
                if b.alive and not collisions[count]:
                    b.move()
                count += 1
            self.draw_everything(score)

            #COLLISIONS DETECTED
            if not computer_playing and any(collisions):
                self.playing_game = False
            else:
                col_count = 0
                #CHECK ALL COLLISIONS
                for i in range(len(collisions)-1, -1, -1):
                    if self.birds[i].alive:
                        if collisions[i]:
                            self.birds[i].alive = False
                            self.scores[i] = self.frame_score
                            self.num_alive -= 1
                            self.computer_player.network_score(self.networks[i], self.frame_score)
                #IF NO BIRDS LEFT, RESET GAME AND CONTINUE
                if self.num_alive == 0:
                    if self.computer_player.cur_gen < self.computer_player.max_gen:
                        self.reset_for_new_gen()
                        collisions = [False] * len(self.birds)
                        time_since_pipe = 1
                        score = 0
                        continue
                    else:
                        self.print_network_stats()
                    self.playing_game = False
            col_count = 0
            for b in self.birds:
                if b.alive:
                    collisions[col_count] = self.check_for_collision(b)
                col_count += 1
            if play_with_pipes:
                self.update_pipes()
            if time_since_pipe % 62 == 0 and play_with_pipes:
                time_since_pipe = 1
                self.lay_pipe()
            pygame.display.update()
            pygame.event.pump()
            pygame.time.Clock().tick(30)
            time_since_pipe += 1
            score = self.increment_score(score, self.birds[0])
            self.increment_frame_score()

        self.display_score()
        self.quit_game()

    def reset_for_new_gen(self):
        self.print_network_stats()
        self.birds = []
        self.pipes = []
        for i in range(self.computer_player.num_per_gen):
            self.birds.append(Bird())
        self.networks = self.computer_player.increment_gen()
        self.scores = [0] * self.computer_player.num_per_gen
        self.num_alive = len(self.birds)
        self.frame_score = 0
        self.lay_pipe()

    def get_stimuli(self, bird):
        #x distance to next pipe, y distance to center of pipe
        stimuli = [999, 999]
        next_pipe = None
        for p in self.pipes:
            if p.top_left[0] + p.pipe_width > bird.top_left[0]:
                next_pipe = p
                break
        if next_pipe:
            stimuli = [next_pipe.top_left[0] - bird.top_left[0] + next_pipe.pipe_width,  next_pipe.center - bird.top_left[1]]
        return stimuli

    def increment_frame_score(self):
        self.frame_score += 1
        if self.frame_score == 20000:
        	self.computer_player.save_best_score()

    def get_network_stats(self):
        cur_gen = self.computer_player.cur_gen
        if len(self.computer_player.generations.generations[0].genomes) == 0:
            return 1, 0, 0, 0
        scores = [g.score for g in self.computer_player.generations.generations[-1].genomes]
        best = max(scores)
        avg = np.mean(scores)
        std = np.std(scores)
        return cur_gen, best, avg, std

    def print_network_stats(self):
        cur_gen, best, avg, std = self.get_network_stats()
        print("Generation # %d had a best score of %f, an average score of %f,"
              "and a standard deviation of %f" % (cur_gen, best, avg, std))


    def increment_score(self, score, bird):
        for p in self.pipes:
            if p.top_left[0] < bird.top_left[0] - p.pipe_width and not p.scored:
                p.scored = True
                score += 1
        return score

    def display_score(self):
        pass
    	
    def quit_game(self):
        pygame.quit()

    def read_keyboard_input(self, bird):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.flap()
                    return "SPACE"
                elif event.key == pygame.K_ESCAPE:
                    self.playing_game = False
        return "NO_INPUT"

    def read_computer_input(self, bird, nn):
        s = [self.get_stimuli(bird)]
        action = self.computer_player.make_decision(s, nn)
        if action == "SPACE":
            bird.flap()

    def check_for_collision(self, bird):
        if bird.top_left[1] < 0:

            return True
        if pygame.sprite.collide_rect(bird, self.floor):
            if pygame.sprite.collide_mask(bird, self.floor):
                return True
        for p in self.pipes:
            if p.top_left[0] < size[0]:
                if p.check_for_collision(bird,pixel_collision=False):
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
        self.draw_birds()
        self.draw_pipe()
        self.draw_floor()
        self.draw_score(score)
        if computer_playing:
            self.draw_computer_info()

    def draw_computer_info(self):
        cur_gen, best, avg, std = self.get_network_stats()
        num_alive = len([b for b in self.birds if b.alive])
        num_per_gen = self.computer_player.num_per_gen
        best_ever = self.computer_player.best_score_ever
        if self.frame_score > best_ever:
            best_ever = self.frame_score
        s = self.score_text.render("Frame Score: %d" % self.frame_score, False, (255, 255, 255))
        na = self.score_text.render("Alive: %d / %d" % (num_alive, num_per_gen), False, (255, 255, 255))
        g = self.score_text.render("Generation: %d" % cur_gen, False, (255, 255, 255))
        b = self.score_text.render("Best Score: %d" % best_ever, False, (255, 255, 255))

        self.screen.blit(g, (5, 5))
        self.screen.blit(na, (5, 25))
        self.screen.blit(s, (5, 45))
        self.screen.blit(b, (5, 65))


    def draw_score(self, score):
        t = self.score_text.render("%s" % score, False, (255, 255, 255))
        self.screen.blit(t, (round(size[0]/2), 100))


    def draw_birds(self):
        for b in self.birds:
            if b.alive:
                b.draw(self.screen)

    def draw_background(self):
        self.screen.fill(bg_color)

    def draw_pipe(self):
        for p in self.pipes:
            p.draw(self.screen)

    def draw_floor(self):
        self.floor.draw(self.screen)


if __name__ == "__main__":
    Controller()