# Simulation of the behavior of antagonistic shape memory alloy actuators

The simulation has been conducted using MATLAB.

## Contents

1. `main`: provides the interface to the model and the plotting functions  
2. `simTemp`: models the thermal characteristics of the individual shape memory alloy actuators (considering the shape of a helical spring)  
3. `simForce`:  models the mechanical response of the individual shape memory alloy actuators (the details of the model simplification are available in the paper)
4. `equilibr4CommonNode`: describes the cost-function for the simulation of the position of the common node of the shape memory alloy actuators. The actuators operate antagonistically, connected on one end at a common node. The position of the common node is determined by the equilibrium of forces acting on it. It is assumed that its motion corresponds to pseudo-static transitions between consecutive points. The transition 'dx' of the common node between consecutive points is the result of the changes in the force-magnitudes of the individual actuators, due to the thermal excitation. Since each transition corresponds to a 'pseudo-static' transition, the equilibrium of forces determines the location of the common node, following the changes of each actuator's (thermal) state  
5. `multiSpringPlotter`: plots the 'operating point' of the system on the model of each actuator (it is an elastoplastic operator)
