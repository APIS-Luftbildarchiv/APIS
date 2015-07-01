# -*- coding: utf-8 -*-
#-----------------------------------------------------------
#
# Points2One
# Copyright (C) 2010 Pavol Kapusta <pavol.kapusta@gmail.com>
# Copyright (C) 2010, 2013, 2015 Goyo <goyodiaz@gmail.com>
#
#-----------------------------------------------------------
#
# licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#---------------------------------------------------------------------

from PyQt4.QtCore import *
from qgis.core import *


class Points2Path(object):
    """Data processing for Point2One."""

    def __init__(self, pointLayer, displayName, closeLines=False, sortFields=None):
        self.pointLayer = pointLayer
        self.displayName = displayName
        self.closeLines = closeLines
        self.sortFields = sortFields

    def run(self):
        """Create the Vector Layer in Memory."""
        # create layer
        vlayer = QgsVectorLayer("LineString?crs=EPSG:4326", self.displayName, "memory")
        vlayer.setCrs(self.pointLayer.crs())
        provider = vlayer.dataProvider()
        #vlayer use crs of pointLayer


        vlayer.updateFields()

        for feature in self.iter_features():
            provider.addFeatures([feature])

        vlayer.updateExtents()

        return vlayer

    def iter_features(self):
        """Iterate over features with vertices in the input layer.

        For each consecutive group of points with the same value for the
        given attribute, yields a feature (polygon o polyline depending
        on wkb_ype) with vertices in those points.

        """
        for key, points in self.iter_groups():
            try:
                feature = self.make_feature(points)
            except ValueError, e:
                message = 'Key value %s: %s' % (key, e.message)
            else:
                yield feature

    def iter_groups(self):
        """Iterate over the input layer grouping by attribute.
    
        Returns an iterator of (key, points) pairs where key is the
        attribute value and points is an iterator of (QgsPoint,
        attributeMap) pairs.

        """
        points = self.iter_points()
        provider = self.pointLayer.dataProvider()

        # sorting
        fields = self.sortFields
        while fields:
            attr_idx = provider.fieldNameIndex(fields.pop())
            points = sorted(points, key=lambda p: p[1][attr_idx])

        return [(None, points)]

    def iter_points(self):
        """Iterate over the features of the input layer.
    
        Yields pairs of the form (QgsPoint, attributeMap).
        Each time a vertice is read hook is called.
    
        """
        provider = self.pointLayer.dataProvider()
        features = provider.getFeatures()
        feature = QgsFeature()
        while(features.nextFeature(feature)):
            geom = feature.geometry().asPoint()
            attributes = feature.attributes()
            yield(QgsPoint(geom.x(), geom.y()), attributes)

    def make_feature(self, points):
        """Return a feature with given vertices.
    
        Vertices are given as (QgsPoint, attributeMap) pairs. Returned
        feature is polygon or polyline depending on wkb_type.
    
        """
        point_list = []
        for point in points:
            point_list.append(point[0])
        attributes = point[1]
        feature = QgsFeature()

        if len(point_list) < 2:
            raise ValueError, 'Can\'t make a polyline out of %s points' % len(point_list)
        if len(point_list) > 2 and self.closeLines == True:
            if point_list[0] != point_list[-1]:
                point_list.append(point_list[0])
        feature.setGeometry(QgsGeometry.fromPolyline(point_list))

        feature.setAttributes(attributes)
        return feature