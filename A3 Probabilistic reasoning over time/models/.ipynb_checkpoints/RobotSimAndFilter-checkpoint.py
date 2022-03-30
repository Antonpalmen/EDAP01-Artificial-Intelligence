
import random
import numpy as np

from models import TransitionModel,ObservationModel,StateModel

#
# Add your Robot Simulator here
#pick new heading 
#if(): 

#print(loc.get_current_true_pose())
#print(states.pose_to_state(loc.get_current_true_pose()[0], loc.get_current_true_pose()[1], loc.get_current_true_pose()[2]))

# P(h_t+1 = h_t | not encountering a wall) = 0.7 
# P(h_t+1 != h_t | not encountering a wall) = 0.3 
# P(h_t+1 = h_t | encountering a wall) = 0.0
# P(h_t+1 != h_t | encountering a wall) = 1.0
#
class RobotSim:
    def __init__(self, state, tm, om, sm): 
        self.__current_state = state
        self.__tm = tm
        self.__om = om
        self.__sm = sm
        
    def move(self): 
        #random.seed(0)
        threshold = random.random()
        
        nbr_states = self.__tm.get_num_of_states()
        sum_prob = 0
        state = 0
        
        for i in range(nbr_states):  
            sum_prob += self.__tm.get_T_ij(self.__current_state, i)
            if(sum_prob > threshold):
                state = i
                break
        self.__current_state = state        
        return self.__current_state
        
    def sense(self): 
        #random.seed(0)
        threshold = random.random()
        
        nbr_readings = self.__om.get_nr_of_readings()
        sum_prob = 0
        reading = 0
        
        for i in range(nbr_readings):  
            sum_prob += self.__om.get_o_reading_state(i, self.__current_state)
            if(sum_prob > threshold):
                reading = i
                break
        return reading
        
#
# Add your Filtering approach here (or within the Localiser, that is your choice!)
#
class HMMFilter:
    def __init__(self, probs, tm, om, sm): 
        self.__probs = probs
        self.__tm = tm
        self.__om = om
        self.__sm = sm
        
    def hmm_filter(self, reading): #forumlae from book (f_{1:t+1} = α * O_{t+1} * T^{⊤} * f_{1:t}) - (return f- has to be column vector)
       
        transposed_t_matrix = self.__tm.get_T_transp()
        o_matrix = self.__om.get_o_reading(reading)
        
        temp1 = np.matmul(o_matrix, transposed_t_matrix)
        temp2 = np.matmul(temp1, self.__probs)
        alpha = 1.0/np.sum(temp2)
        #self.__probs = temp2 * alpha
        prob = temp2 * alpha
        
        return prob
        
       
        
        