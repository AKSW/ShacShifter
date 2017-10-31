from .ShapeParser import ShapeParser


# example class for
class ExampleWriter:

    def __init__(self):
        parser = ShapeParser()
        shapes = parser.parseShape('/home/shino/')
        for nodeShape in shapes[0]:
            self.exampleNodeShapeEvaluation(nodeShape)

    def exampleNodeShapeEvaluation(self, nodeShape):
        print('-------------------------------------')
        print('This NodeShape is called:')
        print(nodeShape.uri)
        print('This Resource needs to be in the following classes:')
        for tClass in nodeShape.targetClass:
            print(tClass)
        print('The following ressources are targets of this Shape(unnecessary for RDForms):')
        for nodes in nodeShape.targetNode:
            print(nodes)
        print('The following ressources need to be Objects of those predicates:')
        for nodes in nodeShape.targetObjectsOf:
            print(nodes)
        print('The following ressources need to be Subjects of those predicates:')
        for nodes in nodeShape.targetSubjectsOf:
            print(nodes)
        print('The Ressource has ' + len(nodeShape.properties) + 'properties')
        paths = []
        for property in nodeShape.properties:
            if not (property.path in paths):
                paths.append(property.path)
        print('...and ' + len(paths) + 'unique paths')
        for property in nodeShape.properties:
            self.examplePropertyShapeEvaluation(property)
        print('-------------------------------------')

    def examplePropertyShapeEvaluation(self, propertyShape):
        if isInstance(propertyShape.path, dict):
            print('Complex path saves as Dictionary:')
            print(propertyShape.path)
        else:
            print('Simple path:')
            print(propertyShape.path)
