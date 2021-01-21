import random
import numpy as np
import copy

from game import Game
from model import Model




class DodgeNN():
    def generateInitialPopulation(self):

        self.populationSize = 25
        self.alive_after_death = 5
        models = np.empty((self.populationSize), Model)

        for i in range(self.populationSize):
            models[i] = Model()

        self.models = models
        nn.generations = 0

        self.highest = 0

    def fitnessFunc(self):


        self.massSimulate(True)



    def sort_by_fitness(self):
        """I'm just wondering, why they don't have better sorting in numpy"""

        fitScores = [model.fitScore for model in self.models]
        fitScores.sort(reverse=True)
        tmp = []

        for model in self.models:
            model.checked = False

        for score in fitScores:
            for model in self.models:
                if model.fitScore == score and model.checked == False:
                    tmp.append(model)
                    model.checked = True


        self.models = tmp.copy()

    def killPopulation(self):

        self.sort_by_fitness()

        if nn.generations % 5 == 0:
            self.saveModel(self.models[0])

        movingOn = self.models[:self.alive_after_death]




        for model in self.models:
            self.models = np.delete(self.models, np.where(self.models == model))
        self.models = np.delete(self.models, 0)


        for model in movingOn:
            self.models = np.append(self.models, model)


        for i in range(self.populationSize - len(self.models)):
            self.models = np.append(self.models, self.genBabyModel()) ##Makes a child






    def genBabyModel(self):

        if random.randint(0, 100) <= 25:

            chosenModel = copy.deepcopy(random.choice(
                self.models[:self.alive_after_death]))
            model = Model() # Random duplicate of alive person
            model.nodes = chosenModel.nodes
            model.connections = chosenModel.connections

            return model
        else:

            # Baby making time between two parents
            parent1 = random.choice(self.models[:self.alive_after_death])

            #Finds another parent from same species
            parent2 = random.choice(self.models[:self.alive_after_death])

            while parent1 == parent2:
                parent2 = random.choice(self.models[:self.alive_after_death]) #You can't breed with yourself



            # Stronger parent get's priority in genes 75% to 25%
            if parent1.fitScore >= parent2.fitScore:
                babyModel, babyConnections = parent1.crossover(parent2)
            else:
                babyModel, babyConnections = parent2.crossover(parent1)



            baby = Model()
            baby.nodes, baby.connections = babyModel, babyConnections


            baby.mutate()  # This is how the evolution happens


            return baby

    def massSimulate(self, visualize):

        game = Game(len(self.models), visualize)
        information = game.start()


        while game.population_alive != 0:
            predictions = []
            for i, model in enumerate(self.models):

                predictions.append(model.predict(information[i]))

            information  = game.run(predictions)

        for i, player in enumerate(game.players):
            self.models[i].fitScore = player.fitness







    def saveModel(self, model):

        with open("checkpoint.txt", "w") as file:
            file.write(str(model.Summary()))


if __name__ == "__main__":


    nn = DodgeNN()

    nn.generateInitialPopulation()



    with open("avg.txt", "w") as file:
        file.write("")
    file.close()
    with open("highest.txt", "w") as file:
        file.write("")
    file.close()
    with open("lowest.txt", "w") as file:
        file.write("")
    file.close()

    while True:
        nn.fitnessFunc()
        avg = sum(model.fitScore for model in nn.models) / len(nn.models)
        print("Generation " + str(nn.generations) + " Average: " + str(round(avg, 2)))

        Min = round(min(node.fitScore for node in nn.models), 2)
        Max = round(max(node.fitScore for node in nn.models), 2)

        nn.killPopulation()

        #nn.killPopulation(0.2)
        with open("avg.txt", "a+") as file:
            file.write(str(round(avg, 2)) + "\n")
        file.close()
        with open("highest.txt", "a+") as file:
            file.write(str(round(Max, 2)) + "\n")
        file.close()
        with open("lowest.txt", "a+") as file:
            file.write(str(round(Min, 2)) + "\n")
        file.close()

        print("Generation " + str(nn.generations) + " Highest: " + str(Max))

        nn.generations += 1









