class gshared:
    def __init__(self, bits_to_index, ghist_size):
        self.total_predictions = 0
        self.total_taken_pred_taken = 0
        self.total_taken_pred_not_taken = 0
        self.total_not_taken_pred_taken = 0
        self.total_not_taken_pred_not_taken = 0

        self.bits_to_index = bits_to_index
        self.ghist = 0
        self.ghist_size = ghist_size
        self.size_of_branch_table = 2**(max(bits_to_index, ghist_size))
        self.branch_table = [0 for i in range(self.size_of_branch_table)]

        

    def print_info(self):
        print("Parámetros del predictor:")
        print("\tTipo de predictor:\t\t\t\tG-Shared")

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
        index = (int(PC) % self.size_of_branch_table) ^ (self.ghist)
        branch_table_entry = self.branch_table[index]
        if branch_table_entry in [0,1]:
            return "N"
        else:
            return "T"



    def update(self, PC, result, prediction):
        #Escriba aquí el código para actualizar
        #La siguiente línea es solo para que funcione la prueba
        #Quítela para implementar su código
        index = (int(PC) % self.size_of_branch_table) ^ self.ghist
        branch_table_entry = self.branch_table[index]

        # Update global history
        if result == "T":
            self.update_ghist(1)
        else:
            self.update_ghist(0)

        #Update entry accordingly
        if branch_table_entry == 0 and result == "N": # SATURATION
            updated_branch_table_entry = branch_table_entry
            #print(PC,branch_table_entry,updated_branch_table_entry,result,prediction)
        elif branch_table_entry != 0 and result == "N":
            updated_branch_table_entry = branch_table_entry - 1
            #print(PC,branch_table_entry,updated_branch_table_entry,result,prediction)
        elif branch_table_entry == 3 and result == "T": # SATURATION
            updated_branch_table_entry = branch_table_entry
            #print(PC,branch_table_entry,updated_branch_table_entry,result,prediction)
        else:
            updated_branch_table_entry = branch_table_entry + 1
            #print(PC,branch_table_entry,updated_branch_table_entry,result,prediction)
        self.branch_table[index] = updated_branch_table_entry



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


        a = PC

    def update_ghist(self, taken):
            # Shift the GHR to the left by one bit
            self.ghist = (self.ghist << 1) & ((1 << self.ghist_size) - 1)  # Mask to maintain register size
            # Set the LSB to 1 if the branch is taken, else 0
            if taken:
                self.ghist |= 1 

    