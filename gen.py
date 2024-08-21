import random
import neural
import game
import os
import copy
import time



class Generation:
    def __init__(self, num_gens:int, num_games_per_agent:int, num_survivors:int, num_children:int, num_changes:int, mutation_range:float, layers:list) -> None:
        
        self.game = game.Game()
        self.agents = {} 

        self.num_gens = num_gens
        self.num_agents_per_gen = num_survivors * num_children
        self.num_games_per_agent = num_games_per_agent

        self.num_survivors = num_survivors
        self.num_children = num_children
        self.num_changes = num_changes
        self.mutation_range = mutation_range

        self.layers = layers

    # TODO more nodes and layers
    def mutate(self, agent_id: int) -> None:

        layer_sizes, parent_weight_dict = self.load_weights_from_parent(agent_id)
        for new_agent in range(self.num_children):
            new_agent_weights = copy.deepcopy(parent_weight_dict)
            for change in range(self.num_changes):
                choosed_layer = random.choice([key for key in new_agent_weights])
                choosed_node = random.choice([key for key in new_agent_weights[choosed_layer]])
                choosed_link = random.randint(0, len(new_agent_weights[choosed_layer][choosed_node])-1)
                new_agent_weights[choosed_layer][choosed_node][choosed_link] += 2*self.mutation_range*random.random() - self.mutation_range # Denne kan bli endret på

            new_generation = self.agents[agent_id]["generation"]+1
            
            new_agent_id = self.save_weights(layer_sizes, new_agent_weights, new_generation)
            self.agents[new_agent_id] = {"score": -1, "generation": new_generation, "statistics": {"points":-1, "jumps": -1}}
    
    # Ferdig
    def load_weights_from_parent(self, agent_id: int) -> None:
        generation = self.agents[agent_id]["generation"]
        with open(f"generation{generation}/weights{agent_id}.txt", "r") as f:
            layer_sizes = [int(i) for i in f.readline().split(",")]
            w_dict = {}
            for i in range(len(layer_sizes)-1):
                w_dict[i] = {}
                for j in range(int(layer_sizes[i])):
                    line = f.readline().split(",")
                    w_dict[i][j] = [float(w) for w in line]
        
        return [layer_sizes, w_dict]

    # Ferdig
    def save_weights(self, layer_sizes, weight_dict, gen_num: int) -> None:
        with open("num_files.txt", "r") as f:
            num = int(f.readline())
            num+=1
        with open("num_files.txt", "w") as f:
            f.write(str(num))

        
        with open(f"generation{gen_num}/weights{num}.txt", "w") as f:
            self.write_line(f, self.list_to_string(layer_sizes))

            for i in range(len(layer_sizes)-1):
                for j in range(int(layer_sizes[i])):
                    self.write_line(f, self.list_to_string(weight_dict[i][j]))
        
        return num
    
    # Ferdig
    def list_to_string(self, list: list) -> str:
        string = ""
        for i, item in enumerate(list):
            if i < len(list) -1:
                string += str(item) + ","
            else:
                string += str(item)
        
        return string
    
    # Ferdig
    def write_line(self, file, str):
        file.write(str + "\n")
    
    #TODO fix agent_id_greiene
    def run_agent(self, agent_id):
        avg_score = 0
        avg_points = 0
        avg_jumps = 0
        for i in range(self.num_games_per_agent):
            data = self.run_game_from_agent_id(agent_id)
            avg_score += data[0]
            avg_points += data[1]
            avg_jumps += data[2]
        avg_score /= self.num_games_per_agent
        avg_points /= self.num_games_per_agent
        avg_jumps /= self.num_games_per_agent

        return [avg_score, avg_points, avg_jumps]
    
    # vet ikke om ferdig
    def find_best_agents(self, generation):
        agent_ids = [] # stores ids of best agents
        agent_scores = [] # store scores (pairs up with the above list)

        for agent in self.agents.keys():

            if self.agents[agent]["generation"] == generation: 
                agent_ids.append(agent)
                agent_scores.append(self.agents[agent]["score"])
        
        while len(agent_ids) > self.num_survivors:
            index_to_remove = self.index_of_lowest_value(agent_scores)
            agent_scores.pop(index_to_remove)
            agent_ids.pop(index_to_remove)
        
        return agent_ids

    def index_of_lowest_value(self, list: list) -> int:
        lowest_value = 1E9 # TODO if there is an unexplainable bug, choose a higher number
        lowest_index = 0

        for i, item in enumerate(list):
            if item < lowest_value:
                lowest_value = item
                lowest_index = i
        
        return lowest_index
        
    #TODO fix agent_id_greiene
    def run_game_from_agent_id(self, agent_id: int):
        self.game.ai.agent_info = [agent_id, self.agents[agent_id]["generation"]]
        self.game.ai.load_from_file(self.game.ai.agent_info)
        score, points, jumps = self.game.run()
        return [score, points, jumps]
    
    def simulate_one_generation(self, gen_num):
        if gen_num  % 10 == 0:
            print(f"Currently simulating generation {gen_num}")

        if gen_num == 0:
            for i in range(self.num_agents_per_gen):
                agent = neural.Network().make_new_weights_from_size(self.layers) # TODO endre på layers
                self.agents[agent] = {"score": -1, "generation": 0, "statistics": {"points":-1, "jumps": -1}} 

        # simulere for hver agent i generasjonen
        list_of_agents_in_gen = [agent for agent in self.agents.keys() if self.agents[agent]["generation"]==gen_num]
        
        for agent in list_of_agents_in_gen:
            data = self.run_agent(agent)
            self.agents[agent]["score"] = data[0]
            self.agents[agent]["statistics"]["points"] = data[1]
            self.agents[agent]["statistics"]["jumps"] = data[2]
        
        
        best_agents = self.find_best_agents(gen_num)
        
        if gen_num == 0 or gen_num == self.num_gens - 1:
            print("generation", gen_num)
            for i in best_agents:
                print(f"agent_id: {i}")
                print(self.agents[i]["score"])
                print(self.agents[i]["statistics"])

        if gen_num != self.num_gens-1:
            self.mutate_from_list(best_agents)

    def mutate_from_list(self, best_agents: list) -> None:
        for agent in best_agents:
            self.mutate(agent)
    
    def run(self):
        parent_path = "/Users/hakonstoren/Python_i_VSCODE/Neural/" 
        for dir in os.listdir(parent_path):                         # TODO DETTE ER FARLIG
            if dir.startswith("generation"):                        # TODO DETTE ER FARLIG
                d_path = os.path.join(parent_path, dir)             # TODO DETTE ER FARLIG
                for file in os.listdir(d_path):                     # TODO DETTE ER FARLIG
                    file_path = os.path.join(d_path, file)          # TODO DETTE ER FARLIG
                    os.remove(file_path)                            # TODO DETTE ER FARLIG
                os.rmdir(d_path)                                    # TODO DETTE ER FARLIG
        
        for i in range(self.num_gens):
            directory_name = "generation" + str(i)
            
            path = os.path.join(parent_path, directory_name)
            os.mkdir(path)
        for i in range(self.num_gens):
            self.simulate_one_generation(i)
        


def main():
    start_time = time.time()
    gen = Generation(100, 4, 20, 4, 3 , 0.5, [2,4,1])
    
    gen.run()
    total_elapsed_time = time.time()-start_time

    print(f"[Program finished in {round(total_elapsed_time, 3)} seconds]")

    print()


main()