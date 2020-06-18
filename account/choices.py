from datetime import date
BRANCH = [
    ('ND', '---'),
    ('CE', 'Civil Eng.'),
    ('CS', 'Computer Science Eng.'),
    ('EC', 'Electronics & Commu.'),
    ('EEE','Electrical and Electronics Eng.'),
    ('IT', 'Information Tech.'),
    ('ME', 'Mechanical Eng.'),
    ('MCA', 'Master of Computer App.'),
]

year = date.today().year
YEARSSTART= [x for x in range(1990,year-2)]
def yearsend(startyear):
    YEARSEND = [int(startyear)+4,]
    return YEARSEND
    
BRANCH_JSON= []
for i in BRANCH :
 BRANCH_JSON.append({"id":i[0],"branch":i[1]})
