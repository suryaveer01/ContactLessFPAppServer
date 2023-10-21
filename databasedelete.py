import os
import re
class databasedeletehelper:

    def __init__(self) -> None:
        
        print("__init__")



    def deleteenrolledimages(data):

        for key,value in data.items():
            print('datakeyvalue',key,value)
            if os.path.exists(value):
                os.remove(value)
            else:
                print("The file does not exist:",key) 

        # data_keys = data.keys()

        # if('Picture_Right' in data_keys and data['Picture_Right'] is not None):
        #     os.remove(data['Picture_Right'])
        # if('Picture_Left' in data_keys and data['Picture_Left'] is not None):
        #     os.remove(data['Picture_Left'])
        # if('Annotated_fingerprintRight' in data_keys and data['Annotated_fingerprintRight'] is not None):
        #     os.remove(data['Annotated_fingerprintRight'])
        # if('Annotated_fingerprintLeft' in data_keys and data['Annotated_fingerprintLeft'] is not None):
        #     os.remove(data['Annotated_fingerprintLeft'])
        # if('Segmented_fingerprintRight0' in data_keys and data['Segmented_fingerprintRight0'] is not None):
        #     os.remove(data['Segmented_fingerprintRight0'])
        # if('Segmented_fingerprintRight1' in data_keys and data['Segmented_fingerprintRight1'] is not None):
        #     os.remove(data['Segmented_fingerprintRight1'])
        # if('Segmented_fingerprintRight2' in data_keys and data['Segmented_fingerprintRight2'] is not None):
        #     os.remove(data['Segmented_fingerprintRight2'])
        # if('Segmented_fingerprintRight3' in data_keys and data['Segmented_fingerprintRight3'] is not None):
        #     os.remove(data['Segmented_fingerprintRight3'])
        # if('Segmented_fingerprintLeft0' in data_keys and data['Segmented_fingerprintLeft0'] is not None):
        #     os.remove(data['Segmented_fingerprintLeft0'])
        # if('Segmented_fingerprintLeft1' in data_keys and data['Segmented_fingerprintLeft1'] is not None):
        #     os.remove(data['Segmented_fingerprintLeft1'])
        # if('Segmented_fingerprintLeft2' in data_keys and data['Segmented_fingerprintLeft2'] is not None):
        #     os.remove(data['Segmented_fingerprintLeft2'])
        # if('Segmented_fingerprintLeft3' in data_keys and data['Segmented_fingerprintLeft3'] is not None):
        #     os.remove(data['Segmented_fingerprintLeft3'])

        
        # if('Enhanced_fingerprintRight0' in data_keys and data['Enhanced_fingerprintRight0'] is not None):
        #     os.remove(data['Enhanced_fingerprintRight0'])
        # if('Enhanced_fingerprintRight1' in data_keys and data['Enhanced_fingerprintRight1'] is not None):
        #     os.remove(data['Enhanced_fingerprintRight1'])
        # if('Enhanced_fingerprintRight2' in data_keys and data['Enhanced_fingerprintRight2'] is not None):
        #     os.remove(data['Enhanced_fingerprintRight2'])
        # if('Enhanced_fingerprintRight3' in data_keys and data['Enhanced_fingerprintRight3'] is not None):
        #     os.remove(data['Enhanced_fingerprintRight3'])
        # if('Enhanced_fingerprintLeft0' in data_keys and data['Enhanced_fingerprintLeft0'] is not None):
        #     os.remove(data['Enhanced_fingerprintLeft0'])
        # if('Enhanced_fingerprintLeft1' in data_keys and data['Enhanced_fingerprintLeft1'] is not None):
        #     os.remove(data['Enhanced_fingerprintLeft1'])
        # if('Enhanced_fingerprintLeft2' in data_keys and data['Enhanced_fingerprintLeft2'] is not None):
        #     os.remove(data['Enhanced_fingerprintLeft2'])
        # if('Enhanced_fingerprintLeft3' in data_keys and data['Enhanced_fingerprintLeft3'] is not None):
        #     os.remove(data['Enhanced_fingerprintLeft3'])


    def deleteenrolljson(jsonpath):
        if os.path.exists(jsonpath):
                os.remove(jsonpath)
        else:
            print("The file does not exist:",jsonpath) 

    def deleteverificationimages(data):

        data_keys = data.keys()
        if('Annotated_fingerprintRight' in data_keys and data['Annotated_fingerprintRight'] is not None):
            os.remove(data['Annotated_fingerprintRight'])
        if('Annotated_fingerprintLeft' in data_keys and data['Annotated_fingerprintLeft'] is not None):
            os.remove(data['Annotated_fingerprintLeft'])
        if('Segmented_fingerprintRight0' in data_keys and data['Segmented_fingerprintRight0'] is not None):
            os.remove(data['Segmented_fingerprintRight0'])
        if('Segmented_fingerprintRight1' in data_keys and data['Segmented_fingerprintRight1'] is not None):
            os.remove(data['Segmented_fingerprintRight1'])
        if('Segmented_fingerprintRight2' in data_keys and data['Segmented_fingerprintRight2'] is not None):
            os.remove(data['Segmented_fingerprintRight2'])
        if('Segmented_fingerprintRight3' in data_keys and data['Segmented_fingerprintRight3'] is not None):
            os.remove(data['Segmented_fingerprintRight3'])
        if('Segmented_fingerprintLeft0' in data_keys and data['Segmented_fingerprintLeft0'] is not None):
            os.remove(data['Segmented_fingerprintLeft0'])
        if('Segmented_fingerprintLeft1' in data_keys and data['Segmented_fingerprintLeft1'] is not None):
            os.remove(data['Segmented_fingerprintLeft1'])
        if('Segmented_fingerprintLeft2' in data_keys and data['Segmented_fingerprintLeft2'] is not None):
            os.remove(data['Segmented_fingerprintLeft2'])
        if('Segmented_fingerprintLeft3' in data_keys and data['Segmented_fingerprintLeft3'] is not None):
            os.remove(data['Segmented_fingerprintLeft3'])

        
        if('Enhanced_fingerprintRight0' in data_keys and data['Enhanced_fingerprintRight0'] is not None):
            os.remove(data['Enhanced_fingerprintRight0'])
        if('Enhanced_fingerprintRight1' in data_keys and data['Enhanced_fingerprintRight1'] is not None):
            os.remove(data['Enhanced_fingerprintRight1'])
        if('Enhanced_fingerprintRight2' in data_keys and data['Enhanced_fingerprintRight2'] is not None):
            os.remove(data['Enhanced_fingerprintRight2'])
        if('Enhanced_fingerprintRight3' in data_keys and data['Enhanced_fingerprintRight3'] is not None):
            os.remove(data['Enhanced_fingerprintRight3'])
        if('Enhanced_fingerprintLeft0' in data_keys and data['Enhanced_fingerprintLeft0'] is not None):
            os.remove(data['Enhanced_fingerprintLeft0'])
        if('Enhanced_fingerprintLeft1' in data_keys and data['Enhanced_fingerprintLeft1'] is not None):
            os.remove(data['Enhanced_fingerprintLeft1'])
        if('Enhanced_fingerprintLeft2' in data_keys and data['Enhanced_fingerprintLeft2'] is not None):
            os.remove(data['Enhanced_fingerprintLeft2'])
        if('Enhanced_fingerprintLeft3' in data_keys and data['Enhanced_fingerprintLeft3'] is not None):
            os.remove(data['Enhanced_fingerprintLeft3'])
           

    def purge(dir, pattern):
        for f in os.listdir(dir):
            if re.search(pattern, f):
                os.remove(os.path.join(dir, f))