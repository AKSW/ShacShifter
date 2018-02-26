from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape
from .ShapeParser import ShapeParser
import logging


# example class for
class HTMLSerializer:
    """A Serializer that writes HTML."""

    logger = logging.getLogger('ShacShifter.HTMLSerializer')
    content = []
    outputfile = ''

    def __init__(self, shapes, outputfile):
        try:
            fp = open(outputfile, 'w')
            self.outputfile = outputfile
            fp.close
        except Exception:
            raise Exception('Can''t write to file {}'.format(outputfile))

        self.content.append('<html> <body>\n')
        self.logger.debug(shapes)
        nodeShapes = shapes[0]
        for nodeShape in nodeShapes:
            self.nodeShapeEvaluation(nodeShapes[nodeShape], fp)
        self.content.append('</body></html>')
        print(self.content)

    def nodeShapeEvaluation(self, nodeShape, fp):
        self.content.append("<form >\n")
        self.logger.debug('This NodeShape is called:')
        self.logger.debug(nodeShape.uri)
        self.logger.debug(
            'This Resource needs to be in the following classes'
            + '(can be used through rdfa annotation?):'
            )

        for tClass in nodeShape.targetClass:
            self.logger.debug(tClass)
        self.logger.debug(
            'The following ressources are targets of this Shape'
            + '(unnecessary for RDForms/Forms in general):'
            )

        for nodes in nodeShape.targetNode:
            self.logger.debug(nodes)
        self.logger.debug(
            'The following ressources need to be Objects of those predicates'
            + '(can be used through rdfa annotation?):'
            )

        for nodes in nodeShape.targetObjectsOf:
            self.logger.debug(nodes)
        self.logger.debug(
            'The following ressources need to be Subjects of those predicates'
            + '(can be used through rdfa annotation?):'
            )

        for nodes in nodeShape.targetSubjectsOf:
            self.logger.debug(nodes)

        for property in nodeShape.properties:
            self.propertyShapeEvaluation(property, fp)

        self.content.append("</form>")

    def propertyShapeEvaluation(self, propertyShape, fp):
        if isinstance(propertyShape.path, dict):
            self.logger.debug('Complex path saves as Dictionary(unsure how to exactly use it):')
            self.logger.debug(propertyShape.path)
        else:
            self.logger.debug('Simple path:')
            self.logger.debug(propertyShape.path)

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
