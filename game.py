import random
import neural


class Game:
    def __init__(self) -> None:
        self.ai = neural.Network()
        self.restart()

    def restart(self):
        self.speed = 10
        self.jump_cooldown = 2 * self.speed
        self.jump_distance = 4 * self.speed
        self.distance_since_last_jump = 0
        self.new_obstacle = True
        self.is_jumping = False
        self.game_over = False
        self.obstacle_distance = 100
        self.obstacle_distance2 = 200

        self.want_to_jump = False

        self.points = 0
        self.num_jumps = 0
    
    def step(self):        
        self.obstacle_distance -= self.speed
        self.obstacle_distance2 -= self.speed
        self.distance_since_last_jump += self.speed

        if self.new_obstacle:
            self.obstacle_distance = self.obstacle_distance2
            self.obstacle_distance2 += random.randint(4, 10) * self.speed
            self.new_obstacle = False
    

        if self.want_to_jump and not self.is_jumping and self.distance_since_last_jump > self.jump_distance + self.jump_cooldown:
            self.distance_since_last_jump = 0
            self.is_jumping = True
            self.num_jumps += 1
        
        
        if self.is_jumping and self.distance_since_last_jump == self.jump_distance:
            self.is_jumping = False
        
        #print(self.obstacle_distance)
        self.network_output = self.ai.run_network_from_input([self.obstacle_distance /200, self.obstacle_distance2 /200 ])[0]
        
        if self.network_output > 0.5:
            self.want_to_jump = True


        #print(self.ai.neural_network["values"])
        
        if self.obstacle_distance <= 0 and not self.is_jumping:
            self.game_over = True
        elif self.obstacle_distance <= 0:
            self.new_obstacle = True
            self.points += 1
    
    def run(self):
        self.restart()
        while self.points < 100 and not self.game_over:
            self.step()
        #print(f"num_jumps: {self.num_jumps}")
        #print(f"points: {self.points}")
        if self.num_jumps == 0:
            return [0, 0, 0]
        score = round(self.points**2/self.num_jumps, 4)
        if self.num_jumps > self.points +3:
            score = score
        return [score, self.points, self.num_jumps]



