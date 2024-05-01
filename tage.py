class TAGE:
    def __init__(self):
        self.num_components = 5  # Including T0
        self.base_table_size = 2048  # Number of entries in T0
        self.tagged_table_size = 512  # Number of entries in T1 to T4
        self.tag_width = 9  # Width of the tag in bits
        self.history_lengths = [0, 5, 10, 15, 20]  # Example geometric progression of history lengths
        self.ghist = 0
        self.ghist_size = 20

        self.total_predictions = 0
        self.total_taken_pred_taken = 0
        self.total_taken_pred_not_taken = 0
        self.total_not_taken_pred_taken = 0
        self.total_not_taken_pred_not_taken = 0



        # Initialize the base prediction table T0
        self.T0 = [0] * self.base_table_size  # Simple bimodal (2-bit counters initialized to weakly taken)

        # Initialize tagged tables T1 to T4
        self.tagged_tables = []
        for _ in range(1, self.num_components):
            # Each entry has a tag, a useful counter (2 bits), and a counter (3 bits)
            # Initialize all entries with tag = 0, u = 0, ctr = 0 (weakly not taken)
            table = [{'tag': 0, 'u': 0, 'ctr': 0} for _ in range(self.tagged_table_size)]
            self.tagged_tables.append(table)


    def print_info(self):
        print("Parámetros del predictor:")
        print("\tTipo de predictor:\t\t\tNombre de su predictor")

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


    def hash_index(self, PC, ghist, history_length, size):
        
            return (int(PC) ^ (ghist % history_length)) % size

    def predict(self, PC):
        # Hash function to index into the tables
        # assert isinstance(PC, int), "PC must be an integer"
        # Start with the base predictor
        # print(PC, self.history_lengths[0], self.base_table_size)
        base_index = int(PC) % self.base_table_size
        if (self.T0[base_index] >= 2):
            prediction = "T" # 2-bit counter: 0,1 = not taken; 2,3 = taken
        else:
            prediction = "N"

        # print("BIMODAL:", prediction, "\n")

        # Check tagged tables for overriding predictions
        provider = None
        for i, table in enumerate(self.tagged_tables, start=1):
            index = self.hash_index(PC, self.ghist, self.history_lengths[i], self.tagged_table_size)
            entry = table[index]
            tag = self.hash_index(PC, self.ghist, self.history_lengths[i] + 1, 1 << self.tag_width)  # Simplified tag computation

            if entry['tag'] == tag and entry['ctr'] >= 2:
                prediction = "T"
                provider = (i, index)
            elif entry['tag'] == tag and entry['ctr'] < 2:
                prediction = "N"
                provider = (i, index)

        return prediction, provider

    def update(self, PC, result, prediction, provider):
        # Update logic based on the prediction result and provider component

        if result == "T":
            self.update_ghist(1)
        else:
            self.update_ghist(0)

        result_bit = 1 if result == "T" else 0

        if provider is None:  # Update the base predictor only
            base_index = int(PC) % self.base_table_size
            if result == "T":
                if self.T0[base_index] < 3:
                    self.T0[base_index] += 1
            else:
                if self.T0[base_index] > 0:
                    self.T0[base_index] -= 1
        else:
            # tagged_index = 
            # print(provider)
            # print("MATCH!!!!!")
            i, index = provider
            table = self.tagged_tables[i - 1]
            entry = table[index]

            # Update the prediction counter
            if result_bit == (entry['ctr'] >= 2):
                if entry['ctr'] < 7:
                    entry['ctr'] += 1
            else:
                if entry['ctr'] > 0:
                    entry['ctr'] -= 1

            # Update the useful bit (simplified example)
            entry['u'] = min(3, entry['u'] + 1) if result == prediction else max(0, entry['u'] - 1)


        if self.total_predictions % 50000 == 0:
            print("PROVIDER:", provider)
            print("PRED:", prediction)
            print("RESULT:", result)

            # print("WEIGHTS: ", self.weights_table, "\n")  
            # print(ghist_list)
            print("")  
        
         #Update stats
        if result == "T" and result == prediction:
            self.total_taken_pred_taken += 1
        elif result == "T" and result != prediction:
            self.total_taken_pred_not_taken += 1
        elif result == "N" and result == prediction:
            self.total_not_taken_pred_not_taken += 1
        else:
            self.total_not_taken_pred_taken += 1

        self.total_predictions += 1

    def update_ghist(self, taken):
        # Shift the GHR to the left by one bit
        self.ghist = (self.ghist << 1) & ((1 << self.ghist_size) - 1)  # Mask to maintain register size
        # Set the LSB to 1 if the branch is taken, else 0
        if taken:
            self.ghist |= 1 
