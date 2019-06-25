
import os
import utils
import spacy
import pprint
from spacy.matcher import Matcher
import multiprocessing as mp
import io

class ResumeParser(object):
    def __init__(self, resume):
        nlp = spacy.load('en_core_web_sm')
        self.__matcher = Matcher(nlp.vocab)
        self.__details = {
            'name'              : None,
            'email'             : None,
            'mobile_number'     : None,
            'skills'            : None,
            'education'         : None,
            'experience'        : None,
            'no_of_pages'       : None,
        }
        self.__resume      = resume
        if not isinstance(self.__resume, io.BytesIO):
            ext = os.path.splitext(self.__resume)[1].split('.')[1]
        else:
            ext = self.__resume.name.split('.')[1]
        self.__text_raw    = utils.extract_text(self.__resume, '.' + ext)
        self.__text        = ' '.join(self.__text_raw.split())
        self.__nlp         = nlp(self.__text)
        self.__noun_chunks = list(self.__nlp.noun_chunks)
        self.__get_basic_details()

    def get_extracted_data(self):
        return self.__details

    def __get_basic_details(self):
        name       = utils.extract_name(self.__nlp, matcher=self.__matcher)
        email      = utils.extract_email(self.__text)
        mobile     = utils.extract_mobile_number(self.__text)
        skills     = utils.extract_skills(self.__nlp, self.__noun_chunks)
        edu        = utils.extract_education([sent.string.strip() for sent in self.__nlp.sents])
        entities   = utils.extract_entity_sections_grad(self.__text_raw)
        self.__details['name'] = name
        self.__details['email'] = email
        self.__details['mobile_number'] = mobile
        self.__details['skills'] = skills
        self.__details['education'] = edu
        try:
            self.__details['experience'] = entities['experience']
        except KeyError:
            self.__details['total_experience'] = 0
        self.__details['no_of_pages'] = utils.get_number_of_pages(self.__resume)
        return