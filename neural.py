import random

#TODO Kommenter koden!!!

""" 
-------Formen på nettverket------
Neural_Network = {
    "Size":     [2, 2, 1],
    "Weights":   {0: {0:[0.34, 0.75], 1:[0.9, 0.1] },
                 1: {0:[0.43], 1:[0.19] }},
    "Values":   {0: {0: 0.3, 1: 0.5}, 1: {0: None, 1: None}, 2: {0:None}},
    "Output":   {0: 0.4}
}
---------------------------------
"""

class Network:
    def __init__(self) -> None:
        self.neural_network =    {"size": None,
                             "weights": None,
                             "values": None,
                             "output": None}
        self.agent_info = [0, 0]
        #self.load_from_file(self.agent_info)
        
 
    
    def read_input(self, file: str) -> dict:
        input_dict = {}
        with open(file, "r") as f:
            data = f.readline().split(",")

            num_req_inputs = self.neural_network["size"][0]
            if len(data) != num_req_inputs: 
                print(f"Invalid input size: {len(data)} inputs were given, but {num_req_inputs} inputs are required")
                return None
            for i, item in enumerate(data):
                input_dict[i] = float(item)
        return input_dict
    
    
    def calculate_node(self, values_dict:dict, layer: int, node: int) -> None:
        avg = 0
        for i in range(self.neural_network["size"][layer - 1]):

            avg += values_dict[layer - 1][i] * self.neural_network["weights"][layer-1][i][node]
        avg /= self.neural_network["size"][layer - 1]
         

        return round(self.activating_function(avg), 5)


    def load_from_file(self, agent_info: list) -> None:

        with open(f"generation{agent_info[1]}/weights{agent_info[0]}.txt", "r") as f:
            layer_sizes = [int(i) for i in f.readline().split(",")]
            w_dict = {}
            for i in range(len(layer_sizes)-1):
                w_dict[i] = {}
                for j in range(int(layer_sizes[i])):
                    line = f.readline().split(",")
                    w_dict[i][j] = [float(w) for w in line]
        
        self.neural_network["size"] = layer_sizes
        self.neural_network["weights"] = w_dict
        
    
    def run_network_from_file(self, file: str) -> None:
        v_dict = {}
        
        v_dict[0] = self.read_input(file)
        
        layer_sizes = self.neural_network["size"]

        for layer in range(1, len(layer_sizes)):
            v_dict[layer] = {}
            for node in range(int(layer_sizes[layer])):
                v_dict[layer][node] = self.calculate_node(v_dict, layer, node)
        
        self.neural_network["values"] = v_dict
        self.neural_network["output"] = self.neural_network["values"][len(self.neural_network["size"])-1]
    

    def run_network_from_input(self, inputs: list) -> None:
        v_dict = {}
        input_dict = {}
        for i, item in enumerate(inputs):
                input_dict[i] = float(item)
        v_dict[0] = input_dict
        
        layer_sizes = self.neural_network["size"]
        for layer in range(1, len(layer_sizes)):
           v_dict[layer] = {}
           for node in range(int(layer_sizes[layer])):
               v_dict[layer][node] = self.calculate_node(v_dict, layer, node)


        self.neural_network["values"] = v_dict
        self.neural_network["output"] = self.neural_network["values"][len(self.neural_network["size"])-1]

        return self.neural_network["output"]

   



    def list_to_string(self, list: list) -> str:
        string = ""
        for i, item in enumerate(list):
            if i < len(list) -1:
                string += str(item) + ","
            else:
                string += str(item)
        
        return string
    
    def write_line(self, file, str):
        file.write(str + "\n")

    def activating_function(self, x: float) -> float:

        e = 2.71828
        return (1 - 1/(1+e**(5*x-2.5)))
    

    
    def make_new_weights_from_size(self, size: list) -> int:
        with open("num_files.txt", "r") as f:
                num = int(f.readline())
                num+=1
        with open("num_files.txt", "w") as f:
            f.write(str(num))
        with open(f"generation0/weights{num}.txt", "w") as f:
            self.write_line(f, self.list_to_string(size))

            for i in range(len(size)-1):
                for j in range(int(size[i])):
                    self.write_line(f, self.list_to_string([round(2* random.random() -1,5) for _ in range(size[i+1])]))

        return num


# Network().make_new_weights_from_size([1,2,1])