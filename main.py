#! /bin/env python3
from ast import Eq
import numpy as np
import cv2
from mss import mss
from PIL import Image
import pytesseract
import mouse
import time
import sys
import os
from collections import Counter
import random
import re
import card_logic
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

#Pixel locations for certain game buttons
opp = {'top': 955, 'left': 1087, 'width': 30, 'height': 25}
me = {'top': 1227, 'left': 1336, 'width': 40, 'height': 25}
indicator = {'top': 827, 'left': 1089, 'width': 500, 'height': 38}
stand2 = {'top': 720, 'left': 1465, 'width': 90, 'height': 40}

#Open CV detects the stand button to say this instead of "stand"
stand_nickname = "Ear te)"



def main():
    print("Application Running...")
    counter = 0;
    while 1:
        sct = mss()
        sct.get_pixels(indicator)
        indicator_img = Image.frombytes('RGB', (sct.width, sct.height), sct.image)
        indicator_nparr = np.array(indicator_img)

        counter += 1;
        ## Indicator image capture
        if ((counter%100) == 0):
            indicator_gry = cv2.cvtColor(indicator_nparr, cv2.COLOR_BGR2GRAY)
            indicator_thr = cv2.adaptiveThreshold( indicator_gry, 255, cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV, 11, 4)
            #cv2.imshow('test',  indicator_thr)
            indicator_txt = pytesseract.image_to_string(indicator_thr)

            ## if "place your bets" then bet
            if "CLOSING" in indicator_txt:
                print("Betting...")
                mouse.move(1460,1200, duration=0.2)
                #click
                time.sleep(3)
                player, dealer = scan()
                card_logic.compute(player, dealer)
            if cv2.waitKey(2) & 0xFF == ord('q'):
                break
            


def scan():
    # Wait for hit stand buttons then scan cards, or restart the app if new game
    print("Waiting for HIT/STAND Buttons")
    counter = 0
    stand_txt = ""
    while stand_nickname not in stand_txt:
        counter += 1;

        # If Indicator says "place your bets" then restart the application
        sct = mss()
        sct.get_pixels(indicator)
        indicator_img = Image.frombytes('RGB', (sct.width, sct.height), sct.image)
        indicator_nparr = np.array(indicator_img)
        if ((counter%10) == 0):
            indicator_gry = cv2.cvtColor(indicator_nparr, cv2.COLOR_BGR2GRAY)
            indicator_thr = cv2.adaptiveThreshold( indicator_gry, 255, cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV, 11, 4)
            indicator_txt = pytesseract.image_to_string(indicator_thr)
            if "PLEACE" in indicator_txt or "PUACE" in indicator_txt:
                print("Application restarting, Starting new game...")
                main()

        # If not restart then scan and wait for HIT STAND buttons
        sct.get_pixels(stand2)
        stand_img = Image.frombytes('RGB', (sct.width, sct.height), sct.image)
        stand_nparr = np.array(stand_img)
        stand_nparr = 255 - stand_nparr
        stand_txt = ""
        stand_gry = cv2.cvtColor(stand_nparr, cv2.COLOR_BGR2GRAY)
        stand_thr = cv2.adaptiveThreshold( stand_gry, 255, cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV, 11, 4)
        stand_txt = pytesseract.image_to_string( stand_thr)
        # cv2.imshow('test',  stand_thr)
        if cv2.waitKey(2) & 0xFF == ord('q'):
            break

    counter = 0;
    player_txt = "";
    dealer_txt = "";
    final_dealer_hand = "";
    final_player_hand = "";
    print("Scan")
    while True:
        #Scan Dealer Hand
        sct = mss()
        sct.get_pixels(opp)
        img = Image.frombytes('RGB', (sct.width, sct.height), sct.image)
        nparr = np.array(img)
        gray = cv2.cvtColor(nparr, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 4)
        thresh = cv2.bitwise_not(thresh)
        double = cv2.resize(thresh, None, fx=2, fy=2)
        
        #Scan Player Hand
        sct.get_pixels(me)
        player_img = Image.frombytes('RGB', (sct.width, sct.height), sct.image)
        player_nparr = np.array(player_img)
        player_gray = cv2.cvtColor(player_nparr, cv2.COLOR_BGR2GRAY)
        player_thresh = cv2.adaptiveThreshold(player_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 4)
        player_thresh = cv2.bitwise_not(player_thresh)
        player_double = cv2.resize(player_thresh, None, fx=2, fy=2)

        counter +=1;
        ## Dealer image capture
        if ((counter%100)==0):
            dealer_txt = pytesseract.image_to_string(double, config="--psm 7 digits")
            if cv2.waitKey(2) & 0xFF == ord('q'):
                break

        ## Player image capture
        if ((counter%100)==0):
            player_txt = pytesseract.image_to_string( player_double, config="--psm 7 digits")
            if cv2.waitKey(2) & 0xFF == ord('q'):
                break
        
        if player_txt and not player_txt.isspace():
            player_list = []
            dealer_list = []
            player_list.append(player_txt)
            dealer_list.append(dealer_txt)

            if ((counter%100)==0):
                counts = Counter(player_list)
                greatest = max(counts.values())
                final_player_hand = random.choice([item for item, count in counts.items() if count == greatest])
                final_player_hand = final_player_hand.replace(" ", "")
                final_player_hand = re.search(r'\d+',final_player_hand).group()
                final_player_hand = int(final_player_hand)

                counts2 = Counter(dealer_list)
                greatest2 = max(counts2.values())
                final_dealer_hand = random.choice([item for item, count in counts2.items() if count == greatest2])
                final_dealer_hand = final_dealer_hand.replace(" ", "")
                final_dealer_hand = re.search(r'\d+',final_dealer_hand).group()
                final_dealer_hand = int(final_dealer_hand)

                print("PLAYER: ",final_player_hand)
                print("DEALER: ",final_dealer_hand)
                break

    return final_player_hand, final_dealer_hand


    

def hit():
    print("Hit")
    mouse.move(1340,711, duration=0.2)
    #click
    time.sleep(10)

def stand():
    print("Stand")
    mouse.move(1471,700, duration=0.2)
    #click
    time.sleep(10)

def double():
    print("Double")
    mouse.move(1205,726, duration=0.2)
    #click
    time.sleep(10)









if __name__ == '__main__':
    _, *script_args = sys.argv
    main(*script_args)