from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape
from .ShapeParser import ShapeParser
import logging


# example class for
class RDFormsSerializer:
    """A serializer for RDForms."""

    logger = logging.getLogger('ShacShifter.RDFormsSerializer')
    content = []
    outputfile = None

    def __init__(self, shapes, outputfile):
        try:
            fp = open(outputfile, 'w')
            self.outputfile = outputfile
            fp.close()
        except Exception:
            self.logger.error('Can''t write to file {}'.format(outputfile))
            self.logger.error('Content will be printed to sys.')

        nodeShapes = shapes[0]
        self.propertyShapes = shapes[1]

        self.content.append('{\n')

        for nodeShape in nodeShapes:
            self.nodeShapeEvaluation(nodeShapes[nodeShape])

        self.content.append('}')

    def write(self):
        """Write RDForms to file oder sysout."""
        if self.outputfile:
            self.saveToFile()
        print(''.join(self.content))

    def saveToFile(self):
        fp = open(self.outputfile, 'w')
        fp.write(''.join(self.content))
        fp.close()

    def nodeShapeEvaluation(self, nodeShape):
        """Evaluate a nodeShape.

        args:   nodeShape a nodeShape object
        """
        def addNodeLabel():
            if nodeShape.isSet['targetClass']:
                label = '"en":"Create new ' + ', '.join(nodeShape.targetClass) + '"'
            if nodeShape.isSet['targetNode']:
                label = '"en":"Edit ' + ', '.join(nodeShape.targetNode) + '"'
            if nodeShape.isSet['targetObjectsOf']:
                label = '"en":"Edit ' + ', '.join(nodeShape.targetObjectsOf) + '"'
            if nodeShape.isSet['targetSubjectsOf']:
                label = '"en":"Edit ' + ', '.join(nodeShape.targetSubjectsOf) + '"'
            return '  "label":{' + label + '},\n'

        def addNodeDescription():
            descriptions = ''
            if nodeShape.isSet['message']:
                for lang, message in nodeShape.message.items():
                    descriptions += ('"' + lang + '":"' + message + '", ')
            return '  "description":{' + descriptions + '},\n'

        def addNodeRoot():
            return '  "root":"' + nodeShape.uri + '",\n'

        def addTemplates():
            """Check Propertey Shapes to fill the templates."""
            templates = ['  "templates":[\n']
            for id, propertyShape in self.propertyShapes.items():
                templates.append(self.getTemplate(propertyShape))
            templates.append('\n    ]\n')
            return ''.join(templates)

        self.content.append(addNodeLabel())
        self.content.append(addNodeDescription())
        self.content.append(addNodeRoot())
        # self.content.append(addTemplates())
        if len(nodeShape.properties) > 0:
            self.content.append(addTemplates())

    def getTemplate(self, propertyShape):
        """Evaluate a propertyShape to serialize a template section.

        args:   propertyShape a propertyShape object
        return: template string
        """
        def getId():
            return '\t\t"id":"' + propertyShape.path + '",\n'

        def getProperty():
            return '\t\t"property":"' + propertyShape.path + '",\n'

        def getType():
            if propertyShape.isSet['shIn']:
                return '\t\t"type":"choice",\n' + getChoices()
            else:
                return '\t\t"type":"string",\n'

        def getLabel():
            label = propertyShape.name \
                if propertyShape.isSet['name'] else propertyShape.path.rsplit('/', 1)[-1]
            return '\t\t"label":"' + label + '",\n'

        def getDescription():
            if propertyShape.isSet['message']:
                message = ''
                for lang, message in propertyShape.message.items():
                    message += '"' + lang + '":"' + message + '", '
            elif propertyShape.isSet['description']:
                message = '"en":"' + propertyShape.description + '"'
            else:
                message = '"en":"' + propertyShape.path.rsplit('/', 1)[-1] + '"'
            return '\t\t"label":{' + message + '},\n'

        def getCardinality():
            cardinality = '\t\t"cardinality":{'

            if propertyShape.isSet['minCount']:
                cardinality += '"min": ' + propertyShape.minCount + ','
            else:
                cardinality += '"min": 0,'

            if propertyShape.isSet['maxCount']:
                cardinality += ' "max": ' + propertyShape.maxCount

            cardinality += '}\n'
            return cardinality

        def getChoices():
            choiceItem = ''
            for index in range(0, len(propertyShape.shIn)):
                choiceItem += '{"_reference: "' + propertyShape.shIn[index] + '"}'
                choices = '{"value": "' + propertyShape.shIn[index] + '"},\n'
                choices += '{"label": "' + propertyShape.shIn[index] + '"}\n}'

                if index != len(propertyShape.shIn - 1):
                    choiceItem += ',\n'
                    choices += ','

            choiceItem += ']\n},'
            choiceItem += choices + '\n]'
            return choiceItem

        template = ['\t{\n']

        if isinstance(propertyShape.path, dict):
            # TODO handle complex paths (inverse, oneOrMorePath ...)
            self.logger.info('Complex path not supported, yet')
        elif isinstance(propertyShape.path, list):
            # TODO handle sequence paths
            self.logger.info('Sequence path not supported, yet')
        else:
            template.append(getId())
            template.append(getType())
            template.append(getLabel())
            template.append(getDescription())
            template.append(getCardinality())
            template.append('\t},')
            return ''.join(template)

            # choiceItem += 'choices: [{\n' + '"value: "' + propertyShape.path + '",\n'
            # self.logger.debug(
            #     'choices and single choice items have labels and descriptions again')
            # choiceItem += '"children":[\n'
            #
            # for index in range(0, len(propertyShape.shIn)):
            #     choiceItem += '{"_reference: "' + propertyShape.shIn[index] + '"}'
            #     choices = '{"value": "' + propertyShape.shIn[index] + '"},\n'
            #     choices += '{"label": "' + propertyShape.shIn[index] + '"}\n}'
            #
            #     if index != len(propertyShape.shIn - 1):
            #         choiceItem += ',\n'
            #         choices += ','
            #
            # choiceItem += ']\n},'
            # choiceItem += choices + '\n]'


# x = RDFormsWriter()

# choices: [{
#         "top":true,
#         "value": "http://example.com/instanceTop",
#         "selectable": false,
#         "label": {"sv": "Toppen", "en":"Ze top!"},
#         "children":[
#             {"_reference": "http://example.com/instance1"},
#             {"_reference": "http://example.com/instance2"}
#         ]
#     },{
#         "value": "http://example.com/instance1",
#         "label": {"sv": "Matematik", "en":"Mathematics"},
#         "description": {"sv": "Matematik är ett coolt ämne", "en":"Mathematics is a cool subject"}
#     },{
#         "value": "http://example.com/instance2",
#         "label": {"sv": "Kemi", "en":"Chemistry"}
#     }
# ]
