



class gameDirector:

    def __init__(self,tree_size,root,ConnectsTo):
        self.tree_size = tree_size
        self.root = root
        self.ConnectsTo = ConnectsTo
        self.vertexPositioning = {}