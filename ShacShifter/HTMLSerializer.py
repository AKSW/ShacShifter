from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape
from .modules.StringSupplier import StringSupplier
from .ShapeParser import ShapeParser
from XSDreg import XSDreg
import logging


class HTMLPart:
    """A super class that provides some methods."""
    def __str__(self):
        """Print HTMLFormTemplate object."""
        return ', '.join(['%s: %s' % (key, value) for (key, value) in self.__dict__.items()])

    def toHTML(self):
        # TODO consider BeautifulSoup for indention
        return self.htmlRepr()

    def htmlRepr(self):
        """Build HTML"""
        pass


class HTMLForm(HTMLPart):
    """The HTMLForm class."""
    def __init__(self, endpoint, ressourceIRI, namedGraph, targetClass, targetObjectsOf,
                 targetSubjectsOf):

        """Initialize an HTMLForm object."""
        self.label = ''
        self.description = {}
        self.root = ''
        self.formItems = []
        self.endpoint = '' if endpoint is None else endpoint
        self.ressourceIRI = '' if ressourceIRI is None else ressourceIRI
        self.namedGraph = '' if namedGraph is None else namedGraph
        self.targetClass = '' if targetClass is None else targetClass
        self.targetObjectsOf = '' if targetObjectsOf is None else targetObjectsOf
        self.targetSubjectsOf = '' if targetSubjectsOf is None else targetSubjectsOf

    def __str__(self):
        """Print HTMLFormTemplate object."""
        printdict = {}
        for key, value in self.__dict__.items():
            if key == 'formItems':
                printdict[key] = [str(template) for template in value]
            else:
                printdict[key] = value
        return ', '.join(['%s: %s' % (key, value) for (key, value) in printdict.items()])

    def htmlRepr(self):
        """Build HTML"""
        plainHTML = StringSupplier().header.format(self.endpoint, self.ressourceIRI,
                                                   self.namedGraph)
        if self.targetClass:
            plainHTML += StringSupplier().headerTargetClassSelect
            for target in self.targetClass:
                plainHTML += StringSupplier().headerTargetOption.format(target=target)
            plainHTML += StringSupplier().headerTargetClassSelectClose

        if self.targetObjectsOf:
            plainHTML += StringSupplier().headerTargetObjectsOfSelect
            for target in self.targetObjectsOf:
                plainHTML += StringSupplier().headerTargetOption.format(target=target)
            plainHTML += StringSupplier().headerTargetObjectsOfSelectClose
        if self.targetSubjectsOf:
            plainHTML += StringSupplier().headerTargetSubjectsOfSelect
            for target in self.targetSubjectsOf:
                plainHTML += StringSupplier().headerTargetOption.format(target=target)
            plainHTML += StringSupplier().headerTargetSubjectsOfSelectClose
        for item in self.formItems:
            plainHTML += item.htmlRepr()
        plainHTML += StringSupplier().submit
        plainHTML += StringSupplier().script
        return plainHTML


class HTMLFormTemplate(HTMLPart):
    """The HTMLForm template (super)class."""

    def __init__(self):
        """Initialize an HTMLFormTemplate object."""
        self.id = ''
        self.label = ''
        self.description = {}
        self.property = ''
        self.cardinality = {'min': 0, 'pref': 0}

    def htmlRepr(self):
        """Build HTML"""
        pass


class HTMLFormTextItem(HTMLFormTemplate):
    """A template item of type "group"."""

    def __init__(self):
        """Initialize an HTMLFormTextItem object."""
        super().__init__()
        self.cardinality = {'min': 0, 'pref': 1}
        self.type = 'text'
        self.nodeKind = ''
        self.datatype = ''
        self.pattern = ''

    def htmlRepr(self):
        """Build HTML"""
        maxSet = False
        if 'max' in self.cardinality:
            maxSet = True
        if self.pattern == '' and self.datatype != '':
            self.pattern = XSDreg.XSDreg().getRegex(self.datatype)
        plainHTML = StringSupplier().propertyMainDiv.format(
            self.id, self.cardinality['min'], self.cardinality['max'] if maxSet else 0,
            self.datatype, self.pattern, self.label)
        disableChoice = 'disabled' if self.datatype != '' else ''
        counter = 1
        minFields = self.cardinality['pref']
        if self.cardinality['min'] > 0:
            minFields = self.cardinality['min']
        while counter <= minFields:
            if maxSet and counter >= self.cardinality['max'] + 1:
                break

            datatypeLink = StringSupplier().datatypeLink.format(datatype=self.datatype)
            plainHTML += StringSupplier().propertySubDiv.format(
                'checked' if not disableChoice else '',
                'checked' if disableChoice else '',
                datatypeLink if self.datatype != '' else '',
                self.id, id=(self.id + str(counter)), choice=disableChoice, pattern=self.pattern)
            counter += 1
        nmin = ('min:' + str(self.cardinality['min']) + ' ') if self.cardinality['min'] else ""
        nmax = ('max:' + str(self.cardinality['max'])) if maxSet else ''
        plainHTML += StringSupplier().propertyMainDivClose.format(self.id, nmin, nmax)
        return plainHTML


class HTMLFormChoiceItem(HTMLFormTemplate):
    """A template item of type "group"."""

    def __init__(self):
        """Initialize an HTMLFormChoiceItem object."""
        super().__init__()
        self.type = 'choice'
        self.constraints = {}
        self.nodeKind = ''
        self.choices = []

    def __str__(self):
        """Print HTMLFormChoiceItem object."""
        printdict = {}
        for key, value in self.__dict__.items():
            if key == 'choices':
                printdict[key] = [str(choice) for choice in value]
        return ', '.join(['%s: %s' % (key, value) for (key, value) in printdict.items()])

    def htmlRepr(self):
        """Build HTML"""
        plainHTML = ""
        for choice in sorted(self.choices, key=lambda x: x.value, reverse=True):
            plainHTML += choice.htmlRepr()
        return plainHTML


class HTMLFormChoiceExpression(HTMLPart):
    """A class for choice expressions."""

    def __init__(self):
        """Initialize an HTMLFormChoiceExpression object."""
        self.value = ''
        self.label = ''
        self.description = ''
        self.selectable = True

    def __str__(self):
        """Print HTMLFormChoiceExpression object."""
        printdict = {}
        for key, value in self.__dict__.items():
            if key == 'children':
                printdict[key] = [str(child) for child in value]
            else:
                printdict[key] = value
        return ', '.join(['%s: %s' % (key, value) for (key, value) in printdict.items()])

    def htmlRepr(self):
        """Build HTML"""
        plainHTML = StringSupplier().choiceInput.format(
                self.label, self.label, self.label)


class HTMLSerializer:
    """A Serializer that writes HTML."""

    logger = logging.getLogger('ShacShifter.HTMLSerializer')
    forms = []
    outputfile = None

    def __init__(self, nodeShapes, outputfile=None, endpoint="", ressourceIRI="", namedGraph=""):
        """Initialize the Serializer and parse des ShapeParser results.

        args: shapes
              string outputfile
              string endpoint
              string ressourceIRI
              string namedGraph
        """
        try:
            fp = open(outputfile, 'w')
            self.outputfile = outputfile
            fp.close()
        except Exception:
            self.logger.error('Can\'t write to file {}'.format(outputfile))
            self.logger.error('Content will be printed to sys.')

        self.nodeShapes = nodeShapes
        self.endpoint = "http://localhost:8890/sparql" if (endpoint is None) else endpoint
        self.ressourceIRI = "http://www.example.org/a" if (ressourceIRI is None) else ressourceIRI
        self.namedGraph = "http://www.example.org/graph" if (namedGraph is None) else namedGraph

        counter = 0
        for nodeShape in nodeShapes:
            if counter == 0:
                form = self.createForm(nodeShapes[nodeShape])
                self.forms.append(form)
            else:
                self.logger.info('HTMLSerializer only supports displaying one Nodeshape.')
            counter += 1

    def write(self):
        """Write HTMLForm to file or sysout."""
        if self.outputfile:
            fp = open(self.outputfile, 'w')
            for form in self.forms:
                htmlForm = form.toHTML()
                print(StringSupplier().jqueryCDN)
                print(htmlForm)
                fp.write(StringSupplier().jqueryCDN)
                fp.write(htmlForm + '\n')
            fp.close()
        else:
            for form in self.forms:
                print(StringSupplier().jqueryCDN)
                print(form.toHTML())

    def createForm(self, nodeShape):
        """Evaluate a nodeShape.

        args:   NodeShape nodeShape
        """
        def addNodeLabel():
            label = 'Template: ' + nodeShape.uri
            if nodeShape.isSet['targetClass']:
                label = 'Create new Instance of: ' + ', '.join(nodeShape.targetClass)
            if nodeShape.isSet['targetNode']:
                label = 'Edit Instance of: ' + ', '.join(nodeShape.targetNode)
            if nodeShape.isSet['targetObjectsOf']:
                label = ', '.join(nodeShape.targetObjectsOf)
            if nodeShape.isSet['targetSubjectsOf']:
                label = 'Edit: '', '.join(nodeShape.targetSubjectsOf)
            return label

        def sortPropertyShapes(nodeShape):
            groups = list()
            groupedShapes = list()
            for propertyShape in nodeShape.properties:
                if propertyShape.isSet['group'] and propertyShape.group.isSet['order']:
                    if propertyShape.group.order not in groups:
                        groups.append(propertyShape.group.order)
                else:
                    if -1 not in groups:
                        groups.append(-1)
            groups.sort()
            for group in groups:
                shapes = list()
                for propertyShape in nodeShape.properties:
                    if propertyShape.isSet['group'] and propertyShape.group.isSet['order']:
                        if propertyShape.group.order == group:
                            shapes.append(propertyShape)
                    else:
                        if group == -1:
                            shapes.append(propertyShape)
                groupedShapes.append(sorted(shapes, key=lambda x: x.order, reverse=False))
            for shapes in groupedShapes:
                groupname = ''
                if shapes[0].isSet['group']:
                    groupname = '<b>' + shapes[0].group.rdfsLabel['default'] + '</b><br>'
                # isSet['name'] is still False if it was prior, important for later check
                shapes[0].name = '<hr>' + groupname + shapes[0].name
            return [y for x in groupedShapes for y in x]

        def addFormItems(nodeShape):
            """Check Propertey Shapes to fill the templates."""
            formItems = []
            for propertyShape in sortPropertyShapes(nodeShape):
                formItem = self.getFormItem(propertyShape, nodeShape.nodeKind)
                if formItem is not None:
                    formItems.append(formItem)
                    if propertyShape.isSet['nodes']:
                        subFormItems = []
                        for node in propertyShape.nodes:
                            subFormItems.extend(addFormItems(self.nodeShapes[node]))
                        if len(subFormItems) > 0:
                            formItems.extend(subFormItems)
            return formItems

        targetClass, targetObjectsOf, targetSubjectsOf = (None, )*3
        if nodeShape.isSet['targetClass']:
            targetClass = nodeShape.targetClass
        if nodeShape.isSet['targetObjectsOf']:
            targetObjectsOf = nodeShape.targetObjectsOf
        if nodeShape.isSet['targetSubjectsOf']:
            targetSubjectsOf = nodeShape.targetSubjectsOf
        form = HTMLForm(self.endpoint, self.ressourceIRI, self.namedGraph, targetClass,
                        targetObjectsOf, targetSubjectsOf)
        form.label = addNodeLabel()
        if nodeShape.isSet['message']:
            form.description = nodeShape.message
        form.root = nodeShape.uri
        if len(nodeShape.properties) > 0:
            form.formItems = addFormItems(nodeShape)
        return form

    def getFormItem(self, propertyShape, nodeKind):
        """Evaluate a propertyShape to serialize a formObject section.

        args:   PropertyShape propertyShape
        return: HTMLFormItem
        """
        def initFormItem():
            if propertyShape.isSet['shIn']:
                item = fillChoiceItem(HTMLFormChoiceItem())
            else:
                item = fillTextItem(HTMLFormTextItem())

            return fillBasicItemValues(item)

        def fillChoiceItem(item):
            item = fillBasicItemValues(item)
            item.cardinality = getCardinality()
            item.choices = self.getChoices(propertyShape)
            return item

        def fillTextItem(item):
            item.cardinality = getCardinality()
            if propertyShape.isSet['datatype']:
                item.datatype = propertyShape.datatype
            return item

        def fillBasicItemValues(item):
            item.id = propertyShape.path
            item.label = propertyShape.name if propertyShape.isSet['name'] else (
                                    propertyShape.name + propertyShape.path.rsplit('/', 1)[-1])
            item.description = getDescription()
            item.nodeKind = nodeKind
            item.pattern = propertyShape.pattern + propertyShape.flags
            return item

        def getDescription():
            if propertyShape.isSet['message']:
                if 'en' in propertyShape.message:
                    return propertyShape.message['en']
                elif 'default' in propertyShape.message:
                    return propertyShape.message['default']
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
            item = initFormItem()
            return item

    def getChoices(self, propertyShape):
        """Search for choice candidates in propertyShape and return a choice list.

        args: PropertyShape propertyShape
        returns: list
        """
        choices = []
        for choice in propertyShape.shIn:
            choiceItem = HTMLChoiceExpression()
            choiceItem.label = choice
            choiceItem.value = choice
            choices.append(choiceItem)

        return choices
