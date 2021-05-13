

def getPrediction(feat_list, coeffs, link_function):

    res = coeffs[0] #The constant in all equations. 

    if(link_function == 'identity'):

        for i, val in enumerate(feat_list):
            res += coeffs[i+1] * val

    elif link_function == 'poisson':

        from math import pow, e

        for i, val in enumerate(feat_list):
            res += coeffs[i+1] * (val)

        pois_res = pow(e, res)

        return pois_res

    else :
        print("ERROR in Link Function")
        exit(0) #FIGURE OUT WHAT CODE TO FOLLOW

    return res

#Call this function with the list of values and the associated name of the feature
def setHistory(feat_name, feat_list):

    #for player forms the list should be in the order gw-1, gw-2 and gw-3
    #for score :  off_strength, def_strength, off_form ,def_form
    #for attPlayer and defPlayer_points: minutes, player_cost, value, ict, team_score

    if feat_name == 'player_ict':
        
        coeffs = [1.975542, 0.206890, 0.150760, 0.184476]
        link_function = 'identity'

    elif feat_name == 'player_value':

        coeffs = [-0.117605, 1.129997, -0.025257, -0.103505]
        link_function = 'identity'

    elif feat_name == 'player_minutes':

        coeffs = [26.229026, 0.331036, 0.161746, 0.116634]
        link_function = 'identity'

    elif feat_name == 'score':  #For a fixture (A vs B) we generate two scores : 1. off A vs def B and 2. off B vs def A. Use example: When we predict for players in off A or def B then we use 1.   

        coeffs = [-1.857362, 0.000359, 0.000151, 0.030452, 0.043995]
        link_function = 'poisson'

    elif feat_name == 'team_att': # Att points history

        coeffs = [16.547586, 0.105863, 0.008679, 0.176439]
        link_function = 'identity'

    elif feat_name == 'team_def': # Def points history

        coeffs = [14.627808, 0.083712, 0.020588, 0.096803]
        link_function = 'identity'

    elif feat_name == 'attPlayer_points': #For an attacking player (element = 3 or 4). Example use for team A vs B. We want to predict for an offensive player in A. We use feats as mentioned above. 
                                          # Score here would be the one derived from off A vs def B.

        coeffs = [0.107617, 0.007059, 0.058934, -0.050233, 0.065789, -0.261031]
        link_function = 'identity'

    elif feat_name == 'defPlayer_points': #For a defensive player (element  = 1 or 2). Example use for team A vs B and we want to predict for a team A defender. Score here would be off B vs Def A. 
                                          # Basically, def A player use off B vs def A and att A player use off A vs def B score.  

        coeffs = [0.107034, 0.007108, 0.059717, -0.01240, 0.062791, -0.239849]
        link_function = 'identity'

    else:
        print("ERROR")
        exit(0) #FIGURE OUT WHAT CODE TO FOLLOW


    return getPrediction(feat_list, coeffs, link_function)



