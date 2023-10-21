from tornado import websocket, web, ioloop
import json
import random
import string
import base64
from database import Database
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, send
import cv2

from lib import enhance_contact, enhance_contactless, hr_segmentation, segmentation
from lib.Fingerprint_Matching import infer


#

cl = []
base_address = "/home/easgrad/suryavee"
# mapping = {}
# init database class

db = Database()
# with open("mapping.csv") as file:
    # lines = file.readlines()
    # for line in lines:
    #     # print(line)
    #     mapping[line.split(",")[0]] = line.split(",")[1] 

def enhance(file, fg_type):
    if (fg_type == "contact-based"):
        enh = enhance_contact.main(file)
    else:
        enh = enhance_contactless.main(file)
    return enh

def segment(file, fg_type):
    enh = segmentation.main(file, fg_type)
    return enh

def match_full(file1, file2, hand1, hand2, ground_truth,data,data_enroll):
    annotated_image, segments_verify = segmentation.main(file1, hand1)
    annotated_image_enroll, segments_enroll = segmentation.main(file2, hand2)
    print(f"Segments for {hand1} verification : {len(segments_verify)}")
    personid = data["personid"]
    print(personid)
    # fileid = (mapping[personid]).strip()
    # print(fileid)
    annotated_image_path = base_address + '/images/' + data["sessionid"] + "_" +personid + "_" + data["setting"]  + hand1 +"_""Annotated_fingerprint" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".png"
    data[f"Annotated_fingerprint{hand1}"] = annotated_image_path
    cv2.imwrite(annotated_image_path, annotated_image)

    if(f"Annotated_fingerprint{hand1}" not in data_enroll.keys()):
        annotated_image_path_enroll = base_address + '/images/enroll/' + data["sessionid"] + "_" +personid + "_" + data["setting"]  + hand1 +"_""Annotated_fingerprint" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".png"
        data_enroll[f"Annotated_fingerprint{hand1}"] = annotated_image_path_enroll
        cv2.imwrite(annotated_image_path_enroll, annotated_image_enroll)

    

    for i,cropped_fingerprint in enumerate(segments_verify):
        semented_finger_path = base_address + '/images/' + data["sessionid"] + "_" +personid + "_" + data["setting"]  + hand1 +"_"+str(i)+"_Segmented_fingerprint" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".png"
        data[f"Segmented_fingerprint{hand1}{i}"] = semented_finger_path
        if(hand1 == "Right"):
            segmented_finger = cv2.rotate(cropped_fingerprint, cv2.ROTATE_90_CLOCKWISE)
        if(hand1 == "Left"):
            segmented_finger = cv2.rotate(cropped_fingerprint, cv2.ROTATE_90_COUNTERCLOCKWISE)
        cv2.imwrite(semented_finger_path, segmented_finger)
        print(f"Segmented_fingerprint{hand1}{i} saved")
        try:
            enh = enhance(cropped_fingerprint,fg_type="contactless")
            print('enhance successful')
            image, clahe_img, ridge_img, enh_img =  enh
            enh_path = base_address + '/images/' + data["sessionid"] + "_" +personid + "_" + data["setting"]  + hand1 +"_"+str(i)+"_Enhanced_fingerprint" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".png"
            data[f"Enhanced_fingerprint{hand1}{i}"] = enh_path
            if(hand1 == "Right"):
                enh_img = cv2.rotate(enh_img, cv2.ROTATE_180)
            cv2.imwrite(enh_path, enh_img)
            print('write successful')
            # clahe_path = base_address + '/images/' + data["sessionid"] + "_" +personid + "_" + data["setting"]  + hand1 +"_"+str(i)+"_Enhanced_fingerprint_clahe" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".png"
            # data[f"Clahe_fingerprint{hand1}{i}"] = clahe_path
            # if(hand1 == "Right"):
            #     clahe_img = cv2.rotate(clahe_img, cv2.ROTATE_180)
            # cv2.imwrite(clahe_path, clahe_img)
            # ridge_path = base_address + '/images/' + data["sessionid"] + "_" +personid + "_" + data["setting"]  + hand1 +"_"+str(i)+"_Enhanced_fingerprint_ridge" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".png"
            # data[f"Ridge_fingerprint{hand1}{i}"] = ridge_path
            # if(hand1 == "Right"):
            #     ridge_img = cv2.rotate(ridge_img, cv2.ROTATE_180)
            # cv2.imwrite(ridge_path, ridge_img)
        except:
            print("Error in enhancement")
            enh = cropped_fingerprint
    if(f"Segmented_fingerprint{hand1}0" not in data_enroll.keys()):
        for i,cropped_fingerprint in enumerate(segments_enroll):
            semented_finger_path = base_address + '/images/enroll/' + data["sessionid"] + "_" +personid + "_" + data["setting"]  + hand1 +"_"+str(i)+"_Segmented_fingerprint" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".png"
            data_enroll[f"Segmented_fingerprint{hand1}{i}"] = semented_finger_path
            if(hand1 == "Right"):
                segmented_finger = cv2.rotate(cropped_fingerprint, cv2.ROTATE_90_CLOCKWISE)
            if(hand1 == "Left"):
                segmented_finger = cv2.rotate(cropped_fingerprint, cv2.ROTATE_90_COUNTERCLOCKWISE)
            cv2.imwrite(semented_finger_path, segmented_finger)
            print(f"Segmented_fingerprint{hand1}{i} saved")
            try:
                enh = enhance(cropped_fingerprint,fg_type="contactless")
                image, clahe_img, ridge_img, enh_img =  enh
                enh_path = base_address + '/images/enroll/' + data["sessionid"] + "_" +personid + "_" + data["setting"]  + hand1 +"_"+str(i)+"_Enhanced_fingerprint" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".png"
                data_enroll[f"Enhanced_fingerprint{hand1}{i}"] = enh_path
                if(hand1 == "Right"):
                    enh_img = cv2.rotate(enh_img, cv2.ROTATE_180)
                cv2.imwrite(enh_path, enh_img)
                # clahe_path = base_address + '/images/enroll/' + data["sessionid"] + "_" +personid + "_" + data["setting"]  + hand1 +"_"+str(i)+"_Enhanced_fingerprint_clahe" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".png"
                # data_enroll[f"Clahe_fingerprint{hand1}{i}"] = clahe_path
                # if(hand1 == "Right"):
                #     clahe_img = cv2.rotate(clahe_img, cv2.ROTATE_180)
                # cv2.imwrite(clahe_path, clahe_img)
                # ridge_path = base_address + '/images/enroll/' + data["sessionid"] + "_" +personid + "_" + data["setting"]  + hand1 +"_"+str(i)+"_Enhanced_fingerprint_ridge" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".png"
                # data_enroll[f"Ridge_fingerprint{hand1}{i}"] = ridge_path
                # if(hand1 == "Right"):
                #     ridge_img = cv2.rotate(ridge_img, cv2.ROTATE_180)
                # cv2.imwrite(ridge_path, ridge_img)
            except:
                print("Error in enhancement")
                enh = cropped_fingerprint
        

    score, pred, scores = infer.main_full_cl2cl(segments_verify, segments_enroll)
    return score, pred, scores, data, data_enroll
def getEnrollDataForPerson(personid):
    data = db.getImages(personid)
    return data

def getEnrolledImages(data,response):
    data_keys = data.keys()
    if('Annotated_fingerprintRight' in data_keys and data['Annotated_fingerprintRight'] is not None):
        Annotated_Right = cv2.imread(data['Annotated_fingerprintRight'])
        #base64 string encode images
        _, buffer = cv2.imencode('.png', Annotated_Right)
        response['Annotated_Right'] = base64.b64encode(buffer).decode('utf-8')
    if('Annotated_fingerprintLeft' in data_keys and data['Annotated_fingerprintLeft'] is not None):
        Annotated_Left = cv2.imread(data['Annotated_fingerprintLeft'])
        _, buffer = cv2.imencode('.png', Annotated_Left)
        response['Annotated_Left'] = base64.b64encode(buffer).decode('utf-8')

    if('Segmented_fingerprintRight0' in data_keys and data['Segmented_fingerprintRight0'] is not None):
        Segmented_Right = cv2.imread(data['Segmented_fingerprintRight0'])
        #base64 string encode images
        _, buffer = cv2.imencode('.png', Segmented_Right)
        response['Segmented_fingerprintRight0'] = base64.b64encode(buffer).decode('utf-8')
    if('Segmented_fingerprintRight1' in data_keys and data['Segmented_fingerprintRight1'] is not None):
        Segmented_Left = cv2.imread(data['Segmented_fingerprintRight1'])
        _, buffer = cv2.imencode('.png', Segmented_Left)
        response['Segmented_fingerprintRight1'] = base64.b64encode(buffer).decode('utf-8')
    if('Segmented_fingerprintRight2' in data_keys and data['Segmented_fingerprintRight2'] is not None):
        Segmented_Right = cv2.imread(data['Segmented_fingerprintRight2'])
        #base64 string encode images
        _, buffer = cv2.imencode('.png', Segmented_Right)
        response['Segmented_fingerprintRight2'] = base64.b64encode(buffer).decode('utf-8')
    if('Segmented_fingerprintRight3' in data_keys and data['Segmented_fingerprintRight3'] is not None):
        Segmented_Left = cv2.imread(data['Segmented_fingerprintRight3'])
        _, buffer = cv2.imencode('.png', Segmented_Left)
        response['Segmented_fingerprintRight3'] = base64.b64encode(buffer).decode('utf-8')
    if('Segmented_fingerprintLeft0' in data_keys and data['Segmented_fingerprintLeft0'] is not None):
        Segmented_Right = cv2.imread(data['Segmented_fingerprintLeft0'])
        #base64 string encode images
        _, buffer = cv2.imencode('.png', Segmented_Right)
        response['Segmented_fingerprintLeft0'] = base64.b64encode(buffer).decode('utf-8')
    if('Segmented_fingerprintLeft1' in data_keys and data['Segmented_fingerprintLeft1'] is not None):
        Segmented_Left = cv2.imread(data['Segmented_fingerprintLeft1'])
        _, buffer = cv2.imencode('.png', Segmented_Left)
        response['Segmented_fingerprintLeft1'] = base64.b64encode(buffer).decode('utf-8')
    if('Segmented_fingerprintLeft2' in data_keys and data['Segmented_fingerprintLeft2'] is not None):
        Segmented_Right = cv2.imread(data['Segmented_fingerprintLeft2'])
        #base64 string encode images
        _, buffer = cv2.imencode('.png', Segmented_Right)
        response['Segmented_fingerprintLeft2'] = base64.b64encode(buffer).decode('utf-8')
    if('Segmented_fingerprintLeft3' in data_keys and data['Segmented_fingerprintLeft3'] is not None):
        Segmented_Left = cv2.imread(data['Segmented_fingerprintLeft3'])
        _, buffer = cv2.imencode('.png', Segmented_Left)
        response['Segmented_fingerprintLeft3'] = base64.b64encode(buffer).decode('utf-8')

    
    if('Enhanced_fingerprintRight0' in data_keys and data['Enhanced_fingerprintRight0'] is not None):
        Enhanced_Right = cv2.imread(data['Enhanced_fingerprintRight0'])
        #base64 string encode images
        _, buffer = cv2.imencode('.png', Enhanced_Right)
        response['Enhanced_fingerprintRight0'] = base64.b64encode(buffer).decode('utf-8')
    if('Enhanced_fingerprintRight1' in data_keys and data['Enhanced_fingerprintRight1'] is not None):
        Enhanced_Left = cv2.imread(data['Enhanced_fingerprintRight1'])
        _, buffer = cv2.imencode('.png', Enhanced_Left)
        response['Enhanced_fingerprintRight1'] = base64.b64encode(buffer).decode('utf-8')
    if('Enhanced_fingerprintRight2' in data_keys and data['Enhanced_fingerprintRight2'] is not None):
        Enhanced_Right = cv2.imread(data['Enhanced_fingerprintRight2'])
        #base64 string encode images
        _, buffer = cv2.imencode('.png', Enhanced_Right)
        response['Enhanced_fingerprintRight2'] = base64.b64encode(buffer).decode('utf-8')
    if('Enhanced_fingerprintRight3' in data_keys and data['Enhanced_fingerprintRight3'] is not None):
        Enhanced_Left = cv2.imread(data['Enhanced_fingerprintRight3'])
        _, buffer = cv2.imencode('.png', Enhanced_Left)
        response['Enhanced_fingerprintRight3'] = base64.b64encode(buffer).decode('utf-8')
    if('Enhanced_fingerprintLeft0' in data_keys and data['Enhanced_fingerprintLeft0'] is not None):
        Enhanced_Right = cv2.imread(data['Enhanced_fingerprintLeft0'])
        #base64 string encode images
        _, buffer = cv2.imencode('.png', Enhanced_Right)
        response['Enhanced_fingerprintLeft0'] = base64.b64encode(buffer).decode('utf-8')
    if('Enhanced_fingerprintLeft1' in data_keys and data['Enhanced_fingerprintLeft1'] is not None):
        Enhanced_Left = cv2.imread(data['Enhanced_fingerprintLeft1'])
        _, buffer = cv2.imencode('.png', Enhanced_Left)
        response['Enhanced_fingerprintLeft1'] = base64.b64encode(buffer).decode('utf-8')
    if('Enhanced_fingerprintLeft2' in data_keys and data['Enhanced_fingerprintLeft2'] is not None):
        Enhanced_Right = cv2.imread(data['Enhanced_fingerprintLeft2'])
        #base64 string encode images
        _, buffer = cv2.imencode('.png', Enhanced_Right)
        response['Enhanced_fingerprintLeft2'] = base64.b64encode(buffer).decode('utf-8')
    if('Enhanced_fingerprintLeft3' in data_keys and data['Enhanced_fingerprintLeft3'] is not None):
        Enhanced_Left = cv2.imread(data['Enhanced_fingerprintLeft3'])
        _, buffer = cv2.imencode('.png', Enhanced_Left)
        response['Enhanced_fingerprintLeft3'] = base64.b64encode(buffer).decode('utf-8')
    
    # if('Clahe_fingerprintRight0' in data_keys and data['Clahe_fingerprintRight0'] is not None):
    #     Clahe_Right = cv2.imread(data['Clahe_fingerprintRight0'])
    #     #base64 string encode images
    #     _, buffer = cv2.imencode('.png', Clahe_Right)
    #     response['Clahe_fingerprintRight0'] = base64.b64encode(buffer).decode('utf-8')
    # if('Clahe_fingerprintRight1' in data_keys and data['Clahe_fingerprintRight1'] is not None):
    #     Clahe_Left = cv2.imread(data['Clahe_fingerprintRight1'])
    #     _, buffer = cv2.imencode('.png', Clahe_Left)
    #     response['Clahe_fingerprintRight1'] = base64.b64encode(buffer).decode('utf-8')
    # if('Clahe_fingerprintRight2' in data_keys and data['Clahe_fingerprintRight2'] is not None):
    #     Clahe_Right = cv2.imread(data['Clahe_fingerprintRight2'])
    #     #base64 string encode images
    #     _, buffer = cv2.imencode('.png', Clahe_Right)
    #     response['Clahe_fingerprintRight2'] = base64.b64encode(buffer).decode('utf-8')
    # if('Clahe_fingerprintRight3' in data_keys and data['Clahe_fingerprintRight3'] is not None):
    #     Clahe_Left = cv2.imread(data['Clahe_fingerprintRight3'])
    #     _, buffer = cv2.imencode('.png', Clahe_Left)
    #     response['Clahe_fingerprintRight3'] = base64.b64encode(buffer).decode('utf-8')
    # if('Clahe_fingerprintLeft0' in data_keys and data['Clahe_fingerprintLeft0'] is not None):
    #     Clahe_Right = cv2.imread(data['Clahe_fingerprintLeft0'])
    #     #base64 string encode images
    #     _, buffer = cv2.imencode('.png', Clahe_Right)
    #     response['Clahe_fingerprintLeft0'] = base64.b64encode(buffer).decode('utf-8')
    # if('Clahe_fingerprintLeft1' in data_keys and data['Clahe_fingerprintLeft1'] is not None):
    #     Clahe_Left = cv2.imread(data['Clahe_fingerprintLeft1'])
    #     _, buffer = cv2.imencode('.png', Clahe_Left)
    #     response['Clahe_fingerprintLeft1'] = base64.b64encode(buffer).decode('utf-8')
    # if('Clahe_fingerprintLeft2' in data_keys and data['Clahe_fingerprintLeft2'] is not None):
    #     Clahe_Right = cv2.imread(data['Clahe_fingerprintLeft2'])
    #     #base64 string encode images
    #     _, buffer = cv2.imencode('.png', Clahe_Right)
    #     response['Clahe_fingerprintLeft2'] = base64.b64encode(buffer).decode('utf-8')
    # if('Clahe_fingerprintLeft3' in data_keys and data['Clahe_fingerprintLeft3'] is not None):
    #     Clahe_Left = cv2.imread(data['Clahe_fingerprintLeft3'])
    #     _, buffer = cv2.imencode('.png', Clahe_Left)
    #     response['Clahe_fingerprintLeft3'] = base64.b64encode(buffer).decode('utf-8')

    # if('Ridge_fingerprintRight0' in data_keys and data['Ridge_fingerprintRight0'] is not None):
    #     Ridge_Right = cv2.imread(data['Ridge_fingerprintRight0'])
    #     #base64 string encode images
    #     _, buffer = cv2.imencode('.png', Ridge_Right)
    #     response['Ridge_fingerprintRight0'] = base64.b64encode(buffer).decode('utf-8')
    # if('Ridge_fingerprintRight1' in data_keys and data['Ridge_fingerprintRight1'] is not None):
    #     Ridge_Left = cv2.imread(data['Ridge_fingerprintRight1'])
    #     _, buffer = cv2.imencode('.png', Ridge_Left)
    #     response['Ridge_fingerprintRight1'] = base64.b64encode(buffer).decode('utf-8')
    # if('Annotated_fingerprintLeft' in data_keys and data['Ridge_fingerprintRight2'] is not None):
    #     Ridge_Right = cv2.imread(data['Ridge_fingerprintRight2'])
    #     #base64 string encode images
    #     _, buffer = cv2.imencode('.png', Ridge_Right)
    #     response['Ridge_fingerprintRight2'] = base64.b64encode(buffer).decode('utf-8')
    # if('Ridge_fingerprintRight3' in data_keys and data['Ridge_fingerprintRight3'] is not None):
    #     Ridge_Left = cv2.imread(data['Ridge_fingerprintRight3'])
    #     _, buffer = cv2.imencode('.png', Ridge_Left)
    #     response['Ridge_fingerprintRight3'] = base64.b64encode(buffer).decode('utf-8')
    # if('Ridge_fingerprintLeft0' in data_keys and data['Ridge_fingerprintLeft0'] is not None):
    #     Ridge_Right = cv2.imread(data['Ridge_fingerprintLeft0'])
    #     #base64 string encode images
    #     _, buffer = cv2.imencode('.png', Ridge_Right)
    #     response['Ridge_fingerprintLeft0'] = base64.b64encode(buffer).decode('utf-8')
    # if('Ridge_fingerprintLeft1' in data_keys and data['Ridge_fingerprintLeft1'] is not None):
    #     Ridge_Left = cv2.imread(data['Ridge_fingerprintLeft1'])
    #     _, buffer = cv2.imencode('.png', Ridge_Left)
    #     response['Ridge_fingerprintLeft1'] = base64.b64encode(buffer).decode('utf-8')
    # if('Ridge_fingerprintLeft2' in data_keys and data['Ridge_fingerprintLeft2'] is not None):
    #     Ridge_Right = cv2.imread(data['Ridge_fingerprintLeft2'])
    #     #base64 string encode images
    #     _, buffer = cv2.imencode('.png', Ridge_Right)
    #     response['Ridge_fingerprintLeft2'] = base64.b64encode(buffer).decode('utf-8')
    # if('Ridge_fingerprintLeft3' in data_keys and data['Ridge_fingerprintLeft3'] is not None):
    #     Ridge_Left = cv2.imread(data['Ridge_fingerprintLeft3'])
    #     _, buffer = cv2.imencode('.png', Ridge_Left)
    #     response['Ridge_fingerprintLeft3'] = base64.b64encode(buffer).decode('utf-8')
    
    return response

def getVerificationImages(data,response):
    data_keys = data.keys()
    if('Annotated_fingerprintRight' in data_keys and data['Annotated_fingerprintRight'] is not None):
        Annotated_Right = cv2.imread(data['Annotated_fingerprintRight'])
        #base64 string encode images
        _, buffer = cv2.imencode('.png', Annotated_Right)
        response['Annotated_Right'] = base64.b64encode(buffer).decode('utf-8')
    if('Annotated_fingerprintLeft' in data_keys and data['Annotated_fingerprintLeft'] is not None):
        Annotated_Left = cv2.imread(data['Annotated_fingerprintLeft'])
        _, buffer = cv2.imencode('.png', Annotated_Left)
        response['Annotated_Left'] = base64.b64encode(buffer).decode('utf-8')

    if('Segmented_fingerprintRight0' in data_keys and data['Segmented_fingerprintRight0'] is not None):
        Segmented_Right = cv2.imread(data['Segmented_fingerprintRight0'])
        #base64 string encode images
        _, buffer = cv2.imencode('.png', Segmented_Right)
        response['Segmented_fingerprintRight0'] = base64.b64encode(buffer).decode('utf-8')
    if('Segmented_fingerprintRight1' in data_keys and data['Segmented_fingerprintRight1'] is not None):
        Segmented_Left = cv2.imread(data['Segmented_fingerprintRight1'])
        _, buffer = cv2.imencode('.png', Segmented_Left)
        response['Segmented_fingerprintRight1'] = base64.b64encode(buffer).decode('utf-8')
    if('Segmented_fingerprintRight2' in data_keys and data['Segmented_fingerprintRight2'] is not None):
        Segmented_Right = cv2.imread(data['Segmented_fingerprintRight2'])
        #base64 string encode images
        _, buffer = cv2.imencode('.png', Segmented_Right)
        response['Segmented_fingerprintRight2'] = base64.b64encode(buffer).decode('utf-8')
    if('Segmented_fingerprintRight3' in data_keys and data['Segmented_fingerprintRight3'] is not None):
        Segmented_Left = cv2.imread(data['Segmented_fingerprintRight3'])
        _, buffer = cv2.imencode('.png', Segmented_Left)
        response['Segmented_fingerprintRight3'] = base64.b64encode(buffer).decode('utf-8')
    if('Segmented_fingerprintLeft0' in data_keys and data['Segmented_fingerprintLeft0'] is not None):
        Segmented_Right = cv2.imread(data['Segmented_fingerprintLeft0'])
        #base64 string encode images
        _, buffer = cv2.imencode('.png', Segmented_Right)
        response['Segmented_fingerprintLeft0'] = base64.b64encode(buffer).decode('utf-8')
    if('Segmented_fingerprintLeft1' in data_keys and data['Segmented_fingerprintLeft1'] is not None):
        Segmented_Left = cv2.imread(data['Segmented_fingerprintLeft1'])
        _, buffer = cv2.imencode('.png', Segmented_Left)
        response['Segmented_fingerprintLeft1'] = base64.b64encode(buffer).decode('utf-8')
    if('Segmented_fingerprintLeft2' in data_keys and data['Segmented_fingerprintLeft2'] is not None):
        Segmented_Right = cv2.imread(data['Segmented_fingerprintLeft2'])
        #base64 string encode images
        _, buffer = cv2.imencode('.png', Segmented_Right)
        response['Segmented_fingerprintLeft2'] = base64.b64encode(buffer).decode('utf-8')
    if('Segmented_fingerprintLeft3' in data_keys and data['Segmented_fingerprintLeft3'] is not None):
        Segmented_Left = cv2.imread(data['Segmented_fingerprintLeft3'])
        _, buffer = cv2.imencode('.png', Segmented_Left)
        response['Segmented_fingerprintLeft3'] = base64.b64encode(buffer).decode('utf-8')

    
    if('Enhanced_fingerprintRight0' in data_keys and data['Enhanced_fingerprintRight0'] is not None):
        Enhanced_Right = cv2.imread(data['Enhanced_fingerprintRight0'])
        #base64 string encode images
        _, buffer = cv2.imencode('.png', Enhanced_Right)
        response['Enhanced_fingerprintRight0'] = base64.b64encode(buffer).decode('utf-8')
    if('Enhanced_fingerprintRight1' in data_keys and data['Enhanced_fingerprintRight1'] is not None):
        Enhanced_Left = cv2.imread(data['Enhanced_fingerprintRight1'])
        _, buffer = cv2.imencode('.png', Enhanced_Left)
        response['Enhanced_fingerprintRight1'] = base64.b64encode(buffer).decode('utf-8')
    if('Enhanced_fingerprintRight2' in data_keys and data['Enhanced_fingerprintRight2'] is not None):
        Enhanced_Right = cv2.imread(data['Enhanced_fingerprintRight2'])
        #base64 string encode images
        _, buffer = cv2.imencode('.png', Enhanced_Right)
        response['Enhanced_fingerprintRight2'] = base64.b64encode(buffer).decode('utf-8')
    if('Enhanced_fingerprintRight3' in data_keys and data['Enhanced_fingerprintRight3'] is not None):
        Enhanced_Left = cv2.imread(data['Enhanced_fingerprintRight3'])
        _, buffer = cv2.imencode('.png', Enhanced_Left)
        response['Enhanced_fingerprintRight3'] = base64.b64encode(buffer).decode('utf-8')
    if('Enhanced_fingerprintLeft0' in data_keys and data['Enhanced_fingerprintLeft0'] is not None):
        Enhanced_Right = cv2.imread(data['Enhanced_fingerprintLeft0'])
        #base64 string encode images
        _, buffer = cv2.imencode('.png', Enhanced_Right)
        response['Enhanced_fingerprintLeft0'] = base64.b64encode(buffer).decode('utf-8')
    if('Enhanced_fingerprintLeft1' in data_keys and data['Enhanced_fingerprintLeft1'] is not None):
        Enhanced_Left = cv2.imread(data['Enhanced_fingerprintLeft1'])
        _, buffer = cv2.imencode('.png', Enhanced_Left)
        response['Enhanced_fingerprintLeft1'] = base64.b64encode(buffer).decode('utf-8')
    if('Enhanced_fingerprintLeft2' in data_keys and data['Enhanced_fingerprintLeft2'] is not None):
        Enhanced_Right = cv2.imread(data['Enhanced_fingerprintLeft2'])
        #base64 string encode images
        _, buffer = cv2.imencode('.png', Enhanced_Right)
        response['Enhanced_fingerprintLeft2'] = base64.b64encode(buffer).decode('utf-8')
    if('Enhanced_fingerprintLeft3' in data_keys and data['Enhanced_fingerprintLeft3'] is not None):
        Enhanced_Left = cv2.imread(data['Enhanced_fingerprintLeft3'])
        _, buffer = cv2.imencode('.png', Enhanced_Left)
        response['Enhanced_fingerprintLeft3'] = base64.b64encode(buffer).decode('utf-8')
    
    # if('Clahe_fingerprintRight0' in data_keys and data['Clahe_fingerprintRight0'] is not None):
    #     Clahe_Right = cv2.imread(data['Clahe_fingerprintRight0'])
    #     #base64 string encode images
    #     _, buffer = cv2.imencode('.png', Clahe_Right)
    #     response['Clahe_fingerprintRight0'] = base64.b64encode(buffer).decode('utf-8')
    # if('Clahe_fingerprintRight1' in data_keys and data['Clahe_fingerprintRight1'] is not None):
    #     Clahe_Left = cv2.imread(data['Clahe_fingerprintRight1'])
    #     _, buffer = cv2.imencode('.png', Clahe_Left)
    #     response['Clahe_fingerprintRight1'] = base64.b64encode(buffer).decode('utf-8')
    # if('Clahe_fingerprintRight2' in data_keys and data['Clahe_fingerprintRight2'] is not None):
    #     Clahe_Right = cv2.imread(data['Clahe_fingerprintRight2'])
    #     #base64 string encode images
    #     _, buffer = cv2.imencode('.png', Clahe_Right)
    #     response['Clahe_fingerprintRight2'] = base64.b64encode(buffer).decode('utf-8')
    # if('Clahe_fingerprintRight3' in data_keys and data['Clahe_fingerprintRight3'] is not None):
    #     Clahe_Left = cv2.imread(data['Clahe_fingerprintRight3'])
    #     _, buffer = cv2.imencode('.png', Clahe_Left)
    #     response['Clahe_fingerprintRight3'] = base64.b64encode(buffer).decode('utf-8')
    # if('Clahe_fingerprintLeft0' in data_keys and data['Clahe_fingerprintLeft0'] is not None):
    #     Clahe_Right = cv2.imread(data['Clahe_fingerprintLeft0'])
    #     #base64 string encode images
    #     _, buffer = cv2.imencode('.png', Clahe_Right)
    #     response['Clahe_fingerprintLeft0'] = base64.b64encode(buffer).decode('utf-8')
    # if('Clahe_fingerprintLeft1' in data_keys and data['Clahe_fingerprintLeft1'] is not None):
    #     Clahe_Left = cv2.imread(data['Clahe_fingerprintLeft1'])
    #     _, buffer = cv2.imencode('.png', Clahe_Left)
    #     response['Clahe_fingerprintLeft1'] = base64.b64encode(buffer).decode('utf-8')
    # if('Clahe_fingerprintLeft2' in data_keys and data['Clahe_fingerprintLeft2'] is not None):
    #     Clahe_Right = cv2.imread(data['Clahe_fingerprintLeft2'])
    #     #base64 string encode images
    #     _, buffer = cv2.imencode('.png', Clahe_Right)
    #     response['Clahe_fingerprintLeft2'] = base64.b64encode(buffer).decode('utf-8')
    # if('Clahe_fingerprintLeft3' in data_keys and data['Clahe_fingerprintLeft3'] is not None):
    #     Clahe_Left = cv2.imread(data['Clahe_fingerprintLeft3'])
    #     _, buffer = cv2.imencode('.png', Clahe_Left)
    #     response['Clahe_fingerprintLeft3'] = base64.b64encode(buffer).decode('utf-8')

    # if('Ridge_fingerprintRight0' in data_keys and data['Ridge_fingerprintRight0'] is not None):
    #     Ridge_Right = cv2.imread(data['Ridge_fingerprintRight0'])
    #     #base64 string encode images
    #     _, buffer = cv2.imencode('.png', Ridge_Right)
    #     response['Ridge_fingerprintRight0'] = base64.b64encode(buffer).decode('utf-8')
    # if('Ridge_fingerprintRight1' in data_keys and data['Ridge_fingerprintRight1'] is not None):
    #     Ridge_Left = cv2.imread(data['Ridge_fingerprintRight1'])
    #     _, buffer = cv2.imencode('.png', Ridge_Left)
    #     response['Ridge_fingerprintRight1'] = base64.b64encode(buffer).decode('utf-8')
    # if('Annotated_fingerprintLeft' in data_keys and data['Ridge_fingerprintRight2'] is not None):
    #     Ridge_Right = cv2.imread(data['Ridge_fingerprintRight2'])
    #     #base64 string encode images
    #     _, buffer = cv2.imencode('.png', Ridge_Right)
    #     response['Ridge_fingerprintRight2'] = base64.b64encode(buffer).decode('utf-8')
    # if('Ridge_fingerprintRight3' in data_keys and data['Ridge_fingerprintRight3'] is not None):
    #     Ridge_Left = cv2.imread(data['Ridge_fingerprintRight3'])
    #     _, buffer = cv2.imencode('.png', Ridge_Left)
    #     response['Ridge_fingerprintRight3'] = base64.b64encode(buffer).decode('utf-8')
    # if('Ridge_fingerprintLeft0' in data_keys and data['Ridge_fingerprintLeft0'] is not None):
    #     Ridge_Right = cv2.imread(data['Ridge_fingerprintLeft0'])
    #     #base64 string encode images
    #     _, buffer = cv2.imencode('.png', Ridge_Right)
    #     response['Ridge_fingerprintLeft0'] = base64.b64encode(buffer).decode('utf-8')
    # if('Ridge_fingerprintLeft1' in data_keys and data['Ridge_fingerprintLeft1'] is not None):
    #     Ridge_Left = cv2.imread(data['Ridge_fingerprintLeft1'])
    #     _, buffer = cv2.imencode('.png', Ridge_Left)
    #     response['Ridge_fingerprintLeft1'] = base64.b64encode(buffer).decode('utf-8')
    # if('Ridge_fingerprintLeft2' in data_keys and data['Ridge_fingerprintLeft2'] is not None):
    #     Ridge_Right = cv2.imread(data['Ridge_fingerprintLeft2'])
    #     #base64 string encode images
    #     _, buffer = cv2.imencode('.png', Ridge_Right)
    #     response['Ridge_fingerprintLeft2'] = base64.b64encode(buffer).decode('utf-8')
    # if('Ridge_fingerprintLeft3' in data_keys and data['Ridge_fingerprintLeft3'] is not None):
    #     Ridge_Left = cv2.imread(data['Ridge_fingerprintLeft3'])
    #     _, buffer = cv2.imencode('.png', Ridge_Left)
    #     response['Ridge_fingerprintLeft3'] = base64.b64encode(buffer).decode('utf-8')
    
    return response
    


def verifyPerson(data):
    if(data["Picture_Right"] or data["Picture_Left"]):
        data_enroll = getEnrollDataForPerson(data["personid"])
        if(data["Picture_Right"] and data_enroll["Picture_Right"] ):
            verify_right_picture = cv2.imread(data["Picture_Right"])
            person_right_picture = cv2.imread(data_enroll["Picture_Right"])
            score_right, pred_right, scores_right, data, data_enroll = match_full(verify_right_picture,person_right_picture , "Right","Right","Match",data,data_enroll)
        if(data["Picture_Left"] and data_enroll["Picture_Left"] ):
            verify_left_picture = cv2.imread(data["Picture_Left"])
            person_left_picture = cv2.imread(data_enroll["Picture_Left"])
            score_left, pred_left, scores_left, data, data_enroll = match_full(verify_left_picture,person_left_picture , "Left","Left","Match",data,data_enroll)
        score = f" Average Score Right: {score_right} Average ScoreLeft: {score_left}"
        pred = f"Right: {pred_right} Left: {pred_left}"
        # scores = f"RightIndex: {scores_right[0]} RightMiddle: {scores_right[1]} RightRing: {scores_right[2]} RightLittle: {scores_right[3]} LeftIndex: {scores_left[0]} LeftMiddle: {scores_left[1]} LeftRing: {scores_left[2]} LeftLittle: {scores_left[3]}"
        scores_dict = {"RightIndex": round(scores_right[0],4), "RightMiddle": round(scores_right[1],4), "RightRing": round(scores_right[2],4), "RightLittle": round(scores_right[3],4), "LeftIndex": round(scores_left[0],4), "LeftMiddle": round(scores_left[1],4), "LeftRing": round(scores_left[2],4), "LeftLittle": round(scores_left[3],4)}
    return score, pred, scores_dict, data, data_enroll

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@app.route('/api', methods=['GET', 'POST'])
def handle_api():
        if request.method == 'GET':
            id = request.args.get('id')
            value = request.args.get('value')
            data = {"id": id, "value": value}
            data = json.dumps(data)
            socketio.send(data)
            return jsonify({"message": "Message sent"})
        elif request.method == 'POST':
            print('recievedreuest')
            data = request.json
            personid = (data["personid"])
            print(personid)
            # fileid = (mapping[personid]).strip()
            # print(fileid)

            if(data["type"] == "Authenticate"):
                result = {
                    "message": "Authentication Unsuccessful",
                    "status_code": 400,
                    "type": "Authenticate"
                }
                sessionid = data["sessionid"]
                # personid = fileid
                user = None
                print('result',result)
                result = {
                    "message": "Authentication Successful",
                    "status_code": 200,
                    "type": "Authenticate"
                }
            elif(data["type"] == "Picture_Left"):
                with open(base_address + '/images/' + data["sessionid"] + "_" +personid + "_" + data["setting"]  + "_LEFT_image_fingerprint" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".png", "wb") as fh:
                    photo = data["photo"]
                    db.saveImages(data)
                    fh.write(base64.decodebytes(str.encode(photo)))
                    result = {
                        "message": "Message Received",
                        "type": "Picture_Left"
                    }
                    print(result)
            elif(data["type"] == "Picture_Right"):
                with open(base_address + '/images/' + data["sessionid"] + "_" +personid + "_" + data["setting"]  +  "_RIGHT_image_fingerprint" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".png", "wb") as fh:
                    photo = data["photo"]
                    db.saveImages(data)
                    fh.write(base64.decodebytes(str.encode(photo)))
                    result = {
                        "message": "Message Received",
                        "type": "Picture_Right"
                    }
                    print(result)
            # enroll
            elif(data["type"] == "Enroll"):
                if(data["Picture_Right"] or data["Picture_Left"]):
                    right_image_file_name = base_address + '/images/enroll/' + data["sessionid"] + "_" +personid + "_" + data["setting"]  +  "_RIGHT_image_fingerprint" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".png"
                    left_image_file_name = base_address + '/images/enroll/' + data["sessionid"] + "_" +personid + "_" + data["setting"]  +  "_LEFT_image_fingerprint" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".png"
                    try:
                        with open(right_image_file_name, "wb") as fh:
                            photo_right = data["Picture_Right"]
                            fh.write(base64.decodebytes(str.encode(photo_right)))
                            print('Right Image saved:',right_image_file_name)
                        with open(left_image_file_name, "wb") as fh:
                            photo_left = data["Picture_Left"]
                            fh.write(base64.decodebytes(str.encode(photo_left)))
                            print('Left Image saved:',left_image_file_name)

                        data['Picture_Right'] = right_image_file_name
                        data['Picture_Left'] = left_image_file_name
                        db.saveImages(data)
                        result = {
                            "message": "Message Received",
                            "type": "Enroll"
                        }
                       
                    except Exception as e:
                        print(e)
                        result = {
                            "message": "Saving Images Unsuccessful",
                            "status_code": 400,
                            "type": "Enroll"
                        }

                    print(result)
            # elif(data["type"] == "Video_Left"):
            #     with open(base_address + '/videos/' + data["sessionid"] + "_" +fileid + "_" + data["setting"]  + "_LEFT_video_fingerprint" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".mp4", "wb") as fh:
            #         photo = data["photo"]
            #         fh.write(base64.decodebytes(str.encode(photo)))
            #         result = {
            #             "message": "Message Received",
            #             "type": "Video_Left"
            #         }
            #         print(result)
            # elif(data["type"] == "Video_Right"):
            #     with open(base_address + '/videos/' + data["sessionid"] + "_" +fileid + "_" + data["setting"]  + "_RIGHT_video_fingerprint" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".mp4", "wb") as fh:
            #         photo = data["photo"]
            #         fh.write(base64.decodebytes(str.encode(photo)))
            #         result = {
            #             "message": "Message Received",
            #             "type": "Video_Right"
            #         }
                    # print(result)
            # verify
            elif(data["type"] == "Verify"):
                # open('Request.json', 'w').write(json.dumps(data))
                    
                if(data["Picture_Right"] or data["Picture_Left"]):
                    right_image_file_name = base_address + '/images/' + data["sessionid"] + "_" +personid + "_" + data["setting"]  +  "_RIGHT_image_fingerprint" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".png"
                    left_image_file_name = base_address + '/images/' + data["sessionid"] + "_" +personid + "_" + data["setting"]  +  "_LEFT_image_fingerprint" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".png"
                    try:
                        with open(right_image_file_name, "wb") as fh:
                            photo_right = data["Picture_Right"]
                            fh.write(base64.decodebytes(str.encode(photo_right)))
                            print('Right Image saved:',right_image_file_name)
                        with open(left_image_file_name, "wb") as fh:
                            photo_left = data["Picture_Left"]
                            fh.write(base64.decodebytes(str.encode(photo_left)))
                            print('Left Image saved:',left_image_file_name)

                        data['Picture_Right'] = right_image_file_name
                        data['Picture_Left'] = left_image_file_name
                        db.saveImages(data)
                        score,pred, scores_dict,data,data_enroll =  verifyPerson(data)
                        print('score',score)
                        print('pred',pred)
                        print('Full Scores',scores_dict)
                        db.updateImages(data["sessionid"],data)
                        db.updateImages(data_enroll["sessionid"],data_enroll)
                        result = {
                            "message": "Verification Completed",
                            "type": "Verify",
                            'score':score,
                            'Prediction':pred,
                            'full_scores':scores_dict
                        }
                    except Exception as e:
                        print(e)
                        result = {
                            "message": "Verification Unsuccessful",
                            "status_code": 400,
                            "type": "Verify"
                        }

                    # print(result)
            # elif(data["type"] == "Video_Left"):
            #     with open(base_address + '/videos/' + data["sessionid"] + "_" +fileid + "_" + data["setting"]  + "_LEFT_video_fingerprint" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".mp4", "wb") as fh:
            #         photo = data["photo"]
            #         fh.write(base64.decodebytes(str.encode(photo)))
            #         result = {
            #             "message": "Message Received",
            #             "type": "Video_Left"
            #         }
            #         print(result)
            # elif(data["type"] == "Video_Right"):
            #     with open(base_address + '/videos/' + data["sessionid"] + "_" +fileid + "_" + data["setting"]  + "_RIGHT_video_fingerprint" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".mp4", "wb") as fh:
            #         photo = data["photo"]
            #         fh.write(base64.decodebytes(str.encode(photo)))
            #         result = {
            #             "message": "Message Received",
            #             "type": "Video_Right"
            #         }
                    # print(result)
            print('result',result)
            return result
        
@app.route('/images', methods=['GET', 'POST'])
def handle_get_images_api():
    if request.method == 'GET':
        sessionid = request.args.get('sessionid')
        print(sessionid)
        imagetype = request.args.get('imagetype')
        print(imagetype)
        personid = request.args.get('personid')
        print(personid)

        response = dict()


        data = db.getImagesfromSession(sessionid)
        # data['_id'] = str(data['_id'])
        data_keys = data.keys()

        if(imagetype == 'Annotated'):
            try:
                if('Annotated_fingerprintRight' in data_keys and data['Annotated_fingerprintRight'] is not None):
                    Annotated_Right = cv2.imread(data['Annotated_fingerprintRight'])
                    #base64 string encode images
                    _, buffer = cv2.imencode('.png', Annotated_Right)
                    response['Annotated_Right'] = base64.b64encode(buffer).decode('utf-8')
                if('Annotated_fingerprintLeft' in data_keys and data['Annotated_fingerprintLeft'] is not None):
                    Annotated_Left = cv2.imread(data['Annotated_fingerprintLeft'])
                    _, buffer = cv2.imencode('.png', Annotated_Left)
                    response['Annotated_Left'] = base64.b64encode(buffer).decode('utf-8')
            except Exception as e:
                print(e)
                response['status_code'] = 400
                response['message'] = 'Images not found'
        elif(imagetype == 'Segmented'):
            try:
                if('Segmented_fingerprintRight0' in data_keys and data['Segmented_fingerprintRight0'] is not None):
                    Segmented_Right = cv2.imread(data['Segmented_fingerprintRight0'])
                    #base64 string encode images
                    _, buffer = cv2.imencode('.png', Segmented_Right)
                    response['Segmented_fingerprintRight0'] = base64.b64encode(buffer).decode('utf-8')
                if('Segmented_fingerprintRight1' in data_keys and data['Segmented_fingerprintRight1'] is not None):
                    Segmented_Left = cv2.imread(data['Segmented_fingerprintRight1'])
                    _, buffer = cv2.imencode('.png', Segmented_Left)
                    response['Segmented_fingerprintRight1'] = base64.b64encode(buffer).decode('utf-8')
                if('Segmented_fingerprintRight2' in data_keys and data['Segmented_fingerprintRight2'] is not None):
                    Segmented_Right = cv2.imread(data['Segmented_fingerprintRight2'])
                    #base64 string encode images
                    _, buffer = cv2.imencode('.png', Segmented_Right)
                    response['Segmented_fingerprintRight2'] = base64.b64encode(buffer).decode('utf-8')
                if('Segmented_fingerprintRight3' in data_keys and data['Segmented_fingerprintRight3'] is not None):
                    Segmented_Left = cv2.imread(data['Segmented_fingerprintRight3'])
                    _, buffer = cv2.imencode('.png', Segmented_Left)
                    response['Segmented_fingerprintRight3'] = base64.b64encode(buffer).decode('utf-8')
                if('Segmented_fingerprintLeft0' in data_keys and data['Segmented_fingerprintLeft0'] is not None):
                    Segmented_Right = cv2.imread(data['Segmented_fingerprintLeft0'])
                    #base64 string encode images
                    _, buffer = cv2.imencode('.png', Segmented_Right)
                    response['Segmented_fingerprintLeft0'] = base64.b64encode(buffer).decode('utf-8')
                if('Segmented_fingerprintLeft1' in data_keys and data['Segmented_fingerprintLeft1'] is not None):
                    Segmented_Left = cv2.imread(data['Segmented_fingerprintLeft1'])
                    _, buffer = cv2.imencode('.png', Segmented_Left)
                    response['Segmented_fingerprintLeft1'] = base64.b64encode(buffer).decode('utf-8')
                if('Segmented_fingerprintLeft2' in data_keys and data['Segmented_fingerprintLeft2'] is not None):
                    Segmented_Right = cv2.imread(data['Segmented_fingerprintLeft2'])
                    #base64 string encode images
                    _, buffer = cv2.imencode('.png', Segmented_Right)
                    response['Segmented_fingerprintLeft2'] = base64.b64encode(buffer).decode('utf-8')
                if('Segmented_fingerprintLeft3' in data_keys and data['Segmented_fingerprintLeft3'] is not None):
                    Segmented_Left = cv2.imread(data['Segmented_fingerprintLeft3'])
                    _, buffer = cv2.imencode('.png', Segmented_Left)
                    response['Segmented_fingerprintLeft3'] = base64.b64encode(buffer).decode('utf-8')
            
            except Exception as e:
                print(e)
                response['status_code'] = 400
                response['message'] = 'Images not found'
        elif(imagetype == 'Enhanced'):
            try:
                if('Enhanced_fingerprintRight0' in data_keys and data['Enhanced_fingerprintRight0'] is not None):
                    Enhanced_Right = cv2.imread(data['Enhanced_fingerprintRight0'])
                    #base64 string encode images
                    _, buffer = cv2.imencode('.png', Enhanced_Right)
                    response['Enhanced_fingerprintRight0'] = base64.b64encode(buffer).decode('utf-8')
                if('Enhanced_fingerprintRight1' in data_keys and data['Enhanced_fingerprintRight1'] is not None):
                    Enhanced_Left = cv2.imread(data['Enhanced_fingerprintRight1'])
                    _, buffer = cv2.imencode('.png', Enhanced_Left)
                    response['Enhanced_fingerprintRight1'] = base64.b64encode(buffer).decode('utf-8')
                if('Enhanced_fingerprintRight2' in data_keys and data['Enhanced_fingerprintRight2'] is not None):
                    Enhanced_Right = cv2.imread(data['Enhanced_fingerprintRight2'])
                    #base64 string encode images
                    _, buffer = cv2.imencode('.png', Enhanced_Right)
                    response['Enhanced_fingerprintRight2'] = base64.b64encode(buffer).decode('utf-8')
                if('Enhanced_fingerprintRight3' in data_keys and data['Enhanced_fingerprintRight3'] is not None):
                    Enhanced_Left = cv2.imread(data['Enhanced_fingerprintRight3'])
                    _, buffer = cv2.imencode('.png', Enhanced_Left)
                    response['Enhanced_fingerprintRight3'] = base64.b64encode(buffer).decode('utf-8')
                if('Enhanced_fingerprintLeft0' in data_keys and data['Enhanced_fingerprintLeft0'] is not None):
                    Enhanced_Right = cv2.imread(data['Enhanced_fingerprintLeft0'])
                    #base64 string encode images
                    _, buffer = cv2.imencode('.png', Enhanced_Right)
                    response['Enhanced_fingerprintLeft0'] = base64.b64encode(buffer).decode('utf-8')
                if('Enhanced_fingerprintLeft1' in data_keys and data['Enhanced_fingerprintLeft1'] is not None):
                    Enhanced_Left = cv2.imread(data['Enhanced_fingerprintLeft1'])
                    _, buffer = cv2.imencode('.png', Enhanced_Left)
                    response['Enhanced_fingerprintLeft1'] = base64.b64encode(buffer).decode('utf-8')
                if('Enhanced_fingerprintLeft2' in data_keys and data['Enhanced_fingerprintLeft2'] is not None):
                    Enhanced_Right = cv2.imread(data['Enhanced_fingerprintLeft2'])
                    #base64 string encode images
                    _, buffer = cv2.imencode('.png', Enhanced_Right)
                    response['Enhanced_fingerprintLeft2'] = base64.b64encode(buffer).decode('utf-8')
                if('Enhanced_fingerprintLeft3' in data_keys and data['Enhanced_fingerprintLeft3'] is not None):
                    Enhanced_Left = cv2.imread(data['Enhanced_fingerprintLeft3'])
                    _, buffer = cv2.imencode('.png', Enhanced_Left)
                    response['Enhanced_fingerprintLeft3'] = base64.b64encode(buffer).decode('utf-8')
            
            except Exception as e:
                print(e)
                response['status_code'] = 400
                response['message'] = 'Images not found'
        elif(imagetype == 'Clahe'):
            try:
                if('Clahe_fingerprintRight0' in data_keys and data['Clahe_fingerprintRight0'] is not None):
                    Clahe_Right = cv2.imread(data['Clahe_fingerprintRight0'])
                    #base64 string encode images
                    _, buffer = cv2.imencode('.png', Clahe_Right)
                    response['Clahe_fingerprintRight0'] = base64.b64encode(buffer).decode('utf-8')
                if('Clahe_fingerprintRight1' in data_keys and data['Clahe_fingerprintRight1'] is not None):
                    Clahe_Left = cv2.imread(data['Clahe_fingerprintRight1'])
                    _, buffer = cv2.imencode('.png', Clahe_Left)
                    response['Clahe_fingerprintRight1'] = base64.b64encode(buffer).decode('utf-8')
                if('Clahe_fingerprintRight2' in data_keys and data['Clahe_fingerprintRight2'] is not None):
                    Clahe_Right = cv2.imread(data['Clahe_fingerprintRight2'])
                    #base64 string encode images
                    _, buffer = cv2.imencode('.png', Clahe_Right)
                    response['Clahe_fingerprintRight2'] = base64.b64encode(buffer).decode('utf-8')
                if('Clahe_fingerprintRight3' in data_keys and data['Clahe_fingerprintRight3'] is not None):
                    Clahe_Left = cv2.imread(data['Clahe_fingerprintRight3'])
                    _, buffer = cv2.imencode('.png', Clahe_Left)
                    response['Clahe_fingerprintRight3'] = base64.b64encode(buffer).decode('utf-8')
                if('Clahe_fingerprintLeft0' in data_keys and data['Clahe_fingerprintLeft0'] is not None):
                    Clahe_Right = cv2.imread(data['Clahe_fingerprintLeft0'])
                    #base64 string encode images
                    _, buffer = cv2.imencode('.png', Clahe_Right)
                    response['Clahe_fingerprintLeft0'] = base64.b64encode(buffer).decode('utf-8')
                if('Clahe_fingerprintLeft1' in data_keys and data['Clahe_fingerprintLeft1'] is not None):
                    Clahe_Left = cv2.imread(data['Clahe_fingerprintLeft1'])
                    _, buffer = cv2.imencode('.png', Clahe_Left)
                    response['Clahe_fingerprintLeft1'] = base64.b64encode(buffer).decode('utf-8')
                if('Clahe_fingerprintLeft2' in data_keys and data['Clahe_fingerprintLeft2'] is not None):
                    Clahe_Right = cv2.imread(data['Clahe_fingerprintLeft2'])
                    #base64 string encode images
                    _, buffer = cv2.imencode('.png', Clahe_Right)
                    response['Clahe_fingerprintLeft2'] = base64.b64encode(buffer).decode('utf-8')
                if('Clahe_fingerprintLeft3' in data_keys and data['Clahe_fingerprintLeft3'] is not None):
                    Clahe_Left = cv2.imread(data['Clahe_fingerprintLeft3'])
                    _, buffer = cv2.imencode('.png', Clahe_Left)
                    response['Clahe_fingerprintLeft3'] = base64.b64encode(buffer).decode('utf-8')
            
            except Exception as e:
                print(e)
                response['status_code'] = 400
                response['message'] = 'Images not found'

        elif(imagetype == 'Ridge'):
            try:
                if('Ridge_fingerprintRight0' in data_keys and data['Ridge_fingerprintRight0'] is not None):
                    Ridge_Right = cv2.imread(data['Ridge_fingerprintRight0'])
                    #base64 string encode images
                    _, buffer = cv2.imencode('.png', Ridge_Right)
                    response['Ridge_fingerprintRight0'] = base64.b64encode(buffer).decode('utf-8')
                if('Ridge_fingerprintRight1' in data_keys and data['Ridge_fingerprintRight1'] is not None):
                    Ridge_Left = cv2.imread(data['Ridge_fingerprintRight1'])
                    _, buffer = cv2.imencode('.png', Ridge_Left)
                    response['Ridge_fingerprintRight1'] = base64.b64encode(buffer).decode('utf-8')
                if('Annotated_fingerprintLeft' in data_keys and data['Ridge_fingerprintRight2'] is not None):
                    Ridge_Right = cv2.imread(data['Ridge_fingerprintRight2'])
                    #base64 string encode images
                    _, buffer = cv2.imencode('.png', Ridge_Right)
                    response['Ridge_fingerprintRight2'] = base64.b64encode(buffer).decode('utf-8')
                if('Ridge_fingerprintRight3' in data_keys and data['Ridge_fingerprintRight3'] is not None):
                    Ridge_Left = cv2.imread(data['Ridge_fingerprintRight3'])
                    _, buffer = cv2.imencode('.png', Ridge_Left)
                    response['Ridge_fingerprintRight3'] = base64.b64encode(buffer).decode('utf-8')
                if('Ridge_fingerprintLeft0' in data_keys and data['Ridge_fingerprintLeft0'] is not None):
                    Ridge_Right = cv2.imread(data['Ridge_fingerprintLeft0'])
                    #base64 string encode images
                    _, buffer = cv2.imencode('.png', Ridge_Right)
                    response['Ridge_fingerprintLeft0'] = base64.b64encode(buffer).decode('utf-8')
                if('Ridge_fingerprintLeft1' in data_keys and data['Ridge_fingerprintLeft1'] is not None):
                    Ridge_Left = cv2.imread(data['Ridge_fingerprintLeft1'])
                    _, buffer = cv2.imencode('.png', Ridge_Left)
                    response['Ridge_fingerprintLeft1'] = base64.b64encode(buffer).decode('utf-8')
                if('Ridge_fingerprintLeft2' in data_keys and data['Ridge_fingerprintLeft2'] is not None):
                    Ridge_Right = cv2.imread(data['Ridge_fingerprintLeft2'])
                    #base64 string encode images
                    _, buffer = cv2.imencode('.png', Ridge_Right)
                    response['Ridge_fingerprintLeft2'] = base64.b64encode(buffer).decode('utf-8')
                if('Ridge_fingerprintLeft3' in data_keys and data['Ridge_fingerprintLeft3'] is not None):
                    Ridge_Left = cv2.imread(data['Ridge_fingerprintLeft3'])
                    _, buffer = cv2.imencode('.png', Ridge_Left)
                    response['Ridge_fingerprintLeft3'] = base64.b64encode(buffer).decode('utf-8')
            
            except Exception as e:
                print('exception:',e)
                response['status_code'] = 400
                response['message'] = 'Images not found'

        elif(imagetype == 'Enrolled'):
            try:
                data_enroll = getEnrollDataForPerson(personid)
                response = getEnrolledImages(data_enroll,response)
            
            except Exception as e:
                print('exception:',e)
                response['status_code'] = 400
                response['message'] = 'Images not found'
        elif(imagetype == 'Verification'):
            try:
                # data_enroll = getEnrollDataForPerson(personid)
                data_verification = db.getImagesfromSession(sessionid)
                response = getVerificationImages(data_verification,response)
            
            except Exception as e:
                print('exception:',e)
                response['status_code'] = 400
                response['message'] = 'Images not found'


        # print(response)
        return response
    elif request.method == 'POST':

        data = request.json
        response = dict()
        response['status_code'] = 200
        response['message'] = 'Enrolled Data deleted successfully.'

        sessionid = data['sessionid']
        print("Deletesessionid",sessionid)
        db.deleteImages(sessionid)
        
        personid = data['personid']
        print("Deletepersonid",personid)
        db.deleteImages(personid)
        return response




if __name__ == "__main__":
    app.run(debug=True,port=19001,host='0.0.0.0')