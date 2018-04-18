from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape
from .ShapeParser import ShapeParser
import json
import logging


class RDFormsPart:
    """A super class that provides some methods."""
    def __str__(self):
        """Print RDFormsTemplate object."""
        return ', '.join(['%s: %s' % (key, value) for (key, value) in self.__dict__.items()])

    def toJson(self):
        return json.dumps(self.jsonRepr(), indent=4)

    def jsonRepr(self):
        jd = {}
        for arg, value in self.__dict__.items():
            if value not in ['', []]:
                jd[arg] = value
        return jd


class RDFormsTemplateBundle(RDFormsPart):
    """The RDForms template bundle class."""

    def __init__(self):
        """Initialize an RDFormsTemplateBundle object."""
        self.label = ''
        self.description = {}
        self.root = ''
        self.templates = []
        self.cachedCoices = {}

    def __str__(self):
        """Print RDFormsTemplateBundle object."""
        printdict = {}
        for key, value in self.__dict__.items():
            if key == 'templates':
                printdict[key] = [str(template) for template in value]
            else:
                printdict[key] = value
        return ', '.join(['%s: %s' % (key, value) for (key, value) in printdict.items()])

    def jsonRepr(self):
        """Return a representation that is parseable by json encoder."""
        jd = {}
        for key, value in self.__dict__.items():
            if key == 'templates' and len(value) > 0:
                jd[key] = [template.jsonRepr() for template in value]
            else:
                jd[key] = value
        return jd


class RDFormsTemplate(RDFormsPart):
    """The RDForms template (super)class."""

    def __init__(self):
        """Initialize an RDFormsTemplate object."""
        self.id = ''
        self.label = ''
        self.description = {}
        self.property = ''
        self.cardinality = {'min': 0, 'pref': 0}


class RDFormsGroupItem(RDFormsTemplate):
    """A template item of type "group"."""

    def __init__(self):
        """Initialize an RDFormsGrouptItem object."""
        super().__init__()
        self.type = 'group'
        self.constraints = {}
        self.nodetype = ''
        self.styles = []
        self.cls = ''
        self.items = []
        self.automatic = False


class RDFormsPropertyGroupItem(RDFormsTemplate):
    """A template item of type "propertygroup"."""

    def __init__(self):
        """Initialize an RDFormsPropertyGrouptItem object."""
        super().__init__()
        self.type = 'propertygroup'
        self.constraints = {}
        self.nodetype = ''
        self.styles = []
        self.cls = ''
        self.items = []


class RDFormsTextItem(RDFormsTemplate):
    """A template item of type "group"."""

    def __init__(self):
        """Initialize an RDFormsTextItem object."""
        super().__init__()
        self.cardinality = {'min': 0, 'pref': 1}
        self.type = 'text'
        self.nodetype = ''
        self.datatype = ''
        self.styles = []
        self.cls = ''
        self.uriValueLabelProperties = []

    def jsonRepr(self):
        """Return a representation that is parseable by json encoder."""
        jd = {}
        for arg, value in self.__dict__.items():
            if value not in ['', []]:
                jd[arg] = value
        return jd


class RDFormsChoiceItem(RDFormsTemplate):
    """A template item of type "group"."""

    def __init__(self):
        """Initialize an RDFormsChoiceItem object."""
        super().__init__()
        self.type = 'choice'
        self.constraints = {}
        self.nodetype = ''
        self.styles = []
        self.cls = ''
        self.ontologyUrl = ''
        self.parentProperty = ''
        self.hierarchyProperty = ''
        self.isParentPropertyInverted = False
        self.isHierarchyPropertyInverted = False
        self.choices = []
        self.uriValueLabelProperties = []

    def __str__(self):
        """Print RDFormsChoiceItem object."""
        printdict = {}
        for key, value in self.__dict__.items():
            if key == 'choices':
                printdict[key] = [str(choice) for choice in value]
        return ', '.join(['%s: %s' % (key, value) for (key, value) in printdict.items()])

    def jsonRepr(self):
        """Return a representation that is parseable by json.dumps() method."""
        jd = {}
        for arg, value in self.__dict__.items():
            if value not in ['', []]:
                jd[arg] = value if arg != 'choices' else [choice.jsonRepr() for choice in value]
        return jd


class RDFormsChoiceExpression(RDFormsPart):
    """A a class for choice expressions."""

    def __init__(self):
        """Initialize an RDFormsChoiceExpression object."""
        self.value = ''
        self.label = ''
        self.description = ''
        self.top = False
        self.selectable = True
        self.children = {}

    def __str__(self):
        """Print RDFormsChoiceExpression object."""
        printdict = {}
        for key, value in self.__dict__.items():
            if key == 'children':
                printdict[key] = [str(child) for child in value]
            else:
                printdict[key] = value
        return ', '.join(['%s: %s' % (key, value) for (key, value) in printdict.items()])

    def jsonRepr(self):
        """Return a representation that is parseable by json.dumps() method."""
        jd = {}
        for arg, value in self.__dict__.items():
            if value not in ['', []]:
                jd[arg] = value
        return jd


class RDFormsSerializer:
    """A serializer for RDForms."""

    logger = logging.getLogger('ShacShifter.RDFormsSerializer')
    templateBundles = []
    outputfile = None

    def __init__(self, nodeShapes, outputfile=None):
        """Initialize the Serializer and parse des ShapeParser results.

        args: shapes
              string outputfile
        """
        try:
            fp = open(outputfile, 'w')
            self.outputfile = outputfile
            fp.close()
        except Exception:
            self.logger.error('Can''t write to file {}'.format(outputfile))
            self.logger.error('Content will be printed to sys.')

        for nodeShape in nodeShapes:
            bundle = self.createTemplateBundle(nodeShapes[nodeShape])
            self.templateBundles.append(bundle)

    def write(self):
        """Write RDForms to file or sysout."""
        if self.outputfile:
            fp = open(self.outputfile, 'w')
            for bundle in self.templateBundles:
                jsonstring = bundle.toJson()
                print(jsonstring)
                fp.write(jsonstring + '\n')
            fp.close()
        else:
            for bundle in self.templateBundles:
                print(bundle.toJson())

    def createTemplateBundle(self, nodeShape):
        """Evaluate a nodeShape.

        args:   NodeShape nodeShape
        """
        def addNodeLabel():
            label = {'en': 'Template: ' + nodeShape.uri}
            if nodeShape.isSet['targetClass']:
                label = {'en': 'Create new Instance of: ' + ', '.join(nodeShape.targetClass)}
            if nodeShape.isSet['targetNode']:
                label = {'en': 'Edit Instance of: ' + ', '.join(nodeShape.targetNode)}
            if nodeShape.isSet['targetObjectsOf']:
                label = {'en': ', '.join(nodeShape.targetObjectsOf)}
            if nodeShape.isSet['targetSubjectsOf']:
                label = {'en': 'Edit: '', '.join(nodeShape.targetSubjectsOf)}
            return label

        def addTemplates():
            """Check Propertey Shapes to fill the templates."""
            templates = []
            for propertyShape in nodeShape.properties:
                templates.append(self.getTemplate(propertyShape))
            return templates

        bundle = RDFormsTemplateBundle()
        bundle.label = addNodeLabel()
        if nodeShape.isSet['message']:
            bundle.description = nodeShape.message
        bundle.root = nodeShape.uri
        if len(nodeShape.properties) > 0:
            bundle.templates = addTemplates()

        return bundle

    def getTemplate(self, propertyShape):
        """Evaluate a propertyShape to serialize a template section.

        args:   PropertyShape propertyShape
        return: RDFormsItem
        """
        def initTemplateItem():
            if propertyShape.isSet['shIn']:
                item = fillChoiceItem(RDFormsChoiceItem())
            else:
                item = fillTextItem(RDFormsTextItem())

            return fillBasicItemValues(item)

        def fillChoiceItem(item):
            item = fillBasicItemValues(item)
            item.cardinality = getCardinality()
            item.choices = self.getChoices(propertyShape)
            return item

        def fillTextItem(item):
            item.cardinality = getCardinality()
            return item

        def fillBasicItemValues(item):
            item.id = propertyShape.path
            item.label = propertyShape.name if propertyShape.isSet['name'] else (
                                    propertyShape.path.rsplit('/', 1)[-1])
            item.description = getDescription()
            return item

        def getDescription():
            if propertyShape.isSet['message']:
                return propertyShape.message
            elif propertyShape.isSet['description']:
                return {'en': propertyShape.description}
            else:
                return {'en': 'This is about ' + propertyShape.path}

        def getCardinality():
            cardinality = {'min': 0, 'pref': 1}

            if propertyShape.isSet['minCount']:
                cardinality['min'] = propertyShape.minCount

            if propertyShape.isSet['maxCount']:
                cardinality['max'] = propertyShape.maxCount

            return cardinality

        if isinstance(propertyShape.path, dict):
            # TODO handle complex paths (inverse, oneOrMorePath ...)
            self.logger.info('Complex path not supported, yet')
        elif isinstance(propertyShape.path, list):
            # TODO handle sequence paths
            self.logger.info('Sequence path not supported, yet')
        else:
            item = initTemplateItem()
            return item

    def getChoices(propertyShape):
        """Search for choice candidates in propertyShape and return a choice list.

        args: PropertyShape propertyShape
        returns: list
        """
        choices = []
        for choice in propertyShape.shIn:
            choiceItem = RDFormsChoiceExpression()
            choiceItem.label = choice
            choiceItem.value = choice
            choiceItem.children = set(propertyShape.shIn) - set([choice])
            choices.append[choiceItem]

        return choices
