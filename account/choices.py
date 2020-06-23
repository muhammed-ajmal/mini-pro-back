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

VERIF_STATUS = [
    ('PD', 'PENDING'),
    ('ND', 'NOT VALID'),
    ('VD','VERIFIED'),
]

year = date.today().year
YEARSSTART= [x for x in range(1990,year-2)]
def yearsend(startyear):
    YEARSEND = [int(startyear)+4,]
    return YEARSEND

BRANCH_JSON= []
BRANCH_WITHOUT_ND = BRANCH
BRANCH_WITHOUT_ND.pop(0)
for i in BRANCH_WITHOUT_ND :
 BRANCH_JSON.append({"id":i[0],"branch":i[1]})
