class pshared:
    def __init__(self, bits_to_index, lhist_size):
        #Escriba aquí el init de la clase
        self.total_predictions = 0
        self.total_taken_pred_taken = 0
        self.total_taken_pred_not_taken = 0
        self.total_not_taken_pred_taken = 0
        self.total_not_taken_pred_not_taken = 0

        self.bits_to_index = bits_to_index
        self.lhist_size = lhist_size
        self.size_of_history_table = 2**bits_to_index
        self.size_of_pattern_table = 2**lhist_size
        self.history_table = [0 for i in range(self.size_of_history_table)]
        self.pattern_table = [0 for i in range(self.size_of_pattern_table)]

    def print_info(self):
        print("Parámetros del predictor:")
        print("\tTipo de predictor:\t\t\tP-Shared")

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

    def predict(self, PC):
        index = self.history_table[(int(PC) % self.size_of_history_table)]
        pattern_table_entry = self.pattern_table[index]
        if pattern_table_entry in [0,1]:
            return "N"
        else:
            return "T"

    def update(self, PC, result, prediction):
        htable_index = int(PC) % self.size_of_history_table
        ptable_index = self.history_table[htable_index]
        pattern_table_entry = self.pattern_table[ptable_index]

        # Update local history
        if result == "T":
            self.history_table[htable_index] = self.update_lhist(self.history_table[htable_index], 1)
        else:
            self.history_table[htable_index] = self.update_lhist(self.history_table[htable_index], 0)

        #Update entry accordingly
        if pattern_table_entry == 0 and result == "N": # SATURATION
            updated_pattern_table_entry = pattern_table_entry
            #print(PC,pattern_table_entry,updated_pattern_table_entry,result,prediction)
        elif pattern_table_entry != 0 and result == "N":
            updated_pattern_table_entry = pattern_table_entry - 1
            #print(PC,pattern_table_entry,updated_pattern_table_entry,result,prediction)
        elif pattern_table_entry == 3 and result == "T": # SATURATION
            updated_pattern_table_entry = pattern_table_entry
            #print(PC,pattern_table_entry,updated_pattern_table_entry,result,prediction)
        else:
            updated_pattern_table_entry = pattern_table_entry + 1
            #print(PC,pattern_table_entry,updated_pattern_table_entry,result,prediction)
        self.pattern_table[ptable_index] = updated_pattern_table_entry

        # if result == "T":
        #     self.history_table[htable_index] = self.update_lhist(self.history_table[htable_index], 1)
        # else:
        #     self.history_table[htable_index] = self.update_lhist(self.history_table[htable_index], 0)

        #  # Update local history
        # if result == "T":
        #     self.history_table[htable_index] = self.update_lhist(self.history_table[htable_index], 1)
        # else:
        #     self.history_table[htable_index] = self.update_lhist(self.history_table[htable_index], 0)


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


    def update_lhist(self, lhist, taken):
            # Shift the GHR to the left by one bit
            lhist = (lhist << 1) & ((1 << self.lhist_size) - 1)  # Mask to maintain register size
            # Set the LSB to 1 if the branch is taken, else 0
            if taken:
                lhist |= 1 
            
            return lhist