class TAGE:
    def __init__(self):
        self.num_components = 5  # Including T0
        self.base_table_size = 2048  # Number of entries in T0
        self.tagged_table_size = 512  # Number of entries in T1 to T4
        self.tag_width = 9  # Width of the tag in bits
        self.history_lengths = [0, 5, 15, 44, 130]  # Geometric progression of history lengths
        self.ghist = 0
        self.ghist_size = 130

        self.total_predictions = 0
        self.total_taken_pred_taken = 0
        self.total_taken_pred_not_taken = 0
        self.total_not_taken_pred_taken = 0
        self.total_not_taken_pred_not_taken = 0



        # Initialize the base prediction table T0
        self.T0 = [1] * self.base_table_size  # Simple bimodal predictor

        # Initialize tagged tables T1 to T4
        self.tagged_tables = []
        for _ in range(1, self.num_components):
            # Initialize all entries with tag = 0, u = 0, ctr = 0 
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


    # Give prediction
    def predict(self, PC):
        # Get prediction from base table
        base_idx = int(PC) % self.base_table_size
        entry = self.T0[base_idx]
        if entry >= 2:
            pred = "T"
        else:
            pred = "N"

        provider_idx = 0
        alt_pred = pred

        # Look for matches in tagged tables to make predictions.
        for i, table in enumerate(self.tagged_tables, start=1):
            idx = self.table_hash(PC, self.ghist, self.history_lengths[i], self.tagged_table_size)
            tag = self.tag_hash(PC, self.ghist, self.history_lengths[i], self.tagged_table_size)

            entry = table[idx]
            # Get prediction from longest history table and set alt_pred to the last prediction
            if entry['tag'] == tag:
                provider_idx = i
                alt_pred = pred
                pred = "T" if entry['ctr'] >= 0 else "N"
            # If there is no tag at the current index, set it to the current tag
            elif entry['tag'] == 0:
                entry['tag'] = tag
                entry['u'] = 0
                entry['ctr'] = 0

        return pred, alt_pred, provider_idx
    
    def update(self, PC, result, pred, alt_pred, provider_idx):

        base_idx = int(PC) % self.base_table_size

        # Update base table
        if result == "T":
            if self.T0[base_idx] < 3:
                self.T0[base_idx] += 1
        else:
            if self.T0[base_idx] > 0:
                self.T0[base_idx] -= 1

        # If there was a match:
        if provider_idx != 0:
        
            idx = self.table_hash(PC, self.ghist, self.history_lengths[provider_idx], self.tagged_table_size)
            # Update provider's useful counter
            if pred != alt_pred:
                u = self.tagged_tables[provider_idx-1][idx]['u']

                if pred == result:
                    if u < 3:
                        self.tagged_tables[provider_idx-1][idx]['u'] += 1
                else:
                    if u > 0:
                        self.tagged_tables[provider_idx-1][idx]['u'] -= 1

            # Periodically reset all useful counters (alternate between resetting LSB and MSB every 256K predictions)
            if self.total_predictions % 256e3 == 0:
                if self.total_predictions % 512e3 == 0:
                    for table in self.tagged_tables:
                        for p in table:
                            p['u'] &= 2
                else:
                    for table in self.tagged_tables:
                        for p in table:
                            p['u'] &= 1

            # Update provider prediction counter whether the prediction was correct or not
            ctr = self.tagged_tables[provider_idx-1][idx]['ctr']
            if result == "T":
                if ctr < 3:
                    self.tagged_tables[provider_idx-1][idx]['ctr'] += 1
            else:
                if ctr > -4:
                    self.tagged_tables[provider_idx-1][idx]['ctr'] -= 1
            
            # If the prediction was incorrect:
            if pred != result:
                updated = False

                # If the provider was not the table with the longest history:
                if provider_idx != self.num_components-1:
                    # Find the next table in wich a useful counter is 0
                    for j, table in enumerate(self.tagged_tables[provider_idx-1:], start=provider_idx):
                        if not updated:
                            tag = self.tag_hash(PC, self.ghist, self.history_lengths[j], self.tagged_table_size)
                            for p in table:
                                if p['u'] == 0:
                                    p['tag'] = tag
                                    updated = True
                                    break
                        continue
                    # If there is none, decrease in one all useful counters from subsequent tables
                    if not updated:
                        for table in self.tagged_tables[provider_idx+1:]:
                            for p in table:
                                if p['u'] > 0:
                                    p['u'] -= 1     

        # Update global history register       
        if result == "T":
            self.update_ghist(1)
        else:
            self.update_ghist(0)
        
         #Update stats
        if result == "T" and result == pred:
            self.total_taken_pred_taken += 1
        elif result == "T" and result != pred:
            self.total_taken_pred_not_taken += 1
        elif result == "N" and result == pred:
            self.total_not_taken_pred_not_taken += 1
        else:
            self.total_not_taken_pred_taken += 1

        self.total_predictions += 1

        return None


    # Update history register
    def update_ghist(self, taken):
        # Shift the GHR to the left by one bit
        self.ghist = (self.ghist << 1) % 2**self.ghist_size  # Mask to maintain register size
        # Set the LSB to 1 if the branch is taken, else 0
        if taken:
            self.ghist |= 1 

    # Hash funciton to index tagged tables
    def table_hash(self, PC, ghist, history_length, size):
        return (int(PC) ^ (ghist % 2**history_length)) % size

    # Hash function to get tag
    def tag_hash(self, PC, ghist, history_length, size):       
        return ( ((int(PC) << 1)) ^ (ghist % 2**history_length)) % size


    