import re

#PASSED
#Customer and Business Validation
def validate_username(username):
    #Checks if username contains letters, numbers, and '_'... It cannot have spaces.
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return False, "Username must be 3-20 characters long and can only contain letters, numbers, and underscores."
    if ' ' in username:
        return False, "Username cannot contain spaces."
    return True, ""

#PASSED
#Customer and Business Validation
def validate_password(password):
    #Checks if password is at least 6 characters long and contains no spaces.
    if len(password) < 6:
        return False, "Password must be at least 7 characters long."
    if ' ' in password:
        return False, "Password cannot contain spaces."
    return True, ""

#PASSED
#Customer and Business Validation
def validate_name(firstname, lastname):
    
    errors = []

    #Checks if name is at least 2 characters longs
    if not re.match(r'^[a-zA-Z\s]{3,30}$', firstname):
        errors.append("First name can only contain letters and spaces and only limited 3 - 30 characters.")
    if not re.match(r'^[a-zA-Z\s]{3,30}$', lastname):
        errors.append("Last name can only contain letters and spaces and only limited 3 - 30 characters.")
    if errors:
        return False, errors 
    return True, ""


#Customer and Business Validation
def validate_location(country, state, city):

    errors = []

    #Checks if country, state, city only contains letters
    if not re.match(r'^[a-zA-Z\s]+$', country):
        errors.append("Country can only contain letters and spaces.")
    if not re.match(r'^[a-zA-Z\s]+$', state):
        errors.append("State can only contain letters and spaces.")
    if not re.match(r'^[a-zA-Z\s]+$', city):
        errors.append("City can only contain letters and spaces.")
    
    if errors:
        return False, errors 
    return True, ""

#PASSED
#Customer and Business Validation
def validate_address(address):
    #Checks if address is valid
    if not re.match(r'^[a-zA-Z0-9\s,.-]{1,100}$', address):
        return False, "Address must be 2-100 characters long and can contain letters, numbers, and certain punctuation marks."
    return True, ""

#Business Validation
def validate_businessname(businessname):
    if not re.match(r'^[a-zA-Z0-9\s]{3,30}$'):
        return False, "Business name can only contain letters, numbers, and spaces. only limited 3 - 30 characters."
    return True


#def capitalize(firstname, lastname, country, state, city):
    
    #firstname = firstname.capitalize()
    #lastname = lastname.capitalize()
    #country = country.capitalize()
    #state = state.capitalize()
    #city = city.capitlize()

    #return firstname,lastname,country,state,city 

