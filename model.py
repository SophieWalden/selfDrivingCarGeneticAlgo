import numpy as np
import random



class Model():

    def __init__(self):
        self.genModel()
        self.fitScore = -1



    def indexNodes(self, nodes, lookingFor):
        for j, List in enumerate(nodes):
            for i, value in enumerate(List):
                if value == lookingFor:
                    return (i, j)
        return -1

    def randomNode(self, nodes, baseNode):
        """Chooses a random node out of the list"""
        rng = np.random.default_rng()

        if baseNode == None:
            return random.choice(random.choice([node for node in nodes[:len(nodes) - 1] if len(node) != 0]))
        else:
            return random.choice(random.choice([node for node in nodes[self.indexNodes(nodes, baseNode)[1] + 1:] if
                                          len(node) != 0]))  # Indexes startingNode and gives node in a later Layer

    def genModel(self):
        # Layer 1 Nodes 1-5: Input nodes
        # Layer 2 Node 8: Middle nodes, may mutate for more
        # Layer 3 Nodes 6-7: Output nodes, either 0 or 1 for states 0 or 1
        self.nodes = np.array(
            [np.array([1, 2, 3, 4, 5]), np.array([]), np.array([]), np.array([]), np.array([6, 7, 8])])
        self.connections = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}

        # Starting connections
        for i in range(6):
            self.newConnection()


        #Pre-done model
        #self.nodes = np.array([list([1, 2, 3, 4, 5]), list([]), list([]), list([]),list([6, 7, 8])])
        #self.connections = {1: [[8, -0.38550895579950145]], 2: [[8, -0.5995181403412123], [7, -0.4237285674580474]], 3: [[6, -0.6282153477412172]], 4: [[8, 0.6057289123964497], [7, -0.37032096596267106]], 5: [[8, -0.8773839266357248], [7, 0.52]], 6: [], 7: [], 8: []}


    def newConnection(self):

        count = 0
        run = True
        startingNode = self.randomNode(self.nodes, None)

        endNode = self.randomNode(self.nodes, startingNode)
        while endNode in [node[0] for node in self.connections[startingNode]] and run:
            startingNode = self.randomNode(self.nodes, None)

            endNode = self.randomNode(self.nodes, startingNode)

            count += 1
            if count == 50:
                run = False

        if run:
            self.connections[startingNode].append([endNode, random.randint(-100, 100) / 100])

    def Summary(self):
        return [self.nodes, self.connections]

    def predict(self, baseValues):

        # Setting up base dict to establish connections
        values = {}


        for key, value in self.connections.items():
            if key in self.nodes[0]:
                values[key] = baseValues[key - 1]
            else:
                values[key] = 0



        # Adding all connections together
        for i in range(len(self.nodes) - 1):
            for key, value in self.connections.items():
                if key in self.nodes[i] and len(value) != 0:
                    for subValue in value:
                        try:
                            values[subValue[0]] += values[key] * subValue[1]
                        except Exception as e:

                            print(self.nodes, self.connections, values, value, key, subValue, e)

        valueList = [values[6], values[7], values[8]]

        return valueList.index(max(valueList))

    def crossover(self, parent2):
        # Breeds two brains with this one having dominant genes:
        babyModel = np.array(
            [[1, 2, 3, 4, 5], [], [], [], [6, 7, 8]])
        babyConnections = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [],  8: []}



        # The only layer that changes, since Layer 0 is input and Layer 2 is output
        nodeList = self.nodes[1:-1].copy()
        otherNodeList = parent2.nodes[1:-1].copy()

        for i, nodes in enumerate(nodeList):
            for node in nodes:
                if node in nodes:
                    babyModel[1+i] = np.append(babyModel[1 + i], node)
                    babyConnections[node] = []

                if self.indexNodes(otherNodeList, node) == -1 and random.randint(0, 100) >= 25 and self.indexNodes(
                        babyModel, node) == -1:
                    babyModel[1+i] = np.append(babyModel[1 + i], node)

                    babyConnections[node] = self.connections[node].copy()

        for i, otherNodes in enumerate(otherNodeList):
            for node in otherNodes:
                if node not in nodes and random.randint(0, 100) <= 25 and self.indexNodes(babyModel, node) == -1:
                    babyModel[1+i] = np.append(babyModel[1 + i], node)
                    babyConnections[node] = parent2.connections[node].copy()

        # Changing connections where necessary
        for key, value in babyConnections.items():
            if random.randint(0, 100) <= 75:
                if key in self.connections:
                    for value in self.connections[key]:
                        if self.indexNodes(babyModel, value[0]) != -1:
                            babyConnections[key].append(value.copy())
            elif random.randint(0, 100) <= 95:
                if key in parent2.connections:
                    for value in parent2.connections[key]:
                        if self.indexNodes(babyModel, value[0]) != -1:
                            babyConnections[key].append(value.copy())


        return babyModel, babyConnections

    def findMaxOf2dArray(self, array):
        highest = -99999
        highestIndex = -1
        for j, row in enumerate(array):
            for i, num in enumerate(row):
                if num > highest:
                    highest, highestIndex = num, [i, j]
        return highest

    def mutate(self):
        num = random.randint(0, 100)


        if num <= 80:  # Change Weights

            """
            slow and reliable mutation
            
            node = self.randomNode(self.nodes, None)

            for i, value in enumerate(self.connections[node]):
                if random.randint(0, 100) <= 10:
                    self.connections[node][i][1] = random.randint(-100, 100) / 100
                else:
                    self.connections[node][i][1] += random.gauss(0, 1) / 50
                    self.connections[node][i][1] = max(min(self.connections[node][i][1], 1), -1)

            """


            #Fast and unreliable multiple mutations (More fun basically)
            for key, value in self.connections.items():
                for i, subValue in enumerate(value):
                    if random.randint(0, 100) <= 10:
                        self.connections[key][i][1] = random.randint(-100, 100) / 100
                    else:
                        self.connections[key][i][1] += random.gauss(0, 1) / 50
                        self.connections[key][i][1] = max(min(self.connections[key][i][1], 1), -1)


        elif num <= 85:  # Add Connection
            self.newConnection()
        elif num <= 86:  # New node
            layer = random.randint(1, len(self.nodes) - 2)

            node = self.findMaxOf2dArray(self.nodes) + 1

            self.nodes[layer] = np.append(self.nodes[layer], node)
            self.connections[node] = []



