#!/usr/bin/env python3

import rdflib


class ShapeParser:
    def __init__(self, inputFilePath):
        g = rdflib.Graph()
        result = g.parse(inputFilePath, format='turtle')
        print(len(g))
        for stmt in g:
            print(stmt)

# class Shape:
