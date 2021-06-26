 

# Title  
	Computational Process Management for Laboratory Works of CPO Course    
	
# Group Name and List of Group Menmber      
	Group Name: PZEZ  
	Group Member:   Chen Jinhua && Wang Maoyu       
	
# Laboratory Work Number    
	3    
	
# Variant Description   
Implement a library for programming in the style ( implement  all processes as finite state machines in one global infinite loop with concurrency.) by using decorators to specify state machine handlers where all  oilerplate code with working with the state was hidden from a programmer. Decorators should support:  
    
	• call the function after a specific delay (like machine 1 in the manual coded example)      
	• simple sequence of states (like machine 2 in the manual coded example)    
	• conduction state transition between, based on a return value
	• work with IO (socket or standard input)
	• work with queue.
   
	
# Synopsis
Project simulate the concurrency of process running.
Implement all processes as finite state machines in an infinite loop (see decorator.execute () function). Have each state machine work with the environment in a non-blocking manner by waiting for some external event and change state after they are implemented. And Each cycle represents a unit of time.     

The function (in other words, the emulated process) that is decorated by the decorator is placed in the wait queue (in the code, it is stored in the variable "WORK_QUEUE").    

In execute() function, the wait queue is traversed, and execute the "processes" in the wait and the corresponding operations.Finally, The execution record is recorded in the variable "WORK_POOL".

Our code has been committed into the github https://github.com/JavaNickChen/Computational-Process-Management    

# Contribution Summary for Each Group Member
Wang and Chen discussed the implement design togother. Then, Wang implemented the Decorator.py and the test code. And Chen modified the unsuitable name of variables and files, added necessary comment and summarized the project.

   
