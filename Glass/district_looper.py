i = 1
d = 1
state = 'AL'
while i < 436:
	if i == 8:
		state = 'AK'
		d = 1
	if i == 9:
		state = 'AZ'
		d = 1
	if i == 18:
		state = 'AR'
		d = 1
	if i == 22:
		state = 'CA'
		d = 1
	if i == 75:
		state = 'CO'
		d = 1
	if i == 82:
		state = 'CT'
		d = 1
	if i == 87:
		state = 'DE'
		d = 1
	if i == 88:
		state = 'FL'
		d = 1
	if i == 115:
		state = 'GA'
		d = 1
	if i == 129:
		state = 'HI'
		d = 1
	if i == 131:
		state = 'ID'
		d = 1
	if i == 133:
		state = 'IL'
		d = 1	
	if i == 151:
		state = 'IN'
		d = 1
	if i == 160:
		state = 'IA'
		d = 1
	if i == 164:
		state = 'KS'
		d = 1
	if i == 168:
		state = 'KY'
		d = 1
	if i == 174:
		state = 'LA'
		d = 1
	if i == 180:
		state = 'ME'
		d = 1
	if i == 182:
		state = 'MD'
		d = 1
	if i == 190:
		state = 'MA'
		d = 1
	if i == 199:
		state = 'MI'
		d = 1
	if i == 213:
		state = 'MN'
		d = 1
	if i == 221:
		state = 'MS'
		d = 1
	if i == 225:
		state = 'MO'
		d = 1
	if i == 233:
		state = 'MT'
		d = 1
	if i == 234:
		state = 'NE'
		d = 1
	if i == 237:
		state = 'NV'
		d = 1
	if i == 241:
		state = 'NH'
		d = 1
	if i == 243:
		state = 'NJ'
		d = 1
	if i == 255:
		state = 'NM'
		d = 1
	if i == 258:
		state = 'NY'
		d = 1
	if i == 285:
		state = 'NC'
		d = 1
	if i == 298:
		state = 'ND'
		d = 1
	if i == 299:
		state = 'OH'
		d = 1
	if i == 315:
		state = 'OK'
		d = 1
	if i == 320:
		state = 'OR'
		d = 1
	if i == 325:
		state = 'PA'
		d = 1
	if i == 343:
		state = 'RI'
		d = 1
	if i == 345:
		state = 'SC'
		d = 1
	if i == 352:
		state = 'SD'
		d = 1
	if i == 353:
		state = 'TN'
		d = 1
	if i == 362:
		state = 'TX'
		d = 1
	if i == 398:
		state = 'UT'
		d = 1
	if i == 402:
		state = 'VT'
		d = 1
	if i == 403:
		state = 'VA'
		d = 1
	if i == 414:
		state = 'WA'
		d = 1
	if i == 424:
		state = 'WV'
		d = 1
	if i == 427:
		state = 'WI'
		d = 1
	if i == 427:
		state = 'WI'
		d = 1
	if i == 435:
		state = 'WY'
		d = 1
	if i == 436:
		state = 'WI'
		d = 1
	district = '%s:%d' % (state, d)
	print district
	i += 1
	d += 1