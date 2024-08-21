# FLAPPY BIRD BUT NEAT
 AI learns to play Flappy Bird using the NEAT python module.

## Demo

## The NEAT Algorithm

### How NEAT Works
The NEAT algorithm (NeuroEvolution of Augmenting Topologies) is a method used to evolve neural networks. It's like a combination of genetic algorithms and neural networks. It works like this:
1. NEAT starts with a simple NN of few neurons and connections.
2. **Evolve by mutation:** The algorithm randomly modifies (mutates) the NN by for example:
   - Adding a new neuron.
   - Adding a new connection between neurons.
   - Changing the strength (weigh) of an existing connection.
3. **Combine Networks:** NEAT combines two NNs (parents) to create a new one (offspring). This is called *crossover*, it helps to mix and match successful traits from both parents.
4. **Speciation:** NEAT groups similar networks into species. Networks within one species compete with each other. This allows for new innovative structures to develop without being immediately outcompeted by larger, more complex networks.
5. **Fitness Evaluation:** The performance (fitness) of networks is tested. Best-performing networks are more likely to be selected for creating the next generation.
6. **Iterate and Improve:** From Generation to Generation, the networks become more complex and better suited to the task. NEAT automatically discovers the right balance between network complexity and performance.

### NEAT with Flappy Bird
- **Inputs:**
  - *bird.y* 
  - *distance to the upcoming top and bottom pipe:* You might only need one of these distances to keep it simple, as the network can learn to figure out the rest.
- **Output:**
  - Deside whether the bird should *jump* or *not jump*
- **Activation Function:**
  - *[TanH](https://neat-python.readthedocs.io/en/latest/_images/activation-tanh.png)* for the output neuron. It takes the output and squeezes it between -1 and 1. 
  - To decide if the bird should jump, we check if the output is greater than *0.5*.
- **Population Size:**
  - *20 birds:* The more birds, the more variety.
  - In first Generation, all birds have random NNs. After testing, the best performers are selected to create the next generation of 20 birds. This process repeats, with each generation improving upon the last.
- **Fitness Function:**
  - The fitness function is how we measure how well a bird is doing.  In this case, the bird that flies the furthest (x position) before hitting an obstacle scores the best.
- **Max Generation:**
  - *50 generations:* If no bird is perfect by then, the program stops.
