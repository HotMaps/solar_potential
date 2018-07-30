
# Calculation module documentation and guidelines

**Definition** :

A calulation Module (CM) is a plugin for hotmaps toolbox. It is able to extend toolbox functionality.

**How to connect my CM into Hotmaps toolbox?**

the CM can run on his own, but when it is on the same network of the the hotmaps toolbox API (HTAPI). the CM is automatically detected
 
the HTAPI will retrive the CM SIGNATURE and modify the frontend to allow the user to use the CM. and modify the user interface with the inputs it needs to be ran

**SIGNATURE** :
**************
It is some information that describes the calculation module and how to use it.the signature can be found in constants.py file. the SIGNATURE must be modiied by the Developer this signature can be divided into 2 parts,
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
    
***SIGNATURE FIELD***
*******************************
the signature comtained some parameter that are needed by the HTAPI for the data exchange:

 **category:**
 ***************
this is the category of the calculation module
 
**cm name:**
***************
this is the name of the calculation module, that will be displayed on the frontend GUI


**layers needed:**
*****************
layer that is needed to run the calculation module

**cm description:**
*****************
Description of purpose of the CM that will be displayed on the frontend GUI

**cm id:**
*****************

Unique identidier that isdefined by the WP4 leader

       
    

***INPUTS CALCULATION MODULE FIELD***
*******************************
the purpose of this part is giving the ability to the developer to build is own user interface.
 the JSON payload will be use to modify automatically the user interface. it's an array of inputs. see bellow what is an input object

 **Input name:**
 ***************
 input_name is the name that will be display on the frontend (User interface)
 
 **Input type:**
 **************
 the input is the graphical control element that user need to acces enter data. there are five possible inputs, see https://getuikit.com/docs/form for more information about the implentation of the frontend Graphical user interface (GUI)
 - input:
   
 ![alt text][logoinput]
           

This is a textbox where the user can type a value. 
 - select: 
 
 ![alt text][logoselect]
           

 this is a drop down menu that allows the user to choose one value from a list.
 - radio :
 
  
   ![alt text][logoradio]
           

 it allows the user to choose only one of a predefined set of mutually exclusive options.
 - checkbox 
 
 
 
 ![alt text][logocheckbox]
 
 this graphical component allows the user to choose between one of two possible mutually exclusive options
           
[logocheckbox]: https://upload.wikimedia.org/wikipedia/commons/2/2f/Checkbox2.png   ""  
 - range
 
  
 ![alt text][logorange]
 
the range is graphical control element with which a user may set a value by moving an indicator.
           
[logorange]: https://upload.wikimedia.org/wikipedia/commons/e/ed/Slider_%28computing%29_example.PNG ""
 
 
**Input Parameter Name:**
*************************
 it's the name of the parameter input  the CM needs to retrieve in order to launch some calculations 
   
**input value:**
*****************

it's a default value for the input that will be displayed on the user interface

**input min & max:**
*****************
this is the range of the input value needed, this will prevent from  mistake in the calculation 
         

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
* `app/api_v1/calculation_module.py ` -this is the place where the function for the CM belong
* `app/api_v1/transactions.py ` contain all the requests that allows to interacted with the CM




###Guidelines

retriving the code from git and start writing my own code

add a remote from the base_calculation module name it zeus


***Accessing and testing my CM:***
- for manual testing after launching the calculation module on a local (Docker or  computer environement )
go to the url(http://0.0.0.0:5001/apidocs/)

- for automatic tests type python cm/test.py on the terminal


    
    

Running my CM with docker:

```bash
docker-compose up -d --build
```
Running my CM in my computer:

```bash
python cm/run.py
```
***implementing my CM***

1 . modify the signature in constant.py to describe the of your CM

2 . modify the input parameter name in transaction.py in the input of calculation() from calculation module

2 . add main function  in calculation() functions (calculation_module.py )




```json


```


#TODO LIST of layers 
[logoinput]: https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Textbox2.gif/220px-Textbox2.gif ""

[logoselect]: https://upload.wikimedia.org/wikipedia/commons/d/d1/Drop-down_list_example.PNG ""
[logoradio]: https://upload.wikimedia.org/wikipedia/commons/c/cb/Radio_button.png ""