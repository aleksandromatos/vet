#!/bin/env python3

with open("laudo.txt", "r") as f:
    for line in f:
        line = line.strip()
        #print(line)

        if not line:
            continue

        if line.isupper():
            print(line)
