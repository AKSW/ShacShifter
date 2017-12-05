from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape
from .ShapeParser import ShapeParser
import logging


# example class for
class ExampleHTMLWriter:

    def __init__(self):
        self.logger = logging.getLogger()
        fp = open('testhtml.html', 'w')
        fp.write('<html> <body>\n')
        parser = ShapeParser()
        shapes = parser.parseShape('/home/shino/Documents/example.ttl')
        nodeShapes = shapes[0]
        for nodeShape in nodeShapes:
            self.exampleNodeShapeEvaluation(nodeShapes[nodeShape], fp)
        fp.write('</body></html>')
        fp.close()

    def exampleNodeShapeEvaluation(self, nodeShape, fp):
        fp.write("<form >\n")
        self.logger.warning('-------------------------------------')
        self.logger.warning('This NodeShape is called:')
        self.logger.warning(nodeShape.uri)
        self.logger.warning(
            'This Resource needs to be in the following classes'
            + '(can be used through rdfa annotation?):'
            )
        for tClass in nodeShape.targetClass:
            self.logger.warning(tClass)
        self.logger.warning(
            'The following ressources are targets of this Shape'
            + '(unnecessary for RDForms/Forms in general):'
            )
        for nodes in nodeShape.targetNode:
            self.logger.warning(nodes)
        self.logger.warning(
            'The following ressources need to be Objects of those predicates'
            + '(can be used through rdfa annotation?):'
            )
        for nodes in nodeShape.targetObjectsOf:
            self.logger.warning(nodes)
        self.logger.warning(
            'The following ressources need to be Subjects of those predicates'
            + '(can be used through rdfa annotation?):'
            )
        for nodes in nodeShape.targetSubjectsOf:
            self.logger.warning(nodes)
        for property in nodeShape.properties:
            self.examplePropertyShapeEvaluation(property, fp)
        self.logger.warning('-------------------------------------')
        fp.write("</form>")

    def examplePropertyShapeEvaluation(self, propertyShape, fp):
        if isinstance(propertyShape.path, dict):
            self.logger.warning('Complex path saves as Dictionary(unsure how to exactly use it):')
            self.logger.warning(propertyShape.path)
        else:
            self.logger.warning('Simple path:')
            self.logger.warning(propertyShape.path)
            if propertyShape.isSet['message']:
                if propertyShape.isSet['minCount']:
                    for i in range(0, propertyShape.minCount):
                        fp.write(
                            propertyShape.message['default'] + ' ' + str(i+1)
                            + ' : <br>\n <input type="text" name="' + propertyShape.path
                            + str(i+1) + '" value=""><br>\n'
                        )
                if propertyShape.isSet['maxCount']:
                    for i in range(max(propertyShape.minCount, 0), propertyShape.maxCount):
                        fp.write(
                            propertyShape.message['default'] + ' Optional Entry '
                            + str(i - propertyShape.minCount + 1)
                            + ' : <br>\n <input type="text" name="' + propertyShape.path
                            + str(i - propertyShape.minCount + 1) + '" value=""><br>\n'
                        )
            else:
                if propertyShape.isSet['minCount']:
                    for i in range(0, propertyShape.minCount):
                        fp.write(
                            propertyShape.path + ' [no name set] Entry ' + str(i+1)
                            + ' : <br>\n <input type="text" name="' + propertyShape.path
                            + str(i+1) + '" value=""><br>\n'
                        )
                if propertyShape.isSet['maxCount']:
                    for i in range(max(propertyShape.minCount, 0), propertyShape.maxCount):
                        fp.write(
                            propertyShape.path + ' [no name set] Optional Entry '
                            + str(i - propertyShape.minCount + 1)
                            + ' : <br>\n <input type="text" name="' + propertyShape.path
                            + str(i - propertyShape.minCount + 1) + '" value=""><br>\n'
                        )

# x = ExampleHTMLWriter()
