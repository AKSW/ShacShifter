from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape
from .ShapeParser import ShapeParser
import logging


# example class for
class RDFormsWriter:

    def __init__(self):
        self.logger = logging.getLogger()
        fp = open('rdformsExample.json', 'w')
        parser = ShapeParser()
        shapes = parser.parseShape('/home/shino/Documents/example.ttl')
        nodeShapes = shapes[0]
        for nodeShape in nodeShapes:
            self.exampleNodeShapeEvaluation(nodeShapes[nodeShape], fp)
        fp.close()

    def exampleNodeShapeEvaluation(self, nodeShape, fp):
        fp.write('{\n')
        self.loggger.warning(
            'No real "Label" for Nodeshapes -> add rdfs:label as option? otherwise check message?'
            )
        fp.write('"label":{')
        if nodeShape.isSet['message']:
            for lang, message in nodeShape.message.items():
                labels += ('"' + lang + '":"' + message + '", ')
        fp.write(labels[0:-3] + '},\n')
        fp.write('"root":"' + nodeShape.uri + '",')
        self.logger.warning(
            'description just like label has no correct'
            + ' sh:equvivalent on core shacl -> messages could be used'
            )
        self.logger.warning(
            'Unsure how to handle the sh:targetClass, targetSubjectOf and targetObjectOf'
            + ' properties, should they be constraints for all templates?')
        self.logger.warning('sh:targetNode has no use for forms')
        self.logger.warning(
            'sh:closed, sh:ignoredProperties, sh:nodeKind and sh:severity'
            + ' arent useful for forms either')
        fp.write('"templates":[\n')
        for property in nodeShape.properties:
            propertyString += ('{\n' + self.examplePropertyShapeEvaluation(property) + '\n},')
        fp.write(propertyString[0:-3] + ']\n}')

    def examplePropertyShapeEvaluation(self, propertyShape):
        if isinstance(propertyShape.path, dict):
            self.logger.warning('Complex path saves as Dictionary(unsure how to exactly use it):')
        else:
            if propertyShape.isSet['shIn']:
                # choice type
                pass
            else:
                # text type
                pass

# x = RDFormsWriter()
