import logging


# example class for
class JekyllRDFSerializer:
    """A Serializer that writes Template for JekyllRDF"""

    logger = logging.getLogger('ShacShifter.JekyllRDFSerializer')
    content = []
    outputfile = ''

    def __init__(self, shapes, outputfile):
        try:
            fp = open(outputfile, 'w')
            self.outputfile = outputfile
            fp.close
        except Exception:
            raise Exception('Can''t write to file {}'.format(outputfile))

        self.content.append('''<html><head>
                                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css">
                            </head><body>\n''')
        self.logger.debug(shapes)
        self.content.append('<div class ="container">')
        self.content.append("<h1>{{ page.rdf.iri }}</h1>\n")

        nodeShapes = shapes[0]
        for nodeShape in nodeShapes:
            self.nodeShapeEvaluation(nodeShapes[nodeShape], fp)
        self.content.append("""</div><div>
                    <hr>
                    Footer<br/>
                    The data ist taken from: diggr.project
                </div>""")
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
        self.logger.debug(
            'This Resource needs to be in the following classes'
            + '(can be used through rdfa annotation?):'
            )

        if len(nodeShape.targetClass) > 1:
            self.content.append("Uebersicht")

            for tClass in nodeShape.targetClass:
                self.content.append(
                    '<h1>{type}</h1><br><h3>{short}</h3><br>'.format(
                        type=tClass, short=tClass.rsplit('/', 1)[-1]))

        elif len(nodeShape.targetClass) == 1:
            self.content.append("Ressource: {resource} ({type})<br>".format(
                resource=nodeShape.targetClass[0].rsplit('/', 1)[-1], type=nodeShape.targetClass[0]))

            self.content.append(
                '{{% assign {resource} = page.rdf | rdf_property: "<{type}>" %}} <br>'.format(
                    type=nodeShape.targetClass[0], resource=nodeShape.targetClass[0].rsplit('/', 1)[-1]))

        for nodes in nodeShape.targetNode:
            self.logger.debug(nodes)
        self.logger.debug(
            'The following ressources need to be Objects of those predicates'
            + '(can be used through rdfa annotation?):'
            )
            
        for nodes in nodeShape.targetObjectsOf:
            self.logger.debug(nodes)

        for nodes in nodeShape.targetSubjectsOf:
            self.logger.debug(nodes)

        for property in nodeShape.properties:
            shapeName = nodeShape.targetClass[0].rsplit('/', 1)[-1]
            content = self.propertyShapeEvaluation(property, fp, shapeName)
            self.content.append(content)

    def propertyShapeEvaluation(self, propertyShape, fp, shapeName):
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
            uri = propertyShape.path
            label = propertyShape.name \
                if propertyShape.isSet['name'] else propertyShape.path.rsplit('/', 1)[-1]

            html += """<dl>"""

            if not propertyShape.isSet['minCount'] and not propertyShape.isSet['maxCount']:
                html += """<dt>{label}</dt>
                    <dd>{{{{ {type} | rdf_property: "<{uri}>" }}}}</dd>""".format(
                        uri=uri, label=label, type=shapeName)
            else:
                html += """<dt>{label}</dt>
                    <dd>{{{{ {type} | rdf_property: "<{uri}>" }}}}""".format(
                        uri=uri, label=label, type=shapeName)
            '''
                if propertyShape.isSet['minCount']:
                    for i in range(0, propertyShape.minCount):
                        html += """ (min: {counter})</dd>\n""".format(counter=str(i+1))

                if propertyShape.isSet['maxCount']:
                    for i in range(max(propertyShape.minCount, 0), propertyShape.maxCount):
                        html += """ (max: {counter})</dd>\n""".format(
                            counter=str(propertyShape.minCount + i-1)) '''
            html += """</dl>"""
        
        return html
'''
        html+= '<h1>TEST:</h1>'
        uri = propertyShape.path
        html+= """<a class="page-link" href="{{{{ statement.object.page_url | prepend: site.baseurl }}}}">
            {{{{ statement.object }}}}
            {{% if statement.object.iri %}}
            ({{{{ statement.object | rdf_property: '{uri}' }}}})
            {{% endif %}}
          </a>""".format(uri=uri)'''
    
