class perceptron:
    def __init__(self, bits_to_index, ghist_size):
        #Escriba aquí el init de la clase
        self.total_predictions = 0
        self.total_taken_pred_taken = 0
        self.total_taken_pred_not_taken = 0
        self.total_not_taken_pred_taken = 0
        self.total_not_taken_pred_not_taken = 0

        self.bits_to_index = bits_to_index
        self.ghist = 0
        self.y = 0
        self.threshold =  (1.93*ghist_size)+14 
        self.ghist_size = ghist_size
        self.table_size = 2**bits_to_index
        self.weights_table = [[0 for i in range(ghist_size+1)] for i in range(self.table_size)]

    def print_info(self):
        print("Parámetros del predictor:")
        print("\tTipo de predictor:\t\t\tPerceptron")

    def print_stats(self):
        print("Resultados de la simulación")
        print("\t# branches:\t\t\t\t\t\t"+str(self.total_predictions))
        print("\t# branches tomados predichos correctamente:\t\t"+str(self.total_taken_pred_taken))
        print("\t# branches tomados predichos incorrectamente:\t\t"+str(self.total_taken_pred_not_taken))
        print("\t# branches no tomados predichos correctamente:\t\t"+str(self.total_not_taken_pred_not_taken))
        print("\t# branches no tomados predichos incorrectamente:\t"+str(self.total_not_taken_pred_taken))
        perc_correct = 100*(self.total_taken_pred_taken+self.total_not_taken_pred_not_taken)/self.total_predictions
        formatted_perc = "{:.3f}".format(perc_correct)
        print("\t% predicciones correctas:\t\t\t\t"+str(formatted_perc)+"%")

    # Give prediction
    def predict(self, PC):
        index = int(PC) % self.table_size
        ghist_bin = bin(self.ghist)[2:] if self.ghist >= 0 else bin(self.ghist)[1:]
        ghist_list = [int(i) if int(i) != 0 else -1 for i in list(ghist_bin.zfill(self.ghist_size))]
        ghist_list.insert(0,1) # Include bias
        self.y = self.dot_product(self.weights_table[index], ghist_list)
        
        return "T" if self.y >= 0 else "N"
    
    # Update predictors
    def update(self, PC, result, prediction):
        index = int(PC) % self.table_size    
        ghist_bin = bin(self.ghist)[2:] if self.ghist >= 0 else bin(self.ghist)[1:]
        ghist_list = [int(i) if int(i) != 0 else -1 for i in list(ghist_bin.zfill(self.ghist_size))]
        ghist_list.insert(0,1) # Include bias
        
        # Update weights
        t = 1 if result == "T" else -1
        y = self.y
        if (self.get_sign(y) != t) | (abs(y) <= self.threshold):
            self.weights_table[index] = self.train(y, t, self.weights_table[index], ghist_list) 
           
        # Update global history
        if result == "T":
            self.update_ghist(1)
        else:
            self.update_ghist(0)

        # Update stats
        if result == "T" and result == prediction:
            self.total_taken_pred_taken += 1
        elif result == "T" and result != prediction:
            self.total_taken_pred_not_taken += 1
        elif result == "N" and result == prediction:
            self.total_not_taken_pred_not_taken += 1
        else:
            self.total_not_taken_pred_taken += 1

        self.total_predictions += 1

    # Train individual perceptron
    def train(self, y, t, P, H):
        for i in range(len(P)):
            P[i] += H[i]*t
        return P
    
    # Get sign of y
    def get_sign(self, y):
        return 1 if y >= 0 else -1
    
    # Update history register
    def update_ghist(self, taken):
            # Shift ghist to the left by one bit
            self.ghist = (self.ghist << 1) & ((1 << self.ghist_size) - 1)  # Mask to maintain register size
            # Set the LSB to 1 if the branch is taken, else 0
            if taken:
                self.ghist |= 1 

    # Get dot product of two vectors
    def dot_product(self, P, ghist_list):
        return sum([(x*y) for x,y in zip(P, ghist_list)])