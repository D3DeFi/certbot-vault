"""
Created on 27 oct. 2022

@author: thomas
"""
import requests

while True:
    try:
        value = input("Value: ")

    except KeyboardInterrupt:
        print("Goodbye")
        requests.post("http://localhost:8055/clear-txt",json={
            "host": "_acme-challenge.toto123.fr."})
        break

    else:
        print(requests.post("http://localhost:8055/set-txt", json={
            "host": "_acme-challenge.toto123.fr.",
            "value": value},
             headers={"Content-Type": "application/x-www-form-urlencoded"}
        ))
