# LocToMap

A PoC to display DNS LOC records on a map. It uses fastapi to serve a minimal api which responds to domains. A static map file is served from the root from where domains can be entered

Give it a spin, try ```SW1A2AA.find.me.uk``` for example

![image](https://github.com/semyonsh/LocToMap/assets/3471635/d7b2a86e-2460-4ed6-b614-9be030ac4122)


Some more information on the LOC record

https://en.wikipedia.org/wiki/LOC_record

https://www.rfc-editor.org/rfc/rfc1876.html




# Running it

Create a new virtualenv

```shell
python -m venv venv
```

Load the virtualenv and pull in the requirements

```shell
# Linux
source venv/bin/activate
# Windows
.\venv\Scripts\activate

pip install -r requirements.txt
```

Run the app with uvicorn

```shell
uvicorn main:app --reload
```
