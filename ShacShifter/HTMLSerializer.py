import logging


# example class for
class HTMLSerializer:
    """A Serializer that writes HTML."""

    logger = logging.getLogger('ShacShifter.HTMLSerializer')
    content = []
    outputfile = ''

    def __init__(self, nodeShapes, outputfile):
        try:
            fp = open(outputfile, 'w')
            self.outputfile = outputfile
            fp.close
        except Exception:
            raise Exception('Can''t write to file {}'.format(outputfile))

        self.content.append('<html> <body>\n')
        self.logger.debug(nodeShapes)
        for nodeShape in nodeShapes:
            self.nodeShapeEvaluation(nodeShapes[nodeShape], fp)
        self.content.append('</body></html>')
        self.saveToFile()

    def saveToFile(self):
        fp = open(self.outputfile, 'w')
        fp.write(''.join(self.content))
        fp.close

    def nodeShapeEvaluation(self, nodeShape, fp):
        """Evaluate a nodeShape.

        args:   nodeShape a nodeShape object
                fp
        """
        self.content.append("<form >\n")
        self.logger.debug(
            'This Resource needs to be in the following classes'
            + '(can be used through rdfa annotation?):'
            )

        if len(nodeShape.targetClass) > 1:
            self.content.append("<p>Create new resource</p><br>")
            self.content.append("<fieldset>Type<br>")

            for tClass in nodeShape.targetClass:
                self.content.append(
                    '<input type="radio" name="type" value={type}>{short}</input><br>'.format(
                        type=tClass, short=tClass.rsplit('/', 1)[-1]))

            self.content.append("</fieldset><br>")
        elif len(nodeShape.targetClass) == 1:
            self.content.append("<p>Create new {}</p><br>".format(
                nodeShape.targetClass[0].rsplit('/', 1)[-1]))
            self.content.append(
                '<input type="hidden" name="type" value={type}></input><br>'.format(
                    type=nodeShape.targetClass[0]))

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
            content = self.propertyShapeEvaluation(property, fp)
            self.content.append(content)

        self.content.append("</form>")

    def propertyShapeEvaluation(self, propertyShape, fp):
        """Evaluate a propertyShape and return HTML.

        args:   propertyShape a propertyShape object
                fp
        return: html string
        """
        html = ''

        if isinstance(propertyShape.path, dict):
            # TODO handle complex paths (inverse, oneOrMorePath ...)
            self.logger.info('Complex path not supported, yet')
        elif isinstance(propertyShape.path, list):
            # TODO handle sequence paths
            self.logger.info('Sequence path not supported, yet')
        else:
            label = propertyShape.name \
                if propertyShape.isSet['name'] else propertyShape.path.rsplit('/', 1)[-1]

            if not propertyShape.isSet['minCount'] and not propertyShape.isSet['maxCount']:
                html += """{label}:<br>
                    <input type="text" name="{label}"><br>\n""".format(label=label)
            else:
                html += "<fieldset>{}<br>".format(label)

                if propertyShape.isSet['minCount']:
                    for i in range(0, propertyShape.minCount):
                        html += """{counter}:<br>
                            <input type="text" name="{label}[{counter}]"><br>\n""".format(
                            label=label, counter=str(i+1))

                if propertyShape.isSet['maxCount']:
                    for i in range(max(propertyShape.minCount, 0), propertyShape.maxCount):
                        html += """{counter}:<br>
                            <input type="text" name="{label}[{counter}]"><br>\n""".format(
                            label=label, counter=str(propertyShape.minCount + i-1))

                html += "</fieldset><br>"

        return html
