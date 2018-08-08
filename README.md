
# Calculation module documentation and guidelines

**Definition** :

A calulation Module (CM) is a plugin for hotmaps toolbox which is able to extend toolbox functionality.

**How to connect a CM into the Hotmaps toolbox?**

The CM can run on its own, but when it is on the same network as the Hotmaps toolbox API (HTAPI), it will be automatically detected.
 
the HTAPI will retrieve the CM SIGNATURE and modify the frontend to allow the user to use the CM and modify the user interface with the inputs it needs to be ran.


**Retrieving the calculation module base for my CM from git**:

Find bellow the architecture of the CMs. All the CMs inherit from the base calculation module (cm base)


```
*GIT Repository architecture*:

___________ 
│ CM base │
│_________│
  │
  │
  │   __________
  └── │   CM1  │
  │   │________│
  │
  │
  │   __________
  └── │   CM2  │
      │________│



```
0. Create a repository on github named name_of_my_module

1. Type on your terminal :
```bash
git clone https://github.com/HotMaps/base_calculation_module.git name_of_my_module
cd name_of_my_module

``` 

3. Link my code with my repositority in github 
```bash
git remote add mycm https://github.com/HotMaps/name_of_my_module.git
``` 

4. Now the CM is able to retrieve changes from the CM base with the command:


```bash
git pull origin master
``` 
5. To update my changes on my git repository for a version release on the toolbox

```bash
git add .
git commit -m "message"
git push mycm master
``` 

6.  To update changes on my git repository for a version in development 
if there is no develop branch please create it with this command :

```bash
git checkout -b develop
git push mycm develop
``` 

to update the develop
```bash
git add .
git commit -m "message"
git push mycm develop
``` 

**Connection with the main webservice HTAPI**
*******************************************


**SIGNATURE** :
**************
It's information that describes the calculation module and how to use it. The signature can be found in **constants.py** file. the SIGNATURE must be modified by the developer this signature can be divided into 2 parts,
see bellow:
   
    
    
    
    
    INPUTS_CALCULATION_MODULE=  [
        { 'input_name': 'Reduction factor',
          'input_type': 'input',
          'input_parameter_name': 'reduction_factor',
          'input_value': 1,
          'input_unit': 'none',
          'input_min': 1,
          'input_max': 10
            , 'cm_id': CM_ID
          },
        { 'input_name': 'Blablabla',
          'input_type': 'range',
          'input_parameter_name': 'bla',
          'input_value': 50,
          'input_unit': '',
          'input_min': 10,
          'input_max': 1000,
          'cm_id': CM_ID
          }
    ]
    
  
    
    SIGNATURE = {
        "category": "Buildings",
        "cm_name": CM_NAME,
        "layers_needed": [
            "heat_density_tot"
        ],
        "cm_url": "",
        "cm_description": "this computation module allows to divide the HDM",
        "cm_id": CM_ID,
        'inputs_calculation_module': INPUTS_CALCULATION_MODULE
    }
    
***SIGNATURE FIELDS***
*******************************
The signature contained some parameters that are needed by the main webservice HTAPI for the data exchange:

 **category:**
 ***************
This is the category of the calculation module
 
**cm name:**
***************
This is the name of the calculation module that will be displayed on the frontend Graphical user interface(GUI)


**layers needed:**
*****************
Layer that is needed to run the calculation module

**cm description:**
*****************
Description of purpose of the CM that will be displayed on the frontend GUI

**cm id:**
*****************

Unique identifier that is defined by the WP4 leader

       
    

***INPUTS CALCULATION MODULE FIELD***
*******************************
The purpose of this part is giving the ability to the developer to build is own user interface.
 the JSON payload will be use to modify automatically the user interface. it's an array of inputs. see bellow what is an input object

 **Input name:**
 ***************
 it is the name of the CM that will be displayed on the frontend (User interface)
 
 **Input type:**
 **************
 The input is the graphical control element that user need to access enter data. There are five possible inputs, see https://getuikit.com/docs/form for more information about the implementation of the frontend GUI
 - input:
   
 ![alt text][logoinput]
           

This is a textbox where the user can type a value. 
 - select: 
 
 ![alt text][logoselect]
           

 This is a drop down menu that allows the user to choose one value from a list.
 - radio :
 
  
   ![alt text][logoradio]
           

 It allows the user to choose only one of a predefined set of mutually exclusive options.
 - checkbox 
 
 
 
 ![alt text][logocheckbox]
 
 This graphical component allows the user to choose between one of two possible mutually exclusive options
           
[logocheckbox]: https://upload.wikimedia.org/wikipedia/commons/2/2f/Checkbox2.png   ""  
 - range
 
  
 ![alt text][logorange]
 
The range is graphical control element with which a user may set a value by moving an indicator.
           
[logorange]: https://upload.wikimedia.org/wikipedia/commons/e/ed/Slider_%28computing%29_example.PNG ""
 
 
**Input Parameter Name:**
*************************
 It's the input parameter name the CM needs to retrieve for calculations 
   
**input value:**
*****************

It's a default value for the input that will be displayed on the user interface

**input min & max:**
*****************
This is the range of the input value needed, this will prevent from mistake in the calculation 
         

### Application Structure:


```
cm/
├── app/  
│   ├── api_v1/
│   │    ├── __init__.py
│   │    ├── calculation_module.py 
│   │    ├── errors.py
│   │    └── transactions.py
│   │
│   │ 
│   │── decorators/
│   │   ├── __init__.py
│   │   ├── caching.py
│   │   ├── json.py
│   │   ├── paginate.py
│   │   └──rate_limit.py
│   │
│   │
│   ├── __init__.py
│   │── constant.py
│   │── logging.conf
│   │── utils.py
│   │
│   │
│   │── config/
│   │      ├── __init__.py
│   │      ├── development.py
│   │      ├── production.py
│   │      └── transactions.py
│   │
│   │── tests/
│   │      ├── __init__.py
│   │      ├── test_client.py
│   │      └── test.py
│   ├── __init__.py
│   ├── aync_consumer.py
│   ├── Dockerfile.py
│   ├── gunicorn-config.py
│   ├── requirements.txt
│   ├── run.py
│   ├── run_cm_services.sh
│   └── test.py
│    
├── .gitiginore
├── docker-compose-der.yml
├── LICENCE
└── README.md


*the place of the main function for the calculation module *
```
* `app/requirements.txt` - The list of Python framework  (PyPi) requirements.
* `app/api_v1/calculation_module.py ` - this is the place where the function for the CM belongs
* `app/api_v1/transactions.py ` contains all the requests that allows to interacted with the CM
* `app/constant.py ` contains the constants of the applications the most important constant is the SIGNATURE




###Guidelines




***Accessing and testing my CM:***
- For manual testing after launching the calculation module on a local (Docker or  computer environement )
    ```bash
    cd cm
    python run.py
    ```
    go to the url(http://0.0.0.0:5001/apidocs/)

- For automatic testing type on the terminal,
before running test you must run for downloading file in the directory 
    ```bash
    cd cm
    python run.py #give access to the service needeed for testing
    python test.py #tests if the compute fucntion is working and validate the integration of the CM 
    
    ```



***Running my CM with docker***:

In the root directory:
```bash
docker-compose up -d --build
```
***Running my CM in my computer(local environment):***

```bash
cd cm
python run.py
```
***implementing my CM***

1 . modify the signature in constant.py to describe your CM

2 . modify the input parameter name in transaction.py in the input of calculation() from **calculation_module.py**

2 . add main function in calculation() functions (calculation_module.py )




```json


```


#TODO LIST of layers 
[logoinput]: https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Textbox2.gif/220px-Textbox2.gif ""

[logoselect]: https://upload.wikimedia.org/wikipedia/commons/d/d1/Drop-down_list_example.PNG ""
[logoradio]: https://upload.wikimedia.org/wikipedia/commons/c/cb/Radio_button.png ""