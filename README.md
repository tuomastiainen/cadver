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
* Creo Parametric 3.0 M 110
* Celery task queue


### Installing

Install the pip packages in requirements.txt.
Configure settings.py suitably

CADVER also requires the following software to work:

* pywin32 - Python for Windows Extensions (https://github.com/mhammond/pywin32)
* A running PTC Creo session with VBAPI installed and activated (please refer to PTC Creo VBAPI documentation).
* A running Celery worker (start with: python manage.py celeryd)


CD into the directory where you want to install CADVER

Clone the repository and install Python packages:

```
git clone git@github.com:tuomastiainen/cadver.git
mkvirtualenv env-name
cd cadver
pip install -r requirements.txt
```








#### Configuring Django settings

Edit settings.py:

* Configure a database backend, which can be either an SQL server (a MySQL server is running on the CADVER server) or SQLITE for development (commented out section in the settings)
* Set ROOT variable to the folder where CADVER is installed.
* Make sure that DEBUG = False in production (If debug is set to True, an auto authentication middleware is added and no login is required to the admin site)
* REFRESH_RATE is the delay between refreshes of the returned exercise table.The more users there are, the higher this delay should be.
Set a unique secret key for production (random 50 character string)
* When settings.DEBUG is True, the system administration interface requires no login.


#### Configuring Creo

* Install and activate the Creo VBAPI (run C:\Program Files\PTC\Creo 3.0\M110\Parametric\bin\vb_api_register.bat)

* Use the provided config.pro file or set the following settings manually. 

* For the mass prop checks and regeneration to work, the following settings are needed:
```
regen_failure_handling = resolve_mode
mass_property_calculate = automatic
```


If not properly configured, the following settings produce annoyances which do not matter, as the VBAPI can be used regardless:

* The settings to disable the Creo community popups did not work.

* last_session_directory_path. Creo requires that this is a local directory. Make sure that Windows UAC does not restrict Creo's write access to the folder.



### Running tests


The tests can be used to verify that the win32com/Creo VBAPI connection works.
Start a Creo session and run
```
python manage.py test
```

If run on a Windows system and a Creo session is running (parameter in test base class), the tests open a cube model and run some checks.


### Running the system
The development server can then be started with:
```
workon env-name
python manage.py runserver
```

To run check tasks via Creo, a Creo session and a Celery worker must be started:
```
workon env-name
python manage.py celeryd
```



## Using the system


### Web UI

The system consists of an interface which can be used to select an assignment and upload files. Before using the interface, session variables containing a unique user identifier and an assignment collection must be activated by visiting a link:
```
http://127.0.0.1:8000/
```


### Creating new assignments
* Add an Assignment collection entry in the Django admin panel. A collection name needs to be specified. A link can then be used to activate a collection and user to a session:  /login/?user_id=123123&ac_name=123


* Add an Assignment entry in the Django admin panel. Name, description and a correct file (optional, the correct file needs to be opened only if there is something data that was not specified in JSON) need to be specified. An optional order can also be specified. This defines the order in which the assignments are displayed in the list on the main page.


* Add Check templates which specify the check functions to be run.


* When files with the selected assignment are uploaded, a CheckTask object is created and Check objects are created from all the related CheckTemplates. If all of the checks pass, the CheckTask is marked as passed.

### Available check functions
#### MassPropChecker
The mass prop checker will regenerate the model with the given paramsets. The class then populates all null fields with real values from the assignment's correct file. If no null values are present, the correct file is not needed and will not be opened. By default, there is a 1% relative tolerance for each of the checks.

```
    [
        {
        "paramset" : {"THICK": false, "PARAM2": 50},
        "volume" : 500,
        "surface_area" : 400
        },
        {
        "paramset" : {"THICK": true, "PARAM2": 40},
        "volume" : null,
        "surface_area" : null
        }
    ]
```


The paramset can also be left empty ("paramset": {}). In this case, the model is not regenerated with any parameters, but the volume and surface area comparisons will still work. This could also probably be used on neutral file formats.

```
    [
        {
        "paramset" : {},
        "volume" : 300,
        "surface_area" : 200
        }
    [
```


#### RegenChecker
The regen checker tries to regenerate the model with all of the given paramsets and passes if the regenerations succeed.

```
    [
        {
        "paramset" : {"THICK": false, "PARAM2": 50}
        },
        {
        "paramset" : {"THICK": false, "PARAM2": 40}
        }
    ]
```

#### ModelTreeChecker

The model tree checker can be used to verify if the model tree of the returned file is correct when the model has been regenerated with a certain paramset (the paramset can also be left empty).  A base feature will need to be specified (by feature name). Creo starts listing child features from this base feature and forms the model tree (by feature type names) read into CADVER.

If the modeltree parameter is set to null, the model tree is read from the correct file of the assignment and the comparison is strict (the model trees must match exactly).

If the modeltree is provided as a list of feature type names, the comparison is sublist based (the given features must appear in the read model tree in that specific order).

```
    [
        {
        "base_feature": "BASE",
        "paramset" : {"THICK": false, "PARAM2": 50},
        "modeltree": ["PROTRUSION", "PROTRUSION"]
        },
        {
        "base_feature": "BASE",
        "paramset" : {"THICK": false, "PARAM2": 40},
        "modeltree": null
        }
    ]
```



#### MacroRunner

The MacroRunner is a class to run any custom functions with custom parameters. These will need to be implemented in the MacroRunner class.

```
    [
        {
        "custom_data" : {"do": "something"},
        "custom_funcs": ["custom_func1"]
        }
    ]
```


#### SaveMetaData

Can be used to dump any possible metadata associated to the model file. Unfortunately Creo does not save as much information as other CAD programs. Also a possibility would be to use hash of file or some filesystem info to save here.



#### SleepOneSecond

Does nothing but sleeps one second. Can be used for testing purposes. Also generates logs.





## Built With

* [Django](https://www.djangoproject.com/) - The web framework used
* [Celery](http://www.celeryproject.org/) - An open source distributed task queuing system
* [PTC Creo Parametric](https://www.ptc.com/en/products/cad/creo/parametric) - A commercial parametric CAD software package


## Authors

* **Tuomas Tiainen** - [tuomastiainen](https://github.com/tuomastiainen)


<!--## License-->


## Acknowledgments

* I would like to thank my thesis instructors Panu Kiviluoma and Kaur Jaakma for valuable advice and guidance during the project.
