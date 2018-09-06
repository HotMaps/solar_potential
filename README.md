
# Calculation module documentation and guidelines

**requirement:**

- Having GIT command installed on your computer
- Having a Python version >= 3.5
- Having a Gdal version >= 2.0

**Definition** :

A calulation Module (CM) is a plugin for hotmaps toolbox which is able to extend toolbox functionality.

**How to connect a CM into the Hotmaps toolbox?**

```
*Registration and hearthbeat:

_______________________________
│                    │        │      1. Once in the network, CM won't stop trying to register until it get a response from the HTAPI. 
│         HTAPI      │ CM DB  │      2. Once registered HTAPI will request the CM in order to know if it's still alive or not.   
│                    │        │      3. While alive a CM can be computed from the frontend using the interface GUI it describe on its SIGNATURE.   
│____________________│________│ 
                        │    │
                        │    │
                        │    │    _________
                        │    └── │   CM2  │
                        │        │________│
                        │  __________
                        └─│  CM1    │
                          │________ │
 
   
```

The CM can run on its own, but when it is on the same network as the Hotmaps toolbox API (HTAPI), it will be automatically detected.
using Celery queue to register, HTAPI contains heartbear that will Check at anytime if a calculation is running or not. That means the achitecture for CMs is working in realtime
 
**Calculation module regitration**

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
0. Create a repository on github named name_of_my_module, create a folder on your computer named it "name_of_my_module", 
go inside your new folder create

1. Using git command on your terminal be ready to code:
```bash

git init
git remote add origin https://github.com/HotMaps/name_of_my_module.git # add a remote link to my repository
git remote add upstream https://github.com/HotMaps/base_calculation_module.git # add a remote link to the base calculation module (BCM)# .
git pull upstream master
git add .
git commit -m "first commit" #update changes
git push -u origin master # push the changes (minimum code for run) .

``` 

3. Start coding, switch branch from master to develop
```bash
git fetch && git checkout develop
``` 

4. After coding

```bash
git add .
git commit -m "message to describe the changes"
git push origin develop

``` 


5. Updating code with the base calculation module (BCM) code

```bash
git pull upstream master

``` 

If you encounter any issue like GIT conflict please contact CREM.



6. Release a version of my CM

After testing your calculation module using and update all the changes in develop branch
```bash
git fetch && git checkout master # retrieved master branch
git merge develop # update the changes from develop to master
git push origin master # push changes on master branch
``` 
now tag your version then take a snapshot on your current version
```bash
git fetch && git checkout master # retrieved master branch
git merge develop # update the changes from develop to master
git push origin master # push changes on master branch
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
Layers needed to run the calculation module

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

***Retriving list of layers available for CM***

please find in the link the list of layers available as input for a  CM (ressource name column):

https://docs.google.com/spreadsheets/d/1cGMRWkgIL8jxghrpjIWy6Xf_kS3Dx6LqGNfrCBLQ_GI/edit#gid=1730959780


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
    cd cm/
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
***Implementing my CM***

1. modify the signature in constant.py to describe your CM

2. modify the input parameter name in transaction.py in the input of calculation() from **calculation_module.py**

3. add main function in calculation() functions (calculation_module.py )

***multiple Raster as input***

1. In constants.py file there is the SIGNATURE file named layers *layers_needed* Layers needed to run the calculation module 
```bash
    "layers_needed": [
           "heat_density_tot",
           "cdd_curr_tif",
           "gfa_nonres_curr_density",
           "gfa_res_curr_density_lau"
       ],
```
 When HTAPI will be compute a CM, it will send a python dictionnary named  inputs_raster_selection in which there is a key ,the name of the layer for example heat_curr_density_tot and a value, the name of the files generated by HATPI  
 Raster wanted can be retrieved from the inputs_raster_selection dictionary
 
 ```bash
      clipped_heat_tot =  inputs_raster_selection["heat_tot_curr_density"]  
      clipped_gfa_tot =  inputs_raster_selection["gfa_tot_curr_density"]  
      
 ```
 ***multiple Raster as output***
 
 A CM can generate multiple layers as output. the calculation_module.calculation() function 
 must return all the path of the raster generated

 ```bash
       output_raster_path1,output_raster_path2, indicator1 ,indicator2= calculation_module.calculation()
       outputs_raster_selection['layes1'] = output_raster_path1
       outputs_raster_selection['layes2'] = output_raster_path2
 ```


```json


```










 
[logoinput]: https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Textbox2.gif/220px-Textbox2.gif ""

[logoselect]: https://upload.wikimedia.org/wikipedia/commons/d/d1/Drop-down_list_example.PNG ""
[logoradio]: https://upload.wikimedia.org/wikipedia/commons/c/cb/Radio_button.png ""