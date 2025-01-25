#!/usr/bin/env python3
from polka.tools import calculate_routeid, print_poly
DEBUG = False


def _main():
    print("Insering irred poly (node-ID)")
    s = [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1],  # s1
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1],  # s2
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1],  # s3
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],  # s4      
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1],  # s5
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1],  # s6
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1],  # s7
        #[1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1],  # s8
        #[1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1],  # s9
        #[1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1],  # s10
    ]
    print("From h1 to h2 ====")
    # defining the nodes from h1 to h6
    nodes = [
        s[0],
        #s[1],
        #s[2],
        #s[3],
	    s[4],
	    s[5],
	    s[6],	
    ]
    # defining the transmission state for each node from h1 to h2
    o = [
        [1, 1, 0, 0, 0, 0],     # s1   
	    #[1, 0],  # s2
        #[1, 0],  # s3
        #[1, 0],  # s4
	    [1, 0],	# s5	
	    [1, 0],	#s6
	    [0, 0, 0, 0, 0, 1, 0, 0], # s7
    ]
    print("routeid h1 to h2 ====")
    print_poly(calculate_routeid(nodes, o, debug=DEBUG))
    print("From h1 to h2 ====")
    # defining the nodes from h1 to h6
    nodes = [
        s[0],
        #s[1],
        #s[2],
        #s[3],
	    s[4],
	    s[5],
	    s[6],	
    ]
    # defining the transmission weight for each node from h1 to h2
    w = [
        [0, 0, 0, 0, 0, 1],     # s1
        #[0, 0],  # s2
        #[0, 0],  # s3
        #[0, 0],  # s4
	    [0, 0],	# s5	
	    [0, 0], # s6
        [0, 0, 0, 0, 0, 0, 0, 0],  # s7
    ]
    print("wid h1 to h2 ====")
    print_poly(calculate_routeid(nodes, w, debug=DEBUG))

    print("From h1 to h2 ====")
    # defining the nodes from h2 to h1
    nodes = [
        s[6],
        s[5],
        s[4],
        #s[3],
	    #s[2],
	    #s[1],
	    s[0],
    ]
    # defining the transmission state for each node from h2 to h1
    o = [
        [1, 1, 0, 0, 0, 0, 0, 0],     # s7
	    [0, 1],  # s6
        [0, 1],  # s5
	    #[0, 1],	# s4	
	    #[0, 0], # s3
	    #[0, 1], # s2        
	    [0, 0, 0, 0, 0, 1], # s1
    ]
    print("routeid h2 to h1 ====")
    print_poly(calculate_routeid(nodes, o, debug=DEBUG))

    print("From h1 to h2 ====")
    # defining the nodes from h1 to h2
    nodes = [
        s[6],
        s[5],
        s[4],
        #s[3],
	    #s[2],
	    #s[1],
	    s[0],
    ]
     # defining the transmission weight for each node from h2 to h1
    w = [
        [0, 0, 0, 0, 0, 1], # s7
	    [0, 0],  # s6
        [0, 0],  # s5
	    #[0, 0],	# s4	
	    #[0, 0], # s3
	    #[0, 0], # s2        
	    [0, 0, 0, 0, 0, 0], # s1
    ]    
    print("wid h2 to h1 ====")
    print_poly(calculate_routeid(nodes, w, debug=DEBUG)) 


if __name__ == '__main__':
    _main()
