#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 15:41:26 2019

@author: mathijs
"""

import json

with open('nlogdata.json', 'r') as f:
    data = json.load(f)

print (data)