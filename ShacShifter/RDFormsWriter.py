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
                choiceItem = '"id":"' + propertyShape.path + '",\n"type":"choice",\n'
                self.logger.warning('Labels for choice items could be needed as well (message?)')
                if propertyShape.isSet['message']:
                    choiceItem += '"label":{'
                    for lang, message in propertyShape.message.items():
                        choiceItem += '"' + lang + '":"' + message + '", '
                    choiceItem = choiceItem[0:-3]
                    choiceItem += '},\n'
                self.logger.warning('description exists as well again...')
                choiceItem += '"property": "' + propertyShape.path + '",\n'
                if propertyShape.isSet['minCount']:
                    choiceItem += '"cardinality":{"min": ' + propertyShape.minCount + ','
                else:
                    choiceItem += '"cardinality":{"min": 1,'
                if propertyShape.isSet['maxCount']:
                    choiceItem += ' "max": ' + propertyShape.maxCount + '}\n'
                else:
                    choiceItem += ' "max": 1}\n'
                choiceItem += 'choices: [{\n' + '"value: "' + propertyShape.path + '",\n'
                self.logger.warning('choices and single choice items have labels and descriptions again')
                choiceItem += '"children":[\n'
                for index in range(0, len(propertyShape.shIn))
                    choiceItem += '{"_reference: "' + propertyShape.shIn[index] + '"}'
                    choices += '{"value": "' + propertyShape.shIn[index] + '"},\n'
                    choices += '{"label": "' + propertyShape.shIn[index] + '"}\n}'
                    if index != len(propertyShape.shIn -1):
                        choiceItem += ',\n'
                        choices += ','

                choiceItem += ']\n},'
                choiceItem += choices + '\n]'
            else:
                # text type
                pass

# x = RDFormsWriter()

choices: [{
        "top":true,
        "value": "http://example.com/instanceTop",
        "selectable": false,
        "label": {"sv": "Toppen", "en":"Ze top!"},
        "children":[
            {"_reference": "http://example.com/instance1"},
            {"_reference": "http://example.com/instance2"}
        ]
    },{
        "value": "http://example.com/instance1",
        "label": {"sv": "Matematik", "en":"Mathematics"},
        "description": {"sv": "Matematik är ett coolt ämne", "en":"Mathematics is a cool subject"}
    },{
        "value": "http://example.com/instance2",
        "label": {"sv": "Kemi", "en":"Chemistry"}
    }
]