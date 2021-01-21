# selfDrivingCarGeneticAlgo
2d car learns to drive through genetic algorithims

MAKE SURE TO EXTRACT AFTER DOWNLOADING, that was my main problem when I tried to redownload this from github


Using my new and improved genetic algorithim that fixes a bunch of previous bugs, this one actually finds a solution evauntally. It runs a bit slow as doing 25 cars at once, with all the calculations might not be the best, but you can expirement with lower population it just takes longer to converge on the optimal solution. 

THINGS TO MESS WITH IF YOU WANT TO:

Under game.py: self.show_bounds, set it to True if you want to see all car sights, the boundaries, and the gates which give fitness.

Under neuralNetwork.py: self.populationSize, how many cars you want.

Under neuralNetwork.py: self.alive_after_death, how many cars, ranked by highest fitness, to breed and create the next generation


Some basic explanation on how the model works:

Step 1: Make 25 random neural networks, with the model.nodes being the nodes in the network and model.connections having a connection between the node with each strength

Step 2: Run the models through the simulated game and see how far they get

Step 2.5: The neural networks during the game are taking in the data called their sights based on how far away each wall is from them on left, forward, and right sides, but also the two 45 degree angles in front of them and predict whether to turn or go forward.

Step 3: Sorts them by their score which is determined by how many invisible gates they go through, and then keeps the best ones for crossover

Step 4: Refill the population with either crossovers (Basically combining two neural networks to get a slightly tweaked, but similar child of the two) or duplications of already alive neural networks with a slight mutation.

Repeats step 2-4 as long as you want
