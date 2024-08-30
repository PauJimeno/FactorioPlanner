# Factorio Planner

Factorio Planner és una eina que optimitza layouts de blueprints del joc Factorio. El projecte s'ha fet com a treball de final de grau per la Universitat de Girona.
La base de l'optimitzador tracta d'un encoding usant SAT i l'eina Z3. A més l'eina té un front end web que permet generar, resoldre i visualitzar instàncies.

## Executar localment

- Clona el projecte

```bash
git clone https://github.com/PauJimeno/FactorioPlanner.git
```

- Situa't al directori del projecte

```bash
cd FactorioPlanner
```

- Crea un entorn virtual python3
```bash
python -m <nom de l'entorn> <directori on es guardarà>
```

- Activa l'entorn virtual
En linux:
```bash
source <nom del directori de l'entorn>/bin/activate
```
- En Windows (CMD)
```bash
<nom del directori de l'entorn>\Scripts\activate.bat
```
- Instal·la els requisits
```bash
pip install -r requirements.txt
```

- Executa el servidor i accedeix a la web a partir de l'URL imprès al terminal
```bash
python mainWeb.py
```

## Exemples de blueprints optimitzats

![solved_instance_29_output](https://github.com/user-attachments/assets/1a148008-0c84-4e83-ac59-bc4586564eb7)
![solved_instance_39_output](https://github.com/user-attachments/assets/2dfc8b10-1759-48ea-94be-a93c7db0b5f8)
![solved_instance_37_output](https://github.com/user-attachments/assets/a4d4ed1c-7183-44e3-acc8-6a5acb13dfa2)
![solved_instance_29_output](https://github.com/user-attachments/assets/e3626c38-7882-4a9b-bb2f-397b24984070)
![solved_instance_21_output](https://github.com/user-attachments/assets/97854d25-88f8-45b9-9a04-3ef644d489c9)

## Tecnologies usades

**Client:** JavaScript, HTML i CSS

**Server:** Python, Z3, Flask

## Documentació
La documentació del codi s'ha fet usant Sphinx i està hostejada amb GitHub pages
[Documentació](https://paujimeno.github.io/FactorioPlanner/)
