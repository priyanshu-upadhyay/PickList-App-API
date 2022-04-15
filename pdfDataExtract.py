import fitz
import pyrebase
from datetime import date
import os
from pyairtable import Api, Base, Table
today = date.today()

def getTableData():
    api = Api('keySEggjjmQflEbcj')
    table1 = Table('keySEggjjmQflEbcj', 'app6y22UosSuCzuuI', 'Table 1')
    return table1.all()



def getImage(productid, productname, tableAll):
    for records in tableAll:
        if(records['fields']['Product Code'] == productid and 'Attachments' in records['fields']):
            url = records['fields']['Attachments'][0]["url"]
            return url
    else:
        return "https://dl.airtable.com/.attachments/65efc8359db42a0152fa467bc519f5b5/eb1a3d08/defaultimage.png"
        
        

def processPDF():

    config = {
    "apiKey": "AIzaSyDUXLsUt3xmWu0ExTcfJEAQHnzvfpyXiBk",
    "authDomain": "itempicklist.firebaseapp.com",
    "databaseURL": "https://itempicklist-default-rtdb.firebaseio.com",
    "projectId": "itempicklist",
    "storageBucket": "itempicklist.appspot.com",
    "messagingSenderId": "893490853778",
    "appId": "1:893490853778:web:e07d2223793c6a6ba4334b",
    "measurementId": "G-KVFN0SLQ24"
    }

    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    allfiles = os.listdir("./uploaded_files")

    tableall = getTableData()

    today = date.today()
    for fileitem in allfiles:
        if fileitem.startswith(str(today)) and fileitem.endswith(".pdf"):
            doc = fitz.open("./uploaded_files/"+fileitem)
            page1 = doc[0]
            words = page1.get_text("words")
            line_dict = {} 

            words.sort(key=lambda w: w[0])

            for w in words:  

                y1 = round(w[3], 1)  

                word = w[4] 

                line = line_dict.get(y1, [])  

                line.append(word)  

                line_dict[y1] = line  
            lines = list(line_dict.items())
            lines.sort()  

            result = {}

            table = []
            recipt_header = " ".join(line_dict[39.0]).title()
            billing_date = line_dict[57.5][-1]
            result["recipt_header"] = recipt_header
            result["billing_date"] = billing_date



            start = 0
            pre = 0
            for i in lines:
                if(start == 0 and i[1] == ['(PC)', '(PC)']):
                    start = 1
                elif(i[1][0] == "Total:"):
                    start = 0
                    break
                elif(start == 1):
                    if(int(i[0]) == pre or int(i[0]) == pre + 1):
                        table[-1].insert(2, " ".join(i[1]))
                    else:
                        table.append(i[1])
                    pre = int(i[0])
                    
                

            finalTable = []
            for entry in table:
                temp = []
                temp.append(int(entry[0]))
                product_id = entry[1]
                temp.append(product_id)
                product_name = ""
                price_index = -1

                for i in range(2, len(entry)):
                    if('.' in entry[i] and entry[i].replace('.', '', 1).isdigit()):
                        price_index = i
                        break
                    product_name = product_name + " " + entry[i]

                temp.append(product_name.strip())
                productUrl = getImage(product_id, product_name, tableall)
                temp.append(float(entry[price_index]))
                
                for i in range(price_index + 1, price_index+6):
                    if(entry[i] == '-'):
                        temp.append(0)
                    else:
                        temp.append(int(entry[i]))
                temp.append(productUrl)
                finalTable.append(temp)


            # Second Last Column
            total_value = lines[-2][1][-2]
            no_of_invoices = lines[-2][1][4]


            # Last Column
            lastCol = lines[-1][1]

            picklist_number = lastCol[lastCol.index(":") + 1]
            salesman = " ".join(lastCol[lastCol.index("Salesman:") + 1 : lastCol.index("Route:")])
            route = " ".join(lastCol[lastCol.index("Route:")+1:])




            result["entries"] = finalTable
            result["total_value"] = total_value
            result["no_of_invoices"] = int(no_of_invoices)
            result["salesman"] = salesman.title()
            result["route"] = route

            

            today = date.today()
            response = db.child(str(today)).child(picklist_number).set(result)
    return "Data Processed. Thank You for Using"



    # remove files


