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
        break

    else:
        res = requests.post("http://localhost:8055/set-txt", json={
            "host": "_acme-challenge.toto123.fr.",
            "value": "nGG-0BfA3dTzMRIBTOXeMaQsh0_HqfWHCyZYeJ5as3M"},
            headers={"Accept": "*/*", "Content-Type": "application/x-www-form-urlencoded"}
        )

        print(res.content)
