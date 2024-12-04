# ESGF-Validate

A simple script written to validate the symmetric difference in content between two STAC endpoints. This can be run with:

```bash
poetry run python src/validate.py
```

By default (as a test) we are verifying the first 100 entries of `https://api.stac.esgf-west.org/` but this can be changed with commandline options.

```bash
usage: validate.py [-h] [-e ENDPOINTS ENDPOINTS] [-l LIMIT]

options:
  -h, --help            show this help message and exit
  -e ENDPOINTS ENDPOINTS, --endpoints ENDPOINTS ENDPOINTS
  -l LIMIT, --limit LIMIT
```

The script will raise an error if differences are found and details will be logged in a file `errors.log` and take the form:

```bash
2024-12-04 09:22:42 differences found!
id=CMIP6.PAMIP.UCI.E3SM-1-0.futSST-pdSIC.r1i1p1f1.Amon.clt.gr.v20211020
values_changed:
  root['properties']['grid_label']:
    com_value: gn
    ref_value: gr
```

where the `ref` and `com` endpoints will be identified in the logfile.