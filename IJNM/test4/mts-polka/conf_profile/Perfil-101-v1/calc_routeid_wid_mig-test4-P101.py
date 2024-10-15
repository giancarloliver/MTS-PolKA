#!/usr/bin/env python3
from polka.tools import calculate_routeid, print_poly
DEBUG = False


def _main():
    print("Insering irred poly (node-ID)")
    s = [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1],  # s1_0
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1],  # s2_0
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1],  # s2_1
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],  # s2_2     
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1],  # s2_3
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1],  # s2_4
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1],  # s1_1
        #[1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1],  # s8
        #[1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1],  # s9
        #[1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1],  # s10
    ]
    print("From h1 to h4 ====")
    # defining the nodes from h1 to h4
    nodes = [
        s[0], # s1_0
        s[1], # s2_0
        s[2], # s2_1
        s[3], # s2_2
	    s[4], # s2_3
	    #s[5], # s2_4
	    s[6],	# s1_1
    ]
    # defining the transmission state for each node from h1 to h4
    o = [
        [0, 1, 1, 1, 1, 0, 0],     # s1_0   
	    [1, 0],  # s2_0
        [1, 0],  # s2_1
        [1, 0, 0],  # s2_2
	    [1, 0],	# s2_3	
	    #[1, 0],	# s2_4
	    [0, 0, 0, 0, 0, 0, 1], # s1_1
    ]
    print("routeid h1 to h4 ====")
    print_poly(calculate_routeid(nodes, o, debug=DEBUG))
    print("From h1 to h4 ====")
    # defining the nodes from h1 to h4
    nodes = [
        s[0], # s1_0
        s[1], # s2_0
        s[2], # s2_1
        s[3], # s2_2
	    s[4], # s2_3
	    #s[5], # s2_4
	    s[6],	# s1_1
    ]
    # defining the transmission weight for each node from h1 to h4
    w = [
        [0, 0, 0, 0, 1, 0, 1],     # s1_0   
	    [0, 0],  # s2_0
        [0, 0],  # s2_1
        [0, 0, 0],  # s2_2
	    [0, 0],	# s2_3	
	    #[1, 0],	# s2_4
	    [0, 0, 0, 0, 0, 0, 0], # s1_1
    ]
    print("wid h1 to h4 ====")
    print_poly(calculate_routeid(nodes, w, debug=DEBUG))

    print("From h4 to h1 ====")
    # defining the nodes from h1 to h4
    nodes = [
        s[6], # s1_1
        #s[5], # s2_4
        s[4], # s2_3	
        s[3], # s2_2
	    s[2], # s2_1
	    s[1],  # s2_0
	    s[0], # s1_0
    ]
    # defining the transmission state for each node from h1 to h4
    o = [
        [0, 1, 1, 1, 1, 0, 0],     # s1_1  
	    #[0, 1],  # s2_4
        [0, 1],  # s2_3
        [0, 1, 0],  # s2_2
	    [0, 1],	# s2_1	
	    [0, 1],	# s2_0
	    [0, 0, 0, 0, 0, 0, 1], # s1_0
    ]
    print("routeid h4 to h1 ====")
    print_poly(calculate_routeid(nodes, o, debug=DEBUG))

    print("From h4 to h1 ====")
    # defining the nodes from h1 to h4
    nodes = [
        s[6], # s1_1
        #s[5], # s2_4
        s[4], # s2_3	
        s[3], # s2_2
	    s[2], # s2_1
	    s[1],  # s2_0
	    s[0], # s1_0
    ]
     # defining the transmission weight for each node from h4 to h1
    w = [
        [0, 0, 0, 0, 1, 0, 0],     # s1_1  
	    #[0, 1],  # s2_4
        [0, 0],  # s2_3
        [0, 0],  # s2_2
	    [0, 0],	# s2_1	
	    [0, 0],	# s2_0
	    [0, 0, 0, 0, 0, 0, 0], # s1_0
    ]    
    print("wid h4 to h1 ====")
    print_poly(calculate_routeid(nodes, w, debug=DEBUG)) 


if __name__ == '__main__':
    _main()
