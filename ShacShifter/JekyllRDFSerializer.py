import logging
import uuid

# example class for Jekyll-RDF
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
        self.content.append('<div class ="container">\n')
        self.content.append("<h2>{{ page.rdf.iri }}</h2>\n")
        self.content.append("""{% assign type = page.rdf | rdf_property: "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>" %}\n""")

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

        if len(nodeShape.targetClass) > 1:
            self.content.append("Uebersicht")

            for tClass in nodeShape.targetClass:
                self.content.append(
                    '<h2>{type}</h2><br><h3>{short}</h3><br>'.format(
                        type=tClass, short=tClass.rsplit('/', 1)[-1]))

        elif len(nodeShape.targetClass) == 1:
            self.content.append('{{% if type.iri == "{type}" %}}\n\n'.format(
                type=nodeShape.targetClass[0].lower()))
            self.content.append("Ressource: <strong>{resource}</strong> ({type})<br><br>\n\n".format(
                resource=nodeShape.targetClass[0].rsplit('/', 1)[-1], type=nodeShape.targetClass[0]))


        for nodes in nodeShape.targetNode:
            self.logger.debug(nodes)
        self.logger.debug(
            'The following ressources need to be Objects of those predicates'
            )

        for nodes in nodeShape.targetObjectsOf:
            self.logger.debug(nodes)

        for nodes in nodeShape.targetSubjectsOf:
            self.logger.debug(nodes)

        for property in nodeShape.properties:
            shapeName = nodeShape.targetClass[0].rsplit('/', 1)[-1]
            content = self.propertyShapeEvaluation(property, fp, shapeName)
            
            self.content.append(content)

        resource_hack = nodeShape.targetClass[0].rsplit('/', 1)[-1]
        self.content.append(
                '{{% assign {resource} = page.rdf | rdf_property: "<{type}/{resource}>", nil, true %}} <br>\n'.format(
                    type=nodeShape.targetClass[0].rsplit('/', 1)[-2], resource=resource_hack.lower()))
        self.content.append('\n{{% for {instance}_instance in {resource} %}}\n<h3>{{{{ {instance}_instance.iri }}}}</h3>\n'.format(
                    instance=nodeShape.targetClass[0].rsplit('/', 1)[-1].lower(), resource=resource_hack.lower()))

        if len(nodeShape.targetClass) == 1:
            self.content.append("\n{% endfor %}\n{% endif %}\n<hr/>")

    def propertyShapeEvaluation(self, propertyShape, fp, shapeName):
        """Evaluate propertyShape and return HTML.

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
            lowercase_str = uuid.uuid4().hex[:4]
            label_jekyll = propertyShape.name.lower() \
                if propertyShape.isSet['name'] else propertyShape.path.lower().rsplit('/', 1)[-1]
            label_jekyll += "_"+ lowercase_str
            label = propertyShape.name.lower() \
                if propertyShape.isSet['name'] else propertyShape.path.lower().rsplit('/', 1)[-1]

            html += """{{% assign {label} = page.rdf | rdf_property: "<{uri}>", nil, true %}}\n""".format(
                    uri=uri, label=label_jekyll, type=shapeName.lower())

            html += """{{% if {label} %}}\n""".format(label=label_jekyll)

            html += """<dl>"""
            html += """<dt>{label}</dt>""".format(label=label)  
            html += """{{% for each_{label} in {label} %}}\n""".format(label=label_jekyll)
            html += """{{% if each_{label}.iri %}}\n""".format(label=label_jekyll)
            html += """<dd>Link: <a href={{{{each_{label}.page_url}}}}>{{{{each_{label}}}}}</a></dd>\n
                        {{% else %}}\n""".format(label=label_jekyll)
            html += """<dd>{{{{each_{label} }}}}</dd>\n{{% endif %}}\n""".format(label=label_jekyll)

            html += """\n{% endfor %}\n</dl>\n{% endif %}\n"""

        return html

