# API examples

## Find Rodrigues specimens

```bash
curl 'http://127.0.0.1:8000/api/v1/specimens?island=Rodrigues&limit=25'
```

## Find photographed Solitaire material

```bash
curl 'http://127.0.0.1:8000/api/v1/specimens?scientific_name=Pezophaps%20solitaria&photograph_available=Yes'
```

## Retrieve one specimen with its linked evidence and Darwin Core row

```bash
curl 'http://127.0.0.1:8000/api/v1/specimens/MAS-SP-0001'
```

## Search all indexed entity types

```bash
curl 'http://127.0.0.1:8000/api/v1/search?q=Thirioux'
```

## Darwin Core: literature-derived material citations

```bash
curl 'http://127.0.0.1:8000/api/v1/dwc/occurrences?basis_of_record=MaterialCitation'
```

## CSV downloads

```bash
curl -O -J 'http://127.0.0.1:8000/api/v1/export/specimens.csv'
curl -O -J 'http://127.0.0.1:8000/api/v1/export/darwin-core-occurrence.csv'
```
