# CADVER

CADVER is a prototype online system for automatic assessment of mechanical engineering CAD exercises. CADVER was implemented as a part of the author's masters thesis in Aalto University School of Engineering. The system prototype was tested to assess Creo Parametric 3.0 exercises on a course of 102 students.

Using CAD software API's, CADVER compares returned CAD modelling exercises to specified correct files or given information.

<!--![CADVER main page](/cadverui.png)-->


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Overview


CADVER runs on Python 3.5 and requires Creo Parametric 3.0. M110

The following software are required to use CADVER:


* pywin32 - Python for Windows Extensions (https://github.com/mhammond/pywin32)
* Creo Parametric
* Celery


### Installing

Install the pip packages in requirements.txt.
Configure settings.py suitably

CADVER also requires the following software to work:

* pywin32 - Python for Windows Extensions (https://github.com/mhammond/pywin32)
* A running PTC Creo session with VBAPI installed and activated (please refer to PTC Creo VBAPI documentation).
* A running Celery worker (start with: python manage.py celeryd)


The development server can then be started with:
```
python manage.py runserver
```

The basic migrations provide a dummy database which can be used to test the system. When settings.DEBUG is True, the system administration interface requires no login.



## Using the system


### Web UI

The system consists of an interface which can be used to select an assignment and upload files. Before using the interface, session variables containing a unique user identifier and an assignment collection nam must be activated by visiting a link:
```
http://127.0.0.1:8000/
```

### CREO VBAPI


The system can be used to run checks via Creo's VBAPI. When developing, the checks and the connection can be tested by running creo.py, which is the core Creo wrapper of the system:
```
python creo.py
```



## Running the tests

Basic unit tests have been implemented for CADVER. The tests only cover functionality in Django. If a Creo session is running (parameter in test base class), the tests actually open a model and run checks.

```
python manage.py test
```


## Built With

* [Django](https://www.djangoproject.com/) - The web framework used
* [Celery](http://www.celeryproject.org/) - An open source distributed task queuing system
* [PTC Creo Parametric](https://www.ptc.com/en/products/cad/creo/parametric) - A commercial parametric CAD software package


## Authors

* **Tuomas Tiainen** - [tuomastiainen](https://github.com/tuomastiainen)


<!--## License-->


## Acknowledgments

* I would like to thank my thesis instructors Panu Kiviluoma and Kaur Jaakma
