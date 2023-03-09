# Build remote request to call SOLR server.

import pysolr


# Default URL.
class URLAddress:
    ADDRESS = 'http://localhost:8993/solr/AddressIndex'
    NAME = 'http://localhost:8993/solr/NameIndex'


# Define the core location of SOLR index with the field name.
CORE_LOCATION = {
    'branchName': URLAddress.ADDRESS,
    'applicantName': URLAddress.NAME,
    'minorGuardiansName': URLAddress.NAME,
    'mothersName': URLAddress.NAME,
    'grandFatherName': URLAddress.NAME,
    'grandMotherName': URLAddress.NAME,
    'husbandWifeName': URLAddress.NAME,
    'permanentToleStreet': URLAddress.ADDRESS,
    'permanentMunicipality': URLAddress.ADDRESS,
    'permanentDistrict': URLAddress.ADDRESS,
    'permanentState': URLAddress.ADDRESS,
    'permanentCountry': URLAddress.ADDRESS,
    'currentToleStreet': URLAddress.ADDRESS,
    'currentMunicipality': URLAddress.ADDRESS,
    'currentDistrict': URLAddress.ADDRESS,
    'currentState': URLAddress.ADDRESS,
    'currentCountry': URLAddress.ADDRESS,
    'officeToleStreet': URLAddress.ADDRESS,
    'officeMunicipality': URLAddress.ADDRESS,
    'district': URLAddress.ADDRESS,
    'officeState': URLAddress.ADDRESS,
    'officeCountry': URLAddress.ADDRESS,
    'localContactName': URLAddress.NAME,
    'localContactAddress': URLAddress.ADDRESS,
    'landlordName': URLAddress.NAME,
    'idIssuedPlace': URLAddress.ADDRESS,
    'salariedInstitutionName': URLAddress.NAME
}

# Address Index.
addressIndex = pysolr.Solr(URLAddress.ADDRESS_URL, timeout=10)

# Name Index.
nameIndex = pysolr.Solr(URLAddress.NAME_URL, timeout=10)


class SOLRRequest:
    # Default constructor.
    def __init__(self, textGrams: list[list[str]], fieldName: str):
        self.textGrams = textGrams
        self.fieldName = fieldName

    # Check if the grams set is empty.
    def __isEmpty(self):
        return len(self.textGrams) < 1

    # Extract URL part of the get SOLR query.
    def __extractURL(self):
        print(self.fieldName)
        return CORE_LOCATION.get(self.fieldName, None)

    # NGram query part.
    def __ngramPart(self, grams):
        gramsBoost = [f'{self.fieldName}:({gram})^{2 ** (len(gram) - 1)}' for gram in grams]
        return ' OR '.join(gramsBoost)

    # Combine list items.
    def __combineTextGrams(self, grams):
        return "".join(grams)

    # Build URL.
    def __buildURL(self):
        url = self.__extractURL()
        return None if not url else f'{url}{self.__ngramPart()}'

    # Get Request Template.
    def __buildQuery(self) -> str:
        return None if self.__isEmpty() else self.__buildURL()

    def __unionOfGrams(self):
        return set([item for beamGram in self.textGrams for item in beamGram])

    def __partialAddress(self):
        query = self.__ngramPart(self.__unionOfGrams())
        response = addressIndex.search(query, results_cls=dict, rows=1)

        response.items()[0]

        value = None
        for doc in response:
            value = doc[f'{self.fieldName}']

        return value

    def __singleWord(self, beam: list[str]) -> str:
        return "".join(beam)

    def __exactAddressSearch(self):
        result = None
        for beam in self.textGrams:
            response = addressIndex.search(f'{self.fieldName}Str:"{self.__singleWord(beam)}"', results_cls=dict)
            if len(response) > 0:
                result = response[0][f'{self.fieldName}Str']
                break
        return result

    # Perform address search.
    def __addressSearch(self):
        exact = self.__exactAddressSearch()
        return self.__partialAddress() if not exact else exact

    # Perform name search.
    def __nameSearch(self):
        return URLAddress.NAME

    # Build result.
    # Needs to work here.
    def findBestMatch(self):
        # 1. Find if it has exact solution as the best one.
        # 2. Find approximated bast solution by finding the union of token and
        #    result from the SOLR index.
        print(f"Match {self.__extractURL()}")
        match self.__extractURL():
            case URLAddress.ADDRESS:
                return self.__addressSearch()
            case URLAddress.NAME:
                return self.__nameSearch()
            case None:
                return None
