# LFS raw data dictionary (preliminary)

Source: PBS Stata file, 325,445 records and 167 fields.
Labels and codes below are embedded in the Stata file; the separate PBS coding scheme describes sampling codes. Missing codes and questionnaire routing are not yet verified.

| Field | Stata variable label | Read type | Value labels |
|---|---|---|---|
| PCode | Processing Code | str | Not labelled |
| EBCode | BLOCK | float64 | Not labelled |
| HHNo |  | float64 | Not labelled |
| Weights |  | float64 | Not labelled |
| Province |  | category | 1: KP; 2: Punjab; 3: Sindh; 4: Balochistan |
| Region | Region | category | 1: Rural; 2: Urban |
| Quarter |  | str | Not labelled |
| Fstatus |  | float64 | Not labelled |
| SNo |  S.No | float64 | Not labelled |
| S4C3 | Reltionship with Head of Household | category | 1: Head of household; 2:  Spouse; 3:  Son/daughter (unmarried); 4:  Son/daughter (married); 5:  Father/mother; 6:  Brother/sister; 7:  Other relative; 8:  Servant; 9:  Non relative |
| S4C2 | Name of Houshold Member | float64 | Not labelled |
| S4C4 | Present Status | category | 1: Present; 2: Temporaily absent |
| S4C5 | 1'Male' 2'Female' | category | 1: Male; 2: Female |
| S4C6 | Age | float64 | Not labelled |
| S4C7 | Marital Status | category | 1: Never married; 2: Married; 3: Widow/Widower; 4: Divorced |
| S4C81 | Can Read Simple Statement with Understanding | category | 1: Yes' 2'No |
| S4C82 | Can Write Simple Statement with Understanding | category | 1: Yes; 2: No |
| S4C9 | Education Level | category | 1: No formal education; 2: Nursery but below K.G.; 3: K.G but below primary; 4: Primary but below middle; 5: Middle but below matric; 6: Matric but below intermediate; 7: Inter. but below degree; 8: Degree in engineering; 9: Degree in medicine; 10: Degree in computer; 11: Degree in agriculture; 12: Degree in other subjects (2-years); 13: BS/BE (4-years); 14: M.A/M.Sc.; 15: M.Phil/MS; 16: Ph.D |
| S4C10 | Current Enrollment | category | 1: Currently Not Enrolled; 2: Nursery; 3: K.G; 4: Primary; 5: Middle; 6: Matric; 7: Intermediate; 8: Graduation in engineering; 9: Graduation in medicine; 10: Graduation  in computer; 11: Graduation  in agriculture; 12: Graduation  in other subjects; 13: BS/BE (4-years); 14: M.A/M.Sc.; 15: M.Phil/MS; 16: Ph.D |
| S4C11 |   Ever received or currently receiving any training | category | 1: Yes received During Job; 2: Yes received Before Job; 3: Currently Receiving; 4: Not Received/Receiving |
| S4C12 |  Type of Training | float64 | Not labelled |
| S4C13 | Duration of training in weeks | float64 | Not labelled |
| S4C14 |  Provider of training | category | 1: Govt./ Public Technical/ Vocational Institute; 2: Private Technical/ Vocational Institute; 3: Informal apprentice |
| S4C15 | Duration of living in current district | category | 1: Since birth; 2: Less than one year; 3: 1- year; 4: 2- years; 5: 3-years; 6: 4-years; 7: 5-10 years; 8: 11 years  &   over |
| S4C16 | Previous District of living | category | 386 labelled codes; see source |
| S4C17 |  Previous residence located in rural/urban area | category | 1: Rural; 2: Urban |
| S4C18 |  Reason of Migration | category | 1:  Job transfer; 2:  Found a job; 3:  Searching for a job; 4:  Searching for a better agriculture land; 5:  Education; 6:  Business; 7:  Health; 8:  Marriage; 9:  With parents; 10:  With spouse; 11:  With son/ daughter; 12:  Change of residence; 13:  Returned to his home; 14:  Security/ Law & order situation; 15:  Natural disaster; 16:  Floods; 17:  Other |
| S5C1 | Work for pay or wage | category | 1: Yes; 2:  No |
| S5C2 | Run any kind of business/agri farm | category | 1: Yes; 2:  No |
| S5C3 | Help to work in fmaily farm/business | category | 1: Yes; 2:  No |
| S5C4 | Not work last week and have paid job or business | category | 1: Yes; 2:  No |
| S5C5 | Why.. not work last week | category | 1:  Illness or injury; 2:  Shift work, flexi time; 3:  Holiday, ramzan, vacation or leave; 4:  Maternity /parental leave; 5:  Off-season inactivity; 6:  Long term disability; 7:  Strike or lockout; 8:  Due to bad weather; 9:  Due to mechanical or electrical breakdown/ problem in transport; 10:  Due to shortage of raw materials or fuel; 11:  Educational and training leave; 12:  Reductions in economic activity; 13:  Other personal reasons; 15: Other involuntary |
| S5C6 | When will return to the main job | category | 1: Within three months including the time already spent in absence; 2: After three months; 3: Not sure to return |
| S5C7 | ...Receive income from Job/Business in duration of abasence | category | 1: Yes; 2:  No |
| S5C8 | Last week Did you work in... | category | 1: Farming; 2: Rearing farm animals; 3: Fishing or fish farming; 4: None of the above |
| S5C9 |  was this work you mentioned in... | category | 1: Farming; 2: Rearing farm animals; 3: Fishing or fish farming; 4: Any other type of Job or Business |
| S5C10 | products intended for | category | 1: Only for sale; 2: Mainly for sale; 3: Mainly for family use; 4: Only for family use |
| S5C11 | Status of Employment | category | 1: Employers; 2: Independent Worker; 3: Employee; 4: Contributing Family worker; 5: Paid Apprentice; 6: Dependent Contractor |
| S5C12 | Major Occuption | category | 433 labelled codes; see source |
| S5C13 | Major industry | category | 419 labelled codes; see source |
| S5C14a | Activity performed physical/Online | category | 1: Physical/ Manual; 2: Through Internet / Online; 3: Both |
| S5C14b | Digital platform used | category | 1: Selling goods (Amazon, Daraz, Pakwheels, Alibaba, homemade snackes etc.); 2: Taxi Services (inDrive, Yango, Careem, Bykea etc.); 3: Delivery services (Food panda, Panda Mart, Daraz Express, Bykea, etc.); 4: Freelancing Activities (Software developers, Data analysis, Web or logo designer; 5: Medical/Health Care (eShifa, Teleclinics, Sehat Kahani etc; 6: Teaching (Tuition, Teaching, Quraan etc.); 7: Renting Services (Airbnb, Booking.com etc.); 8: On location Services (cleaning, plumbing, etc.); 9: Other Activities (YouTube, TikTok, Vlog etc.); 10: Any other |
| S5C15 | Kind of Establishment | category | 1: 1 Federal Govt.; 2: 2 Provincial Govt.; 3: 3 Local Body Govt.; 4: 4 Public Enterprise (Corp); 5: 5 Public Ltd. Company; 6: 6 Private Ltd. Company; 7: 7 International Organization; 8: 8 An NGO; 9: 9 Agriculture farm; 10: 10  Private Business; 11: 11 Other |
| S5C16 | Business Registered in | category | 1: Yes; 2: No; 3: Dont know |
| S5C17 | Kind of records keeps | category | 1: A complete set of written accounts for tax purposes; 2: Simplified written accounts not for tax purposes; 3: Informal records of orders, sales, purchases; 4: No records are kept; 5: Dont, Know |
| S5C18 | Person engaged in businees/enterprise | float64 | Not labelled |
| S5C19 | Business hire any regular paid employee | category | 1: Yes; 2: No |
| S5C20 | Member of any Association | category | 1: Yes; 2: No; 3: Dont know |
| S5C21 | Where carry out the work | category | 1: At his/her own dwelling; 2: At family or friends dwelling; 3: At the employers house; 4: On the street / road; 5: Agriculture /Poultry/ Livestock /Fishery / Forestry farm; 6: In a shop, business office or industry; 7: Other |
| S5C22 | Location of work | category | 1: Rural; 2: Urban |
| S5C23 | Time to reach work place | category | 1: Less than 30 Minutes; 2: 31-45 Minutes; 3: 46-60 Minutes; 4: 61 Minutes or more |
| S5C24 | Actual Hours work | float64 | Not labelled |
| S5C25 | Any subsidary work or not | category | 1: Yes; 2: No |
| S5C26 | Subsidary Status of Employment | category | 1: Employers; 2: Independent Worker; 3: Employee; 4: Contributing Family worker; 5: Paid Apprentice; 6: Dependent Contractor |
| S5C27 | Subsidary Occuption | category | 433 labelled codes; see source |
| S5C28 | Subsidary industry | category | 419 labelled codes; see source |
| S5C29a | Subsidary Activity performed physical/Online | category | 1: Physical/ Manual; 2: Through Internet / Online; 3: Both |
| S5C29b | Subsidary Digital platform used | category | 1: Selling goods (Amazon, Daraz, Pakwheels, Alibaba, homemade snackes etc.); 2: Taxi Services (inDrive, Yango, Careem, Bykea etc.); 3: Delivery services (Food panda, Panda Mart, Daraz Express, Bykea, etc.); 4: Freelancing Activities (Software developers, Data analysis, Web or logo designer; 5: Medical/Health Care (eShifa, Teleclinics, Sehat Kahani etc; 6: Teaching (Tuition, Teaching, Quraan etc.); 7: Renting Services (Airbnb, Booking.com etc.); 8: On location Services (cleaning, plumbing, etc.); 9: Other Activities (YouTube, TikTok, Vlog etc.); 10: Any other |
| S5C30 | Subsidary Kind of Establishment | category | 1: 1 Federal Govt.; 2: 2 Provincial Govt.; 3: 3 Local Body Govt.; 4: 4 Public Enterprise (Corp); 5: 5 Public Ltd. Company; 6: 6 Private Ltd. Company; 7: 7 International Organization; 8: 8 An NGO; 9: 9 Agriculture farm; 10: 10  Private Business; 11: 11 Other |
| S5C31 | Subsidary Business Registered in | category | 1: Yes; 2: No; 3: Dont know |
| S5C32 | Subsidary Business Kind of records keeps | category | 1: A complete set of written accounts for tax purposes; 2: Simplified written accounts not for tax purposes; 3: Informal records of orders, sales, purchases; 4: No records are kept; 5: Dont, Know |
| S5C33 | Subsidary Person engaged in businees/enterprise | float64 | Not labelled |
| S5C34 | Subsidary Business hire any regular paid employee | category | 1: Yes; 2: No |
| S5C35 | Susidary Hours Work | float64 | Not labelled |
| S5C36 | Additional work other than subisdary | category | 1: Yes; 2: No |
| S5C37 | Nature of Activity did one year ago | category | 1: Same job; 2: Other job in same enterprise; 3: Employee in other enterprise; 4: Independent worker in the same kind of activity; 5: Independent worker in other kind of activity; 6: Not working; 7: Dont know |
| S6C1 | Why worked less than 35 hours | category | 1: Normally works the same number of hours; 2:   Illness or injury; 3:   Long term disability; 4:  Strike or lockout; 5:  Holiday, Ramadan, vacation or leave of absence; 6:  Off-season inactivity; 7:  Due to bad weather; 8:  Due to mechanical or electrical   breakdown; 9:  Due to shortage of raw materials or fuel; 10:  Educational and training leave; 11:  Maternity or parental leave; 12: Other reasons; 13: Other voluntary or personal reasons; 14:  Other involuntary reasons |
| S6C2 | Want to work more hours | category | 1: Yes; 2: No |
| S6C3 | In last 4 weeks did looks for any additional work | category | 1: Yes; 2: No |
| S6C4 | Could start additional work in next two weeks | category | 1: Yes; 2: No |
| S6C5 | Does you want to change current employment situtation | category | 1: Yes; 2: No |
| S6C6 | Reason why to change employment situation | category | 1:  Present job  is temporary; 2:  To have a better paid job; 3:  To have more business; 4:  To work more hours; 5:  To work fewer hours; 6:  To better match skills; 7:  To work closer to home; 8:  To improve other working conditions; 9:  Present work is unpaid; 10: Other |
| S7C1 | Status of job/Work | category | 1:  Permanent/ pensionable Job; 2:  Less than 3 months; 3:  3 months to less than  12 Months; 4:  12 Months to less than 24 Months; 5:  2 years to less than 3 year; 6:  3 years or more; 7: Without contract/ agreement |
| S7C2 | Periodicity of Payment | category | 1: Daily; 2:  Weekly; 3:  Fortnightly; 4:  Monthly; 5:  Other periodicity; 6:  Piece rate basis for service performed; 7:  Other |
| S7C31 | Net money earn in Cash in last week | float64 | Not labelled |
| S7C32 | Net money earn in in kind in last week | float64 | Not labelled |
| S7C33 | Net money earn in Total in last week | float64 | Not labelled |
| S7C41 | Net money earn in Cash in las month | float64 | Not labelled |
| S7C42 | Net money earn in kind in last month | float64 | Not labelled |
| S7C43 | Net money earn in total  in last month | float64 | Not labelled |
| S7C51 | Net money in bousnes in cash in last year | float64 | Not labelled |
| S7C52 | Net money in bousnes in Kind in last year | float64 | Not labelled |
| S7C53 | Net money in bousnes in Total in last year | float64 | Not labelled |
| S7C61 | Old age Pension. | float64 | Not labelled |
| S7C62 | Family support in case of death of bread winner | float64 | Not labelled |
| S7C63 | Fee reimbursement/education stipend | float64 | Not labelled |
| S7C64 | Disability Insurance/Social Insurance | float64 | Not labelled |
| S7C65 | Medical facilities | float64 | Not labelled |
| S7C66 | Marrage Grant | float64 | Not labelled |
| S7C67 | Child Stipend | float64 | Not labelled |
| S7C68 | None | float64 | Not labelled |
| S7C7 | Does... get paid annual leave | category | 1: Yes; 2: No; 3: Dont know |
| S7C8 | Does.... get Paid Sick leave | category | 1: Yes; 2: No; 3: Dont know |
| S7C9 | Net money earn during last year | float64 | Not labelled |
| S8C1 | In past 12months, did.. suffer from injury | category | 1: Only one; 2: More than one Specify how many; 3: None |
| S8C21 | Main cause of 1st injury | category | 1:  A traffic accident on the way to/from work; 2:  Tiring or painful positions, repetitive hand or arm movements; 3:  Manual handling and lifting; 4:  Falling objects; 5:  Electrical Hazards; 6:  Fatigue and stress; 7:  Fire & explosions; 8:  Other injuries (Specify); 9:  Exposure to hazardous substances such as chemicals, body fluids, dust, fumes, s; 10:  Biological Hazards; 11:  Radiation; 12:  inadequate ventilation and air quality; 13:  Inadequate health and  safety policies; 14:  Other diseases  (Specify) |
| S8C22 | Main cause of 2nd Injury | category | 1:  A traffic accident on the way to/from work; 2:  Tiring or painful positions, repetitive hand or arm movements; 3:  Manual handling and lifting; 4:  Falling objects; 5:  Electrical Hazards; 6:  Fatigue and stress; 7:  Fire & explosions; 8:  Other injuries (Specify); 9:  Exposure to hazardous substances such as chemicals, body fluids, dust, fumes, s; 10:  Biological Hazards; 11:  Radiation; 12:  inadequate ventilation and air quality; 13:  Inadequate health and  safety policies; 14:  Other diseases  (Specify) |
| S8C23 | Main cause of 3rd injury | category | 1:  A traffic accident on the way to/from work; 2:  Tiring or painful positions, repetitive hand or arm movements; 3:  Manual handling and lifting; 4:  Falling objects; 5:  Electrical Hazards; 6:  Fatigue and stress; 7:  Fire & explosions; 8:  Other injuries (Specify); 9:  Exposure to hazardous substances such as chemicals, body fluids, dust, fumes, s; 10:  Biological Hazards; 11:  Radiation; 12:  inadequate ventilation and air quality; 13:  Inadequate health and  safety policies; 14:  Other diseases  (Specify) |
| S8C3 | How many days been away from work | category | 1: 1 to 3 days; 2:   4 to 7 days; 3:  8 days to 1 month; 4:  2 to 4 months after the accident/ disease; 5:  5 to 7 months after the accident/disease; 6: 8 to 12 months after the accident/ disease; 7:   Dont Know |
| S8C4 | Did.. return to the same job | category | 1:   Yes; 2:  Still not at work/have not resumed normal activities; 3:  Will never be able to go back to work/resume normal activities |
| S8C5 | Did.. received medical treatment for the injury | category | 1: Yes, was Hospitalized; 2: Yes, received outpatient treatment; 3:  No; 4:   Dont know |
| S8C6 | Did... receive anu injury compensation | category | 1: Yes; 2: No |
| S9C1 | Was looking for work during last 4-weeks | category | 1: Yes; 2: No |
| S9C21 | Applied to prospective employer | float64 | Not labelled |
| S9C22 | Take a test or interview | float64 | Not labelled |
| S9C23 | Post/Update resume or professional/social networking sites | float64 | Not labelled |
| S9C24 | Checked at work sites, farms, factories, markets, etc. | float64 | Not labelled |
| S9C25 | Applied for permit or license to set up own enterprise such as a shop, business, | float64 | Not labelled |
| S9C26 | Looked for land, building, machinery or equipment for setting up own enterprise | float64 | Not labelled |
| S9C27 | Sought assistance from friends or relatives | float64 | Not labelled |
| S9C28 | Placed or answered advertisements | float64 | Not labelled |
| S9C29 | Registered with Government employment agency | float64 | Not labelled |
| S9C210 | Registered with Private Employment Agency | float64 | Not labelled |
| S9C211 | Arranged for financial resources | float64 | Not labelled |
| S9C212 | Applied for loan/credit | float64 | Not labelled |
| S9C213 | Other (Specify) | float64 | Not labelled |
| S9C3 | How long was being looking for work | category | 1: Less than one month; 2: one month to three months; 3: Three months to six months; 4: six months to 12 months; 5: One year and over |
| S9C4 | At present does want to work for pay or start a business | category | 1: Yes; 2: No |
| S9C5 |  Reasons why did not try to find paid job or start business | category | 1: Already has a job or business to start in the near future; 2: Awaiting to be recalled from a previous job; 3: Waiting for results from a previous search; 4: Waiting for the season to start; 5: Tired of looking, no jobs in the area; 6: No jobs matching his/her skills, lacks experience; 7: Considered too be young/too be old by employers; 8: Family does not approve; 9: Busy studying or doing apprentice work; 10: Busy with household or family responsibilities; 11:  Busy farming or fishing for household use; 12: With a disability, injury or illness; 13: Has other sources of income; 14: Other (Specify) |
| S9C6 | Could start work within next 2 weeks | category | 1: Yes; 2: No |
| S9C7 | Type of work would prefer to do | category | 1: Full-time Job in Public Sector; 2: Full time Job with private Sector/business; 3: Part-time paid employment; 4: Self employment in own business; 5: Other work (short term work, casual, daily work); 6: Any type of work |
| S9C8 | Where would you willing to work | category | 1: Within this household only; 2: Within this village/ town/city only; 3: Anywhere in this district only; 4:  Anywhere in Pakistan only; 5:  Abroad |
| S9C9 | Why not available to start work within next two weeks | category | 1: Illness; 2: Will take a job within a  month; 3: Temporarily laid off; 4: Apprentice and not  willing to work; 5: Agricultural landlord/ property owner and not willing to work; 6: Too young to work; 7: Student and not willing to work; 8: Unable to work/handicapped; 9: Housekeeping and not willing to work; 10: Retired and not willing to work; 11: Too old to work; 12: Family does not allow to work; 13: Other reason |
| S9C10 | Registered with private employment agency | category | 1: Yes; 2: No |
| S9C11 | How long ago you stop working | category | 1:  Less than one month ago; 2:  1 To less than 3 months ago; 3:  3 To less than 6 months ago; 4:  6 To less than 12 months ago; 5:  1 To less than 3 years ago; 6:  3 To less than 5 years ago; 7:  5 To less than 8 years ago; 8:  8 years and more ago; 9:  Dont know |
| S9C12 |  Main Occuption | category | 433 labelled codes; see source |
| S9C13 | Main Industry | category | 419 labelled codes; see source |
| S9C14 |  Worked as.... | category | 1:  Employer; 2:  Independent worker without employee; 3:  Employee; 4:  Contributing family worker; 5:  Paid apprentice, internee; 6:  Dependent contractor |
| S9C15 | For how many years been doing this sort of work | category | 1:  Less than one year; 2: one year but less than 5 years; 3:  Five year but less than 10 Years; 4:  10 Years and above |
| S9C16 | Main reasons for leaving the last job/business | category | 1: Dismissed or made redundant; 2: A job of limited duration has ended; 3: Personal or family responsibilities; 4: Own illness or disability; 5: Education or training; 6: Early retirement; 7: Normal retirement; 8: Could not do the job; 9: Did not like the job; 10: Did not like the employer; 11: The pay was too low; 12: Not consistent with qualification; 13: Violence/harassment at work place, Security/law & order situation; 14: Other  (Specify) |
| S9C17 |  Does receive any of the following benifts | category | 1:  Old age benefit; 2:  Disability benefit; 3:  Unemployment benefit; 4:  Child Stipend; 5:  BISP; 6:  Sehat Card; 7:  Other (Specify); 8:  None |
| S9C171 | Old age benefit | float64 | Not labelled |
| S9C172 | Desability benefits | float64 | Not labelled |
| S9C173 | Unemployment Benefit | float64 | Not labelled |
| S9C174 | Child Stipend | float64 | Not labelled |
| S9C175 | BISP | float64 | Not labelled |
| S9C176 | Sehat Card | float64 | Not labelled |
| S9C177 | Other | float64 | Not labelled |
| S9C178 | None | float64 | Not labelled |
| S10C10_1a | Work or help in agricultural operations | category | 1: Yes; 2:  No |
| S10C10_1b | Hours | float64 | Not labelled |
| S10C10_2a | Work or help in livestock operations | category | 1: Yes; 2:  No |
| S10C10_2b | Hours | float64 | Not labelled |
| S10C10_3a | Work or help poultry raising | category | 1: Yes; 2:  No |
| S10C10_3b | Hours | float64 | Not labelled |
| S10C10_4a | Gather wild food | category | 1: Yes; 2:  No |
| S10C10_4b | Hours | float64 | Not labelled |
| S10C10_5a | Fishing or hunting | category | 1: Yes; 2:  No |
| S10C10_5b | Hours | float64 | Not labelled |
| S10C10_6a | Prepare preserved food or drinks for storage | category | 1: Yes; 2:  No |
| S10C10_6b | Hours | float64 | Not labelled |
| S10C10_7a | Construction work to build, renovate or extend the family home or help a family | category | 1: Yes; 2:  No |
| S10C10_7b | Hours | float64 | Not labelled |
| S10C10_8a | Spend any time making goods for use by your household or family | category | 1: Yes; 2:  No |
| S10C10_8b | Hours | float64 | Not labelled |
| S10C10_9a | Fetch water from natural or public sources | category | 1: Yes; 2:  No |
| S10C10_9b | Hours | float64 | Not labelled |
| S10C10_10a | Collect any firewood | category | 1: Yes; 2:  No |
| S10C10_10b | Hours | float64 | Not labelled |
| S10C10_11a | Spend time in caring for children or health care of ill/aged persons | category | 1: Yes; 2:  No |
| S10C10_11b | Hours | float64 | Not labelled |
| S10C10_12a | Spend time in helping children do homework or other educating activities | category | 1: Yes; 2:  No |
| S10C10_12b | Hours | float64 | Not labelled |
| S10C10_13a | Spend time in cleaning and arranging the house, washing, cooking,  mending or pr | category | 1: Yes; 2:  No |
| S10C10_13b | Hours | float64 | Not labelled |
| S10C10_14a | Spend time in other services activities. | category | 1: Yes; 2:  No |
| S10C10_14b | Hours | float64 | Not labelled |
