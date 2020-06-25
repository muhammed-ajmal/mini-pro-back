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


JOB_TYPES = [
    ('FT','Full Time'),
    ('PT','Part Time'),
    ('IN', 'Intern'),
    ('CN', 'Contract'),

]

APPL_STATUS =[
('APP','Approved'),
('PED','Pending'),
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

JOB_TYPES_JSON=[]
for i in JOB_TYPES :
 JOB_TYPES_JSON.append({"id":i[0],"type":i[1]})
