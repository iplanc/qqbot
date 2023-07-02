#!/usr/bin/env python
#Author: PlanC
#Date: 2023-07-01 20:15:03
#LastEditTime: 2023-07-01 21:58:36
#FilePath: \qqbot\keywords.py
#

import json
import re

class Keywords:
	words = {}

	def __init__(self):
		with open("./keywords.json", "r", encoding="utf-8") as f:
			self.words = json.loads(f.read())

	def block(self, content):
		for eachWord in self.words.keys():
			content = re.sub(eachWord, self.words.get(eachWord), content)
		return content.strip("\n")

	def add(self, key, value):
		self.words[key] = value
		with open("./keywords.json", "w", encoding="utf-8") as f:
			f.write(json.dumps(self.words, indent = 4, ensure_ascii = False))

	def delete(self, key):
		self.words.pop(key)
		with open("./keywords.json", "w", encoding="utf-8") as f:
			f.write(json.dumps(self.words, indent = 4, ensure_ascii = False))
